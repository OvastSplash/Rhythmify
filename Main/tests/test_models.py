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
