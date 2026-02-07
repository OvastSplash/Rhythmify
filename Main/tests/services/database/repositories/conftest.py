from pytest import fixture

from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister
from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister


@fixture
def played_today_tracks_register(user):
    return PlayedTodayTrackRegister(user=user)

@fixture
def fresh_playlist_register():
    return FreshPlaylistRegister()