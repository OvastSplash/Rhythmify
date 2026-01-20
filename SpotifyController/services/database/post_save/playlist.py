import logging

logger = logging.getLogger(__name__)

class PlaylistPostSave:
    def __init__(self, playlist) -> None:
        from SpotifyController.services.client_services import UserClient, PublicClient
        from SpotifyController.services.database.data_builder import BuildDataService

        self.playlist = playlist
        self.user = self.playlist.user

        self.user_client = UserClient(self.user)
        self.public_client = PublicClient()

        self.db_service = BuildDataService()

    def _get_tracks(self, sid: str):
        tracks = self.public_client.get_track_info()