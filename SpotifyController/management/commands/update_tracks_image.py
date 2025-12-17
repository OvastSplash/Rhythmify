from django.core.management.base import BaseCommand

from SpotifyController.models.models import Track
from SpotifyController.services.client_services import PublicClient

from User.services import UserService
import time

class Command(BaseCommand):
    help = 'Updates the images for all tracks'

    def handle(self, *args, **options):
        tracks = Track.objects.all()

        for i, track in enumerate(tracks):
            if track.image:
                continue

            if i % 50 == 0 and i > 0:
                time.sleep(60)

            public_client = PublicClient()
            track_data = public_client.get_track_info(track.spotify_id)
            UserService.update_object_image(track, track_data.image_url)
            print(f"Track image updated: {track.name}")
