from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.services.database.data_builder import PlayedTrackDTO

from SpotifyController.services.construct_data import PlaylistClass

from django.db import transaction
from django.shortcuts import get_object_or_404

import logging
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService


from SpotifyController.models.models import (
    Track,
    Playlist
)
from SpotifyController.models.through import FavoriteUserTracks, RecommendationTracks, UsersListenHistory

from User.models import CustomUser

from typing import (List, Type, Union)

import random

from User.services import UserService

logger = logging.getLogger(__name__)

class SaveUserDataService:
    def __init__(self, user: CustomUser):
        self.user = user
        self.user_service = UserService()
        self.user_cache_service = UserCacheService(user_id=user.id)

    def _clear_existing_tracks(self, tracks: List[Track], model: Union[Type[FavoriteUserTracks], Type[RecommendationTracks]]) -> List[Track]:
        tracks_ids: List[str] = [track.spotify_id for track in tracks]
        model.objects.filter(user=self.user).exclude(track__spotify_id__in=tracks_ids).delete()

        existing_ids = set(
            model.objects
            .filter(user=self.user, track__spotify_id__in=tracks_ids)
            .values_list("track__spotify_id", flat=True)
        )

        return [track for track in tracks if track.spotify_id not in existing_ids]

    #RECOMMENDATION TRACKS

    def save_user_recommendation_tracks(self, tracks: List[Track], cache=True) -> List[Track]:
        if not tracks:
            raise ValueError("Tracks list is empty")

        unique_tracks: List[Track] = list()
        seen = set()
        for track in tracks:
            if track.spotify_id not in seen:
                seen.add(track.spotify_id)
                unique_tracks.append(track)

        tracks = unique_tracks

        cleared_tracks = self._clear_existing_tracks(tracks=tracks, model=RecommendationTracks)
        add_tracks: List[RecommendationTracks] = [
            RecommendationTracks(track=track, user=self.user)
            for track in cleared_tracks
        ]

        random.shuffle(tracks)

        if cache:
            tracks_ids = ConvertSpotifyDataBaseService.convert_tracks_to_ids(tracks)
            self.user_cache_service.set_user_recommended_tracks(tracks_ids)
            logger.debug("Tracks IDs saved to Redis: count=%d", len(tracks_ids))

        RecommendationTracks.objects.bulk_create(add_tracks)
        logger.info("Recommendation tracks saved: count=%d", len(tracks))

        return tracks


    #FAVORITE TRACKS
    def _favorite_tracks(self, tracks: List[Track], term: str) -> List[FavoriteUserTracks]:
        cleared_tracks = self._clear_existing_tracks(tracks, model=FavoriteUserTracks)
        add_tracks: List[FavoriteUserTracks] = [FavoriteUserTracks(track=track, user=self.user, term=term) for track in cleared_tracks]
        return FavoriteUserTracks.objects.bulk_create(add_tracks)

    def _save_and_cache_favorite_tracks(self, tracks: List[Track], term: str, cache=True) -> List[FavoriteUserTracks]:
        if cache:
            cache_methods = {
                'short_term': self.user_cache_service.set_user_favorite_short_term_tracks,
                'medium_term': self.user_cache_service.set_user_favorite_medium_term_tracks,
                'long_term': self.user_cache_service.set_user_favorite_long_term_tracks,
            }
            converted_tracks = ConvertSpotifyDataBaseService.convert_tracks_to_ids(tracks)

            cache_methods[term](converted_tracks)

        return self._favorite_tracks(tracks, term=term)

    def save_favorite_user_tracks_short_term(self, tracks: List[Track], cache=True) -> List[FavoriteUserTracks]:
        if tracks:
            return self._save_and_cache_favorite_tracks(tracks, term="short_term", cache=cache)

        raise ValueError("Tracks list is empty")

    def save_favorite_user_tracks_medium_term(self, tracks: List[Track], cache=True) -> List[FavoriteUserTracks]:
        if tracks:
            return self._save_and_cache_favorite_tracks(tracks, term="medium_term", cache=cache)

        raise ValueError("Tracks list is empty")

    def save_favorite_user_tracks_long_term(self, tracks: List[Track], cache=True) -> List[FavoriteUserTracks]:
        if tracks:
            return self._save_and_cache_favorite_tracks(tracks, term="long_term", cache=cache)

        raise ValueError("Tracks list is empty")


    # USER LISTEN TO HISTORY

    def save_listen_tracks_history(self, tracks: List[PlayedTrackDTO], cache=True) -> List[UsersListenHistory]:
        if not tracks:
            raise ValueError("Tracks list is empty")

        existing = set(UsersListenHistory.objects.filter(user=self.user).values_list(
            "track__spotify_id", "played_at"
        ))

        new_tracks: List[UsersListenHistory] = list()
        for dto in tracks:
            if not dto:
                continue

            if not dto.track or not dto.played_at:
                continue

            key = (dto.track.spotify_id, dto.played_at)

            if key not in existing:
                new_tracks.append(UsersListenHistory(
                    track=dto.track,
                    user=self.user,
                    played_at=dto.played_at,
                ))


        user_listen_history = UsersListenHistory.objects.bulk_create(new_tracks)
        get_user_data = GetUserDataService(user=self.user)

        if cache:
            get_user_data.listen_statistic() # For saving statistics to cache

        return user_listen_history

    @transaction.atomic
    def create_playlist(self, playlist_class: PlaylistClass, process: bool = True) -> Playlist:
        user = get_object_or_404(CustomUser, spotify_id=playlist_class.owner_sid)

        playlist, created = Playlist.objects.get_or_create(
            spotify_id=playlist_class.spotify_id,
            defaults={
                'name': playlist_class.name,
                'spotify_url': playlist_class.spotify_url,
                'description': playlist_class.description,
                'track_count': playlist_class.track_count,
                'user': user,
            }
        )

        if created:
            logger.debug("Playlist created: sid=%s", playlist.spotify_id)
            self._handle_playlist_creation(playlist, playlist_class.image_url)

            from SpotifyController.tasks.fetch_new_obj import process_new_playlist_task

            if process:
                transaction.on_commit(
                    lambda : process_new_playlist_task.delay(playlist.spotify_id)
                )

        else:
            logger.debug("Playlist already exists: sid=%s", playlist.spotify_id)

        return playlist

    def create_playlists(self, playlists_classes: List[PlaylistClass]) -> List[Playlist]:
        playlists: List[Playlist] = list()
        playlists_ids = list()

        for playlist_class in playlists_classes:
            playlist = self.create_playlist(playlist_class)

            playlists.append(playlist)
            playlists_ids.append(playlist.spotify_id)

        self.user_cache_service.set_user_playlists(playlists_ids)
        logger.info(f"Playlists cached: sid=%s", playlists_ids)

        return playlists

    def _handle_playlist_creation(self, playlist: Playlist, image_url: str) -> None:
        self.user_service.update_object_image(playlist, image_url)

