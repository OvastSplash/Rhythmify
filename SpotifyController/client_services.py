from .db_services import GetSpotifyInfoFromDatabase
from .spotify_data_service import ConstructSpotifyDataService
from .services import SpotifyService
from User.models import CustomUser
import spotipy
import random

class SpotifyPublicClientService:
    @staticmethod
    def get_artist_info(artist_id):
        return SpotifyService.get_public_spotify_client().artist(artist_id)

    # Recommended transfer with artist name {name} - {artist_name}
    @staticmethod
    def get_track_info_by_name(track_name: str, artist_name: str) -> dict:
        return SpotifyService.get_public_spotify_client().search(
            q=f"{track_name} - {artist_name}",
            type="track",
            limit=1,
        )['tracks']['items']

class SpotifyClientService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.client = spotipy.Spotify(auth=self.access_token)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def get_user_top_tracks(self, construct=True):
        top_tracks = self.client.current_user_top_tracks(limit=20, time_range="short_term")

        if construct:
            return ConstructSpotifyDataService.construct_track_data(
                tracks_data=top_tracks["items"],
            )

        return top_tracks

    def create_user_recommendation_playlist(self, user: CustomUser, shuffle=True):
        tracks = GetSpotifyInfoFromDatabase.get_user_recommend_tracks(user)

        if shuffle:
            random.shuffle(tracks)

        user = self.client.me()
        playlist = self.client.user_playlist_create(
            user=user['id'],
            name=f"{user['display_name']} Recommendation Playlist",
            public=True,
            description=f"Recommendation for {user['display_name']} playlist",
        )

        print("Создан плейлист:", playlist["name"], playlist["id"])

        tracks_uri = [f"spotify:track:{track.spotify_id}" for track in tracks]
        self.client.playlist_add_items(
            playlist_id=playlist['id'],
            items=tracks_uri,
        )

        print(tracks_uri)


        return 1