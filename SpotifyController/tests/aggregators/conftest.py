from pytest import fixture

from SpotifyController.services.aggregator.aggregator_base import BaseUserAggregator, BaseAggregator
from SpotifyController.services.aggregator.update_artist_data import UpdateArtistData
from SpotifyController.services.aggregator.update_user_favorite_tracks import UpdateUserFavoriteTracks
from SpotifyController.services.aggregator.update_user_listened_tracks import UpdateUserListenedTracks
from SpotifyController.services.aggregator.update_user_playlists import UpdateUserPlaylists
from SpotifyController.services.aggregator.update_user_recommendations import UpdateUserRecommendations


from unittest.mock import Mock, MagicMock


@fixture
def base_aggregator(sp_db, sp_public) -> BaseAggregator:
    return BaseAggregator(sp_db=sp_db, sp_public=sp_public)

@fixture
def base_user_aggregator(sp_public, sp_db, users) -> BaseUserAggregator:
    aggregator = BaseUserAggregator(users)
    aggregator.sp_db = sp_db
    aggregator.sp_public = sp_public
    return aggregator

@fixture
def update_user_favorite_tracks(base_user_aggregator, user) -> UpdateUserFavoriteTracks:
    return UpdateUserFavoriteTracks(user=user, parent=base_user_aggregator)

@fixture
def update_user_listened_tracks(base_user_aggregator, user, sp_client) -> UpdateUserListenedTracks:
    aggregator = UpdateUserListenedTracks(user=user, parent=base_user_aggregator)
    aggregator.user_db = MagicMock()
    aggregator.sp_client = sp_client
    return aggregator

@fixture
def update_user_playlists(base_user_aggregator, user, sp_client) -> UpdateUserPlaylists:
    aggregator = UpdateUserPlaylists(user=user, parent=base_user_aggregator)
    aggregator.user_db = Mock()
    aggregator.sp_client = sp_client
    return aggregator

@fixture
def update_user_recommendations(base_user_aggregator, user, sp_client, user_data) -> UpdateUserRecommendations:
    aggregator = UpdateUserRecommendations(user=user, parent=base_user_aggregator)
    aggregator.user_db = Mock()
    aggregator.user_data = user_data
    return aggregator

@fixture
def update_artist_service(sp_public, sp_db) -> UpdateArtistData:
    return UpdateArtistData(
        sp_public=sp_public,
        sp_db=sp_db,
    )