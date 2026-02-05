import logging

from SpotifyController.services.aggregator.aggregator_base import BaseAggregator

logger = logging.getLogger(__name__)

class UpdateArtistData(BaseAggregator):
    def update_artist(self, artist_sid: str) -> None:
        """
        Updates the metadata of a specified artist by fetching details from a public
        source and saving them to the database.

        Attributes
        ----------
        None

        Parameters
        ----------
        artist_sid : str
            The unique identifier for the artist to be updated.

        Raises
        ------
        Exception
            If an error occurs during the update process, a generic exception is
            raised after logging the error details.
        """
        try:
            logger.info(f"Updating artist {artist_sid}")
            artist_data = self.sp_public.get_artist_info(artist_sid)

            self.sp_db.create_or_update_artist(artist_data)
            logger.info(f"Artist {artist_sid} updated")
        except Exception as e:
            logger.error(f"Error occurred while updating artist {artist_sid}: {e}")
            raise

    def update_artists(self, artists_sids: list[str]):
        """
        Updates multiple artists based on their unique identifiers (SIDs).

        The method iterates over a list of artist SIDs and calls the `update_artist`
        method for each SID. It ensures that all provided artists are updated
        individually.

        Args:
            artists_sids (list[str]): A list of artist SIDs to be updated.
        """

        for artist_sid in artists_sids:
            self.update_artist(artist_sid)