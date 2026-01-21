from spotipy import SpotifyException
import logging

from SpotifyController.services.database.check_data import CheckDataService
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService
from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.construct_data import ConstructDataService, ConstructPlaylistDataService, TrackClass, \
    AlbumClass, PlaylistClass, ArtistClass
from SpotifyController.services.spotify_auth import AuthService
from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.serializers import SpotifyProfileSerializer
from SpotifyController.services.database.data_builder import UpdateDataService


from User.models import CustomUser
from typing import List

logger = logging.getLogger(__name__)

class PublicClient:
    def __init__(self):
        self.client = AuthService.get_public_client()
        self.construct_sp = ConstructDataService()

    def _construct_tracks_data(self, data) -> List[TrackClass]:
        return self.construct_sp.tracks_data(data)

    def _construct_track_data(self, data) -> TrackClass:
        return self.construct_sp.track_data(data)

    def _construct_album_data(self, data) -> AlbumClass:
        return self.construct_sp.get_album_data(data)

    def _construct_albums_data(self, data) -> List[AlbumClass]:
        return self.construct_sp.get_albums_data(data)

    def _construct_artist_data(self, data) -> ArtistClass:
        return self.construct_sp.artist_data(data)


    def get_artist_info(self, artist_id, constructed: bool = True) -> ArtistClass | dict:
        try:
            artist_data = self.client.artist(artist_id)

            if constructed:
                return self._construct_artist_data(artist_data)

            return artist_data
        except SpotifyException as e:
            logger.error("Artist fetching error: id=%s error=%s", artist_id, e)
            raise Exception("Artist not found")

    def get_top_tracks(self):
        return self.client

    def get_artist_albums(self, artist_id, constructed: bool = True):
        album_data = self.client.artist_albums(artist_id)['items']

        if constructed:
            return self._construct_albums_data(data=album_data)

        return album_data

    def get_artist_top_tracks(self, artist_id, constructed: bool = True):
        tracks_data = self.client.artist_top_tracks(artist_id)['tracks']

        if constructed:
            return self._construct_tracks_data(tracks_data)

        return tracks_data

    def get_album_info(self, album_id, constructed: bool = True):
        album_data = self.client.album(album_id)['tracks']['items']

        if constructed:
            return self._construct_tracks_data(album_data)

        return album_data['tracks']

    # Recommended transfer with artist name {name} - {artist_name}
    def get_track_info_by_name(self, track_name: str, artist_name: str) -> dict:
        return self.client.search(
            q=f"{track_name} - {artist_name}",
            type="track",
            limit=1,
        )['tracks']['items'][0]

    def get_track_info(self, spotify_id: str, constructed: bool = True) -> TrackClass | dict:
        track_data = self.client.track(spotify_id, market="US")

        if constructed:
            return self._construct_track_data(track_data)

        return track_data

    def get_tracks_info(self, spotify_ids: List[str], constructed: bool = True) -> List[TrackClass] | List[dict]:
        tracks_data = self.client.tracks(spotify_ids, market="US")

        if constructed:
            return self._construct_tracks_data(tracks_data['tracks'])

        return tracks_data

