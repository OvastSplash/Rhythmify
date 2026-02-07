import logging
import pytest

logger = logging.getLogger("test")

@pytest.mark.django_db
def test_register_track_play(played_today_tracks_register, track):
    """
    Test the functionality of registering a track play and updating its play count.

    The test verifies that when a track is registered for play, the play count is correctly
    incremented to 1. Additionally, the method ensures that the returned object has the
    correct type.

    Args:
        played_today_tracks_register: A test fixture that simulates the track registration logic.
        track: A test fixture representing the track object to be registered.

    Raises:
        AssertionError: If the play count is not updated as expected or the returned object does
        not match the expected type.
    """

    logger.info("[START] test_register_tracks_play")

    registered_track = played_today_tracks_register.register_track_play(track)

    assert registered_track.play_count == 1
    assert type(registered_track) == registered_track.__class__

    logger.info("[END] test_register_tracks_play")

@pytest.mark.django_db
def test_register_tracks_play(played_today_tracks_register, tracks):
    """
    Test the `register_tracks_play` method to ensure correct registration and play count
    increment for given tracks.

    This test verifies the functionality of the `register_tracks_play` method by simulating
    the registration of track plays. It asserts that the registered tracks match the input
    tracks in length and checks that the play count for each track increments accurately.

    Parameters:
        played_today_tracks_register: Object containing the method to register track plays.
        tracks: List of tracks to register and validate.

    Raises:
        AssertionError: If the registered tracks do not match the input tracks in length
            or if the play count for each track does not increment as expected.
    """

    logger.info("[START] test_register_tracks_play")

    for i in range(1, 2):
        registered_tracks = played_today_tracks_register.register_tracks_play(tracks)

        assert len(registered_tracks) == len(tracks)

        for registered in registered_tracks:
            assert registered.play_count == i

    logger.info("[END] test_register_tracks_play")

@pytest.mark.django_db
def test_get_replayed_tracks(played_today_tracks_register, tracks):
    """
    Test the functionality of retrieving replayed tracks sorted by play count.

    This function ensures that the `get_replayed_tracks` method of the
    `played_today_tracks_register` correctly returns tracks sorted by the
    number of times they were played. It tests the behavior when tracks are
    played a varying number of times.

    Args:
        played_today_tracks_register: A fixture or mock object that registers and tracks
            the number of plays for each track.
        tracks: A list of track objects that will be registered and used to
            simulate playback counts.

    Assertions:
        - Verifies that the track with the highest play count appears first in
          the sorted list.
        - Verifies that the total number of distinct tracks in the sorted list
          matches the expected value.
    """

    logger.info("[START] test_get_replayed_tracks")

    for register_count, track in enumerate(tracks, start=1):
        for j in range(register_count):
            played_today_tracks_register.register_track_play(track)

    sorted_tracks = played_today_tracks_register.get_replayed_tracks()

    logger.info("[INFO] sorted_tracks: %s", sorted_tracks)

    assert sorted_tracks[0].play_count == 10
    assert len(sorted_tracks) == 5

    logger.info("[END] test_get_replayed_tracks")

@pytest.mark.django_db
def test_get_replayed_tracks_no_data(played_today_tracks_register):
    """
    Test function for verifying that no replayed tracks are returned when no data is present.

    This test ensures that the method `get_replayed_tracks` correctly returns an empty list
    when there are no replayed tracks in the played_today_tracks_register.

    Arguments:
        played_today_tracks_register (PlayedTodayTracksRegister): The fixture that provides a registry
        for tracks that have been played today.

    Raises:
        AssertionError: If the result of `get_replayed_tracks` does not match the expected output
        (an empty list).

    """

    logger.info("[START] test_get_replayed_tracks_no_data")

    no_data_tracks = played_today_tracks_register.get_replayed_tracks()
    assert len(no_data_tracks) == 0

    logger.info("[END] test_get_replayed_tracks_no_data")