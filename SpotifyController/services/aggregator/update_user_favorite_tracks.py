from .aggregator_base import UserDataProcessor
from typing import List, Tuple
from SpotifyController.models.models import Track

import logging

from ..construct_data import TrackClass

logger = logging.getLogger(__name__)

class UpdateUserFavoriteTracks(UserDataProcessor):
    @property
    def _get_term_constructed_tracks(self) -> Tuple:
        """Get favorite tracks constructed from Spotify API."""
        return (
            self.sp_client.get_user_short_term_top_tracks(limit=20),
            self.sp_client.get_user_medium_term_top_tracks(limit=20),
            self.sp_client.get_user_long_term_top_tracks(limit=20)
        )

    def _create_tracks(self, constructed_tracks: List[TrackClass]) -> List[Track]:
        """Create tracks from constructed data and save them to database."""
        return self.sp_db.create_tracks(constructed_tracks)

    def _save_tracks_to_user(self, short_term_tracks: List[Track], medium_term_tracks: List[Track], long_term_tracks: List[Track]) -> None:
        """Save favorite tracks to user and redis."""
        self.user_db.favorite_user_tracks_short_term(short_term_tracks)
        self.user_db.favorite_user_tracks_medium_term(medium_term_tracks)
        self.user_db.favorite_user_tracks_long_term(long_term_tracks)

    def run(self) -> None:
        """
        Execute the process of constructing and saving the user's favorite tracks.

        This method handles the construction of favorite tracks for different terms, saves
        them to a database, and updates the tracks for the user. Detailed logs are recorded
        at each step to document the process and provide traceability. If any error occurs
        during the process, it is logged and re-raised, halting the execution and ensuring
        proper error handling.

        Raises:
            Exception: Re-raises any exception encountered during the process.
        """

        try:
            logger.info("Construct favorite tracks: username=%s", self.user.username)

            (short_term_constructed_data,
             medium_term_constructed_data,
             long_term_constructed_data) = self._get_term_constructed_tracks

            logger.info("User favorite tracks constructed: username=%s", self.user.username)

            logger.info("Start saving favorite tracks to database: username=%s", self.user.username)
            short_term_tracks: List[Track] = self._create_tracks(short_term_constructed_data)
            medium_term_tracks: List[Track] = self._create_tracks(medium_term_constructed_data)
            long_term_tracks: List[Track] = self._create_tracks(long_term_constructed_data)

            logger.info("User favorite tracks saved: username=%s", self.user.username)

            self._save_tracks_to_user(short_term_tracks, medium_term_tracks, long_term_tracks)

            logger.info("User short term tracks updated: username=%s", self.user.username)
            logger.info("User medium term tracks updated: username=%s", self.user.username)
            logger.info("User long term favorite tracks updated: username=%s", self.user.username)

        except Exception as e:
            logger.error("Error occurred while updating user favorite tracks: %s", e)
            raise