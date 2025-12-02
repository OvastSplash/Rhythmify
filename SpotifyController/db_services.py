from django.db.models.functions import (TruncMonth, ExtractYear, ExtractMonth, Concat)

from .CacheService import UserCacheService
from .models import (
    Artist,
    Track,
    Genre,
    UsersListenHistory
)
from .spotify_data_service import (
    ArtistClass,
    TrackClass,
    GenreClass
)
from typing import (List, Type, Dict)
from User.models import CustomUser
from User.services import UserService
from .spotify_data_service import CheckSpotifyDataService
from django.db.models import (Count, Model, QuerySet, F, CharField, Value)
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class PlayedTrackDTO:
    track: Track
    played_at: datetime = None

class SpotifyDatabaseService:
    def __init__(self):
        self.user_service = UserService()
        self.check_service = CheckSpotifyDataService()

    @staticmethod
    def get_or_create_genre(genre: GenreClass) -> Genre:
        genre, _ = Genre.objects.get_or_create(name=genre)
        return genre

    def _update_artist_genres(self, artist: Artist, genres: List[GenreClass]) -> None:
        new_genres = [self.get_or_create_genre(genre) for genre in genres if genre]

        if set(artist.genres.all()) != set(new_genres):
            artist.genres.set(new_genres)
            print(f"New genre was created for {artist.name} --- {', '.join(genre.name for genre in artist.genres.all())}")

    def create_or_update_artist(self, artist_data: ArtistClass) -> Artist:
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data.spotify_id,
            defaults={
                'name': artist_data.name,
                'spotify_url': artist_data.spotify_url,
            }
        )

        self._update_artist_genres(artist, artist_data.genres)

        if not created and artist.name != artist_data.name:
            print(f"Artist name {artist.name} changed to {artist_data.name}")
            artist.name = artist_data.name
            artist.save()

        if artist_data.image_url and self.check_service.artist_image_update(artist, artist_data.image_url):
            artist.image = self.user_service.update_object_image(
                artist, artist_data.image_url, save=True
            ) if artist_data.image_url else None

            print(f"Image was created or updated for {artist.name} --- Image Name: {artist.image}")

        return artist


    def create_track(self, constructed_track: TrackClass) -> Track:
        track, _ = Track.objects.get_or_create(
            spotify_id=constructed_track.spotify_id,
            defaults={
                'name': constructed_track.name,
                'url': constructed_track.url,
                'release_date': constructed_track.release_date
            }
        )

        if constructed_track.artists:
            artists: List[Artist] = [self.create_or_update_artist(artist) for artist in constructed_track.artists]
            for artist in artists:
                artist.track_list.add(track)

        return track

    def create_tracks(self, constructed_tracks: List[TrackClass]) -> List[Track]:
        tracks: List[Track] = list()
        for constructed_track in constructed_tracks:
            tracks.append(self.create_track(constructed_track))

        return tracks

    def create_played_at_track(self, track: TrackClass) -> PlayedTrackDTO:
        return PlayedTrackDTO(
            track=self.create_track(track),
            played_at=track.played_at,
        )

    def create_played_at_tracks(self, tracks: List[TrackClass]) -> List[PlayedTrackDTO]:
        return [self.create_played_at_track(track) for track in tracks]


    @staticmethod
    def save_tracks_to_user_list(model: Type[Model], tracks: List[Track], user: CustomUser):
        tracks_ids: List[str] = [track.spotify_id for track in tracks]
        to_delete = model.objects.exclude(track__spotify_id__in=tracks_ids, user=user)
        existing_ids = list(to_delete.values_list("track__spotify_id", flat=True))
        to_delete.delete()
        existing_ids = set(existing_ids)

        tracks = [track for track in tracks if track.spotify_id not in existing_ids]
        recommended_objects: List[model] = [model(track=track, user=user) for track in tracks]
        model.objects.bulk_create(recommended_objects)

    @staticmethod
    def save_user_listen_tracks_history(user: CustomUser, tracks: List[PlayedTrackDTO]) -> QuerySet[UsersListenHistory]:
        tracks = [UsersListenHistory(
            track=track_dto.track,
            user=user,
            played_at=track_dto.played_at,
        ) for track_dto in tracks]

        #TODO: Добавить фильтр что бы не добавлялись уже существующие записи, смотреть по (track, played_at)

        UsersListenHistory.objects.bulk_create(tracks)
        return UsersListenHistory.objects.filter(user=user)

