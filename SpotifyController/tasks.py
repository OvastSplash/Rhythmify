from celery import shared_task
from User.models import CustomUser
from .services import SpotifyService
from .db_services import SpotifyDatabaseService
from .client_services import SpotifyClientService

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

    for user in users:
        sp_client = SpotifyClientService(access_token=user.access_token)
        constructed_data = sp_client.get_user_top_tracks()
        tracks = SpotifyDatabaseService.create_track(constructed_data)

        if user.favorite_tracks_links.count() > 0:
            user.favorite_tracks_links.all().delete()

        print(tracks)
        SpotifyDatabaseService.save_tracks_to_user_favorite_list(tracks, user)

        print(f"Updated favorite tracks for {user.username}")

#TODO: Сделать таску на автообновление аватарок всех авторов
