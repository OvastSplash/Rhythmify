import logging

import pytest
from unittest.mock import patch

from LastFM.services.managers.update_top_tracks import GetTopTracksHandler

logger = logging.getLogger("test")

@pytest.mark.django_db
def test_update_top_tracks(update_top_tracks_manager: GetTopTracksHandler, tracks):
    logger.info("[START] test_update_top_tracks")

    top_tracks = update_top_tracks_manager.process_top_tracks()
    assert len(top_tracks) == 10

    logger.info("[END] test_update_top_tracks")


def test_update_top_tracks_error_last_fm(update_top_tracks_manager: GetTopTracksHandler):
    logger.info("[START] test_update_top_tracks_error_last_fm")

    with patch.object(update_top_tracks_manager, "_get_top_tracks", side_effect=Exception("LastFM API Error")):
        with pytest.raises(Exception) as exinfo:
            update_top_tracks_manager.process_top_tracks()

        assert "LastFM API Error" in str(exinfo.value)

    logger.info("[END] test_update_top_tracks_error_last_fm")


def test_update_top_tracks_error_spotify(update_top_tracks_manager: GetTopTracksHandler):
    logger.info("[START] test_update_top_tracks_error_spotify")

    with patch.object(update_top_tracks_manager, "_convert_to_spotify_data", side_effect=Exception("Spotify API Error")):
        with pytest.raises(Exception) as exinfo:
            update_top_tracks_manager.process_top_tracks()

        assert "Spotify API Error" in str(exinfo.value)

    logger.info("[END] test_update_top_tracks_error_spotify")