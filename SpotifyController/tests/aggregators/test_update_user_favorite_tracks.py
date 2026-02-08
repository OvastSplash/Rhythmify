import logging

from unittest.mock import Mock, patch, PropertyMock
import pytest
from SpotifyController.services.aggregator.update_user_favorite_tracks import UpdateUserFavoriteTracks
from SpotifyController.models.models import Track

logger = logging.getLogger("test")

def test_update_user_favorite_tracks_unit(update_user_favorite_tracks: UpdateUserFavoriteTracks):
    """
    Test function to validate the behavior of update_user_favorite_tracks.process_top_tracks method under unit testing
    conditions. This test targets the functionality related to fetching, creating, and saving user favorite
    tracks using mocked dependencies.

    Attributes:
        update_user_favorite_tracks (UpdateUserFavoriteTracks): An instance of the
        UpdateUserFavoriteTracks class, which is the subject under test.

    Raises:
        AssertionError: Raised when any of the test assertions fail during the process.

    Test behavior:
        - Mocks the `_get_term_constructed_tracks` property method to provide mock track data for
          various time terms (e.g., short, medium, long).
        - Mocks the `_create_tracks` method to simulate the creation of favorite track lists for each
          time term.
        - Mocks the `_save_tracks_to_user` method to validate if it correctly saves the created track
          lists to the user.
        - Asserts that the `_create_tracks` method is called exactly three times and for each term.
        - Ensures that the `_save_tracks_to_user` method is called once with the created track lists
          and the correct caching behavior.
    """

    logger.info("test_update_user_favorite_tracks_unit")

    mock_short = Mock()
    mock_medium = Mock()
    mock_long = Mock()

    fake_short_tracks = [Mock(spec=Track)]
    fake_medium_tracks = [Mock(spec=Track)]
    fake_long_tracks = [Mock(spec=Track)]

    with patch.object(UpdateUserFavoriteTracks, "_get_term_constructed_tracks", new_callable=PropertyMock) as mock_get_tracks, \
         patch.object(UpdateUserFavoriteTracks, "_create_tracks", side_effect=[fake_short_tracks, fake_medium_tracks, fake_long_tracks]) as mock_create_tracks, \
         patch.object(UpdateUserFavoriteTracks, "_save_tracks_to_user") as mock_save_to_user:

        mock_get_tracks.return_value = (mock_short, mock_medium, mock_long)

        update_user_favorite_tracks.run(cache=False)

        mock_create_tracks.assert_any_call(mock_short)
        mock_create_tracks.assert_any_call(mock_medium)
        mock_create_tracks.assert_any_call(mock_long)
        assert mock_create_tracks.call_count == 3

        mock_save_to_user.assert_called_once_with(fake_short_tracks, fake_medium_tracks, fake_long_tracks, cache=False)

        logger.info("Finished test_update_user_favorite_tracks_unit")