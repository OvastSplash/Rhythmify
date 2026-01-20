from django.db import transaction
import time
import logging

logger = logging.getLogger(__name__)


class ArtistPostSave:
    def __init__(self, artist) -> None:
        from SpotifyController.services.client_services import PublicClient
        from SpotifyController.services.database.data_builder import BuildDataService

        self.artist = artist
        self.public_client = PublicClient()
        self.db_builder = BuildDataService()

    def handle_top_tracks(self):
        if self.artist.top_tracks.exists():
            return

        logger.info("Updating artist's top_tracks: artist=%s sid=%s", self.artist.name, self.artist.spotify_id)

        time.sleep(0.3)

        top_tracks_data = self.public_client.get_artist_top_tracks(self.artist.spotify_id)
        top_tracks = self.db_builder.create_tracks(top_tracks_data)
        self.artist.top_tracks.add(*top_tracks)

        logger.info(
            "Successfully added %d top tracks to artist=%s sid=%s",
            len(top_tracks_data), self.artist.name, self.artist.spotify_id,
        )

    def handle_albums(self):
        if self.artist.albums.exists():
            return
        logger.info("Updating artist's albums: artist=%s sid=%s", self.artist.name, self.artist.spotify_id)

        time.sleep(0.3)

        albums_data = self.public_client.get_artist_albums(self.artist.spotify_id)
        albums = self.db_builder.create_albums(albums_data)
        self.artist.albums.add(*albums)
        logger.info(
            "Successfully added %d albums to artist=%s sid=%s",
            len(albums), self.artist.name, self.artist.spotify_id,
        )