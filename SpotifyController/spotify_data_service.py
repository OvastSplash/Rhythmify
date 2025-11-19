from dataclasses import dataclass, field
from typing import Optional, List, Union
from datetime import datetime, date
from .models import Artist
import os

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
    artists: Optional[List[ArtistClass]] = field(default_factory=list)
    release_date: Optional[date] = None


class ConstructSpotifyDataService:
    @staticmethod
    def construct_track_data(tracks_data: Union[List[dict], dict]) -> List[TrackClass]:
        from .client_services import SpotifyPublicClientService

        if isinstance(tracks_data, dict):
            tracks_data = [tracks_data]

        tracks: List[TrackClass] = []

        for track in tracks_data:
            artists: List[ArtistClass] = []

            for artist in track.get("artists", []):
                artist_id = artist.get("id")

                if artist_id:
                    spotify_artist_data = SpotifyPublicClientService.get_artist_info(artist_id)
                    artists.append(ConstructSpotifyDataService.construct_artist_data(spotify_artist_data))

            new_track = TrackClass(
                name=track.get("name"),
                url=track.get("external_urls").get("spotify"),
                spotify_id=track.get("id"),
            )

            release_date_str = track.get("album").get("release_date")
            try:
                new_track.release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            except:
                new_track.release_date = None

            new_track.artists.extend([artist for artist in artists if artist])
            tracks.append(new_track)

        return tracks

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