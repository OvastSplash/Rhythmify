from SpotifyController.models.models import Artist, Track, Album
from SpotifyController.services.database.get_spotify_data import GetPlaylistDataService

from typing import Type, Union
import os

import logging

logger = logging.getLogger(__name__)

class CheckDataService:
    @staticmethod
    def _model_image_update(object: Union[Artist, Track, Album], new_image_url: str) -> bool:
        image_exists = bool(object.image)

        if image_exists:
            artist_current_image_name = os.path.basename(object.image.url).replace(".jpg", "")
            new_image_name = os.path.basename(new_image_url)

            if artist_current_image_name in new_image_name:
                return False

        return True

    @staticmethod
    def artist_image_update(artist, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(artist, new_image_url)

    @staticmethod
    def track_image_update(track: Track, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(track, new_image_url)

    @staticmethod
    def album_image_update(album: Album, new_image_url: str) -> bool:
        return CheckDataService._model_image_update(album, new_image_url)


    @staticmethod
    def track_in_playlist(playlist_id: str, track_id: str) -> bool:
        try:
            playlist = GetPlaylistDataService.get_playlist_by_sid(sid=playlist_id)
            return playlist.tracks.filter(spotify_id=track_id).exists()

        except Exception as e:
            logger.exception(e)
            raise
