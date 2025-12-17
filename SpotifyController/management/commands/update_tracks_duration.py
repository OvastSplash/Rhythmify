import time

from django.core.management.base import BaseCommand

from SpotifyController.models.models import Track
from SpotifyController.services.client_services import PublicClient

class Command(BaseCommand):
    help = 'Updates the duration for all tracks'

    def handle(self, *args, **options):
        tracks = Track.objects.all()
        sp_client = PublicClient()

        for i, track in enumerate(tracks):
            if track.duration_ms:
                print(f"Track {track.name} already has duration: {track.duration_ms}")
                continue

            if i % 50 == 0 and i > 0:
                time.sleep(60)

            track_data = sp_client.get_track_info(track.spotify_id)
            track.duration_ms = track_data.duration_ms
            track.save()

            print(f"Track duration updated: {track.name} - {track.duration_ms}")