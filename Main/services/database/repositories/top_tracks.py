import logging

from django.db import transaction
from django.db.models import Max

from Main.models import TopTrack
from Main.services.database.repositories.base_repository_class import BaseRepository

from SpotifyController.models.models import Track

logger = logging.getLogger(__name__)

class TopTrackRegister(BaseRepository):
    """
    Handles registration and management of top tracks.

    The class is designed to interact with the TopTrack model to perform various operations
    such as registering a track, checking if a track is already registered, clearing all
    entries, or retrieving a list of registered top tracks.

    Attributes:
        track (Track | None): The current track being processed.
        registered_track (TopTrack | None): The currently registered top track associated with
        the processed track, if any.
    """

    def __init__(self) -> None:
        self.track: Track | None = None
        self.registered_track: TopTrack | None = None
        super().__init__()

    @transaction.atomic
    def _create_top_track(self) -> TopTrack:
        """
        Creates and returns a top track instance.

        This method is responsible for creating a TopTrack instance
        associated with the specified track. It logs information
        about the created track using its Spotify ID.

        Raises:
            DoesNotExist: If the required database entries do not exist.

        Returns:
            TopTrack: The created instance of the top track.
        """
        created_track = TopTrack.objects.create(track=self.track, position=self._get_last_position + 1)
        logger.info("Created top track: tid=%s", self.track.spotify_id)
        self.cache.update_top_tracks(self.track.spotify_id)

        return created_track

    @property
    def _is_track_registered(self) -> bool:
        """
        Checks if the current track is registered in the TopTrack model.

        Attributes:
            registered_track: Stores the first instance of the TopTrack object associated
                with the current track, or None if no such instance exists.

        Returns:
            bool: A boolean indicating whether the current track is registered in
            the TopTrack model.
        """

        registered_track = TopTrack.objects.filter(track=self.track).first()
        self.registered_track = registered_track
        return registered_track is not None

    def register_top_track(self, track: Track) -> TopTrack:
        """
        Registers a top track if it is not already registered.

        This method checks if the given track is already registered as
        a top track. If the track is already registered, it logs a warning
        message and returns the existing registered track. If the track
        is not registered, it creates and registers the track as a top track.

        Parameters:
            track (Track): The track object to be registered.

        Returns:
            TopTrack: The registered top track object.
        """

        self.track = track

        if self._is_track_registered:
            logger.warning(f"Track {track.name} is already registered")
            return self.registered_track

        return self._create_top_track()

    def register_top_tracks(self, tracks: list[Track]) -> list[TopTrack]:
        registered_top_tracks = list()

        for track in tracks:
            registered_top_tracks.append(self.register_top_track(track))

        return registered_top_tracks

    def clear_top_tracks(self, clear_cache: bool = True) -> None:
        """
        Clears all entries in the TopTrack database table.

        Deletes all objects of the TopTrack model, effectively removing
        all records of tracks from the database.

        Raises:
            None
        Returns:
            None
        """
        TopTrack.objects.all().delete()
        self.cache.clear_top_tracks() if clear_cache else None

        logger.info("Cleared top tracks")

    @classmethod
    def get_top_tracks(cls) -> list[TopTrack]:
        """
        Provides a class method to retrieve and return a list of top tracks from the database.

        Returns:
            list[TopTrack]: A list containing TopTrack objects retrieved from the database.
        """
        return list(TopTrack.objects.all().order_by('-position'))

    @property
    def _get_last_position(self) -> int:
        """
        Retrieves the last position value from the TopTrack objects.

        This property method calculates the maximum value for the 'position' field
        in the TopTrack objects using aggregation. If no value is found, it defaults
        to returning 0.

        Returns:
            int: The maximum position value from TopTrack objects or 0 if no entries
            exist.
        """

        return TopTrack.objects.aggregate(
            max_pos=Max('position')
        )["max_pos"] or 0