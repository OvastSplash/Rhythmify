from time import sleep

from django.core.management.base import BaseCommand

from Deezer.services import ClientService
from SpotifyController.models.models import Track

class Command(BaseCommand):
    help = 'Updates the preview for all tracks'

    def handle(self, *args, **options):
        tracks = Track.objects.all()
        deezer_client = ClientService()

        for i, track in enumerate(tracks):
            if track.preview:
                print(f"Track {track.name} already has preview: {track.preview}")
                continue

            if i % 50 == 0 and i > 0:
                sleep(60)

            preview_mp3 = deezer_client.get_preview_by_track(track)

            if not preview_mp3:
                print(f"Preview not found for track: {track.name}")
                continue

            url = track.save_preview(preview_mp3)
            print(f"Preview has been updated for track: {track.name} --- URL: {url}")
