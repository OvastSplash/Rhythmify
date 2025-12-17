from collections import Counter
from typing import List, Dict

from django.db.models import (
    Count,
    QuerySet,
)

from SpotifyController.models.models import (
    Track,
    Artist,
    Genre,
)
from SpotifyController.models.through import UsersListenHistory

from django.db.models.functions import (
    TruncMonth,
    ExtractYear,
    ExtractMonth,
    Concat,
    Extract,
)

from django.db.models import (
    F,
    Value,
    Subquery,
    OuterRef,
    Case,
    When,
    IntegerField,
    CharField,
    Sum,
)

from SpotifyController.services.user_cache import UserCacheService

class GetUserDataService:
    def __init__(self, user):
        self.user = user
        self.user_cache_service = UserCacheService(user_id=user.id)

    # USER DATA LISTEN HISTORY
    def listen_history_tracks(self, count=5) -> List[Track]:
        recent_tracks_id = (
            Track.objects
            .filter(listen_history__user=self.user)
            .order_by("-listen_history__played_at")
            .values_list("spotify_id", flat=True)[:count]
        )

        return self._sort_tracks_by_frequency(spotify_ids=recent_tracks_id, count=count)

    def _sort_tracks_by_frequency(self, spotify_ids: List[str], count) -> List[Track]:
        return self._sort_by_frequency(spotify_ids=spotify_ids, count=count, model=Track)

    def _sort_by_frequency(self, spotify_ids: List[str], count, model):
        """
            Sorts model objects by the frequency of their spotify_id in the list.

            Args:
                spotify_ids: List of spotify_id (may contain duplicates)
                model: Django model (Track, Artist, etc.)

            Returns:
                List of model objects sorted by frequency (most frequent first)
        """

        counts = Counter(spotify_ids)
        id_sorted: List[str] = [id for id, _ in counts.most_common(count)]
        dict_sorted = {obj.spotify_id: obj for obj in model.objects.filter(spotify_id__in=id_sorted)}

        return [dict_sorted[track_id] for track_id in id_sorted]

    def _sort_artists_by_frequency(self, spotify_ids: List[str], count) -> List[Artist]:
        return self._sort_by_frequency(spotify_ids=spotify_ids, count=count, model=Artist)

    def listen_history_artists(self, count=5) -> List[Artist]:
        # TODO: сделать что бы count треков сохранялся при первом его вызове или же передавать треки сюда напрямую
        recent_tracks = self.listen_history_tracks()
        artist_ids: List[str] = list()

        for track in recent_tracks:
            artist_ids.extend(track.artists.values_list("spotify_id", flat=True))

        return self._sort_artists_by_frequency(spotify_ids=artist_ids, count=count)

    def listen_history_genres(self, count=5) -> List[str]:
        recent_artists = self.listen_history_artists()
        genres: List[str] = list()

        for artist in recent_artists:
            genres.extend(artist.genres.values_list("name", flat=True))

        genre_counters = Counter(genres)
        return [genre for genre, _ in genre_counters.most_common(count)]

    # USER STATISTIC
    def listen_statistic(self) -> Dict:
        favorite_tracks = self.listen_history_tracks_by_month()
        favorite_artists = self.listen_history_artists_by_month()
        favorite_genres = self.listen_history_genre_by_month()

        cache_data = {"tracks": favorite_tracks, "artists": favorite_artists, "genres": favorite_genres}
        self.user_cache_service.set_user_statistics(user_statistic=cache_data)

        return cache_data

    def _sorted_by_period_user_listen_history(self):
        return (
            UsersListenHistory.objects.filter(user=self.user)
            .annotate(
                month_year_dt=TruncMonth("played_at"),
                hour=Extract("played_at", "hour"),
                time_period=Case(
                    When(hour__gte=0, hour__lt=5, then=1),
                    When(hour__gte=5, hour__lt=10, then=2),
                    When(hour__gte=10, hour__lt=18, then=3),
                    When(hour__gte=18, hour__lt=24, then=4),
                    output_field=IntegerField()
                )
            )
            .annotate(
                year=ExtractYear("month_year_dt"),
                month=ExtractMonth("month_year_dt"),
            )
            .annotate(month_year=Concat(
                F("year"),
                Value("-"),
                F("month"),
                output_field=CharField()
            ))
        )

    def _most_popular_period_user_listen_history(self, query: QuerySet):
        return (
            query.annotate(
                hour=Extract("played_at", "hour"),
                time_period=Case(
                    When(hour__gte=0, hour__lt=5, then=Value("00:00 - 05:00")),
                    When(hour__gte=5, hour__lt=10, then=Value("05:00 - 10:00")),
                    When(hour__gte=10, hour__lt=18, then=Value("10:00 - 18:00")),
                    When(hour__gte=18, hour__lt=24, then=Value("18:00 - 00:00")),
                    output_field=CharField()
                )
            )
            .values("time_period")
            .annotate(period_count=Count("id"))
            .order_by("-period_count")
            .values("time_period")[:1]
        )

    def listen_history_tracks_by_month(self, count=None) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get, most listened user track by month for all time
        Returns: QuerySet[UsersListenHistory, dict[track_spotify_id: str, count: int]]
        """

        most_common_period = self._most_popular_period_user_listen_history(
            UsersListenHistory.objects.filter(
                user=self.user,
                track__spotify_id=OuterRef("track__spotify_id"),
                played_at__year=OuterRef("year"),
                played_at__month=OuterRef("month")
            )
        )

        queryset = (
            self._sorted_by_period_user_listen_history()
            .values("month_year", "track__spotify_id", "year", "month")
            .annotate(
                play_count=Count("id"),
                total_listen_ms = Sum(F("track__duration_ms")),
                most_popular_period=Subquery(most_common_period)
            )
            .order_by("month_year_dt", "-play_count")
        )

        if count is not None:
            queryset = queryset[:count]

        return queryset

    def listen_history_artists_by_month(self, count=None) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get most listened user artists by month for all time
        Returns: QuerySet[UsersListenHistory, dict[artist_spotify_id: str, count: int]]
        """

        most_common_period = self._most_popular_period_user_listen_history(
            UsersListenHistory.objects.filter(
                user=self.user,
                track__artists__spotify_id=OuterRef("track__artists__spotify_id"),
                played_at__year=OuterRef("year"),
                played_at__month=OuterRef("month")
            )
        )

        queryset = (
            self._sorted_by_period_user_listen_history()
            .values("month_year", "track__artists__spotify_id", "year", "month")
            .annotate(
                artists_count=Count("id"),
                most_popular_period=Subquery(most_common_period)
            )
            .order_by("month_year_dt", "-artists_count")
        )

        if count is not None:
            queryset = queryset[:count]

        return queryset

    def listen_history_genre_by_month(self, count=None) -> QuerySet[UsersListenHistory, Dict[str, int]]:
        """
        This function is used to get most listened user genres by month for all time
        Returns: QuerySet[UsersListenHistory, dict[genre_name: str, count: int]]
        """

        most_common_period = self._most_popular_period_user_listen_history(
            UsersListenHistory.objects.filter(
                user=self.user,
                track__artists__genres__name=OuterRef("track__artists__genres__name"),
                played_at__year=OuterRef("year"),
                played_at__month=OuterRef("month")
            )
        )

        queryset = (
            self._sorted_by_period_user_listen_history()
            .values("month_year", "track__artists__genres__name", "year", "month")
            .annotate(
                genres_count=Count("id"),
                most_popular_period=Subquery(most_common_period)
            )
            .order_by("month_year_dt", "-genres_count")
        )

        if count is not None:
            queryset = queryset[:count]

        return queryset


    # USER RECOMMENDATIONS
    def top_tracks(self, count: int = 5) -> List[Track]:
        return list(
            Track.objects
            .filter(favorite__user=self.user)
            .prefetch_related("favorite", "artists")
        )[:count]

    # USER TOP ARTISTS
    def top_artists(self, count: int = 5) -> List[Artist]:
        return list(
            Artist.objects
            .filter(track_list__favorite__user=self.user)
            .annotate(user_count=Count('spotify_id'))
            .order_by("-user_count")
        )[:count]

    # USER TOP GENRES
    def top_genres(self, count: int = 5) -> List[str]:
        return list(
            Genre.objects
            .filter(artists__track_list__favorite__user=self.user)
            .annotate(artist_count=Count('artists'))
            .order_by("-artist_count")
            .values_list("name", flat=True)
        )[:count]

    # USER RECOMMENDATIONS
    def recommend_tracks(self) -> List[Track]:
        return list(
            Track.objects
            .filter(recommendations__user=self.user)
        )
