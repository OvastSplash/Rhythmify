import logging
import pytest

logger = logging.getLogger("test")

@pytest.mark.django_db
def test_register_artist(top_artists_register, artist):
    logger.info("[START] test_register_artist")

    registered_artist = top_artists_register.register_top_artist(artist)
    assert registered_artist.artist == artist

    logger.info("[END] test_register_artist")

@pytest.mark.django_db
def test_register_artists(top_artists_register, artists):
    logger.info("[START] test_register_artists")

    registered_artists = top_artists_register.register_top_artists(artists)
    assert len(registered_artists) == len(artists)

    logger.info("[END] test_register_artists")

@pytest.mark.django_db
def test_get_top_artists(top_artists_register, artists):
    logger.info("[START] test_get_top_artists")

    registered_artists = top_artists_register.register_top_artists(artists)
    assert len(top_artists_register.get_top_artists()) == len(artists)

    logger.info("[END] test_get_top_artists")

@pytest.mark.django_db
def test_clear_top_artists(top_artists_register, artists):
    logger.info("[START] test_clear_top_artists")

    registered_artists = top_artists_register.register_top_artists(artists)
    assert len(registered_artists) == len(artists)
    top_artists_register.clear_top_artists()
    assert len(top_artists_register.get_top_artists()) == 0