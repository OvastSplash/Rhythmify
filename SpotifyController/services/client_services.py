from spotipy import SpotifyException

from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService
from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.construct_data import ConstructDataService, TrackClass, AlbumClass
from SpotifyController.services.spotify_auth import AuthService
from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.serializers import SpotifyProfileSerializer

from User.models import CustomUser
from typing import List

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



    def get_artist_info(self, artist_id):
        return self.client.artist(artist_id)

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

class UserClient:
    def __init__(self, user: CustomUser):
        self.user = user

        #Check token on available and refresh if expired
        AuthService.refresh_user_tokens(user)

        self.access_token = user.access_token
        self.client = AuthService.get_client(self.access_token)

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
        print(user_data)
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
        recently_played = self.client.current_user_recently_played(limit=limit)

        if construct:
            construct_sp = ConstructDataService()
            return construct_sp.tracks_data_with_played_at(
                tracks_data=recently_played['items'],
            )

        return recently_played

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

        print("Создан плейлист:", playlist["name"], playlist["id"])

        tracks_uri = [f"spotify:track:{track.spotify_id}" for track in tracks]

        for i in range(0, len(tracks_uri), 100):
            chunk = tracks_uri[i:i + 100]
            self.client.playlist_add_items(
                playlist_id=playlist['id'],
                items=chunk,
            )

        print(tracks_uri)