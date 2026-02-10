import logging

from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor
from Main.services.cache import MainCache

logger = logging.getLogger(__name__)

class CreateTopTracksPlaylist(UserDataProcessor):
    """
    Creates a playlist of top tracks for a user.

    This class processes user data and retrieves their top track IDs from the main cache.
    It then creates a playlist using these track IDs via the Spotify client.

    Attributes:
        user: The user for whom the playlist is being created. This is an instance
            of a user-related object containing user-specific information.
        sp_client: An instance of the Spotify client used to interact with the
            Spotify API.

    Methods:
        run: Executes the process of creating a playlist containing the user's top
            tracks.
    """

    @property
    def _top_tracks_ids(self):
        """
        Retrieves a list of top track IDs stored in the main cache.

        Raises:
            Any error that might occur during the retrieval of top tracks from
            the main cache.
        """
        main_cache = MainCache()
        return main_cache.get_top_tracks()

    def run(self):
        """
        Creates a playlist of top tracks for a user.

        This method generates a playlist containing the user's top tracks by
        fetching their track IDs and utilizing the Spotify client to create the
        playlist. Logs the progress of the playlist creation.

        Raises:
            Exception: If there are issues with accessing the user's top tracks
                       or playlist creation fails.
        """

        logger.info("Creating top tracks playlist for user: user=%", self.user.id)

        top_tracks_ids = self._top_tracks_ids
        self.sp_client.create_playlist(top_tracks_ids)

        logger.info("Top tracks playlist created for user: user=%", self.user.id)
