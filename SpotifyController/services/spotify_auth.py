from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler

from Rhythmify.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, SCOPE
from User.models import CustomUser
from SpotifyController.serializers import SpotifyProfileSerializer
from datetime import datetime, timezone as dt_timezone
import spotipy
import logging

# Cache no save
class NoCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None

    def save_token_to_cache(self, token_info):
        pass

class AuthService:
    _public_client = None
    _user_clients = {}

    @staticmethod
    def oauth():
        try:
            return SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URL,
                scope=SCOPE,
                cache_handler=NoCacheHandler(),
                show_dialog=True,
            )
        except Exception as e:
            logging.getLogger(__name__).exception("Spotify OAuth init error")

    @staticmethod
    def get_client(access_token: str):
        if access_token not in AuthService._user_clients:
            AuthService._user_clients[access_token] = spotipy.Spotify(
                auth=access_token,
                retries=3,
                status_forcelist=(429, 500, 502, 503, 504),
            )

        return AuthService._user_clients[access_token]

    @staticmethod
    def clear_user_client(access_token: str):
        if access_token in AuthService._user_clients:
            AuthService._user_clients.pop(access_token)

    @staticmethod
    def refresh_user_client(access_token: str):
        AuthService.clear_user_client(access_token)
        AuthService.get_client(access_token)

    @staticmethod
    def get_public_client():
        try:
            if AuthService._public_client is None:
                AuthService._public_client = spotipy.Spotify(
                    auth_manager=SpotifyClientCredentials(
                        client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                    ),
                    retries=3,
                    status_forcelist=(429, 500, 502, 503, 504),
                )

            return AuthService._public_client
        except Exception as e:
            logging.getLogger(__name__).exception("Spotify public client init error")

    @staticmethod
    def get_tokens(token_info):
        try:
            access_token = token_info.get('access_token')
            refresh_token = token_info.get('refresh_token')
            expires_at = token_info.get('expires_at')
            return access_token, refresh_token, expires_at
        except Exception as e:
            logging.getLogger(__name__).exception("Spotify token parsing error")

    @staticmethod
    def get_user_data(access_token):
        try:
            profile = spotipy.Spotify(auth=access_token)
            data = profile.current_user()

            serializer = SpotifyProfileSerializer(data=data)

            if serializer.is_valid():
                return serializer.validated_data, None

            return None, serializer.errors
        except SpotifyOAuth as e:
            return None, str(e)

    @staticmethod
    def convert_expires_at(expires_at):
        if isinstance(expires_at, (int, float)):
            return datetime.fromtimestamp(int(expires_at), tz=dt_timezone.utc)
        elif isinstance(expires_at, datetime):
            return expires_at.astimezone(dt_timezone.utc)
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
    def refresh_user_tokens(user: CustomUser) -> bool:
        sp_oauth = AuthService.oauth()
        token_info = {
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'expires_at': user.token_expires_at.timestamp(),
        }

        logging.getLogger(__name__).debug("Token expires_at: %s", token_info.get("expires_at"))

        if sp_oauth.is_token_expired(token_info):
            new_token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))

            user.access_token = new_token_info.get('access_token')
            AuthService.refresh_user_client(user.access_token)

            user.token_expires_at = AuthService.convert_expires_at(new_token_info.get('expires_at'))
            user.save()

            logging.getLogger(__name__).info("User tokens refreshed: username=%s", user.username)
            return True

        return False