from pylast import SimilarItem, TopItem, Track as LFM_Track
from typing import Union, Tuple, List
from SpotifyController.services.client_services import PublicClient
from SpotifyController.models.models import Track, Artist as ArtistModel
from LastFM.services.data_service import LastFMDataService
from SpotifyController.services.construct_data import ConstructDataService, ArtistClass
from SpotifyController.services.database.data_builder import BuildDataService
from SpotifyController.services.construct_data import TrackClass
import logging

logger = logging.getLogger(__name__)

class ConvertToSpotifyDataService:
    @staticmethod
    def convert_track_data(track: Union[LFM_Track, SimilarItem, TopItem]) -> Union[TrackClass, Track]:
        """
        Converts track data from an LFM_Track or SimilarItem object into a dictionary or a Track instance.
        If the track already exists in the database, it returns the existing Track instance.
        If not, it retrieves the track information using a public client and creates a new Track instance.

        Raises:
            No exceptions are described within this method.

        Args:
            track: A Union[LFM_Track, SimilarItem]. The track data to be converted. If track is of
                type SimilarItem, its item attribute will be accessed for further processing.

        Returns:
            Union[dict, Track]: A dictionary representation of the track or an instance of the
            Track model.
        """

        if hasattr(track, 'item'):
            track = track.item

        track_name = track.get_name()
        artist_name = track.get_artist().get_name()

        track_exist = Track.objects.filter(name=track_name).first()

        if track_exist:
            logger.info("Track already exists: track=%s artist=%s", track_name, artist_name)
            return track_exist

        logger.info("Creating track from LastFM: track=%s artist=%s", track_name, artist_name)
        public_client = PublicClient()

        return public_client.get_track_info_by_name(track_name, artist_name)

    @staticmethod
    def convert_artist_data(artist: TopItem) -> Union[ArtistClass, ArtistModel]:
        artist_name = artist.item.get_name()
        artist_exist = ArtistModel.objects.filter(name=artist_name).first()

        if artist_exist:
            logger.info("Artist already exists: artist=%s", artist_name)
            return artist_exist

        logger.info("Creating artist from LastFM: artist=%s", artist_name)
        public_client = PublicClient()

        return public_client.get_artist_by_name(artist_name=artist_name)


class TrackSyncManager:
    @staticmethod
    def collect_recommendations(tracks: List[Track], artists: List[ArtistModel], genres: List[str], commit=True) \
            -> Tuple[Union[List[Track], List[TrackClass]], List[Track]]:

        """
        Collects recommended tracks based on a combination of existing tracks, artists, and genres.

        The method uses an external data service to gather recommendations, leveraging track and artist similarity
        information, along with genre-based recommendations. It processes and converts the gathered track data
        into a consistent format for further use, including saving or directly returning the processed tracks.

        Parameters:
        tracks (List[Track]): A list of tracks to find recommendations based on.
        artists (List[ArtistModel]): A list of artist models to gather similar artists.
        genres (List[str]): A list of genre names used for genre-based recommendations.
        commit (bool, optional): If True, the collected and processed track data will be saved to storage.

        Returns:
        Tuple[Union[List[Track], List[TrackClass]], List[Track]]: A tuple containing two lists. The first list includes
        processed and stored/generated tracks depending on the 'commit' parameter. The second list contains
        tracks already existing in the known dataset.

        Raises:
        None
        """

        last_fm_data_service = LastFMDataService()

        similar_tracks = set()
        similar_tracks.update(last_fm_data_service.collect_tracks_by_tracks(tracks))
        similar_tracks.update(last_fm_data_service.collect_tracks_by_genre(genres))

        similar_artists = last_fm_data_service.collect_similar_artists(artists)
        transformed_artists = last_fm_data_service.transform_similar_artists_to_artists(similar_artists)
        similar_tracks.update(last_fm_data_service.collect_artists_top_tracks(transformed_artists, count=2))


        converted_tracks = list()
        existed_tracks: List[Track] = list()

        construct_sp = ConstructDataService()

        for track in similar_tracks:
            track_data = ConvertToSpotifyDataService.convert_track_data(track)

            if isinstance(track_data, Track):
                existed_tracks.append(track_data)

            else:
                converted_tracks.append(track_data)

        if commit:
            sp_db = BuildDataService()
            saved_tracks: List[Track] = sp_db.create_tracks(converted_tracks)

            return saved_tracks, existed_tracks

        return converted_tracks, existed_tracks