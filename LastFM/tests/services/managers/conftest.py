from LastFM.services.managers.update_top_artists import UpdateTopArtistsManager
from LastFM.services.managers.update_top_tracks import UpdateTopTracksManager

from pytest import fixture
from unittest.mock import MagicMock, patch

@fixture
def update_top_tracks_manager(tracks) -> UpdateTopTracksManager:
    manager = UpdateTopTracksManager()

    mock_data = [MagicMock() for _ in range(10)]
    patch.object(manager, "_get_top_tracks", return_value=mock_data).start()
    patch.object(manager, "_convert_to_spotify_data", return_value=tracks).start()

    return manager

@fixture
def update_top_artists_manager(artists) -> UpdateTopArtistsManager:
    manager = UpdateTopArtistsManager()

    mock_data = [MagicMock() for _ in range(10)]
    patch.object(manager, "_get_top_artists", return_value=mock_data).start()
    patch.object(manager, "_convert_to_spotify_data", return_value=artists).start()

    return manager