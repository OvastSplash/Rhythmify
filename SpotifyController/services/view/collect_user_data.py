import logging

from SpotifyController.models.models import Track, Playlist
from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService

from typing import Tuple, List

logger = logging.getLogger("SpotifyController")

class CollectUserDataService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cache_service = UserCacheService(user_id=user_id)


    def get_favorite_tracks(self) -> Tuple[list, list, list]:
        cached_favorite_tracks = self.cache_service.get_all_user_favorite_tracks()
        return self._convert_favorite_tracks_data(cached_favorite_tracks)

    def _convert_tracks_ids(self, tracks_ids: List[str]) -> List[Track]:
        return ConvertSpotifyDataBaseService.convert_ids_to_tracks(tracks_ids)

    def _convert_favorite_tracks_data(self, favorite_tracks_data: Tuple[list, list, list])\
            -> Tuple[list[Track], list[Track], list[Track]]:

        favorite_tracks = tuple(
            ConvertSpotifyDataBaseService.convert_ids_to_tracks(ids)
            for ids in favorite_tracks_data
        )

        return favorite_tracks


    def get_playlists(self):
        playlists_ids = self.cache_service.get_user_playlists()
        return self._convert_playlists_data(playlists_ids)

    def _convert_playlists_data(self, playlists_ids: List) -> List[Playlist]:
        return ConvertSpotifyDataBaseService.convert_ids_to_playlists(playlists_ids)


    def get_recommended_tracks(self):
        tracks_ids = self.cache_service.get_user_recommended_tracks()
        return self._convert_tracks_ids(tracks_ids)



    def get_statistics(self) -> Tuple[dict, dict] | Tuple[None, None]:
        statistics = self.cache_service.get_user_statistics()

        statistics_sorted = None
        if statistics:
            statistics = ConvertSpotifyDataBaseService.convert_user_statistic(statistics)

            # Prepare a pre-sorted list of (month, data) tuples to avoid using dictsortreversed in the template
            # Month key format is "YYYY-M"; we sort by numeric (year, month) descending

            def _ym_key(item):
                month_str = item[0]
                try:
                    y_str, m_str = month_str.split("-")
                    return (int(y_str), int(m_str))
                except Exception:
                    return (0, 0)

            statistics_sorted = sorted(statistics.items(), key=_ym_key, reverse=True)

            return statistics, statistics_sorted

        return None, None