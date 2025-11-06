from django.core.files.base import ContentFile
from SpotifyController.services import SpotifyService
from .models import CustomUser
from django.contrib.auth import authenticate
import requests
import uuid

class UserService:
    @staticmethod
    def update_user_image(user: CustomUser, image_url, save=True):
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None  # или бросить исключение

        content_type = response.headers.get('Content-Type', '')
        ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        file_name = f"{uuid.uuid4()}.{ext}"

        user.user_image.save(file_name, ContentFile(response.content), save=save)
        return user.user_image.url

    @staticmethod
    def spotify_update_user(access_token, refresh_token, expires_at, user: CustomUser = None):
        data, error = SpotifyService.get_user_data(access_token)

        if error:
            return None, False, error

        # Redirect to user confirm register
        elif user is None:
            data["access_token"] = access_token
            data["refresh_token"] = refresh_token
            data["expires_at"] = expires_at
            return data, False, None

        name, spotify_id, spotify_url, followers, image = SpotifyService.get_user_info(data)

        if CustomUser.objects.filter(spotify_id=spotify_id).exists():
            user = CustomUser.objects.get(spotify_id=spotify_id)


        expires_at = SpotifyService.convert_expires_at(expires_at)

        user.spotify_id = spotify_id
        user.followers = followers
        user.spotify_url = spotify_url
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expires_at = expires_at

        if not user.user_image:
            UserService.update_user_image(user, image)

        user.save()
        return None, True, None