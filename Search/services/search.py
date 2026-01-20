import logging

from django.db.models import QuerySet
from django.contrib.postgres.search import TrigramSimilarity
from User.models import CustomUser

from SpotifyController.models.models import Artist, Track, Genre, Album
from django.db import models

from itertools import chain
from typing import List

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, name: str) -> None:
        self.name = name

    def search(self) -> dict:
        """Search data by name using trigram similarity."""
        """
        Return (Users, Artists, Albums, Tracks, Genres)
        """

        return {
            "users": list(self.users),
            "artists": list(self.artists),
            "albums": list(self.albums),
            "tracks": list(self.tracks),
            "genres": list(self.genres),
        }


    def _filter_data(self, data: list[QuerySet]):
        flat_list: list[models.Model] = list(chain.from_iterable(data))

        return sorted(
            flat_list,
            key=lambda obj: obj.similarity,
            reverse=True
        )

    def _search_by_model(self, model: type[models.Model]) -> QuerySet:
        field = "name"

        if model is CustomUser:
            field = "username"

        return (
            model.objects
            .annotate(similarity=TrigramSimilarity(field, self.name))
            .filter(similarity__gt=0.3)
            .order_by('-similarity')
        )

    @property
    def users(self) -> QuerySet[CustomUser]:
        """Search users by username using trigram similarity."""
        return self._search_by_model(CustomUser)

    @property
    def artists(self) -> QuerySet[Artist]:
        """Search artists by name using trigram similarity."""
        return self._search_by_model(Artist)

    @property
    def albums(self) -> QuerySet[Album]:
        """Search albums by name using trigram similarity."""
        return self._search_by_model(Album)

    @property
    def tracks(self) -> QuerySet[Track]:
        """Search tracks by name using trigram similarity."""
        return self._search_by_model(Track)

    @property
    def genres(self) -> QuerySet[Genre]:
        """Search genres by name using trigram similarity."""
        return self._search_by_model(Genre)