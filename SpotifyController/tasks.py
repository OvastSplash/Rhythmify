from typing import List

from celery import shared_task
from User.models import CustomUser
from .models import Artist, RecommendationTracks, FavoriteUserTracks
from .services import SpotifyService
from .db_services import SpotifyDatabaseService, GetSpotifyInfoFromDatabase
from .client_services import SpotifyClientService, SpotifyPublicClientService
from .spotify_data_service import ConstructSpotifyDataService
from django.db.models import Count
from LastFM.construct_data_services import TrackSyncManager

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

        print(tracks)
        SpotifyDatabaseService.save_tracks_to_user_list(FavoriteUserTracks, tracks, user)

        print(f"Updated favorite tracks for {user.username}")


@shared_task
def update_artist_data():
    artists = Artist.objects.annotate(
        fav_count=Count('track_list__favorite_users')
    ).filter(fav_count=0, spotify_id__isnull=False)

    for artist in artists:
        artist_data = SpotifyPublicClientService.get_artist_info(artist.spotify_id)
        constructed_artist_data = ConstructSpotifyDataService.construct_artist_data(artist_data)
        SpotifyDatabaseService.create_or_update_artist(constructed_artist_data)

@shared_task
def update_user_recommendations():
    users = CustomUser.objects.filter(
        is_active=True,
        access_token__isnull=False,
    ).prefetch_related("favorite_tracks_links__track__artists")

    for user in users:
        print(user.username)

        tracks = GetSpotifyInfoFromDatabase.get_user_top_tracks(user, count=10)
        artists = GetSpotifyInfoFromDatabase.get_user_top_artists(user, count=5)
        genres = GetSpotifyInfoFromDatabase.get_user_top_genres(user, count=5)

        recommended_tracks, existed_tracks = TrackSyncManager.collect_recommendations(tracks, artists, genres, commit=True)
        recommended_tracks.extend(existed_tracks)

        sp_client = SpotifyClientService(access_token=user.access_token)
        SpotifyDatabaseService.save_tracks_to_user_list(RecommendationTracks, recommended_tracks, user)
        sp_client.create_user_recommendation_playlist(recommended_tracks)

        print(tracks)
