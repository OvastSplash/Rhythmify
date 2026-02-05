from pytest import fixture
from LastFM.services.client_service import LastFMClientService
from LastFM.services.construct_data_services import ConvertToSpotifyDataService

@fixture
def last_fm_client() -> LastFMClientService:
    client = LastFMClientService()
    return client

@fixture
def construct_data_service() -> ConvertToSpotifyDataService:
    return ConvertToSpotifyDataService()