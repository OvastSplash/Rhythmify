import pytest
import logging
from django.db import IntegrityError

logger = logging.getLogger("tests")

# -----------------------------
# TopTracks
# -----------------------------

@pytest.mark.django_db
def test_top_tracks_str(track):
    from Main.models import TopTracks

    logger.info(f"Running test_top_tracks_str")
    top = TopTracks.objects.create(track=track, position=1)
    assert str(top) == track.name
    logger.debug(f"Successfully created and verified TopTracks")

    assert top.track.name == track.name
    logger.debug(f"Successfully verified TopTracks")

@pytest.mark.django_db
def test_top_tracks_unique(track):
    from Main.models import TopTracks

    logger.info(f"Running test_top_tracks_unique")
    TopTracks.objects.create(track=track, position=1)
    with pytest.raises(IntegrityError):
        TopTracks.objects.create(track=track, position=1)
    logger.debug(f"IntegrityError raised as expected for duplicate position")

# -----------------------------
# TopArtists
# -----------------------------
@pytest.mark.django_db
def test_top_artists_str(artist, tracks):
    from Main.models import TopArtists

    logger.info(f"Running test_top_artists_str")
    top = TopArtists.objects.create(artist=artist, position=1)
    assert str(top) == "Test Artist"
    logger.debug(f"Successfully created TopArtists")

    logger.info(f"Verifying TopArtists tracks {artist.top_tracks.all()}")
    assert top.artist.top_tracks.count() == len(tracks)

    logger.debug(f"Successfully verified TopArtists")


@pytest.mark.django_db
def test_top_artists_unique_constraint(artist):
    from Main.models import TopArtists

    logger.info(f"Running test_top_artists_unique_constraint")
    TopArtists.objects.create(artist=artist, position=1)
    with pytest.raises(IntegrityError):
        TopArtists.objects.create(artist=artist, position=1)

    logger.debug(f"IntegrityError raised as expected for duplicate position")

# -----------------------------
# TopAlbums
# -----------------------------
@pytest.mark.django_db
def test_top_albums_str(album):
    from Main.models import TopAlbums

    logger.info(f"Running test_top_albums_str")

    top = TopAlbums.objects.create(album=album, position=1)
    assert str(top) == "Test Album"
    logger.debug(f"Successfully created TopAlbums")

    logger.info(f"Verifying TopAlbums tracks --- {top.album.tracks.all()}")
    assert top.album.tracks.count() == len(top.album.tracks.all())

    logger.debug(f"Successfully verified TopAlbums")


@pytest.mark.django_db
def test_top_albums_unique_constraint(album):
    from Main.models import TopAlbums

    logger.info(f"Running test_top_albums_unique_constraint")
    TopAlbums.objects.create(album=album, position=1)
    with pytest.raises(IntegrityError):
        TopAlbums.objects.create(album=album, position=1)

    logger.debug(f"IntegrityError raised as expected for duplicate position")

# -----------------------------
# Recommendations
# -----------------------------
@pytest.mark.django_db
def test_recommendations_str(playlist, tracks):
    from Main.models import RecommendationPlaylist

    logger.info(f"Running test_recommendations_str")
    rec = RecommendationPlaylist.objects.create(playlist=playlist)
    assert str(rec) == "Test Playlist"
    logger.debug(f"Successfully created RecommendationPlaylist")

    logger.info(f"Verifying RecommendationPlaylist tracks {rec.playlist.tracks.all()}")
    assert rec.playlist.tracks.count() == len(tracks)
    logger.info(f"RecommendationPlaylist tracks --- {rec.playlist.tracks.all()}")

    logger.debug(f"Successfully verified RecommendationPlaylist")
