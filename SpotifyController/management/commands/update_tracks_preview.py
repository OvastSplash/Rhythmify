from time import sleep
import logging

from django.core.management.base import BaseCommand

from Deezer.services import ClientService
from SpotifyController.models.models import Track

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates the preview for all tracks'

    def handle(self, *args, **options):
        tracks = Track.objects.all()
        deezer_client = ClientService()

        for i, track in enumerate(tracks):
            if track.preview:
                logger.info("Track already has preview: name=%s preview=%s", track.name, str(track.preview))
                continue

            if i % 50 == 0 and i > 0:
                sleep(60)

            preview_mp3 = deezer_client.get_preview_by_track(track)

            if not preview_mp3:
                logger.warning("Preview not found for track: name=%s sid=%s", track.name, track.spotify_id)
                continue

            url = track.save_preview(preview_mp3)
            logger.info("Preview has been updated for track: name=%s url=%s", track.name, url)
