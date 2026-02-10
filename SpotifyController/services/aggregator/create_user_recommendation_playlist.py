import logging

from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor
from SpotifyController.services.user_cache import UserCacheService

logger = logging.getLogger(__name__)

class CreateUserRecommendationPlaylist(UserDataProcessor):
    """
    Handles the creation of user recommendation playlists.

    This class is responsible for processing user-related data to generate
    a playlist of recommended tracks. It interacts with user-specific
    cache data to retrieve recommended track IDs and uses a Spotify client
    (`sp_client`) to create the playlist.

    Attributes:
        user: The user object containing the details about the user
              for whom the recommendation playlist is to be created.
        sp_client: The Spotify client used to manage playlists and other
                   related actions.
    """

    @property
    def _user_recommendation_tracks_ids(self):
        """
        Provides access to the user's recommended track IDs, retrieving the data
        from the user cache service. This property allows fetching recommended
        tracks for the user in an efficient manner.

        Returns
        -------
        list
            The list of identifiers for tracks recommended for the user.
        """

        user_cache_service = UserCacheService(self.user.id)
        return user_cache_service.get_user_recommended_tracks()

    def run(self):
        """
        Executes the process of generating a user recommendation playlist.

        This method logs the creation process of a recommendation playlist
        for the user. It retrieves the recommended track IDs and utilizes
        a Spotify client to create a playlist from those tracks.

        Raises:
            Any exceptions raised by the Spotify client during playlist creation.
        """

        logger.info("Creating user recommendation playlist")

        recommended_tracks_ids = self._user_recommendation_tracks_ids
        self.sp_client.create_playlist(tracks_ids=recommended_tracks_ids)

        logger.info("Playlist created")