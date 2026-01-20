from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('SpotifyController', '0019_playlist_tracks'),
    ]

    operations = [
        TrigramExtension(),
    ]
