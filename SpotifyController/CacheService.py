from django.core.cache import cache
from typing import List
from .models import Track

class UserCacheService:
    FAVORITE_TRACKS_KEY = "favorite_tracks_{user_id}"
    RECOMMEND_TRACKS_KEY = "recommend_tracks_{user_id}"

    """
    USER FAVORITE TRACKS CACHE
    """

    @staticmethod
    def set_user_favorite_tracks(user_id: int, tracks: List[Track], timeout: int = None):
        cache.set(UserCacheService.FAVORITE_TRACKS_KEY.format(user_id=user_id), tracks, timeout)

    @staticmethod
    def get_user_favorite_tracks(user_id: int) -> List[Track]:
        return cache.get(UserCacheService.FAVORITE_TRACKS_KEY.format(user_id=user_id))

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
    def get_user_recommended_tracks(user_id: int) -> List[Track]:
        return cache.get(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=user_id))

    @staticmethod
    def clear_user_recommended_tracks(user_id: int):
        cache.delete(UserCacheService.RECOMMEND_TRACKS_KEY.format(user_id=user_id))