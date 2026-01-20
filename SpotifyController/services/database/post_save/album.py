import time
import logging

class PostSaveAlbum:
    def __init__(self, album) -> None:
        from SpotifyController.services.client_services import PublicClient

        self.album = album
        self.client = PublicClient()

    def handle(self):
        from SpotifyController.services.database.data_builder import BuildDataService

        time.sleep(10)
        constructed_data = self.client.get_album_info(self.album.spotify_id)
        db_service = BuildDataService()
        self.album.tracks.add(*db_service.create_tracks(constructed_data))
        logging.getLogger(__name__).info(
            "Album was successfully supplement tracks: album=%s sid=%s",
            self.album.name,
            self.album.spotify_id,
        )
