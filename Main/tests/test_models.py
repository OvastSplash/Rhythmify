import pytest
import logging
from django.db import IntegrityError

logger = logging.getLogger("test")

# -----------------------------
# TopTracks
# -----------------------------

@pytest.mark.django_db
def test_top_tracks_str(track):
    from Main.models import TopTrack

    logger.info(f"[START] test_top_tracks_str")
    top = TopTrack.objects.create(track=track, position=1)
    assert str(top) == track.name
    logger.info(f"[PROCESSING] created and verified TopTracks")

    assert top.track.name == track.name
    logger.info(f"[END] verified TopTracks")

@pytest.mark.django_db
def test_top_tracks_unique(track):
    from Main.models import TopTrack

    logger.info(f"[START] test_top_tracks_unique")
    TopTrack.objects.create(track=track, position=1)
    with pytest.raises(IntegrityError):
        TopTrack.objects.create(track=track, position=1)
    logger.info(f"[END] test_top_tracks_unique")

# -----------------------------
# TopArtists
# -----------------------------
@pytest.mark.django_db
def test_top_artists_str(artist, tracks):
    from Main.models import TopArtist

    logger.info(f"[START] test_top_artists_str")
    top = TopArtist.objects.create(artist=artist, position=1)
    assert str(top) == "Test Artist"
    logger.info(f"[PROCESSING] created TopArtists")

    logger.info(f"[PROCESSING] Verifying TopArtists tracks {artist.top_tracks.all()}")
    assert top.artist.top_tracks.count() == len(tracks)

    logger.info(f"[END] test_top_artists_str")


@pytest.mark.django_db
def test_top_artists_unique_constraint(artist):
    from Main.models import TopArtist

    logger.info(f"[START] test_top_artists_unique_constraint")
    TopArtist.objects.create(artist=artist, position=1)
    with pytest.raises(IntegrityError):
        TopArtist.objects.create(artist=artist, position=1)

    logger.info(f"[END] test_top_artists_unique_constraint")

# -----------------------------
# TopAlbums
# -----------------------------
@pytest.mark.django_db
def test_top_albums_str(album):
    from Main.models import TopAlbum

    logger.info(f"[START] test_top_albums_str")

    top = TopAlbum.objects.create(album=album, position=1)
    assert str(top) == "Test Album"
    logger.info(f"[PROCESSING] Successfully created TopAlbums")

    logger.info(f"[PROCESSING] Verifying TopAlbums tracks --- {top.album.tracks.all()}")
    assert top.album.tracks.count() == len(top.album.tracks.all())

    logger.info(f"[END] test_top_albums_str")


@pytest.mark.django_db
def test_top_albums_unique_constraint(album):
    from Main.models import TopAlbum

    logger.info(f"[START] test_top_albums_unique_constraint")
    TopAlbum.objects.create(album=album, position=1)
    with pytest.raises(IntegrityError):
        TopAlbum.objects.create(album=album, position=1)

    logger.info(f"[END] test_top_albums_unique_constraint")

# -----------------------------
# Recommendations
# -----------------------------
@pytest.mark.django_db
def test_recommendations_str(playlist, tracks):
    from Main.models import RecommendationPlaylist

    logger.info(f"[START] test_recommendations_str")
    rec = RecommendationPlaylist.objects.create(playlist=playlist)
    assert str(rec) == "Test Playlist"
    logger.info(f"[PROCESSING] Successfully created RecommendationPlaylist")

    logger.info(f"[PROCESSING] Verifying RecommendationPlaylist tracks {rec.playlist.tracks.all()}")
    assert rec.playlist.tracks.count() == len(tracks)
    logger.info(f"[PROCESSING] RecommendationPlaylist tracks --- {rec.playlist.tracks.all()}")

    logger.info(f"[END] test_recommendations_str")
