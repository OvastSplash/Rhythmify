import logging

from typing import List
from SpotifyController.models.models import Artist
from Main.models import TopArtist

from Main.services.handlers.handle_base_class import BaseHandler
from Main.services.database.repositories.top_artists import TopArtistsRegister

from LastFM.services.managers.update_top_artists import UpdateTopArtistsManager

logger = logging.getLogger(__name__)


class UpdateTopArtistsHandler(BaseHandler):
    """
    Handles the process of updating and managing top artists.

    This class is responsible for managing the update process for top artists
    by integrating with the associated repository and manager. It supports
    clearing existing data and registering new top artists.

    Attributes:
        repository: Instance of TopArtistsRegister used to manage top artist data.
        get_top_artist_manager: Instance of UpdateTopArtistsManager used to retrieve
            the list of top artists.
    """

    repository = TopArtistsRegister()
    get_top_artist_manager = UpdateTopArtistsManager()

    @property
    def _top_artists(self) -> List[Artist]:
        """
        Returns the list of top artists.

        This property retrieves a list of the top artists by running the top artist
        manager function.

        Returns:
            List[Artist]: List containing instances of Artist for the top artists.
        """
        return self.get_top_artist_manager.run()

    def run(self, clear: bool = True) -> List[TopArtist]:
        """
        Updates the list of top artists by optionally clearing the current list and retrieving
        the most recent top artists. The updated list is then registered in the repository and
        returned.

        Parameters:
            clear: bool
                Indicates whether the current list of top artists should be cleared before
                fetching and registering new ones. Defaults to True.

        Returns:
            List[TopArtist]
                A list of the updated and registered top artists.
        """

        logger.info("Start updating top artists")

        if clear:
            self.repository.clear_top_artists()

        top_artists = self._top_artists
        registered_top_artists = self.repository.register_top_artists(artists=top_artists)

        logger.info("Top artists updated: artists=%s", registered_top_artists)
        return registered_top_artists