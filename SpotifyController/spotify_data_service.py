from dataclasses import (dataclass, field)
from typing import (Optional, List, Dict, Tuple)
from datetime import (datetime, date)
from .models import (Artist, Track, Genre)
from django.contrib.auth import get_user_model
import os

CustomUser = get_user_model()

@dataclass
class GenreClass:
    name: str

@dataclass
class ArtistClass:
    name: str
    spotify_id: str
    spotify_url: str
    genres: Optional[List[GenreClass]] = field(default_factory=list)
    image_url: str = None

@dataclass
class TrackClass:
    name: str
    url: str
    spotify_id: str
    played_at: Optional[datetime] = field(default=None)
    artists: Optional[List[ArtistClass]] = field(default_factory=list)
    release_date: Optional[date] = None


class ConstructSpotifyDataService:
    def __init__(self):
        from .client_services import SpotifyPublicClientService

        self.sp_public_client = SpotifyPublicClientService()

    @staticmethod
    def _get_player_at(track_data: dict) -> datetime:
        played_at_str: str = track_data.get("played_at")
        return datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))

    def construct_track_data_with_played_at(self, track_data: dict) -> TrackClass:
        played_at = self._get_player_at(track_data)
        track_data = track_data.get("track")

        constructed_track: TrackClass = self.construct_track_data(track_data)
        constructed_track.played_at = played_at

        return constructed_track

    def construct_tracks_data_with_played_at(self, tracks_data: dict) -> List[TrackClass]:
        tracks: List[TrackClass] = list()

        for track_data in tracks_data:
            tracks.append(self.construct_track_data_with_played_at(track_data))

        return tracks


    def construct_track_data(self, track_data: dict) -> TrackClass:
        artists: List[ArtistClass] = self.get_artist_data(track_data.get("artists"))

        track = TrackClass(
            name=track_data.get("name"),
            url=track_data.get("external_urls").get("spotify"),
            spotify_id=track_data.get("id"),
        )

        track.artists.extend([artist for artist in artists if artist])
        return track

    def construct_tracks_data(self, tracks_data: List[dict]) -> List[TrackClass]:
        tracks: List[TrackClass] = list()

        for track_data in tracks_data:
            tracks.append(self.construct_track_data(track_data))

        return tracks

    @staticmethod
    def _get_release_data(track_data: dict) -> date | None:
        release_date_str = track_data.get("album").get("release_date")

        try:
            return datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def get_artist_data(self, artists_data: List[dict]) -> List[ArtistClass]:
        artists: List[ArtistClass] = list()

        for artist in artists_data:
            artist_id = artist.get("id")

            if artist_id:
                spotify_artist_data = self.sp_public_client.get_artist_info(artist_id)
                artists.append(self.construct_artist_data(spotify_artist_data))

        return artists

    @staticmethod
    def construct_artist_data(artist_data) -> ArtistClass:
        genres: List[GenreClass] = [genre for genre in artist_data.get("genres", []) if genre]

        return ArtistClass(
            spotify_id=artist_data.get("id"),
            name=artist_data.get("name"),
            spotify_url=artist_data.get("external_urls").get("spotify"),
            image_url=artist_data.get("images")[0].get("url") if artist_data.get('images') else None,
            genres=genres
        )

class CheckSpotifyDataService:
    @staticmethod
    def artist_image_update(artist: Artist, new_image_url: str) -> bool:
        image_exists = bool(artist.image)

        if image_exists:
            artist_current_image_name = os.path.basename(artist.image.url).replace(".jpg", "")
            new_image_name = os.path.basename(new_image_url)

            if artist_current_image_name == new_image_name:
                return False
            else:
                print(f"CURRENT IMAGE: {artist_current_image_name}")
                print(f"NEW IMAGE: {new_image_name}")

        return True

@dataclass
class UserFavoriteTrackStat:
    Track: Track
    Count: int

@dataclass
class UserFavoriteGenreStat:
    Genre: Genre
    Count: int

@dataclass
class UserFavoriteArtistStat:
    Artist: Artist
    Count: int

@dataclass
class UserStats:
    FavoriteGenres: Dict[date, List[UserFavoriteGenreStat]] = field(default_factory=dict)
    FavoriteTracks: Dict[date, List[Track]] = field(default_factory=dict)
    FavoriteArtists: Dict[date, List[Artist]] = field(default_factory=dict)

class UserHistoryTrackStatisticsService:
    def __init__(self, tracks_stats: Dict[str, List[Tuple[Track, int]]]):
        self.tracks_stats = tracks_stats

    def get_stats(self):
        user_stats = UserStats()

        for played_at, tracks in self.tracks_stats.items():
            print(f"{played_at}: {tracks}")
