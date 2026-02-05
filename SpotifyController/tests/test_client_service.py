from unittest.mock import Mock
import logging

logger = logging.getLogger("test")

# ///////////////////
# Test Public Client
# ///////////////////


def test_get_artist_info(sp_public: Mock):
    logger.info("[START] test_get_artist_info")

    artist_data = {
        "id": "test_id",
        "name": "test_name",
        "spotify_uri": "test_uri"
    }

    sp_public.get_artist_info.return_value = artist_data
    sp_public.get_artist_info("test_uri", constructed=False)
    sp_public.get_artist_info.assert_called_once_with("test_uri", constructed=False)

    logger.info("[END] test_get_artist_info")

def test_get_artist_info_constructed(sp_public: Mock):
    logger.info("[START] test_get_artist_info_constructed")

    artist_data = {
        "id": "test_id",
        "name": "test_name",
        "spotify_uri": "test_uri"
    }

    sp_public.get_artist_info.return_value = artist_data
    sp_public.get_artist_info("test_uri", constructed=True)

    sp_public.get_artist_info.assert_called_once_with("test_uri", constructed=True)

    logger.info("[END] test_get_artist_info")