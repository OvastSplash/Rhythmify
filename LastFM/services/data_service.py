import logging

from typing import List, Union
from pylast import SimilarItem, Track, Artist

from LastFM.services.client_service import LastFMClientService, LastFMService
from SpotifyController.models.models import Track as TrackModel, Artist as ArtistModel

logger = logging.getLogger(__name__)

class LastFMDataService:
    """
    Provides methods for interacting with LastFM services.

    This class serves as a data aggregation service that interacts with LastFM's data through client
    and service layers. It facilitates fetching tracks, artists, and similar items based on various
    criteria such as tracks, genres, and artists. It also includes methods for data transformation
    like converting similar artists to artist entities.
    """

    def __init__(self):
        self.client = LastFMClientService()
        self.last_fm_service = LastFMService()

    def collect_tracks_by_tracks(self, tracks: List[TrackModel], count: int = 3) -> List[SimilarItem]:
        similar_tracks: List[SimilarItem] = []

        for index, track in enumerate(tracks):
            logger.debug("Processing track: name=%s", track.name)
            get_tracks = self.client.get_track(artist_name=track.artists.first().name, track_name=track.name)
            logger.debug("Fetched LastFM track: track=%s", str(get_tracks))

            multiplier = max(1.0, 2.0 - (index * 0.2))
            track_count = int(count * multiplier)

            try:
                similar = self.last_fm_service.get_similar_tracks(track=get_tracks, count=track_count)
                similar_tracks.extend(similar)

            except Exception:
                logger.exception("Failed to get similar tracks: track=%s", track.name)

        return similar_tracks

    def collect_tracks_by_genre(self, genres: List[str], count: int = 5) -> List[Track]:
        tracks: List[Track] = []

        for index, genre in enumerate(genres):
            get_genre = self.client.get_genre(genre)

            multiplier = max(1.0, 2.0 - (index * 0.2))
            genre_count = int(count * multiplier)

            tracks.extend(self.last_fm_service.get_tracks_by_genre(genre=get_genre, count=genre_count))

        return tracks

    def collect_similar_artists(self, artists: List[ArtistModel], count: int = 2) -> List[SimilarItem]:
        similar_artists: List[SimilarItem] = []

        for index, artist in enumerate(artists):
            get_artist = self.client.get_artist(artist.name)

            multiplier = max(1.0, 2.0 - (index * 0.2))
            artist_count = int(count * multiplier)

            similar_artists.extend(self.last_fm_service.get_similar_artists(artist=get_artist, count=artist_count))

        return similar_artists

    def collect_artists_top_tracks(self, artists: Union[List[Artist], Artist], count: int = 5) -> List[Track]:
        tracks: List[Track] = []

        if isinstance(artists, list):
            for artist in artists:
                tracks.extend(self.last_fm_service.get_artists_top_tracks(artist=artist, count=count))

        else:
            tracks.extend(self.last_fm_service.get_artists_top_tracks(artist=artists, count=count))

        return tracks

    def transform_similar_artists_to_artists(self, similar_artists: Union[List[SimilarItem], Artist]) -> Union[List[Artist], Artist]:
        if isinstance(similar_artists, list):
            artists: List[Artist] = []

            for artist in similar_artists:
                artists.append(self.client.get_artist(artist.item.name))

            return artists

        else:
            return self.client.get_artist(similar_artists.name)
