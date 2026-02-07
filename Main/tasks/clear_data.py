import logging
from celery import shared_task

from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister
from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister

logger = logging.getLogger(__name__)


@shared_task
def clear_all_data():
    logger.info("clear_today_played_tracks"
                )
    PlayedTodayTrackRegister.clear_played_tracks()
    FreshPlaylistRegister.clear_fresh_playlists()

    logger.info("Cleared played tracks")

