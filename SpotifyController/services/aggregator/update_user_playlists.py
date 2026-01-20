import logging

from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor

logger = logging.getLogger(__name__)

class UpdateUserPlaylists(UserDataProcessor):
    def run(self) -> None:
        """
        Updates user playlists by retrieving data from the Spotify client and storing
        it in the user database.

        This method retrieves the playlists for a specific user from an external Spotify
        API client and updates the user's playlist information in a database. Logging
        is used to provide information about the update status and any potential errors.

        Raises:
            Exception: Propagates the exception if an error occurs during the process.
        """

        try:
            logger.info("Updating user playlists: username=%s", self.user.username)

            playlists = self.sp_client.get_user_playlists_data()
            self.user_db.create_playlists(playlists)

            logger.info("User playlists updated: username=%s", self.user.username)
        except Exception as e:
            logger.error("Error occurred while updating user playlists: %s", e)
            raise