from spotipy.oauth2 import SpotifyOAuth, CacheHandler
from Rhythmify.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, SCOPE
from User.models import CustomUser
from .serializers import SpotifyProfileSerializer
from datetime import datetime, timezone as dt_timezone
import spotipy

# Cache no save
class NoCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None

    def save_token_to_cache(self, token_info):
        pass

class SpotifyService:
    @staticmethod
    def oauth():
        return SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URL,
            scope=SCOPE,
            cache_handler=NoCacheHandler(),
        )

    @staticmethod
    def get_tokens(token_info):
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_at = token_info.get('expires_at')
        return access_token, refresh_token, expires_at

    @staticmethod
    def get_user_data(access_token):
        profile = spotipy.Spotify(auth=access_token)
        data = profile.current_user()

        serializer = SpotifyProfileSerializer(data=data)

        if serializer.is_valid():
            return serializer.validated_data, None

        return None, serializer.errors

    @staticmethod
    def convert_expires_at(expires_at):
        if isinstance(expires_at, (int, float)):
            return datetime.fromtimestamp(expires_at, tz=dt_timezone.utc)

        return None

    @staticmethod
    def get_user_info(data):
        name = data.get('display_name')
        spotify_id = data.get('id')
        spotify_url = data.get('external_urls').get('spotify')
        followers = data.get('followers').get('total')
        images = data.get('images', [])
        image = images[0].get('url') if images else None

        return name, spotify_id, spotify_url, followers, image

    @staticmethod
    def refresh_user_tokens(user: CustomUser):
        sp_oauth = SpotifyService.oauth()
        token_info = {
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'expires_at': user.token_expires_at.timestamp(),
        }

        if sp_oauth.is_token_expired(token_info):
            new_token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))

            user.access_token = new_token_info.get('access_token')
            user.token_expires_at = SpotifyService.convert_expires_at(new_token_info.get('expires_at'))
            user.save()

            print(f"User: {user.username} was refreshed successfully")