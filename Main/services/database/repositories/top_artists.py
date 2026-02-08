import logging

from django.db import transaction
from django.db.models import Max

from Main.models import TopArtist
from Main.services.database.repositories.base_repository_class import BaseRepository
from SpotifyController.models.models import Artist

logger = logging.getLogger(__name__)


class TopArtistsRegister(BaseRepository):
    """
    Handles the registration and management of top artists in the application.

    This class provides methods for managing top artists, including registering new top
    artists (individually or in bulk), clearing top artist records, and retrieving top
    artists. It interacts with the `TopArtist` and `Artist` models to perform various
    operations, ensuring data consistency and cache updates where applicable.
    """

    def __init__(self):
        self.artist: Artist | None = None
        self.registered_artist: TopArtist | None = None
        super().__init__()

    @property
    def _is_artist_registered(self) -> bool:
        """
        Indicates whether the artist is registered as a top artist.

        This property checks if the artist is present in the TopArtist collection.
        It retrieves and assigns the matching artist object to the registered_artist
        attribute, and returns a boolean indicating the presence of the artist.

        Returns:
            bool: True if the artist is registered in TopArtist, False otherwise.
        """
        registered_artist = TopArtist.objects.filter(artist=self.artist).first()
        self.registered_artist = registered_artist
        return registered_artist is not None

    @transaction.atomic
    def _create_top_artist(self) -> TopArtist:
        """
        Creates a new TopArtist record for the current artist and updates the cache.

        Returns:
            TopArtist: The newly created TopArtist instance.
        """
        top_track = TopArtist.objects.create(artist=self.artist, position=self._get_last_position + 1)
        self.cache.update_top_artists(self.artist.spotify_id)
        return top_track

    def register_top_artist(self, artist: Artist) -> TopArtist:
        """
        Registers the given artist as a top artist.

        The method assigns the provided `Artist` object to the instance, checks if
        the artist is already registered, and logs a warning in such cases. If the
        artist is not registered, it proceeds to create a new top artist instance.

        Parameters:
            artist (Artist): The artist to be registered.

        Returns:
            TopArtist: The newly created or already registered top artist instance.
        """
        self.artist = artist

        if self._is_artist_registered:
            logger.warning(f"Artist {artist.name} is already registered")
            return self.registered_artist

        return self._create_top_artist()

    def register_top_artists(self, artists: list[Artist]) -> list[TopArtist]:
        """
        Registers a list of top artists by processing each artist through the individual
        registration method and returns a list of registered top artists.

        Parameters:
        artists: list[Artist]
            A list of Artist objects to be registered as top artists.

        Returns:
        list[TopArtist]
            A list of TopArtist objects that have been successfully registered.
        """
        registered_top_artists = list()

        for artist in artists:
            registered_top_artists.append(self.register_top_artist(artist))
        return registered_top_artists

    def clear_top_artists(self, clear_cache: bool = True) -> None:
        """
        Deletes all top artist records from the database and optionally clears
        the related cache.

        Args:
            clear_cache: A boolean indicating whether to clear the cache after
            deleting the top artist records. Defaults to True.

        Returns:
            None
        """
        TopArtist.objects.all().delete()
        self.cache.clear_top_artists() if clear_cache else None
        logger.info("Cleared top artists")

    @classmethod
    def get_top_artists(cls) -> list[TopArtist]:
        """
        Fetches and returns a list of top artist objects ordered by their position.

        Returns:
            list[TopArtist]: A list of TopArtist objects ordered by the "position" attribute in
            descending order.
        """
        return list(TopArtist.objects.all().order_by("-position"))

    @property
    def _get_last_position(self) -> int:
        """
        Retrieves the maximum position value from the TopArtist objects.

        Returns
        -------
        int
            The highest position value among all TopArtist objects. If no
            positions exist, returns 0.
        """
        return TopArtist.objects.aggregate(max_position=Max("position"))["max_position"] or 0