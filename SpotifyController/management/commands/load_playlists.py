import logging

from django.core.management import BaseCommand
from User.models import CustomUser
from SpotifyController.services.aggregator.aggregator_base import BaseUserAggregator
from SpotifyController.services.aggregator.update_user_playlists import UpdateUserPlaylists

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Loads playlists from Spotify'

    def handle(self, *args, **options):
        users = CustomUser.objects.filter(spotify_id__isnull=False)

        aggregator = BaseUserAggregator(users=users)
        aggregator.run_services_for_each_user(UpdateUserPlaylists)