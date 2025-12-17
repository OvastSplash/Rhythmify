from SpotifyController.models.models import Artist, Track, Album
from typing import Type, Union
import os

class CheckDataService:
    @staticmethod
    def _model_image_update(model: Union[Artist, Track, Album], new_image_url: str) -> bool:
        image_exists = bool(model.image)

        if image_exists:
            artist_current_image_name = os.path.basename(model.image.url).replace(".jpg", "")
            new_image_name = os.path.basename(new_image_url)

            if artist_current_image_name in new_image_name:
                return False

        return True

    @staticmethod
    def artist_image_update(artist: Artist, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(artist, new_image_url)

    @staticmethod
    def track_image_update(track: Track, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(track, new_image_url)

    @staticmethod
    def album_image_update(album: Album, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(album, new_image_url)