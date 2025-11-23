from typing import List, Union
from User.models import CustomUser
from .client_services import SpotifyClientService, SpotifyPublicClientService
from .spotify_data_service import ConstructSpotifyDataService
from .db_services import SpotifyDatabaseService, GetSpotifyInfoFromDatabase
from .models import FavoriteUserTracks, RecommendationTracks
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

            tracks = sp_db.create_track(constructed_data)
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

            tracks = GetSpotifyInfoFromDatabase.get_user_top_tracks(user, count=10)
            artists = GetSpotifyInfoFromDatabase.get_user_top_artists(user, count=5)
            genres = GetSpotifyInfoFromDatabase.get_user_top_genres(user, count=5)

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