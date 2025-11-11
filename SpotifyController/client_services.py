from .spotify_data_service import ConstructSpotifyDataService
import spotipy

class SpotifyClientService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.client = spotipy.Spotify(auth=self.access_token)

    def get_artist_info(self, artist_id):
        return self.client.artist(artist_id)

    def get_user_top_tracks(self, construct=True):
        top_tracks = self.client.current_user_top_tracks(limit=20, time_range="short_term")

        if construct:
            spotify_construct = ConstructSpotifyDataService(
                tracks_data=top_tracks["items"],
                access_token=self.access_token,
            )
            return spotify_construct.construct_track_data()

        return top_tracks
