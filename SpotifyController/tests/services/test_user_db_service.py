import pytest
import logging

from SpotifyController.tests.conftest import track_dto

logger = logging.getLogger("test")

# -----------------------------
# Favorite tracks
# -----------------------------

@pytest.mark.django_db
def test_update_user_favorite_tracks(user, tracks, user_db):
    logger.info("[START] test_update_user_favorite_tracks")

    user_db.save_favorite_user_tracks_short_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_medium_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_long_term(tracks, cache=False)

    assert user.top_tracks.count() == len(tracks)

    logger.info("[END] Finished test_update_user_favorite_tracks")

@pytest.mark.django_db
def test_update_user_favorite_tracks_update(user, tracks, user_db):
    logger.info("[START] test_update_user_favorite_tracks_update")

    user_db.save_favorite_user_tracks_short_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_medium_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_long_term(tracks, cache=False)

    assert user.top_tracks.count() == len(tracks)
    logger.info("[PROCESSING] User favorite tracks added successfully")

    user_db.save_favorite_user_tracks_short_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_medium_term(tracks, cache=False)
    user_db.save_favorite_user_tracks_long_term(tracks, cache=False)

    assert user.top_tracks.count() == len(tracks)
    logger.info("[PROCESSING] User favorite tracks count=%s", user.top_tracks.count())
    logger.info("[END] test_update_user_favorite_tracks_update")

@pytest.mark.django_db
def test_update_user_favorite_tracks_none(user, user_db):
    logger.info("[START] test_update_user_favorite_tracks_none")

    tracks = None

    with pytest.raises(ValueError):
        user_db.save_favorite_user_tracks_short_term(tracks, cache=False)
        user_db.save_favorite_user_tracks_medium_term(tracks, cache=False)
        user_db.save_favorite_user_tracks_long_term(tracks, cache=False)

    logger.info("[END] Finished test_update_user_favorite_tracks_none")

# -----------------------------
# Recommendation Tracks
# -----------------------------

@pytest.mark.django_db
def test_update_user_recommendation_tracks(user, tracks, user_db):
    logger.info("[START] test_update_user_recommendation_tracks")

    user_db.save_user_recommendation_tracks(tracks, cache=False)
    assert user.recommendation_tracks.count() == len(tracks)

    logger.info("[END] test_update_user_recommendation_tracks")

@pytest.mark.django_db
def test_update_user_recommendation_existing_track(user, user_db, tracks):
    logger.info("[START] test_update_user_recommendation_existing_track")

    user_db.save_user_recommendation_tracks(tracks, cache=False)
    assert user.recommendation_tracks.count() == len(tracks)

    logger.info("[PROCESSING] Adding existing track to recommendations")

    user_db.save_user_recommendation_tracks(tracks, cache=False)
    assert user.recommendation_tracks.count() == len(tracks)

    logger.info("[END]test_update_user_recommendation_existing_track")

@pytest.mark.django_db
def test_update_user_recommendation_none(user, user_db):
    logger.info("[START] test_update_user_recommendation_none")

    tracks = None

    with pytest.raises(ValueError):
        user_db.save_user_recommendation_tracks(tracks, cache=False)

    logger.info("[END] test_update_user_recommendation_none")


# -----------------------------
# Listen History
# -----------------------------

@pytest.mark.django_db
def test_update_user_listen_history(user, track_dto, user_db):
    logger.info("[START] test_update_user_listen_history")

    user_db.save_listen_tracks_history([track_dto], cache=False)

    assert user.listen_track_history.count() == 1
    logger.info("[END] test_update_user_listen_history")

@pytest.mark.django_db
def test_update_user_listen_history_none(user, user_db):
    logger.info("[START] test_update_user_listen_history_none")

    played_track_dto = None

    user_db.save_listen_tracks_history([played_track_dto], cache=False)
    assert user.listen_track_history.count() == 0

    logger.info("[END] Finished test_update_user_listen_history_none")

@pytest.mark.django_db
def test_update_user_listen_history_dto_none(user, user_db, track_dto):
    logger.info("[START] test_update_user_listen_history_dto_none")

    track_dto.track = None
    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 0

    track_dto.played_at = None
    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 0

    logger.info("[END] test_update_user_listen_history_dto_none")

@pytest.mark.django_db
def test_update_user_listen_history_existing(user, track_dto, user_db):
    logger.info("[START] test_update_user_listen_history_existing")

    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 1

    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 1

    logger.info("[END] test_update_user_listen_history_existing")

@pytest.mark.django_db
def test_update_user_listen_history_different_time(user, track_dto, user_db):
    logger.info("[START] test_update_user_listen_history_different_time")

    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 1

    track_dto.played_at = "2023-01-01T00:00:00Z"
    user_db.save_listen_tracks_history([track_dto], cache=False)
    assert user.listen_track_history.count() == 2

    logger.info("[END] test_update_user_listen_history_different_time")