import logging
from unittest.mock import patch, Mock

import pytest

from SpotifyController.services.aggregator.update_user_recommendations import UpdateUserRecommendations

logger = logging.getLogger("test")

def test_update_user_recommendations(update_user_recommendations: UpdateUserRecommendations):
    """
    Tests the `update_user_recommendations` function of the `UpdateUserRecommendations` class.

    This function verifies the behavior and functionality of the `update_user_recommendations`
    process which involves collecting, verifying, and saving user music recommendations.

    Parameters:
    update_user_recommendations: UpdateUserRecommendations
        The instance of `UpdateUserRecommendations` to be tested.

    Raises:
    AssertionError: If assertions fail during the testing process, indicating discrepancies
    in the behavior of the `update_user_recommendations` method.
    """

    logger.info("[START] test_update_user_recommendations")

    mock_recommended = Mock()
    mock_existed = Mock()

    with patch(
            "SpotifyController.services.aggregator.update_user_recommendations.TrackSyncManager.collect_recommendations",
            return_value=([mock_recommended], [mock_existed])
    ) as mock_collect_recommendations:
        update_user_recommendations.run()
        mock_collect_recommendations.assert_called_once()

        assert update_user_recommendations.user_data.listen_history_tracks.call_count == 1
        assert update_user_recommendations.user_data.listen_history_artists.call_count == 1
        assert update_user_recommendations.user_data.listen_history_genres.call_count == 1

        expected_tracks = [mock_recommended] + [mock_existed]
        update_user_recommendations.user_db.save_user_recommendation_tracks.assert_called_once_with(expected_tracks)

        logger.info("[END] test_update_user_recommendations")

def test_update_user_recommendations_no_data(update_user_recommendations: UpdateUserRecommendations):
    """
    Test function for verifying the behavior of the update_user_recommendations method when
    no data is available.

    This test specifically ensures that the method handles scenarios where the data collection
    fails, and the appropriate exception is raised and logged.

    Arguments:
        update_user_recommendations: UpdateUserRecommendations
            The object responsible for running the recommendation update process.

    Raises:
        ValueError: Thrown when the data collection process encounters an issue, such as no
        available data to process.
    """

    logger.info("[START] test_update_user_recommendations_no_data")

    with patch(
            "SpotifyController.services.aggregator.update_user_recommendations.TrackSyncManager.collect_recommendations",
            side_effect=ValueError("No data")
    ) as mock_collect:

        with pytest.raises(ValueError):
            update_user_recommendations.run()

        mock_collect.assert_called_once()

        logger.info("[END] test_update_user_recommendations_no_data")