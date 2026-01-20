from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor
from LastFM.construct_data_services import TrackSyncManager

import logging

logger = logging.getLogger(__name__)

class UpdateUserRecommendations(UserDataProcessor):
    def run(self) -> None:
        """
        Update user recommendations based on listening history.

        This method collects and updates user-specific track recommendations by
        analyzing their listening history of tracks, artists, and genres, then
        saving these recommendations into the user's database. Any errors that
        occur during the process are logged and re-raised.

        Raises:
            Exception: If an error occurs during the recommendation update process.
        """

        try:
            logger.info("Updating user recommendations: username=%s", self.user.username)

            tracks = self.user_data.listen_history_tracks(count=5)
            artists = self.user_data.listen_history_artists(count=5)
            genres = self.user_data.listen_history_genres(count=5)

            recommended_tracks, existed_tracks = TrackSyncManager.collect_recommendations(tracks, artists, genres, commit=True)
            recommended_tracks.extend(existed_tracks)
            self.user_db.save_user_recommendation_tracks(recommended_tracks)

            logger.info("User recommendations updated: username=%s", self.user.username)
        except Exception as e:
            logger.error("Error occurred while updating user recommendations: %s", e)
            raise