class GetSpotifyInfoFromDatabase:
    def __init__(self, user: CustomUser):
        self.user = user

    def get_user_top_tracks(self, count: int = 5) -> List[Track]:
        return list(
            Track.objects
            .filter(favorite__user=self.user)
            .prefetch_related("favorite", "artists")
        )[:count]

    def get_user_top_artists(self, count: int = 5) -> List[Artist]:
        return list(
            Artist.objects
            .filter(track_list__favorite__user=self.user)
            .annotate(user_count=Count('spotify_id'))
            .order_by("-user_count")
        )[:count]

    def get_user_top_genres(self, count: int = 5) -> List[str]:
        return list(
            Genre.objects
            .filter(artists__track_list__favorite__user=self.user)
            .annotate(artist_count=Count('artists'))
            .order_by("-artist_count")
            .values_list("name", flat=True)
        )[:count]

    def get_user_recommend_tracks(self) -> List[Track]:
        return list(
            Track.objects
            .filter(recommendations__user=self.user)
        )

    def get_user_listen_statistic(self):
        favorite_tracks = self.get_user_listen_history_tracks_by_month()
        favorite_artists = self.get_user_listen_history_artists_by_month()
        favorite_genres = self.get_user_listen_history_genre_by_month()

        cache_data = {"tracks": favorite_tracks, "artists": favorite_artists, "genres": favorite_genres}
        UserCacheService.set_user_statistics(user_id=self.user.id, user_statistic=cache_data)

        return cache_data

    def get_user_listen_history_tracks_by_month(self) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get most listened user track by month for all time
        Returns: QuerySet[UsersListenHistory, dict[track_spotify_id: str, count: int]]
        """

        return (
            UsersListenHistory.objects.filter(user=self.user)
            .annotate(month_year_dt=TruncMonth("played_at"))
            .annotate(year=ExtractYear("month_year_dt"))
            .annotate(month=ExtractMonth("month_year_dt"))
            .annotate(month_year=Concat(
                F("year"),
                Value("-"),
                F("month"),
                output_field=CharField()
            ))
            .values("month_year", "track__spotify_id")
            .annotate(play_count=Count("track__spotify_id"))
            .order_by("month_year_dt", "-play_count")
        )

        # return most_listened_tracks

    def get_user_listen_history_artists_by_month(self) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get most listened user artists by month for all time
        Returns: QuerySet[UsersListenHistory, dict[artist_spotify_id: str, count: int]]
        """

        return (
            UsersListenHistory.objects.filter(user=self.user)
            .annotate(month_year_dt=TruncMonth("played_at"))
            .annotate(year=ExtractYear("month_year_dt"))
            .annotate(month=ExtractMonth("month_year_dt"))
            .annotate(month_year=Concat(
                F("year"),
                Value("-"),
                F("month"),
                output_field=CharField()
            ))
            .values("month_year", "track__artists__spotify_id")
            .annotate(artists_count=Count("track__artists__spotify_id"))
            .order_by("month_year_dt", "-artists_count")
        )

    def get_user_listen_history_genre_by_month(self) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get most listened user genres by month for all time
        Returns: QuerySet[UsersListenHistory, dict[genre_name: str, count: int]]
        """

        return (
            UsersListenHistory.objects.filter(user=self.user)
            .annotate(month_year_dt=TruncMonth("played_at"))
            .annotate(year=ExtractYear("month_year_dt"))
            .annotate(month=ExtractMonth("month_year_dt"))
            .annotate(month_year=Concat(
                F("year"),
                Value("-"),
                F("month"),
                output_field=CharField()
            ))
            .values("month_year", "track__artists__genres__name")
            .annotate(genres_count=Count("track__artists__genres__name"))
            .order_by("month_year_dt", "-genres_count")
        )

    @staticmethod
    def convert_user_statistic(user_statistic_data: Dict):
        converted_user_statistic = defaultdict(lambda: {"tracks": [], "artists": [], "genres": []})

        for track_data in user_statistic_data["tracks"]:
            date = track_data['month_year']
            spotify_id = track_data["track__spotify_id"]
            played_count = track_data["play_count"]

            track = Track.objects.get(spotify_id=spotify_id)
            converted_user_statistic[date]["tracks"].append({
                "track": track,
                "count": played_count,
            })

        for artist_data in user_statistic_data["artists"]:
            date = artist_data['month_year']
            spotify_id = artist_data["track__artists__spotify_id"]
            arist_in_count = artist_data["artists_count"]

            artist = Artist.objects.get(spotify_id=spotify_id)
            converted_user_statistic[date]["artists"].append({
                "artist": artist,
                "count": arist_in_count,
            })

        for genre_data in user_statistic_data["genres"]:
            date = genre_data['month_year']
            genre = genre_data['track__artists__genres__name']
            genre_in_count = genre_data['genres_count']

            converted_user_statistic[date]["genres"].append({
                "genre": genre,
                "count": genre_in_count,
            })
        print(converted_user_statistic)
        return converted_user_statistic