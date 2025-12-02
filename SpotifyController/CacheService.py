from django.core.cache import cache
from typing import List, Dict, Tuple
from .models import Track
from datetime import datetime
from collections import Counter

class UserCacheService:
    FAVORITE_TRACKS_KEY = "favorite_tracks_{user_id}"
    RECOMMEND_TRACKS_KEY = "recommend_tracks_{user_id}"
    USER_LISTEN_HISTORY_KEY = "user_statistics_{user_id}"

    """
    USER FAVORITE TRACKS CACHE
    """

    @staticmethod
    def set_user_favorite_tracks(user_id: int, tracks: List[Track], timeout: int = None):
        cache.set(UserCacheService.FAVORITE_TRACKS_KEY.format(user_id=user_id), tracks, timeout)

    @staticmethod
    def get_user_favorite_tracks(user_id: int) -> List[Track] | None:
        key = UserCacheService.FAVORITE_TRACKS_KEY.format(user_id=user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    @staticmethod
    def clear_user_favorite_tracks(user_id: int):
        cache.delete(UserCacheService.FAVORITE_TRACKS_KEY.format(user_id=user_id))

    """
    USER RECOMMEND CACHE
    """

    @staticmethod
    def set_user_recommended_tracks(user_id: int, tracks: List[Track], timeout: int = None):
        cache.set(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=user_id), tracks, timeout)

    @staticmethod
    def get_user_recommended_tracks(user_id: int) -> List[Track] | None:
        key = UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    @staticmethod
    def clear_user_recommended_tracks(user_id: int):
        cache.delete(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=user_id))

    """
    USER LISTEN HISTORY CACHE
    """

    @staticmethod
    def set_user_statistics(user_id: int, user_statistic: Dict, timeout: int = None) -> None:
        cache.set(UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=user_id), user_statistic, timeout)

    @staticmethod
    def get_user_statistics(user_id: int) -> Dict | None:
        """
        Return Dict[tracks, artists, genres]
        """
        key = UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=user_id)
        if cache.get(key) is not None:
            return cache.get(key)

        return None

    @staticmethod
    def clear_user_statistics(user_id: int):
        cache.delete(UserCacheService.USER_LISTEN_HISTORY_KEY.format(user_id=user_id))