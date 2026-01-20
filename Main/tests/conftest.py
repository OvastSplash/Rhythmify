from pytest import fixture

@fixture
def user(db):
    from User.models import CustomUser

    return CustomUser.objects.create(
        username="Test User",
        user_login="Test_Login",
    )

@fixture
def track(db):
    from SpotifyController.models.models import Track
    return Track.objects.create(
        name="Test Name",
        url="https://Test_Url.com",
        spotify_id="Test_Id"
    )

@fixture
def tracks(db):
    from SpotifyController.models.models import Track

    return [
        Track.objects.create(
            name=f"Test Track {i}",
            url=f"https://Test_Url_{i}.com",
            spotify_id=f"test_id_{i}"
        ) for i in range(5)
    ]


@fixture
def artist(db, tracks):
    from SpotifyController.models.models import Artist, Track
    artist =  Artist.objects.create(
        name="Test Artist",
        spotify_id="Test_Artist_Id",
        spotify_url="https://Test_Artist_Url.com",
    )

    artist.top_tracks.add(*tracks)
    return artist

@fixture
def playlist(db, tracks, user):
    from SpotifyController.models.models import Playlist, Track
    playlist = Playlist.objects.create(
        user=user,
        name="Test Playlist",
        spotify_id="Test_Playlist_Id",
        spotify_url="https://Test_Playlist_Url.com",
    )

    playlist.tracks.add(*tracks)
    return playlist

@fixture
def album(db, tracks):
    from SpotifyController.models.models import Album, Track
    album = Album.objects.create(
        name="Test Album",
        spotify_id="Test_Album_Id",
        spotify_url="https://Test_Album_Url.com",
    )

    album.tracks.add(*tracks)
    return album
