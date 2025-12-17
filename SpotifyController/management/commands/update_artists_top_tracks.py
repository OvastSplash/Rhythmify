import time

from django.core.management.base import BaseCommand

from SpotifyController.models.models import Artist
from SpotifyController.services.client_services import PublicClient
from SpotifyController.services.database.data_builder import BuildDataService
from django.db import transaction

class Command(BaseCommand):
    help = "Command for updating artists top tracks"

    def handle(self, *args, **options):
        artists = Artist.objects.all()
        public_client = PublicClient()
        db_builder = BuildDataService()

        for i, artist in enumerate(artists):
            if artist.top_tracks.exists():
                print(f"Top Tracks --- {artist.name} already exists")
                continue

            print(f"Updating artist --- {artist.name}")

            with transaction.atomic():
                top_tracks_data = public_client.get_artist_top_tracks(artist.spotify_id)
                top_tracks = db_builder.create_tracks(top_tracks_data)

                artist.top_tracks.add(*top_tracks)

                print(f"Updated artist --- {artist.name}")
                print("Top Tracks ---", ", ".join(track.name for track in artist.top_tracks.all()))
                print()
                break

            if i % 5 == 0:
                time.sleep(60)