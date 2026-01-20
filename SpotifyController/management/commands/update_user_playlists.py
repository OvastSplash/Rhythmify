import logging

from django.core.management import BaseCommand

from SpotifyController.models.models import Playlist
from SpotifyController.services.client_services import UserClient
from SpotifyController.services.database.data_builder import BuildDataService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates the playlists for all users'

    def handle(self, *args, **options):
        logger.info("Updating playlists for all users")

        playlists = Playlist.objects.all()[3]

        logger.info("First playlist: name=%s", playlists.name)
        client = UserClient(playlists.user)
        db_builder = BuildDataService()

        constructed_tracks = client.get_playlist_tracks(playlists.spotify_id)
        tracks = db_builder.create_tracks(constructed_tracks)

        playlists.tracks.add(*tracks)

        logger.info("Playlists updated successfully")