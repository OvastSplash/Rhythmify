from pytest import fixture

from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister
from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister

from unittest.mock import Mock

from Main.services.database.repositories.top_artists import TopArtistsRegister
from Main.services.database.repositories.top_tracks import TopTrackRegister


@fixture
def played_today_tracks_register(user) -> PlayedTodayTrackRegister:
    register = PlayedTodayTrackRegister(user=user)
    register.cache = Mock()
    return register

@fixture
def fresh_playlist_register() -> FreshPlaylistRegister:
    register = FreshPlaylistRegister()
    register.cache = Mock()
    return register

@fixture
def top_tracks_register() -> TopTrackRegister:
    register = TopTrackRegister()
    register.cache = Mock()
    return register

@fixture
def top_artists_register() -> TopArtistsRegister:
    register = TopArtistsRegister()
    register.cache = Mock()
    return register