from django.db import transaction
import time

class ArtistPostSave:
    def __init__(self, artist) -> None:
        from SpotifyController.services.client_services import PublicClient
        from SpotifyController.services.database.data_builder import BuildDataService

        self.artist = artist
        self.public_client = PublicClient()
        self.db_builder = BuildDataService()

    @transaction.atomic
    def handle_top_tracks(self):
        if self.artist.top_tracks.exists():
            return

        print()
        print(f"Updating artist's top_tracks --- Artist Name: {self.artist.name}")

        time.sleep(0.3)

        top_tracks_data = self.public_client.get_artist_top_tracks(self.artist.spotify_id)
        top_tracks = self.db_builder.create_tracks(top_tracks_data)
        self.artist.top_tracks.add(*top_tracks)

        print(f"Successfully added {len(top_tracks_data)} tracks to artist --- Artist Name: {self.artist.name}")

    @transaction.atomic
    def handle_albums(self):
        if self.artist.albums.exists():
            return
        print()
        print(f"Updating artist's albums --- Artist Name: {self.artist.name}")

        time.sleep(0.3)

        albums_data = self.public_client.get_artist_albums(self.artist.spotify_id)
        albums = self.db_builder.create_albums(albums_data)
        self.artist.albums.add(*albums)
        print(f"Successfully added {len(albums)} albums to artist --- Artist Name: {self.artist.name}")