from pytest import fixture

from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister
from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister

from unittest.mock import Mock

@fixture
def played_today_tracks_register(user):
    register = PlayedTodayTrackRegister(user=user)
    register.cache = Mock()
    return register

@fixture
def fresh_playlist_register():
    register = FreshPlaylistRegister()
    register.cache = Mock()
    return register