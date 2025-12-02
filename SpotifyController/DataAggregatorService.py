from typing import List, Union

from django.db.models import QuerySet

from User.models import CustomUser
from .client_services import SpotifyClientService, SpotifyPublicClientService
from .spotify_data_service import ConstructSpotifyDataService
from .db_services import SpotifyDatabaseService, GetSpotifyInfoFromDatabase
from .models import FavoriteUserTracks, RecommendationTracks, Track
from .CacheService import UserCacheService
from LastFM.construct_data_services import TrackSyncManager

class AggregatorService:
    @staticmethod
    def update_user_favorite_tracks(users: Union[List[CustomUser], CustomUser], clear_cache: bool = True):
        if isinstance(users, CustomUser):
            users = [users]

        sp_db = SpotifyDatabaseService()
        cache_service = UserCacheService()

        for user in users:
            sp_client = SpotifyClientService(access_token=user.access_token)
            constructed_data = sp_client.get_user_top_tracks()

            tracks:List[Track] = sp_db.create_tracks(constructed_data)

            sp_db.save_tracks_to_user_list(FavoriteUserTracks, tracks, user)

            if clear_cache:
                cache_service.clear_user_favorite_tracks(user.id)

            cache_service.set_user_favorite_tracks(user.id, tracks)

            print(f"User {user.username} favorite tracks has been updated to: {tracks}")

    @staticmethod
    def update_artist_data(artists_sp_ids: Union[List[str], str]):
        if isinstance(artists_sp_ids, str):
            artists_sp_ids = [artists_sp_ids]

            sp_public = SpotifyPublicClientService()
            sp_construct = ConstructSpotifyDataService()
            sp_db = SpotifyDatabaseService()

            for artist_sp_id in artists_sp_ids:
                artist_data = sp_public.get_artist_info(artist_sp_id)
                constructed_artist_data = sp_construct.construct_artist_data(artist_data)
                sp_db.create_or_update_artist(constructed_artist_data)


    @staticmethod
    def update_user_recommendations(users: Union[List[CustomUser], CustomUser], clear_cache: bool = True, create_playlist: bool = False):
        if isinstance(users, CustomUser):
            users = [users]

        sp_db = SpotifyDatabaseService()

        for user in users:
            print(user.username)
            get_sp_db = GetSpotifyInfoFromDatabase(user)

            tracks = get_sp_db.get_user_top_tracks(count=10)
            artists = get_sp_db.get_user_top_artists(count=5)
            genres = get_sp_db.get_user_top_genres(count=5)

            recommended_tracks, existed_tracks = TrackSyncManager.collect_recommendations(tracks, artists, genres, commit=True)
            recommended_tracks.extend(existed_tracks)

            sp_client = SpotifyClientService(access_token=user.access_token)
            sp_db.save_tracks_to_user_list(RecommendationTracks, recommended_tracks, user)

            if create_playlist:
                sp_client.create_user_recommendation_playlist(user)

            if clear_cache:
                UserCacheService.clear_user_recommended_tracks(user.id)

            UserCacheService.set_user_recommended_tracks(user.id, recommended_tracks)

            print(tracks)

    @staticmethod
    def save_users_listen_tracks(users: Union[List[CustomUser]]):
        sp_db = SpotifyDatabaseService()

        for user in users:
            print(user.username)

            sp_client = SpotifyClientService(access_token=user.access_token)
            constructed_tracks = sp_client.get_user_recently_played(limit=5)
            tracks = sp_db.create_played_at_tracks(constructed_tracks)
            sp_db.save_user_listen_tracks_history(user, tracks)

            get_sp_db = GetSpotifyInfoFromDatabase(user)
            cache_data = get_sp_db.get_user_listen_statistic()

            print(cache_data)

            UserCacheService.set_user_statistics(user.id, cache_data)