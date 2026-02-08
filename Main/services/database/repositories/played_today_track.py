import logging

from typing import List

from deezer.resources import track
from django.db import transaction

from Main.models import PlayedTodayTrack
from Main.services.database.repositories.base_repository_class import BaseRepository

from SpotifyController.models.models import Track
from User.models import CustomUser

logger = logging.getLogger(__name__)


class PlayedTodayTrackRegister(BaseRepository):
    """
    Repository class for handling operations related to tracks played today.

    This class is designed to track and manage user interactions with tracks that are played on a specific day.
    It facilitates checking whether a track is already played, updates play counts, and associates users with the
    played tracks while maintaining consistency.

    Attributes:
    user (CustomUser): The user who played the track.
    track (Track): The track played by the user.
    played_track (PlayedTodayTrack | None): The instance representing the played track if it exists.
    """

    def __init__(self, user: CustomUser | None = None) -> None:
        """
        Initializes an instance of the object.

        Attributes:
            user (CustomUser): The user associated with this instance.
            track (Track): The track associated with this instance.
            played_track (PlayedTodayTrack | None): Represents the track played
                today. Defaults to None.

        Args:
            user: The user associated with this instance.
            track: The track associated with this instance.
        """

        self.user = user
        self.track: Track | None = None
        self.played_track: PlayedTodayTrack | None = None
        super().__init__()

    @property
    def _is_track_today_played(self) -> bool:
        """
        Checks if the track has been played today.

        This property determines whether the specific track has been recorded
        in the played tracks for the current day by querying the database.

        Returns
        -------
        bool
            True if the track has been played today, False otherwise.
        """
        played_track = PlayedTodayTrack.objects.filter(track=self.track).first()
        self.played_track = played_track
        return played_track is not None

    def _update_played_today_track(self) -> None:
        """
        Updates the "played today" status of the current track for the user.

        This method updates the internal state of the played track to record that
        the track has been played by the current user. It increments the play count
        of the track and adds the user to the track's user set. The changes are
        persisted to the database, and a log entry is created.

        Raises
        ------
        ValueError
            If the `played_track` attribute is None.
        """

        if self.played_track:
            self.played_track.users.add(self.user)
            self.played_track.play_count += 1
            self.played_track.save()

            logger.info("Track added to today played: tid=%s uid=%s", self.track.spotify_id, self.user.id)

        else:
            raise ValueError("played_track is None")

    @transaction.atomic
    def _create_played_today_track(self) -> None:
        """
        Creates a new track marked as played today and triggers its update process.

        Tracks the creation of a track played today and logs relevant details.

        Raises:
            Ensures no exceptions are directly detailed but keeps the implementation robust.

        """

        self.played_track = PlayedTodayTrack.objects.create(track=self.track)
        self._update_played_today_track()

        self.cache.update_played_tracks(self.track.spotify_id)

        logger.info("Track created today played: tid=%s uid=%s", self.track.spotify_id, self.user.id)

    def register_track_play(self, track: Track) -> PlayedTodayTrack:
        """
        Registers the play of a track and logs its occurrence. If the specified track has already been played
        today, updates the respective record. Otherwise, creates a new record for the track played today.

        Parameters:
            track (Track): The track that has been played.

        Returns:
            None
        """

        if self.user is None:
            raise ValueError("User is not set")

        self.track = track
        logger.info("Registering track play: tid=%s uid=%s", self.track.spotify_id, self.user.id)

        if self._is_track_today_played:
            self._update_played_today_track()
            logger.info("Track already played today: tid=%s uid=%s", self.track.spotify_id, self.user.id)
        else:
            self._create_played_today_track()
            logger.info("Track played today: tid=%s uid=%s", self.track.spotify_id, self.user.id)

        self.track = None
        return self.played_track

    def register_tracks_play(self, tracks: list[Track]) -> List[PlayedTodayTrack]:
        """
        Registers plays for a list of tracks.

        This method iterates through the provided list of tracks and registers each
        individual track play using the `register_track_play` method.

        Args:
            tracks: A list containing instances of Track.

        Returns:
            None
        """

        logger.info("Registering tracks plays: tracks=%s", tracks)
        played_tracks = list()

        for track in tracks:
            self.register_track_play(track)
            played_tracks.append(self.played_track)

        return played_tracks

    def clear_played_tracks(self, clear_cache: bool = True) -> None:
        PlayedTodayTrack.objects.all().delete()
        self.cache.clear_played_tracks() if clear_cache else None
        logger.info("Cleared played tracks")

    @classmethod
    def get_replayed_tracks(cls, limit: int = 5, min_play: int = 3) -> list[PlayedTodayTrack]:
        return list(PlayedTodayTrack.objects.filter(play_count__gte=min_play).order_by('-play_count')[:limit])