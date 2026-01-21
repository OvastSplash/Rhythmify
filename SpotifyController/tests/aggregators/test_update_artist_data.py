import logging
import pytest

from SpotifyController.services.aggregator.update_artist_data import UpdateArtistData

from unittest.mock import Mock

logger = logging.getLogger("test")


def test_update_artist_data(update_artist_service: UpdateArtistData, sp_public: Mock, sp_db: Mock):
    logger.info("[START] test_update_artist_data")

    artist_sid = "3bFkcQbsuV6ROeAkewAHmy"
    artist_data = {
        "id": "test_id",
        "name": "test_name",
    }

    sp_public.get_artist_info.return_value = artist_data
    update_artist_service.update_artist(artist_sid)

    sp_public.get_artist_info.assert_called_once_with(artist_sid)
    sp_db.create_or_update_artist.assert_called_once_with(artist_data)

    logger.info("[END] Finished test_update_artist_data")

def test_update_artist_data_spotify_error(update_artist_service: UpdateArtistData, sp_public: Mock, sp_db: Mock):
    logger.info("[START] test_update_artist_data_spotify_error")

    sp_public.get_artist_info.side_effect = Exception("Spotify API down")

    with pytest.raises(Exception):
        update_artist_service.update_artist("test_sid")

    sp_public.get_artist_info.assert_called_once_with("test_sid")
    sp_db.create_or_update_artist.assert_not_called()

    logger.info("[END] Finished test_update_artist_data_spotify_error")

def test_update_artist_data_db_error(update_artist_service: UpdateArtistData, sp_public: Mock, sp_db: Mock):
    logger.info("[START] test_update_artist_data_db_error")

    artist_data = {
        "id": "test_id",
        "name": "test_name",
    }

    sp_public.get_artist_info.return_value = artist_data
    sp_db.create_or_update_artist.side_effect = Exception("Database error")

    with pytest.raises(Exception):
        update_artist_service.update_artist("test_sid")

    sp_public.get_artist_info.assert_called_once_with("test_sid")
    sp_db.create_or_update_artist.assert_called_once_with({"id": "test_id", "name": "test_name"})

    logger.info("[END] Finished test_update_artist_data_db_error")

def test_update_artist_data_no_data(update_artist_service: UpdateArtistData, sp_public: Mock, sp_db: Mock):
    logger.info("[START] test_update_artist_data_no_data")

    sp_public.get_artist_info.side_effect = Exception("Artist not found")

    with pytest.raises(Exception):
        update_artist_service.update_artist("test_sid")

    sp_public.get_artist_info.assert_called_once_with("test_sid")
    sp_db.create_or_update_artist.assert_not_called()

    logger.info("[END] Finished test_update_artist_data_no_data")