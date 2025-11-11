from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date
from User.services import UserService

@dataclass
class Artist:
    name: str
    spotify_id: str
    spotify_url: str
    image_url: str = None

@dataclass
class Track:
    name: str
    url: str
    spotify_id: str
    artists: Optional[List[Artist]] = field(default_factory=list)
    release_date: Optional[date] = None


class ConstructSpotifyDataService:
    def __init__(self, tracks_data, access_token=None):
        self.access_token = access_token
        self.tracks_data = tracks_data

    def construct_track_data(self) -> List[Track]:
        tracks: List[Track] = []

        for track in self.tracks_data:
            artists: List[Artist] = [self.construct_artist_data(artist) for artist in track.get("artists", []) if artist]

            new_track = Track(
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

    def construct_artist_data(self, artist_data) -> Artist:
        if not artist_data:
            return None

        artist = Artist(
            spotify_id=artist_data.get("id"),
            name=artist_data.get("name"),
            spotify_url=artist_data.get("external_urls").get("spotify"),
        )

        if self.access_token:
            artist.image_url = self.get_artist_image_url(artist.spotify_id)

        return artist

    def get_artist_image_url(self, artist_id) -> Optional[str]:
        try:
            from .client_services import SpotifyClientService

            client = SpotifyClientService(self.access_token)
            artist_data = client.get_artist_info(artist_id)
            artist_image_url = artist_data.get('images')[0].get('url')
            return artist_image_url

        except Exception as e:
            print(f"[WARN] Cannot get artist's image {artist_id}: {e}")
            return None