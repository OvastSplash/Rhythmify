import logging
from typing import List

from pylast import TopItem

from LastFM.services.client_service import LastFMClientService
from LastFM.services.construct_data_services import ConvertToSpotifyDataService
from Main.services.database.update_top_data import UpdateTopTracks

from SpotifyController.models.models import Track
from SpotifyController.services.construct_data import ConstructDataService, TrackClass
from SpotifyController.services.database.data_builder import BuildDataService

from Main.models import TopTrack

logger = logging.getLogger(__name__)

class UpdateTopTracksManager:
    def __init__(self):
        self.last_fm_client = LastFMClientService()
        self.construct_sp = ConstructDataService()
        self.sp_db = BuildDataService()
        self.update_top_data = UpdateTopTracks()

    def _get_top_tracks(self) -> List[TopItem]:
        return self.last_fm_client.get_top_tracks()

    def _create_track(self, track: TrackClass) -> Track:
        return self.sp_db.create_track(track)

    def _convert_to_spotify_data(self, top_tracks: List[TopItem]) -> List[Track]:
        converted_tracks: List[Track] = list()

        for top_track in top_tracks:
            track = ConvertToSpotifyDataService.convert_track_data(top_track)

            if isinstance(track, Track):
                converted_tracks.append(track)
            else:
                constructed_track = self.construct_sp.track_data(track)
                converted_tracks.append(self._create_track(constructed_track))

        return converted_tracks

    def _save_top_tracks(self, tracks: List[Track]) -> List[TopTrack]:
        return self.update_top_data.update_top_tracks(tracks)

    def run(self) -> List[TopTrack]:
        top_tracks = self._get_top_tracks()
        converted_tracks = self._convert_to_spotify_data(top_tracks)

        return self._save_top_tracks(converted_tracks)