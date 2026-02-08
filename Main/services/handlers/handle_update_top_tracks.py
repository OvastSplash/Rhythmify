import logging

from Main.services.database.repositories.top_tracks import TopTrackRegister
from Main.services.handlers.handle_base_class import BaseHandler
from Main.models import TopTrack

from LastFM.services.managers.update_top_tracks import GetTopTracksHandler

from SpotifyController.models.models import Track

logger = logging.getLogger(__name__)


class UpdateTopTracksHandler(BaseHandler):
    repository = TopTrackRegister()
    get_top_tracks_manager = GetTopTracksHandler()

    @property
    def _top_tracks(self) -> list[Track]:
        return self.get_top_tracks_manager.process_top_tracks()

    def run(self, clear: bool = True) -> list[TopTrack]:
        logger.info("Start updating top tracks")

        if clear:
            self.repository.clear_top_tracks()

        top_tracks = self._top_tracks
        registered_top_tracks = self.repository.register_top_tracks(tracks=top_tracks)

        logger.info("Top tracks updated: tracks=%s", registered_top_tracks)
        return registered_top_tracks