from django.utils import timezone

from pytest import fixture

from unittest.mock import Mock

from typing import List

from SpotifyController.services.construct_data import TrackClass, ArtistClass, GenreClass
from SpotifyController.services.database.data_builder import PlayedTrackDTO
from SpotifyController.services.database.save_user_data import SaveUserDataService
from User.models import CustomUser


@fixture
def sp_public() -> Mock:
    return Mock()

@fixture
def sp_client() -> Mock:
    return Mock()

@fixture
def sp_db() -> Mock:
    return Mock()

@fixture
def user_data(user) -> Mock:
    return Mock()

@fixture
def user_db(user) -> SaveUserDataService:
    return SaveUserDataService(user)

@fixture
def track_dto(track) -> PlayedTrackDTO:
    return PlayedTrackDTO(
        track=track,
        played_at=timezone.now(),
    )

@fixture
def genre_class() -> GenreClass:
    return GenreClass(name="Test Genre")

@fixture
def artist_class(genre_class) -> ArtistClass:
    return ArtistClass(
        name="Test Artist",
        spotify_id="Test_Artist_Id",
        spotify_url="https://Test_Artist_Url.com",
        genres=[genre_class],
    )


@fixture
def track_class(artist_class) -> TrackClass:
    return TrackClass(
        name="Test Track",
        url="https://Test_Url.com",
        spotify_id="Test_Id",
        artists=[artist_class],
    )

@fixture
def users(db) -> List[CustomUser]:
    users = list()

    for i in range(5):
        users.append(CustomUser.objects.create(
            username=f"user_{i}",
            user_login=f"user_login_{i}",
        ))

    return users