from unittest.mock import Mock

import logging
import pytest

logger = logging.getLogger("test")

def test_top_tracks(last_fm_client):
    logger.info("[START] test_top_tracks")

    top_tracks = last_fm_client.get_top_tracks()

    assert len(top_tracks) == 10
    logger.info(f"[INFO] Top Tracks: {top_tracks}")

    logger.info("[END] test_top_tracks")

def test_top_tracks_none():
    logger.info("[START] test_top_tracks_none")

    last_fm_client = Mock()
    last_fm_client.get_top_tracks.side_effect = Exception("Test Exception")

    with pytest.raises(Exception):
        last_fm_client.get_top_tracks()

    logger.info("[END] test_top_tracks_none")

def test_top_artists(last_fm_client):
    logger.info("[START] test_top_artists")

    top_artists = last_fm_client.get_top_artists()
    assert len(top_artists) == 10
    logger.info(top_artists)

    logger.info("[END] test_top_artists")

def test_top_artists_none():
    logger.info("[START] test_top_artists_none")

    last_fm_client = Mock()
    last_fm_client.get_top_artists.side_effect = Exception("Test Exception")

    with pytest.raises(Exception):
        last_fm_client.get_top_artists()

    logger.info("[END] test_top_artists_none")