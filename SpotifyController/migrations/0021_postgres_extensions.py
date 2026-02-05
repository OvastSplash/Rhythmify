from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('SpotifyController', '0020_album_album_name_trgm_idx_and_more'),
    ]

    operations = [
        TrigramExtension(),
    ]
