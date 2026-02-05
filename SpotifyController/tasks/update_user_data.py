from celery import shared_task
import logging

from SpotifyController.services.aggregator.update_user_playlists import UpdateUserPlaylists
from User.models import CustomUser
from SpotifyController.models.models import Artist

from SpotifyController.services.aggregator.aggregator_base import BaseUserAggregator

from SpotifyController.services.aggregator.update_user_favorite_tracks import UpdateUserFavoriteTracks
from SpotifyController.services.aggregator.update_artist_data import UpdateArtistData
from SpotifyController.services.aggregator.update_user_recommendations import UpdateUserRecommendations
from SpotifyController.services.aggregator.update_user_listened_tracks import UpdateUserListenedTracks

from typing import List

logger = logging.getLogger(__name__)

def _get_active_users() -> List[CustomUser]:
    return CustomUser.objects.filter(
        is_active=True,
        access_token__isnull=False,
    )

@shared_task
def update_user_favorite_tracks():
    logger.info("update_user_favorite_tracks")

    aggregator = BaseUserAggregator(users=_get_active_users())
    aggregator.run_services_for_each_user(UpdateUserFavoriteTracks)

@shared_task
def update_artist_data():
    logger.info("update_artist_data")

    artists_sids = list(Artist.objects.all().values_list(
        'spotify_id', flat=True))

    aggregator = UpdateArtistData()
    aggregator.update_artists(artists_sids)

@shared_task
def update_user_recommendations():
    logger.info("update_user_recommendations")

    aggregator = BaseUserAggregator(users=_get_active_users())
    aggregator.run_services_for_each_user(UpdateUserRecommendations)

    logger.info("Users recommendations updated")

@shared_task
def update_user_listen_tracks():
    logger.info("update_user_listen_tracks")

    aggregator = BaseUserAggregator(users=_get_active_users())
    aggregator.run_services_for_each_user(UpdateUserListenedTracks)

@shared_task
def update_user_playlists():
    logger.info("update_user_playlists")

    aggregator = BaseUserAggregator(users=_get_active_users())
    aggregator.run_services_for_each_user(UpdateUserPlaylists)





