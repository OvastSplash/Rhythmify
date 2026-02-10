from pylast import Track, SimilarItem, Tag, LastFMNetwork, Artist, TopItem
from typing import List
from Rhythmify.settings import LAST_FM_KEY, LAST_FM_SECRET
import pylast
import logging

logger = logging.getLogger(__name__)

class LastFMService:
    """
    Manages interactions with the LastFM API, providing methods to fetch data such
    as similar tracks, tracks by genre, similar artists, top tracks or genres of
    an artist.

    This class encapsulates various static utility methods for leveraging the LastFM
    API, allowing seamless integration for obtaining music-related information. It
    provides functionalities to fetch data like similar tracks, popular tracks by
    genre, similar artists, top tracks, and genres associated with a particular
    artist. It requires proper configuration with API credentials to access the
    LastFM service.

    Methods:
        get_client: Initializes and returns a LastFM client for API interaction.
        get_similar_tracks: Fetches tracks similar to a given track.
        get_tracks_by_genre: Retrieves top tracks for a specified genre.
        get_similar_artists: Finds artists similar to the given artist.
        get_artists_top_tracks: Gets a list of an artist's top tracks.
        get_artists_top_genres: Retrieves an artist's most prominent genres.

    Raises:
        Exception: If unable to initialize the LastFM client in 'get_client' method.
    """

    @staticmethod
    def get_client() -> LastFMNetwork | None:
        try:
            return pylast.LastFMNetwork(api_key=LAST_FM_KEY, api_secret=LAST_FM_SECRET)
        except Exception as e:
            logger.exception("LastFM client init error")

    @staticmethod
    def get_similar_tracks(track: Track, count: int = 10) -> List[SimilarItem]:
        return track.get_similar(count)

    @staticmethod
    def get_tracks_by_genre(genre: Tag, count: int = 5) -> List[Track]:
        return genre.get_top_tracks(count)

    @staticmethod
    def get_similar_artists(artist: Artist, count: int = 5) -> List[SimilarItem]:
        return artist.get_similar(count)

    @staticmethod
    def get_artists_top_tracks(artist: Artist, count: int = 5) -> List[Track]:
        return artist.get_top_tracks(count)

    @staticmethod
    def get_artists_top_genres(artist: Artist, count: int = 5) -> List[TopItem]:
        return artist.get_top_tags(count)


class LastFMClientService:
    """
    Handles interactions with the LastFM API through the LastFMService.

    Provides methods to fetch data related to tracks, genres, artists, top tracks,
    and top artists using the LastFM client. The service ensures the LastFM client
    is initialized and acts as an interface between the client and specific API
    requests.
    """

    def __init__(self):
        self.client = LastFMService.get_client()

        if not self.client:
            raise Exception("LastFM client is not initialized")

    def get_track(self, artist_name: str, track_name: str) -> Track:
        return self.client.get_track(artist_name, track_name)

    def get_genre(self, genre: str) -> Tag:
        return  self.client.get_tag(genre)

    def get_artist(self, artist_name: str) -> Artist:
        return self.client.get_artist(artist_name)

    def get_top_tracks(self) -> List[TopItem]:
        try:
            return self.client.get_top_tracks(limit=50)
        except Exception as e:
            raise Exception(f"Failed to get top tracks {e}")

    def get_top_artists(self) -> List[TopItem]:
        return self.client.get_top_artists(limit=10)

