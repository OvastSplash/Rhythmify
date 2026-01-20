import logging

from django.core.management import BaseCommand
from User.models import CustomUser
from SpotifyController.services.data_aggregator import AggregatorService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Loads playlists from Spotify'

    def handle(self, *args, **options):
        users = CustomUser.objects.filter(spotify_id__isnull=False)

        aggregator = AggregatorService(users=users)
        aggregator.update_users_playlists()