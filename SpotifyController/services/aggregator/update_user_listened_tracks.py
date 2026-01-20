import logging

from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor

logger = logging.getLogger(__name__)

class UpdateUserListenedTracks(UserDataProcessor):
    def run(self) -> None:
        """
        Updates the user's listening history with recently played tracks.

        This method interacts with the Spotify API and a database to retrieve and save
        the user's recently played tracks. It performs the following steps:
        1. Fetches the user's recently played tracks using the Spotify client.
        2. Constructs track records in the desired format using the database utility.
        3. Saves the constructed track records to the user's listening history in the database.

        If an error occurs at any step during this process, it is logged and re-raised for
        further handling by the calling code.

        Raises:
            Exception: If any error occurs during the process of fetching, constructing, or
            saving recently played tracks.
        """

        try:
            logger.debug("Saving user listened tracks: username=%s", self.user.username)

            constructed_tracks = self.sp_client.get_user_recently_played(limit=5)
            tracks = self.sp_db.create_played_at_tracks(constructed_tracks)

            self.user_db.save_listen_tracks_history(tracks)

            logger.info("User listen statistic updated: username=%s", self.user.username)
        except Exception as e:
            logger.error("Error occurred while updating user listen statistic: %s", e)
            raise