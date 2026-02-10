import logging
from typing import List

from pylast import TopItem

from LastFM.services.client_service import LastFMClientService
from LastFM.services.construct_data_services import ConvertToSpotifyDataService

from SpotifyController.models.models import Track
from SpotifyController.services.construct_data import ConstructDataService, TrackClass
from SpotifyController.services.database.data_builder import BuildDataService

logger = logging.getLogger(__name__)

class GetTopTracksHandler:
    def __init__(self):
        self.last_fm_client = LastFMClientService()
        self.construct_sp = ConstructDataService()
        self.sp_db = BuildDataService()

    @property
    def _get_top_tracks(self) -> List[TopItem]:
        """
        Retrieves the top tracks from the Last.fm client.

        Summary:
        This property method fetches and returns a list of the top tracks by utilizing
        the Last.fm client object. The results are represented as instances of TopItem.

        Returns:
            List[TopItem]: A list of TopItem objects representing the top tracks.
        """
        return self.last_fm_client.get_top_tracks()

    def _create_track(self, track: TrackClass) -> Track:
        """
        Creates a track in the database.

        This method is responsible for adding a new track to the database. The track
        data is passed as an object, and the created track instance is returned upon
        completion.

        Parameters:
        track (TrackClass): The track object containing the information to be added.

        Returns:
        Track: The created track object.
        """
        return self.sp_db.create_track(track)

    def _convert_to_spotify_data(self, top_tracks: List[TopItem]) -> List[Track]:
        """
        Converts a list of top tracks to Spotify-compliant track data.

        This method processes the provided list of top tracks by converting their
        data into instances of Spotify-compatible Track objects. It ensures that each
        converted track conforms to the expected Track structure, either by directly
        applying a conversion method or by constructing a new track object if
        necessary.

        Parameters:
            top_tracks: List of top tracks to be converted. The items in the list are
                instances of TopItem, and they represent the original top track data
                that needs conversion.

        Returns:
            A list of Track objects that are compatible with Spotify's expected track
            data format.
        """
        converted_tracks: List[Track] = list()

        for top_track in top_tracks:
            track = ConvertToSpotifyDataService.convert_track_data(top_track)

            if isinstance(track, Track):
                converted_tracks.append(track)
            else:
                converted_tracks.append(self._create_track(track))

        return converted_tracks

    def process_top_tracks(self) -> List[Track]:
        """
        Processes the top tracks and converts them into Spotify data format.

        Returns
        -------
        List[Track]
            A list of tracks formatted into Spotify data.
        """
        top_tracks = self._get_top_tracks
        return self._convert_to_spotify_data(top_tracks)