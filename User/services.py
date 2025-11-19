from typing import Optional, Union

from django.core.files.base import ContentFile

from SpotifyController.models import Artist
from SpotifyController.services import SpotifyService
from .models import CustomUser
from dataclasses import dataclass
import requests
import os

@dataclass
class SpotifyUserUpdateResult:
    is_existing: bool
    user: Optional[CustomUser] = None
    data: Optional[dict] = None
    error: Optional[str] = None

class UserService:
    @staticmethod
    def update_object_image(object: Union[Artist, CustomUser], image_url, save=True):
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None  # или бросить исключение

        ext = '.jpg'
        file_name = f"{os.path.basename(image_url)}{ext}"

        if object.image and object.image.name != file_name:
            object.image.delete(save=False)

        object.image.save(file_name, ContentFile(response.content), save=save)
        return object.image.name

    @staticmethod
    def spotify_update_user(access_token, refresh_token, expires_at, user: CustomUser = None) -> SpotifyUserUpdateResult:
        data, error = SpotifyService.get_user_data(access_token)

        if error:
            return SpotifyUserUpdateResult(
                is_existing=False,
                error=error,
            )

        name, spotify_id, spotify_url, followers, image = SpotifyService.get_user_info(data)

        user_exists = CustomUser.objects.filter(spotify_id=spotify_id).first()

        if user_exists and not user:
            return SpotifyUserUpdateResult(
                is_existing=True,
                user=user_exists
            )

        if user:
            expires_at = SpotifyService.convert_expires_at(expires_at)

            user.spotify_id = spotify_id
            user.followers = followers
            user.spotify_url = spotify_url
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_expires_at = SpotifyService.convert_expires_at(expires_at)

            if not user.image:
                UserService.update_object_image(user, image, save=False)

            user.save()
            return SpotifyUserUpdateResult(is_existing=True, user=user)

        data["access_token"] = access_token
        data["refresh_token"] = refresh_token
        data["expires_at"] = expires_at
        return SpotifyUserUpdateResult(
            is_existing=False,
            data=data
        )