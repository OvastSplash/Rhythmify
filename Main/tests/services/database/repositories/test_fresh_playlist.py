import logging

import pytest

logger = logging.getLogger("test")

@pytest.mark.django_db
def test_register_playlist(fresh_playlist_register, playlist):
    logger.info("[START] test_register_playlist")

    registered_playlist = fresh_playlist_register.register_playlist(playlist)

    assert registered_playlist.playlist_id == playlist.id
    assert len(fresh_playlist_register.get_fresh_playlists()) == 1

    logger.info("[END] test_register_playlist")

@pytest.mark.django_db
def test_register_playlists_duplicate(fresh_playlist_register, playlists_one_user):
    logger.info("[START] test_register_playlists_duplicate")

    registered_playlists = fresh_playlist_register.register_playlists(playlists_one_user)

    assert len(registered_playlists) == len(playlists_one_user)
    assert len(fresh_playlist_register.get_fresh_playlists()) == 1

    logger.info("[END] test_register_playlists_duplicate")

@pytest.mark.django_db
def test_register_playlists(fresh_playlist_register, playlists_multiple_users):
    logger.info("[START] test_register_playlists")

    registered_playlists = fresh_playlist_register.register_playlists(playlists_multiple_users)

    assert len(registered_playlists) == len(playlists_multiple_users)
    assert len(fresh_playlist_register.get_fresh_playlists()) == 5

    logger.info("[END] test_register_playlists")

@pytest.mark.django_db
def test_get_fresh_playlists_no_data(fresh_playlist_register):
    logger.info("[START] test_get_fresh_playlists_no_data")
    assert len(fresh_playlist_register.get_fresh_playlists()) == 0

    logger.info("[END] test_get_fresh_playlists_no_data")