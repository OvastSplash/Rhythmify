from typing import List, Union, Tuple
import logging

from User.models import CustomUser

from SpotifyController.services.client_services import UserClient, PublicClient
from SpotifyController.services.construct_data import ConstructDataService
from SpotifyController.services.database.data_builder import BuildDataService
from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.database.save_user_data import SaveUserDataService

from SpotifyController.models.models import Track
from LastFM.construct_data_services import TrackSyncManager

logger = logging.getLogger(__name__)


#TODO: Написать декоратор который в случае не правильной передачи данных будет передавать данные в новую функцию
class AggregatorService:
    def __init__(self, users: List[CustomUser] = None, user: CustomUser = None):
        self.user = user
        self.users = users

    def update_user_favorite_tracks(self) -> Tuple[List[Track], List[Track], List[Track]]:
        sp_db = BuildDataService()

        sp_client = UserClient(user=self.user)

        #TODO: Понять почему так долго работает (возможно баг консоли)
        logger.info("Construct favorite tracks: username=%s", self.user.username)

        short_term_constructed_data = sp_client.get_user_short_term_top_tracks(limit=20)
        medium_term_constructed_data = sp_client.get_user_medium_term_top_tracks(limit=20)
        long_term_constructed_data = sp_client.get_user_long_term_top_tracks(limit=20)

        logger.info("User favorite tracks constructed: username=%s", self.user.username)

        logger.info("Start saving favorite tracks to database: username=%s", self.user.username)
        short_term_tracks: List[Track] = sp_db.create_tracks(short_term_constructed_data)
        medium_term_tracks: List[Track] = sp_db.create_tracks(medium_term_constructed_data)
        long_term_tracks: List[Track] = sp_db.create_tracks(long_term_constructed_data)

        logger.info("User favorite tracks saved: username=%s", self.user.username)

        save_user_data = SaveUserDataService(user=self.user)

        save_user_data.favorite_user_tracks_short_term(short_term_tracks)
        save_user_data.favorite_user_tracks_medium_term(medium_term_tracks)
        save_user_data.favorite_user_tracks_long_term(long_term_tracks)

        logger.info("User short term tracks updated: username=%s", self.user.username)
        logger.info("User medium term tracks updated: username=%s", self.user.username)
        logger.info("User long term favorite tracks updated: username=%s", self.user.username)

        return short_term_tracks, medium_term_tracks, long_term_tracks

    def update_users_favorite_tracks(self) -> None:
        if self.users:
            for user in self.users:
                logger.info("Updating favorite tracks: username=%s", user.username)
                self.user = user
                self.update_user_favorite_tracks()
                logger.info("User favorite tracks updated: username=%s", self.user.username)

        else:
            raise Exception("Users list is empty")



    @staticmethod
    def update_artist_data(artists_sp_ids: Union[List[str], str]):
        if isinstance(artists_sp_ids, str):
            artists_sp_ids = [artists_sp_ids]

            sp_public = PublicClient()
            sp_construct = ConstructDataService()
            sp_db = BuildDataService()

            for artist_sp_id in artists_sp_ids:
                artist_data = sp_public.get_artist_info(artist_sp_id)
                constructed_artist_data = sp_construct.artist_data(artist_data)
                sp_db.create_or_update_artist(constructed_artist_data)



    def update_user_recommendations(self, create_playlist: bool = False) -> List[Track]:
        user_data = GetUserDataService(user=self.user)

        tracks = user_data.listen_history_tracks(count=5)
        artists = user_data.listen_history_artists(count=5)
        genres = user_data.listen_history_genres(count=5)

        recommended_tracks, existed_tracks = TrackSyncManager.collect_recommendations(tracks, artists, genres, commit=True)
        recommended_tracks.extend(existed_tracks)

        sp_client = UserClient(user=self.user)
        save_user_data = SaveUserDataService(user=self.user)

        recommendations = save_user_data.recommendation_tracks(recommended_tracks)

        if create_playlist:
            sp_client.create_user_recommendation_playlist(self.user)

        logger.info("User recommendations updated: username=%s", self.user.username)
        return recommendations

    def update_users_recommendations(self, create_playlist: bool = False):
        if self.users:
            for user in self.users:
                self.user = user
                self.update_user_recommendations(create_playlist)

        else:
            raise Exception("Users list is empty")


    def save_user_listen_tracks(self):
        sp_db = BuildDataService()

        logger.debug("Saving user listened tracks: username=%s", self.user.username)

        sp_client = UserClient(user=self.user)
        constructed_tracks = sp_client.get_user_recently_played(limit=5)
        tracks = sp_db.create_played_at_tracks(constructed_tracks)

        save_user_data = SaveUserDataService(user=self.user)
        save_user_data.listen_tracks_history(tracks)

        logger.info("User listen statistic updated: username=%s", self.user.username)


    def save_users_listened_tracks(self):
        if self.users:
            for user in self.users:
                self.user = user
                self.save_user_listen_tracks()

        else:
            raise Exception("Users list is empty")


    def update_user_playlists(self):
        logger.info("Updating user playlists: username=%s", self.user.username)

        client = UserClient(self.user)
        playlists = client.get_user_playlists_data()

        user_db = SaveUserDataService(self.user)
        user_db.create_playlists(playlists)

        logger.info("User playlists updated: username=%s", self.user.username)

    def update_users_playlists(self):
        if self.users:
            for user in self.users:
                self.user = user
                self.update_user_playlists()

        else:
            raise Exception("Users list is empty")