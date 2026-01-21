import logging

import pytest

from SpotifyController.services.aggregator.update_user_playlists import UpdateUserPlaylists

logger = logging.getLogger("test")

def test_update_user_playlists(update_user_playlists: UpdateUserPlaylists):
    """
    Tests the functionality and behavior of the `update_user_playlists` service.
    Verifies its correct invocation, including dependency interactions and logging
    integration.

    Args:
        update_user_playlists (UpdateUserPlaylists): The service instance to be
        tested, responsible for updating user playlists.

    """

    logger.info("[START] test_update_user_playlists")
    update_user_playlists.run()

    update_user_playlists.sp_client.get_user_playlists_data.assert_called_once()
    update_user_playlists.user_db.create_playlists.assert_called_once()

    logger.info("[END] test_update_user_playlists")

def test_update_user_playlists_spotify_error(update_user_playlists: UpdateUserPlaylists):
    """
    This function tests the behavior of the `UpdateUserPlaylists` functionality when the Spotify
    API encounters an error. Specifically, it simulates a scenario where the Spotify API is down
    and verifies that the appropriate exception is raised during the execution of the `run` method.

    Args:
        update_user_playlists (UpdateUserPlaylists): The instance of `UpdateUserPlaylists`
            whose `run` method is being tested under the faulty Spotify API condition.
    """

    logger.info("[START] test_update_user_playlists_spotify_error")
    update_user_playlists.sp_client.get_user_playlists_data.side_effect = Exception("Spotify API down")

    with pytest.raises(Exception):
        update_user_playlists.run()

    logger.info("[END] test_update_user_playlists_spotify_error")