class UserClient:
    def __init__(self, user: CustomUser):
        self.user = user

        #Check token on available and refresh if expired
        if user.access_token:
            AuthService.refresh_user_tokens(user)

            self.access_token = user.access_token
            self.client = AuthService.get_client(self.access_token)
            self.construct_playlist = ConstructPlaylistDataService(user_sid=user.spotify_id)

            if not self._is_token_valid():
                AuthService.refresh_user_tokens(user)
                self.access_token = user.access_token
                self.client = AuthService.get_client(self.access_token)

    def _is_token_valid(self) -> bool:
        try:
            self.client.current_user()
            return True
        except SpotifyException as e:
            if e.http_status == 401:
                return False
            raise


    def get_user_data(self):
        user_data = self.client.current_user()
        logger.debug("Fetched user data: length=%d", len(str(user_data)))
        serializer = SpotifyProfileSerializer(data=user_data)

        if serializer.is_valid():
            return serializer.validated_data, None

        return None, serializer.errors


    def _get_user_top_tracks(self, construct=True, limit: int = 50, time_range="short_term"):
        top_tracks = self.client.current_user_top_tracks(limit=limit, time_range=time_range)
        if construct:
            construct_sp = ConstructDataService()
            return construct_sp.tracks_data(
                tracks_data=top_tracks['items'],
            )

        return top_tracks['items']

    def get_user_short_term_top_tracks(self, construct=True, limit: int = 50):
        return self._get_user_top_tracks(construct=construct, limit=limit, time_range="short_term")

    def get_user_medium_term_top_tracks(self, construct=True, limit: int = 50):
        return self._get_user_top_tracks(construct=construct, limit=limit, time_range="medium_term")

    def get_user_long_term_top_tracks(self, construct=True, limit: int = 50):
        return self._get_user_top_tracks(construct=construct, limit=limit, time_range="long_term")

    def get_user_recently_played(self, construct=True, limit: int = 50):
        try:
            recently_played = self.client.current_user_recently_played(limit=limit)

            if construct:
                construct_sp = ConstructDataService()
                return construct_sp.tracks_data_with_played_at(
                    tracks_data=recently_played['items'],
                )

            return recently_played
        except SpotifyException as e:
            logger.error("Recently played tracks fetching error: error=%s", e)
            raise Exception("Recently played tracks not found")

    def create_user_recommendation_playlist(self, user: CustomUser):
        user_cache_service = UserCacheService(user_id=user.id)
        tracks = user_cache_service.get_user_recommended_tracks()

        if tracks is not None:
            tracks = ConvertSpotifyDataBaseService.convert_ids_to_tracks(tracks)
        else:
            user_data = GetUserDataService(user)
            tracks = user_data.recommend_tracks()


        user = self.client.me()
        playlist = self.client.user_playlist_create(
            user=user['id'],
            name=f"{user['display_name']} Recommendation Playlist",
            public=True,
            description=f"Recommendation for {user['display_name']} playlist",
        )

        logger.info("Playlist created: name=%s id=%s", playlist["name"], playlist["id"])

        tracks_uri = [f"spotify:track:{track.spotify_id}" for track in tracks]

        for i in range(0, len(tracks_uri), 100):
            chunk = tracks_uri[i:i + 100]
            self.client.playlist_add_items(
                playlist_id=playlist['id'],
                items=chunk,
            )
        logger.debug("Playlist tracks URIs: count=%d", len(tracks_uri))


    def get_user_playlists_data(self, construct=True) -> List[PlaylistClass] | List[dict]:
        """Get user playlists data"""

        playlists_data = self.client.current_user_playlists(limit=50)

        if construct:
            logging.debug("Fetched playlists data: length=%d", len(str(playlists_data)))
            return self.construct_playlist.construct_playlists(playlists_data)

        return playlists_data

    # def _track_in_playlist(self, playlist_id: str, track_id: str) -> bool:

    def sync_track_to_playlist(self, playlist_id: str, track_id: str) -> None:
        """Add track to playlist, by id"""
        try:
            update_data_service = UpdateDataService()

            if not CheckDataService.track_in_playlist(playlist_id=playlist_id, track_id=track_id):
                self.client.playlist_add_items(playlist_id=playlist_id, items=[f"spotify:track:{track_id}"])
                update_data_service.add_track_to_playlist(playlist_id=playlist_id, track_id=track_id)

                logger.info("Track added to playlist: pid=%s tid=%s", playlist_id, track_id)

            else:
                self.client.playlist_remove_all_occurrences_of_items(playlist_id=playlist_id, items=[f"spotify:track:{track_id}"])
                update_data_service.remove_track_from_playlist(playlist_id=playlist_id, track_id=track_id)

                logger.info("Track removed from playlist: pid=%s tid=%s", playlist_id, track_id)

        except SpotifyException as e:
            logger.error("Track adding error: pid=%s tid=%s error=%s", playlist_id, track_id, e)


    def get_playlist_tracks(self, playlist_id: str,  constructed=True) -> List[TrackClass] | List[dict]:
        logger.info("Fetching playlist tracks: pid=%s", playlist_id)

        data = self.client.playlist_items(
            playlist_id,
            limit=100,
            offset=0,
            additional_types=["track"]
        )

        tracks_data = []

        while True:
            tracks_data.extend(
                item["track"]
                for item in data["items"]
                if item.get("track")
            )

            if data["next"]:
                data = self.client.next(data)
            else:
                break

        if constructed:
            db_builder = ConstructDataService()
            return db_builder.tracks_data(tracks_data)

        return tracks_data