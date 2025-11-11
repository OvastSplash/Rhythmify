from User.models import CustomUser
import spotipy

class SpotifyClientService:
    def __init__(self, access_token, user:CustomUser = None):
        self.access_token = access_token
        self.client = spotipy.Spotify(auth=self.access_token)
        self.user = user

    def get_artist_info(self, artist_id):
        return self.client.artist(artist_id)

    def get_user_top_tracks(self, commit=False):
        top_tracks = self.client.current_user_top_tracks(limit=20, time_range="medium_term")

        if commit and self.user:
            from .db_services import SpotifyDatabaseService
            spotify_db = SpotifyDatabaseService(top_tracks['items'], self.user, self)
            return spotify_db.add_track_to_db()

        return top_tracks