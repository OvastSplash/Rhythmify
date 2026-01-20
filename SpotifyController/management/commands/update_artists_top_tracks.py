import time
import logging

from django.core.management.base import BaseCommand

from SpotifyController.models.models import Playlist
from SpotifyController.services.client_services import UserClient, PublicClient
from SpotifyController.services.construct_data import CustomUser



from SpotifyController.services.database.save_user_data import SaveUserDataService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Command for updating artists top tracks"

    def handle(self, *args, **options):
        user = CustomUser.objects.filter(id=14).first()
        client = UserClient(user)

        playlist = Playlist.objects.filter().first()
        print(playlist.name)
        track_data = client.get_playlist_tracks(playlist.spotify_id)

        print(track_data)
        print(len(track_data))

        # post_save.disconnect(post_save_artist, sender=Artist)
        #
        # artists = Artist.objects.all()
        # public_client = PublicClient()
        # db_builder = BuildDataService()
        #
        # for i, artist in enumerate(artists):
        #     if artist.top_tracks.exists():
        #         logger.info("[COMMAND] TOP TRACKS ALREADY EXISTS: artist=%s sid=%s", artist.name, artist.spotify_id)
        #         continue
        #
        #     logger.info("[COMMAND] UPDATING ARTIST: artist=%s sid=%s", artist.name, artist.spotify_id)
        #
        #     with transaction.atomic():
        #         top_tracks_data = public_client.get_artist_top_tracks(artist.spotify_id)
        #         top_tracks = db_builder.create_tracks(top_tracks_data)
        #
        #         artist.top_tracks.add(*top_tracks)
        #
        #         logger.info(
        #             "Updated artist top tracks: artist=%s sid=%s tracks=%s",
        #             artist.name,
        #             artist.spotify_id,
        #             ", ".join(track.name for track in artist.top_tracks.all()),
        #         )
        #
        #     time.sleep(0.3)