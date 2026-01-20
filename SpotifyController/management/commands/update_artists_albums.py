from django.core.management import BaseCommand
import logging

from SpotifyController.models.models import Artist
from SpotifyController.services.client_services import PublicClient
from SpotifyController.services.database.data_builder import BuildDataService

import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "This command is used to update artist's albums"

    def handle(self, *args, **options):
        artists = Artist.objects.all()
        db_builder = BuildDataService()

        for i, artist in enumerate(artists):
            if artist.albums.exists():
                continue

            public_client = PublicClient()

            albums_data = public_client.get_artist_albums(artist.spotify_id)
            albums = db_builder.create_albums(albums_data)

            artist.albums.add(*albums)

            logger.info("[COMMAND] Artist albums updated: artist=%s sid=%s", artist.name, artist.spotify_id)

            logger.info(
                "[COMMAND] Albums list: artist=%s albums=%s",
                artist.name,
                ", ".join(album.name for album in artist.albums.all()),
            )

            if i % 5 == 0:
                time.sleep(60)