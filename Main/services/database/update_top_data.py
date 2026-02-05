import logging

from typing import List, Type
from django.db.models import Model

from SpotifyController.models.models import Track, Artist
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService

from Main.models import TopTrack, TopArtist
from Main.services.cache import MainCache

from django.db import transaction

logger = logging.getLogger(__name__)

class UpdateMain:
    def __init__(self, cache: MainCache | None = None, convert_sp:ConvertSpotifyDataBaseService | None = None):
        self.cache = cache or MainCache()
        self.convert_sp = convert_sp or ConvertSpotifyDataBaseService()

    def _clear_data(self, model: Type[Model]) -> None:
        model.objects.all().delete()
        logger.info("Cleared %s", model.__name__)

class UpdateTopTracks(UpdateMain):
    def _update_top_track(self, tracks: List[Track]) -> List[TopTrack]:
        created_top_tracks = TopTrack.objects.bulk_create(
            [
                TopTrack(track=track, position=pos)
                for pos, track in enumerate(tracks, start=1)
            ]
        )
        logger.info("Created top tracks: tracks=%s", created_top_tracks)
        return created_top_tracks

    @transaction.atomic
    def update_top_tracks(self, tracks: List[Track]) -> List[TopTrack]:
        logger.info("Updating top tracks: tracks=%s", tracks)

        self._clear_data(TopTrack)
        created_top_tracks = self._update_top_track(tracks)
        tracks_ids = self.convert_sp.convert_tracks_to_ids(tracks=tracks)

        self.cache.set_top_tracks(tracks_ids)

        logger.info("Top tracks updated")
        return created_top_tracks

class UpdateTopArtists(UpdateMain):
    def _update_top_artists(self, artists: List[Artist]) -> List[TopArtist]:
        created_top_artists = TopArtist.objects.bulk_create(
            [
                TopArtist(artist=artist, position=pos)
                for pos, artist in enumerate(artists, start=1)
            ]
        )

        logger.info("Created top artists: artists=%s", created_top_artists)
        return created_top_artists

    @transaction.atomic
    def update_top_artists(self, artists: List[Artist]) -> List[TopArtist]:
        logger.info("Updating top artists: artists=%s", artists)

        self._clear_data(TopArtist)
        created_top_artists = self._update_top_artists(artists)
        artists_ids = self.convert_sp.convert_artists_to_ids(artists=artists)

        self.cache.set_top_artists(artists_ids)

        logger.info("Top artists updated")
        return created_top_artists