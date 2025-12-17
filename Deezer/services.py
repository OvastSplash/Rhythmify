from SpotifyController.services.construct_data import TrackClass

import deezer
import requests

class AuthService:
    @staticmethod
    def get_client():
        return deezer.Client()


class ClientService:
    def __init__(self):
        self.client = AuthService.get_client()

    def _get_preview_by_name(self, track_name: str, artist_name: str):
        try:
            review_url = self.client.search(track=track_name, artist=artist_name)[0].preview

            if review_url:
                response = requests.get(review_url)

                if response.status_code == 200:
                    mp3_bytes = response.content
                    return mp3_bytes

            return None
        except Exception as e:
            print(f"Deezer Error: {e}")
            return None

    from SpotifyController.models.models import Track

    def get_preview_by_track(self, track: Track):
        return self._get_preview_by_name(
            track_name=track.name,
            artist_name=track.artists.first().name
        )

    def get_preview_by_construct(self, track: TrackClass):
        return self._get_preview_by_name(
            track_name=track.name,
            artist_name=track.artists[0].name
        )