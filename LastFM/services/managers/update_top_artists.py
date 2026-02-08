import logging

from typing import List
from pylast import TopItem

from LastFM.services.construct_data_services import ConvertToSpotifyDataService

from LastFM.services.client_service import LastFMClientService
from SpotifyController.services.construct_data import ConstructDataService, ArtistClass
from SpotifyController.services.database.data_builder import BuildDataService


from SpotifyController.models.models import Artist

logger = logging.getLogger(__name__)

class UpdateTopArtistsManager:
    """
    Manages the updating of top artist data.

    This class provides methods to retrieve top artists from the Last.fm client,
    process the data, and convert it to a structure compatible with Spotify.
    It interacts with various services for data retrieval, transformation,
    and database operations, ensuring the seamless integration of artist
    information across different platforms.
    """

    def __init__(self):
        self.last_fm_client = LastFMClientService()
        self.construct_sp = ConstructDataService()
        self.sp_db = BuildDataService()

    @property
    def _get_top_artists(self) -> List[TopItem]:
        """
        Retrieves the top artists from the Last.fm client.

        Returns:
            List[TopItem]: A list of the top artists retrieved from the Last.fm client.
        """
        return self.last_fm_client.get_top_artists()

    def _create_artist(self, artist: ArtistClass) -> Artist:
        """
        Creates or updates an artist record in the database.

        This method interacts with the database to either create a new artist
        record or update an existing one based on the input data.

        Args:
            artist: An instance of ArtistClass containing the artist information
                to be created or updated.

        Returns:
            An instance of Artist representing the created or updated artist
            record.
        """
        return self.sp_db.create_or_update_artist(artist)

    def _convert_to_spotify_data(self, top_artists: List[TopItem]) -> List[Artist]:
        """
        Converts a list of top artist data to Spotify artist data objects.

        This method processes a list of top artist objects and converts them
        to Spotify artist objects (`Artist`). The conversion is done using
        a utility service that handles the transformation of artist data.
        If the conversion does not return a valid `Artist` object, it uses
        an internal method to create an `Artist` object before appending
        it to the result list.

        Args:
            top_artists: List of top artist objects to be converted.

        Returns:
            List of `Artist` objects corresponding to the given top artist data.
        """

        converted_artists: List[Artist] = list()

        for top_artist in top_artists:
            artist = ConvertToSpotifyDataService.convert_artist_data(top_artist)

            if isinstance(artist, Artist):
                converted_artists.append(artist)
            else:
                converted_artists.append(self._create_artist(artist))

        return converted_artists

    def run(self) -> List[Artist]:
        """
        Retrieves and processes the top artists data.

        This method retrieves the list of top artists and converts it to
        Spotify data format for further use.

        Returns:
            List[Artist]: A list of Artist objects in Spotify data format.
        """

        top_artists = self._get_top_artists
        return self._convert_to_spotify_data(top_artists)