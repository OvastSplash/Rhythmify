from pytest import fixture

from typing import List

from SpotifyController.models.models import Track, Artist, Playlist, Album
from User.models import CustomUser

@fixture
def user(db):
    return CustomUser.objects.create(
        username="Test User",
        user_login="Test_Login",
    )

@fixture
def users(db) -> List[CustomUser]:
    return [
        CustomUser.objects.create(
            username=f"Test User {i}",
            user_login=f"Test_Login_{i}",
        ) for i in range(5)
    ]

@fixture
def track(db, artist) -> Track:
    track = Track.objects.create(
        name="Test Name",
        url="https://Test_Url.com",
        spotify_id="Test_Id",
    )

    track.artists.add(artist)
    track.save()
    return track

@fixture
def tracks(db) -> List[Track]:
    return [
        Track.objects.create(
            name=f"Test Track {i}",
            url=f"https://Test_Url_{i}.com",
            spotify_id=f"test_id_{i}"
        ) for i in range(10)
    ]


@fixture
def artist(db, tracks) -> Artist:
    artist =  Artist.objects.create(
        name="Test Artist",
        spotify_id="Test_Artist_Id",
        spotify_url="https://Test_Artist_Url.com",
    )

    artist.top_tracks.add(*tracks)
    return artist

@fixture
def artists(db) -> List[Artist]:
    return [
        Artist.objects.create(
            name=f"Test Artist {i}",
            spotify_url=f"https://Test_Url_{i}.com",
            spotify_id=f"test_id_{i}"
        ) for i in range(10)
    ]

@fixture
def playlist(db, tracks, user) -> Playlist:
    playlist = Playlist.objects.create(
        user=user,
        name="Test Playlist",
        spotify_id="Test_Playlist_Id",
        spotify_url="https://Test_Playlist_Url.com",
    )

    playlist.tracks.add(*tracks)
    return playlist

@fixture
def playlists_one_user(db, user, tracks) -> List[Playlist]:
    return [
        Playlist.objects.create(
            user=user,
            name=f"Test Playlist {i}",
            spotify_id=f"Test_Playlist_{i}",
            spotify_url=f"https://Test_Playlist_Url_{i}.com"
        ) for i in range(5)
    ]

@fixture
def playlists_multiple_users(db, tracks, users) -> List[Playlist]:
    playlists = list()
    for index, user in enumerate(users):
        playlists.extend(
            [
                Playlist.objects.create(
                    user=user,
                    name=f"Test Playlist {i} for {user.id}",
                    spotify_id=f"Test_Playlist_{user.id}_{i}",
                    spotify_url=f"https://Test_Playlist_Url_{user.id}_{i}.com"
                ) for i in range(5)
            ]
        )

    return playlists

@fixture
def album(db, tracks) -> Album:
    album = Album.objects.create(
        name="Test Album",
        spotify_id="Test_Album_Id",
        spotify_url="https://Test_Album_Url.com",
    )

    album.tracks.add(*tracks)
    return album
