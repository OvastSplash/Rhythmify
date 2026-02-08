import logging

from django.db import transaction

from Main.models import FreshPlaylist
from Main.services.database.repositories.base_repository_class import BaseRepository

from SpotifyController.models.models import Playlist

logger = logging.getLogger(__name__)


class FreshPlaylistRegister(BaseRepository):
    """
    Manages the registration and retrieval of fresh playlists.

    The FreshPlaylistRegister class facilitates creating, checking, and retrieving
    fresh playlists. It also provides functionality to clear all fresh playlists
    from storage.

    Attributes:
        playlist (Playlist | None): Represents the current playlist being handled.
        fresh_playlist (FreshPlaylist | None): Represents the fresh playlist
            associated with the current playlist.
    """

    def __init__(self):
        self.playlist: Playlist | None = None
        self.fresh_playlist: FreshPlaylist | None = None
        super().__init__()

    @property
    def _is_playlist_registered(self) -> bool:
        """
        Checks if the playlist is registered.

        This property checks whether the given playlist is registered in the
        FreshPlaylist database. It assigns the retrieved FreshPlaylist object
        to the 'fresh_playlist' attribute and returns a boolean indicating
        the registration status.

        Returns:
            bool: True if the playlist is registered, False otherwise.
        """

        fresh_playlist = FreshPlaylist.objects.filter(playlist=self.playlist).first()
        self.fresh_playlist = fresh_playlist
        return fresh_playlist is not None

    @transaction.atomic
    def _create_fresh_playlist(self) -> FreshPlaylist:
        """
        Creates a fresh playlist based on an existing playlist. This function utilizes
        the `FreshPlaylist` model to generate a new fresh playlist associated with the
        current `playlist`. Logs an informational message upon successful creation. If
        no valid `playlist` is associated, an exception will be raised.

        Raises:
            Exception: If no playlist is found or associated.

        Returns:
            FreshPlaylist: The newly created fresh playlist.
        """

        if self.playlist:
            self.fresh_playlist = FreshPlaylist.objects.create(playlist=self.playlist)
            logger.info(f"Fresh playlist {self.fresh_playlist.playlist.name} created")
            self.cache.update_fresh_playlists(self.playlist.spotify_id)

            return self.fresh_playlist

        raise Exception("Playlist not found")

    def register_playlist(self, playlist: Playlist) -> FreshPlaylist:
        """
        Registers a playlist into the system.

        This method determines whether a given playlist has already been registered. If the playlist is already
        registered, it logs a warning message and returns the existing fresh playlist. Otherwise, it creates
        and returns a new fresh playlist.

        Args:
            playlist: The playlist instance to be registered.

        Returns:
            A fresh playlist instance created from the provided playlist.
        """
        self.playlist = playlist

        if self._is_playlist_registered:
            logger.warning(f"Playlist {playlist.name} is already registered")
            return self.fresh_playlist

        return self._create_fresh_playlist()

    def register_playlists(self, playlists: list[Playlist]) -> list[FreshPlaylist]:
        """
        Registers a list of playlists and returns a list of freshly registered playlists.

        This method iterates over the provided playlists, registers each playlist using
        an internal `register_playlist` method, and accumulates the results into a new
        list of fresh playlists, which is then returned.

        Parameters:
            playlists: list[Playlist]
                A list of Playlist objects to be registered.

        Returns:
            list[FreshPlaylist]: A list of freshly registered playlists.
        """

        fresh_playlists = list()

        for playlist in playlists:
            fresh_playlists.append(self.register_playlist(playlist))

        return fresh_playlists

    def clear_fresh_playlists(self, clear_cache: bool = True) -> None:
        """
        Clears all fresh playlists from the database and optionally clears the related cache.

        This method deletes all records of fresh playlists stored in the database and
        logs the operation. Additionally, it provides the option to clear the associated
        cache, which may be used to optimize performance for fresh playlist queries.

        Parameters:
            clear_cache (bool): Indicates whether to clear the cache for fresh playlists.
                Defaults to True.

        Returns:
            None
        """

        FreshPlaylist.objects.all().delete()
        self.cache.clear_fresh_playlists() if clear_cache else None
        logger.info("Cleared fresh playlists")

    @classmethod
    def get_fresh_playlists(cls, limit: int = 5) -> list[FreshPlaylist]:
        """
        Returns a list of fresh playlists, each associated with unique users, sorted
        by their order of appearance.

        The method retrieves all available playlists, filters out those created by
        users already considered in the result, and returns up to a specified number
        of unique fresh playlists. If no playlists exist, an empty list is returned.

        Parameters:
            limit (int): The maximum number of unique fresh playlists to return.
                Defaults to 5.

        Returns:
            list[FreshPlaylist]: A list containing unique fresh playlists, up to the
                specified limit.
        """

        playlists = list(FreshPlaylist.objects.all())

        if not playlists:
            return []

        seen_users = set()
        sorted_playlists = list()

        for fresh_playlist in playlists:
            if fresh_playlist.playlist.user.id not in seen_users:
                seen_users.add(fresh_playlist.playlist.user.id)
                sorted_playlists.append(fresh_playlist)

            if len(sorted_playlists) > limit:
                break

        return sorted_playlists