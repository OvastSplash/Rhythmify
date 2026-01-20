from pylast import SimilarItem, Track as LFM_Track
from typing import Union, Tuple, List
from SpotifyController.services.client_services import PublicClient
from SpotifyController.models.models import Track, Artist as ArtistModel
from .services import LastFMDataService
from SpotifyController.services.construct_data import ConstructDataService
from SpotifyController.services.database.data_builder import BuildDataService
from SpotifyController.services.construct_data import TrackClass
import logging

logger = logging.getLogger(__name__)

class ConvertToSpotifyDataService:
    @staticmethod
    def convert_track_data(track: Union[LFM_Track, SimilarItem]) -> Union[dict, Track]:
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

class TrackSyncManager:
    @staticmethod
    def collect_recommendations(tracks: List[Track], artists: List[ArtistModel], genres: List[str], commit=True) \
            -> Tuple[Union[List[Track], List[TrackClass]], List[Track]]:
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
            spotify_data = ConvertToSpotifyDataService.convert_track_data(track)

            if isinstance(spotify_data, Track):
                existed_tracks.append(spotify_data)

            else:
                converted_tracks.append(construct_sp.track_data(spotify_data))

        if commit:
            sp_db = BuildDataService()
            saved_tracks: List[Track] = sp_db.create_tracks(converted_tracks)

            return saved_tracks, existed_tracks

        return converted_tracks, existed_tracks
