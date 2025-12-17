from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.services.database.data_builder import PlayedTrackDTO
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService


from SpotifyController.models.models import (
    Track
)
from SpotifyController.models.through import FavoriteUserTracks, RecommendationTracks, UsersListenHistory

from User.models import CustomUser

from typing import (List, Type, Union)

import random

class SaveUserDataService:
    def __init__(self, user: CustomUser):
        self.user = user
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
    def recommendation_tracks(self, tracks: List[Track]) -> List[Track]:
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

        tracks_ids = ConvertSpotifyDataBaseService.convert_tracks_to_ids(tracks)
        self.user_cache_service.set_user_recommended_tracks(tracks_ids)

        RecommendationTracks.objects.bulk_create(add_tracks)

        print(f"Tracks count: {len(tracks)}")
        print(f"Tracks IDs saved to Redis: {len(tracks_ids)}")

        return tracks


    #FAVORITE TRACKS
    def _favorite_tracks(self, tracks: List[Track], term: str) -> List[FavoriteUserTracks]:
        cleared_tracks = self._clear_existing_tracks(tracks, model=FavoriteUserTracks)
        add_tracks: List[FavoriteUserTracks] = [FavoriteUserTracks(track=track, user=self.user, term=term) for track in cleared_tracks]
        return FavoriteUserTracks.objects.bulk_create(add_tracks)

    def _save_and_cache_favorite_tracks(self, tracks: List[Track], term: str) -> List[FavoriteUserTracks]:
        cache_methods = {
            'short_term': self.user_cache_service.set_user_favorite_short_term_tracks,
            'medium_term': self.user_cache_service.set_user_favorite_medium_term_tracks,
            'long_term': self.user_cache_service.set_user_favorite_long_term_tracks,
        }
        converted_tracks = ConvertSpotifyDataBaseService.convert_tracks_to_ids(tracks)

        cache_methods[term](converted_tracks)
        return self._favorite_tracks(tracks, term=term)

    def favorite_user_tracks_short_term(self, tracks: List[Track]) -> List[FavoriteUserTracks]:
        return self._save_and_cache_favorite_tracks(tracks, term="short_term")

    def favorite_user_tracks_medium_term(self, tracks: List[Track]) -> List[FavoriteUserTracks]:
        return self._save_and_cache_favorite_tracks(tracks, term="medium_term")

    def favorite_user_tracks_long_term(self, tracks: List[Track]) -> List[FavoriteUserTracks]:
        return self._save_and_cache_favorite_tracks(tracks, term="long_term")


    # USER LISTEN HISTORY

    def listen_tracks_history(self, tracks: List[PlayedTrackDTO]) -> List[UsersListenHistory]:
        existing = set(UsersListenHistory.objects.filter(user=self.user).values_list(
            "track__spotify_id", "played_at"
        ))

        new_tracks: List[UsersListenHistory] = list()
        for dto in tracks:
            key = (dto.track.spotify_id, dto.played_at)

            if key not in existing:
                new_tracks.append(UsersListenHistory(
                    track=dto.track,
                    user=self.user,
                    played_at=dto.played_at,
                ))


        user_listen_history =  UsersListenHistory.objects.bulk_create(new_tracks)
        get_user_data = GetUserDataService(user=self.user)
        get_user_data.listen_statistic() # For saving statistics to cache

        return user_listen_history

