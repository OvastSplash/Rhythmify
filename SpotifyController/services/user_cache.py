from django.core.cache import cache
from typing import List, Dict, Tuple


class UserCacheService:
    SHORT_TERM_FAVORITE_TRACKS_KEY = "short_term_favorite_tracks_{user_id}"
    MEDIUM_TERM_FAVORITE_TRACKS_KEY = "medium_term_favorite_tracks_{user_id}"
    LONG_TERM_FAVORITE_TRACKS_KEY = "long_term_favorite_tracks_{user_id}"
    PLAYLISTS_KEY = "playlists_{user_id}"

    TERM_KEYS = {
        'short_term': 'SHORT_TERM_FAVORITE_TRACKS_KEY',
        'medium_term': 'MEDIUM_TERM_FAVORITE_TRACKS_KEY',
        'long_term': 'LONG_TERM_FAVORITE_TRACKS_KEY',
    }

    RECOMMEND_TRACKS_KEY = "recommend_tracks_{user_id}"
    USER_LISTEN_HISTORY_KEY = "user_statistics_{user_id}"

    """
    USER FAVORITE TRACKS CACHE
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    def set_user_favorite_tracks(self, track_ids: List[str], term: str, timeout: int = None):
        key_name = self.TERM_KEYS[term]
        key = getattr(self, key_name).format(user_id=self.user_id)
        cache.set(key, track_ids, timeout)

    def get_user_favorite_tracks(self, term: str) -> List[str] | None:
        key_name = self.TERM_KEYS[term]
        key = getattr(self, key_name).format(user_id=self.user_id)
        return cache.get(key)

    def get_all_user_favorite_tracks(self) -> Tuple[List[str], List[str], List[str]] | None:
        short_term_tracks = self.get_user_favorite_short_term_tracks()
        medium_term_tracks = self.get_user_favorite_medium_term_tracks()
        long_term_tracks = self.get_user_favorite_long_term_tracks()

        return short_term_tracks, medium_term_tracks, long_term_tracks

    def set_user_favorite_short_term_tracks(self, track_ids: List[str], timeout: int = None):
        self.set_user_favorite_tracks(track_ids=track_ids, term="short_term", timeout=timeout)

    def get_user_favorite_short_term_tracks(self) -> List[str] | None:
        return self.get_user_favorite_tracks(term="short_term")


    def set_user_favorite_medium_term_tracks(self, track_ids: List[str], timeout: int = None):
        self.set_user_favorite_tracks(track_ids=track_ids, term="medium_term", timeout=timeout)

    def get_user_favorite_medium_term_tracks(self) -> List[str] | None:
        return self.get_user_favorite_tracks(term="medium_term")


    def set_user_favorite_long_term_tracks(self, track_ids: List[str], timeout: int = None):
        self.set_user_favorite_tracks(track_ids=track_ids, term="long_term", timeout=timeout)

    def get_user_favorite_long_term_tracks(self) -> List[str] | None:
        return self.get_user_favorite_tracks(term="long_term")


    def clear_user_favorite_tracks(self):
        cache.delete(self.SHORT_TERM_FAVORITE_TRACKS_KEY.format(user_id=self.user_id))
        cache.delete(self.MEDIUM_TERM_FAVORITE_TRACKS_KEY.format(user_id=self.user_id))
        cache.delete(self.LONG_TERM_FAVORITE_TRACKS_KEY.format(user_id=self.user_id))

    """
    USER RECOMMEND CACHE
    """

    def set_user_recommended_tracks(self, tracks_ids: List[str], timeout: int = None):
        cache.set(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=self.user_id), tracks_ids, timeout)

    def get_user_recommended_tracks(self) -> List[str] | None:
        key = UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=self.user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    def clear_user_recommended_tracks(self):
        cache.delete(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=self.user_id))

    """
    USER LISTEN HISTORY CACHE
    """

    def set_user_statistics(self, user_statistic: Dict, timeout: int = None) -> None:
        cache.set(UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=self.user_id), user_statistic, timeout)

    def get_user_statistics(self) -> Dict | None:
        """
        Return Dict[tracks, artists, genres]
        """
        key = UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=self.user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    def clear_user_statistics(self):
        cache.delete(UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=self.user_id))


    """
    USER PLAYLIST CACHE
    """

    def set_user_playlists(self, playlist_ids: List[str], timeout: int = None) -> None:
        cache.set(UserCacheService.PLAYLISTS_KEY.format(user_id=self.user_id), playlist_ids, timeout)

    def get_user_playlists(self) -> List[str] | None:
        key = UserCacheService.PLAYLISTS_KEY.format(user_id=self.user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    def add_playlist_to_user_playlists(self, playlist_id: str) -> None:
        playlists = self.get_user_playlists() or list()
        playlists.append(playlist_id)
        self.set_user_playlists(playlists)

    def clear_user_playlists(self):
        cache.delete(UserCacheService.PLAYLISTS_KEY.format(user_id=self.user_id))