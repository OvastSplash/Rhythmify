import logging

import pytest

from SpotifyController.services.aggregator.update_user_listened_tracks import UpdateUserListenedTracks

logger = logging.getLogger("test")

def test_update_user_listened_tracks(update_user_listened_tracks: UpdateUserListenedTracks):
    logger.info("[START] test_update_user_listened_tracks")

    update_user_listened_tracks.run()

    update_user_listened_tracks.sp_client.get_user_recently_played.assert_called_once()
    update_user_listened_tracks.sp_db.create_played_at_tracks.assert_called_once()
    update_user_listened_tracks.user_db.save_listen_tracks_history.assert_called_once()

    logger.info("[END] test_update_user_listened_tracks")

def test_update_user_listened_tracks_spotify_error(update_user_listened_tracks: UpdateUserListenedTracks):
    logger.info("[START] test_update_user_listened_tracks_no_data")

    update_user_listened_tracks.sp_client.get_user_recently_played.side_effect = Exception("Spotify API down")

    with pytest.raises(Exception):
        update_user_listened_tracks.run()

    logger.info("[END] test_update_user_listened_tracks_no_data")