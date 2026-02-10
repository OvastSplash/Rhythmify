import logging
import pytest

logger = logging.getLogger("test")

@pytest.mark.django_db
def test_register_track(top_tracks_register, track):
    logger.info("[START] test_register_track")

    registered_track = top_tracks_register.register_top_track(track)
    assert registered_track.track == track

    logger.info("[END] test_register_track")

@pytest.mark.django_db
def test_register_tracks(top_tracks_register, tracks):
    logger.info("[START] test_register_tracks")

    registered_tracks = top_tracks_register.register_top_tracks(tracks)
    assert len(registered_tracks) == len(tracks)

    logger.info("[END] test_register_tracks")

@pytest.mark.django_db
def test_get_top_tracks(top_tracks_register, tracks):
    logger.info("[START] test_get_top_tracks")

    registered_tracks = top_tracks_register.register_top_tracks(tracks)
    assert len(top_tracks_register.get_top_tracks()) == len(tracks)

    logger.info("[END] test_get_top_tracks")

@pytest.mark.django_db
def test_clear_top_tracks(top_tracks_register, tracks):
    logger.info("[START] test_clear_top_tracks")

    registered_tracks = top_tracks_register.register_top_tracks(tracks)
    assert len(top_tracks_register.get_top_tracks()) == len(tracks)

    top_tracks_register.clear_top_tracks()
    assert len(top_tracks_register.get_top_tracks()) == 0

    logger.info("[END] test_clear_top_tracks")