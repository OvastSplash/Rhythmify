import time

from django.core.management.base import BaseCommand
import logging

from SpotifyController.models.models import Track

logger = logging.getLogger(__name__)
from SpotifyController.services.client_services import PublicClient

class Command(BaseCommand):
    help = 'Updates the duration for all tracks'

    def handle(self, *args, **options):
        tracks = Track.objects.all()
        sp_client = PublicClient()

        for i, track in enumerate(tracks):
            if track.duration_ms:
                logger.info("Track already has duration: name=%s duration_ms=%s", track.name, track.duration_ms)
                continue

            if i % 50 == 0 and i > 0:
                time.sleep(60)

            track_data = sp_client.get_track_info(track.spotify_id)
            track.duration_ms = track_data.duration_ms
            track.save()

            logger.info("Track duration updated: name=%s duration_ms=%s", track.name, track.duration_ms)