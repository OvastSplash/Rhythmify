import logging

from typing import List
from django.core.cache import cache

logger = logging.getLogger(__name__)

class MainCache:
    TOP_TRACKS_KEY = "top_tracks"
    TOP_ARTISTS_KEY = "top_artists"
    RECENTLY_REPLAYED_TRACKS_KEY = "recently_replayed_tracks"
    FRESH_PLAYLISTS_KEY = "fresh_playlists"

    def set_top_tracks(self, top_tracks_ids: List[str]) -> None:
        cache.set(self.TOP_TRACKS_KEY, top_tracks_ids)
        logger.info("[Main Cache] Top tracks updated")


    def get_top_tracks(self) -> List[str] | None:
        top_tracks_ids = cache.get(self.TOP_TRACKS_KEY)

        if top_tracks_ids is not None:
            logger.info("[Main Cache] Top tracks retrieved from cache")
            return top_tracks_ids

        logger.info("[Main Cache] Top tracks not found in cache")
        return None


    def set_top_artists(self, top_artists_ids: List[str]) -> None:
        cache.set(self.TOP_ARTISTS_KEY, top_artists_ids)
        logger.info("[Main Cache] Top artists updated")

    def get_top_artists(self) -> List[str] | None:
        top_artists_ids = cache.get(self.TOP_ARTISTS_KEY)

        if top_artists_ids is not None:
            logger.info("[Main Cache] Top artists retrieved from cache")
            return top_artists_ids

        logger.info("[Main Cache] Top artists not found in cache")
        return None


    def set_recently_replayed_tracks(self, tracks_ids: List[str]) -> None:
        cache.set(self.RECENTLY_REPLAYED_TRACKS_KEY, tracks_ids)
        logger.info("[Main Cache] Recently replayed tracks updated")

    def get_recently_replayed_tracks(self) -> List[str] | None:
        recently_replayed_tracks_ids = cache.get(self.RECENTLY_REPLAYED_TRACKS_KEY)
        return recently_replayed_tracks_ids


    def set_fresh_playlists(self, playlists_ids: List[str]) -> None:
        cache.set(self.FRESH_PLAYLISTS_KEY, playlists_ids)
        logger.info("[Main Cache] Fresh playlists updated")

    def get_fresh_playlists(self) -> List[str] | None:
        fresh_playlists_ids = cache.get(self.FRESH_PLAYLISTS_KEY)

        if fresh_playlists_ids is not None:
            logger.info("[Main Cache] Fresh playlists retrieved from cache")
            return fresh_playlists_ids

        logger.info("[Main Cache] Fresh playlists not found in cache")
        return None