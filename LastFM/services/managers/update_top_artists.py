import logging

from typing import List
from pylast import TopItem

from LastFM.services.construct_data_services import ConvertToSpotifyDataService

from LastFM.services.client_service import LastFMClientService
from SpotifyController.services.construct_data import ConstructDataService, ArtistClass
from SpotifyController.services.database.data_builder import BuildDataService
from Main.services.database.update_top_data import UpdateTopArtists


from SpotifyController.models.models import Artist
from SpotifyController.services.construct_data import TrackClass

from Main.models import TopArtist

logger = logging.getLogger(__name__)

class UpdateTopArtistsManager:
    def __init__(self):
        self.last_fm_client = LastFMClientService()
        self.construct_sp = ConstructDataService()
        self.sp_db = BuildDataService()
        self.update_top_data = UpdateTopArtists()

    def _get_top_artists(self) -> List[TopItem]:
        return self.last_fm_client.get_top_artists()

    def _create_artist(self, artist: ArtistClass) -> Artist:
        return self.sp_db.create_or_update_artist(artist)

    def _convert_to_spotify_data(self, top_artists: List[TopItem]) -> List[Artist]:
        converted_artists: List[Artist] = list()

        for top_artist in top_artists:
            artist = ConvertToSpotifyDataService.convert_artist_data(top_artist)

            if isinstance(artist, Artist):
                converted_artists.append(artist)
            else:
                converted_artists.append(self._create_artist(artist))

        return converted_artists

    def _save_top_tracks(self, artists: List[Artist]) -> List[TopArtist]:
        return self.update_top_data.update_top_artists(artists)

    def run(self) -> List[TopArtist]:
        top_artists = self._get_top_artists()
        converted_tracks = self._convert_to_spotify_data(top_artists)

        return self._save_top_tracks(converted_tracks)
