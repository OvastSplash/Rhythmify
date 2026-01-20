import logging
from dataclasses import (dataclass, field)
from typing import (Optional, List, Dict)
from datetime import (datetime, date)
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@dataclass
class GenreClass:
    name: str

@dataclass
class AlbumClass:
    name: str
    type: str
    spotify_url: str
    spotify_id: str
    total_tracks: int = None
    image_url: str = None
    release_date: Optional[date] = None

@dataclass
class ArtistClass:
    name: str
    spotify_id: str
    spotify_url: str
    genres: Optional[List[GenreClass]] = field(default_factory=list)
    followers: int = None
    image_url: str = None

@dataclass
class TrackClass:
    name: str
    url: str
    spotify_id: str
    album: AlbumClass = None
    duration_ms: int = 0
    played_at: Optional[datetime] = field(default=None)
    artists: Optional[List[ArtistClass]] = field(default_factory=list)
    image_url: str = None


class ConstructDataService:
    @staticmethod
    def _get_player_at(track_data: dict) -> datetime:
        played_at_str: str = track_data.get("played_at")
        return datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))

    def track_data_with_played_at(self, track_data: dict) -> TrackClass:
        played_at = self._get_player_at(track_data)
        track_data = track_data.get("track")

        constructed_track: TrackClass = self.track_data(track_data)
        constructed_track.played_at = played_at

        return constructed_track

    def tracks_data_with_played_at(self, tracks_data: dict) -> List[TrackClass]:
        tracks: List[TrackClass] = list()

        for track_data in tracks_data:
            tracks.append(self.track_data_with_played_at(track_data))

        return tracks


    def track_data(self, track_data: dict) -> TrackClass:
        artists: List[ArtistClass] = self._get_artist_data(track_data.get("artists", ""))
        album = self.get_album_data(track_data.get("album"))

        try:
            image_url = track_data.get("album").get("images")[0].get("url")
        except AttributeError:
            image_url = None

        track = TrackClass(
            name=track_data.get("name") if track_data.get("name") else track_data.get("album").get("name"),
            url=track_data.get("external_urls").get("spotify"),
            spotify_id=track_data.get("id"),
            duration_ms = track_data.get("duration_ms"),
            image_url=image_url,
            album=album,
        )

        track.artists.extend(artists)
        return track

    def tracks_data(self, tracks_data: List[dict]) -> List[TrackClass]:
        tracks: List[TrackClass] = list()

        for track_data in tracks_data:
            tracks.append(self.track_data(track_data))

        return tracks
    def get_album_data(self, album_data: dict) -> AlbumClass | None:
        if album_data:
            release_date_str = album_data.get("release_date")

            try:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
            except ValueError:
                release_date = datetime.strptime(release_date_str, "%Y")
            except Exception as e:
                release_date = None
                print(f"Construct Data {e}: --- {release_date_str}")

            return AlbumClass(
                name=album_data.get("name"),
                type=album_data.get("album_type"),
                spotify_id=album_data.get("id"),
                spotify_url=album_data.get("external_urls").get("spotify"),
                image_url=album_data.get("images")[0].get("url"),
                total_tracks=album_data.get("total_tracks"),
                release_date=release_date
            )

        return None

    def get_albums_data(self, albums_data: List[dict]) -> List[AlbumClass]:
        return [self.get_album_data(album) for album in albums_data]

    def _get_artist_data(self, artists_data: List[dict]) -> List[ArtistClass]:
        artists: List[ArtistClass] = list()

        for artist in artists_data:
            artist_id = artist.get("id")

            if artist_id:
                from SpotifyController.services.client_services import PublicClient
                sp_public_client = PublicClient()

                spotify_artist_data = sp_public_client.get_artist_info(artist_id)
                artists.append(self.artist_data(spotify_artist_data))

        return artists

    @staticmethod
    def artist_data(artist_data) -> ArtistClass:
        genres: List[GenreClass] = [genre for genre in artist_data.get("genres", []) if genre]
        followers = artist_data.get("followers").get('total')

        return ArtistClass(
            spotify_id=artist_data.get("id"),
            name=artist_data.get("name"),
            spotify_url=artist_data.get("external_urls").get("spotify"),
            image_url=artist_data.get("images")[0].get("url") if artist_data.get('images') else None,
            genres=genres,
            followers=followers
        )


@dataclass
class PlaylistClass:
    name: str
    spotify_id: str
    spotify_url: str
    description: str
    image_url: str
    track_count: int
    owner_sid: str

class ConstructPlaylistDataService:
    def __init__(self, user_sid) -> None:
        self.user_sid = user_sid
        self.cached_playlist_data = None

    @property
    def _image(self) -> str:
        try:
            image_url = self.cached_playlist_data.get("images")[0]["url"]
        except Exception as e:
            logging.exception(e)
            image_url = None

        return image_url

    @property
    def _is_user_playlist(self) -> bool:
        owner_data = self.cached_playlist_data.get("owner")
        owner_id = owner_data.get("id")

        if owner_id == self.user_sid:
            return True

        return False

    @property
    def _spotify_url(self) -> str:
        external_urls = self.cached_playlist_data.get("external_urls")
        spotify_id = external_urls.get("spotify")
        return spotify_id

    @property
    def _tracks_count(self) -> int:
        try:
            tracks = self.cached_playlist_data.get("tracks")
            tracks_count = int(tracks.get("total"))
            return tracks_count
        except Exception as e:
            logging.exception(e)
            return 0

    def construct_playlist(self, playlist_data=None) -> PlaylistClass | None:
        logging.debug(f"Construct Playlist: {playlist_data}")

        if self.cached_playlist_data is None:
            logging.warning(f"Construct Playlist: has not been cached yet")

            if playlist_data:
                self.cached_playlist_data = playlist_data
            else:
                raise Exception("Playlist data not found")

        if self._is_user_playlist:
            playlist = PlaylistClass(
                name=self.cached_playlist_data.get("name"),
                spotify_id=self.cached_playlist_data.get("id"),
                spotify_url=self._spotify_url,
                description=self.cached_playlist_data.get("description"),
                image_url=self._image,
                track_count=self._tracks_count,
                owner_sid=self.user_sid,
            )

            logging.debug(f"Construct Playlist: {playlist}")
            return playlist

        return None


    def construct_playlists(self, playlists_data: dict) -> List[PlaylistClass]:
        playlists: List[PlaylistClass] = list()

        for playlist_data in playlists_data.get("items", []):
            self.cached_playlist_data = playlist_data
            playlist = self.construct_playlist()

            if playlist:
                playlists.append(playlist)

        playlists = sorted(playlists, key=lambda playlist: playlist.track_count, reverse=True)
        return playlists