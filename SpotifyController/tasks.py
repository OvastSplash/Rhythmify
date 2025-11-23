from celery import shared_task
from User.models import CustomUser
from .CacheService import UserCacheService
from .models import Artist
from .services import SpotifyService
from .DataAggregatorService import AggregatorService

@shared_task
def refresh_spotify_tokens():
    users = CustomUser.objects.filter(
        is_active=True,
        refresh_token__isnull=False,
        access_token__isnull=False,
        token_expires_at__isnull=False,
    ).all()

    for user in users:
        SpotifyService.refresh_user_tokens(user)

@shared_task
def update_user_favorite_tracks():
    users = CustomUser.objects.filter(
        is_active=True,
        access_token__isnull=False,
    ).prefetch_related('favorite_tracks_links__track')

    AggregatorService.update_user_favorite_tracks(users)


@shared_task
def update_artist_data():
    artists = list(Artist.objects.all().values_list(
        'spotify_id', flat=True))

    AggregatorService.update_artist_data(artists)

@shared_task
def update_user_recommendations():
    users = CustomUser.objects.filter(
        is_active=True,
        access_token__isnull=False,
    ).prefetch_related("favorite_tracks_links__track__artists")

    AggregatorService.update_user_recommendations(users)
    print(UserCacheService.get_user_recommended_tracks(users[0].id))