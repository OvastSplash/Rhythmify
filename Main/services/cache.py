import logging

from typing import List
from django.core.cache import cache

logger = logging.getLogger(__name__)

class MainCache:
    TOP_TRACKS_KEY = "top_tracks"
    TOP_ARTISTS_KEY = "top_artists"
    RECENTLY_REPLAYED_TRACKS_KEY = "recently_replayed_tracks"
    FRESH_PLAYLISTS_KEY = "fresh_playlists"

    def _set_key_cache(self, key: str, value: List[str]) -> None:
        cache.set(key, value)
        logger.info("[Main Cache] %s updated", key)

    def _get_key_cache(self, key: str) -> List[str] | None:
        value = cache.get(key)
        if value is not None:
            logger.info("[Main Cache] %s retrieved from cache", key)
            return value
        logger.info("[Main Cache] %s not found in cache", key)
        return None

    def _update_key_cache(self, key: str, value: str) -> None:
        value_list = self._get_key_cache(key) or list()
        value_list.append(value)
        self._set_key_cache(key, value_list)

    def _clear_key_cache(self, key: str) -> None:
        cache.delete(key)
        logger.info("[Main Cache] %s cleared", key)

    """ TOP TRACKS """


    def set_top_tracks(self, top_tracks_ids: List[str]) -> None:
        self._set_key_cache(self.TOP_TRACKS_KEY, top_tracks_ids)

    def get_top_tracks(self) -> List[str] | None:
        self._get_key_cache(self.TOP_TRACKS_KEY)

    def update_top_tracks(self, top_track_id: str) -> None:
        self._update_key_cache(self.TOP_TRACKS_KEY, top_track_id)

    def clear_top_tracks(self) -> None:
        self._clear_key_cache(self.TOP_TRACKS_KEY)


    """ TOP ARTISTS """


    def set_top_artists(self, top_artists_ids: List[str]) -> None:
        self._set_key_cache(self.TOP_ARTISTS_KEY, top_artists_ids)

    def get_top_artists(self) -> List[str] | None:
        self._get_key_cache(self.TOP_ARTISTS_KEY)

    def update_top_artists(self, top_artist_id: str) -> None:
        self._update_key_cache(self.TOP_ARTISTS_KEY, top_artist_id)

    def clear_top_artists(self) -> None:
        self._clear_key_cache(self.TOP_ARTISTS_KEY)


    """ RECENTLY REPLAYED TRACKS """


    def set_recently_replayed_tracks(self, tracks_ids: List[str]) -> None:
        self._set_key_cache(self.RECENTLY_REPLAYED_TRACKS_KEY, tracks_ids)

    def get_recently_replayed_tracks(self) -> List[str] | None:
        self._get_key_cache(self.RECENTLY_REPLAYED_TRACKS_KEY)

    def update_recently_replayed_tracks(self, track_id: str) -> None:
        self._update_key_cache(self.RECENTLY_REPLAYED_TRACKS_KEY, track_id)

    def clear_recently_replayed_tracks(self) -> None:
        self._clear_key_cache(self.RECENTLY_REPLAYED_TRACKS_KEY)


    """ FRESH PLAYLISTS """


    def set_fresh_playlists(self, playlists_ids: List[str]) -> None:
        self._set_key_cache(self.FRESH_PLAYLISTS_KEY, playlists_ids)

    def get_fresh_playlists(self) -> List[str] | None:
        self._get_key_cache(self.FRESH_PLAYLISTS_KEY)

    def update_fresh_playlists(self, playlist_id: str) -> None:
        self._update_key_cache(self.FRESH_PLAYLISTS_KEY, playlist_id)

    def clear_fresh_playlists(self) -> None:
        self._clear_key_cache(self.FRESH_PLAYLISTS_KEY)