from celery import shared_task

from User.models import CustomUser
from SpotifyController.models.models import Artist

from SpotifyController.services.data_aggregator import AggregatorService

from typing import List

def _get_active_users() -> List[CustomUser]:
    return CustomUser.objects.filter(
        is_active=True,
        access_token__isnull=False,
    )

@shared_task
def update_user_favorite_tracks():
    print("update_user_favorite_tracks")

    aggregator = AggregatorService(users=_get_active_users())
    aggregator.update_users_favorite_tracks()

@shared_task
def update_artist_data():
    print("update_artist_data")

    artists = list(Artist.objects.all().values_list(
        'spotify_id', flat=True))

    AggregatorService.update_artist_data(artists)

@shared_task
def update_user_recommendations():
    print("update_user_recommendations")

    aggregator = AggregatorService(users=_get_active_users())
    aggregator.update_users_recommendations()


@shared_task
def update_user_listen_tracks():
    print("update_user_listen_tracks")

    aggregator = AggregatorService(users=_get_active_users())
    aggregator.save_users_listened_tracks()

