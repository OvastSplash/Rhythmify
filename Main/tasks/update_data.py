import logging

from celery import shared_task

from LastFM.services.managers.update_top_artists import UpdateTopArtistsManager
from LastFM.services.managers.update_top_tracks import UpdateTopTracksManager

logger = logging.getLogger(__name__)


@shared_task
def update_top_tracks():
    logger.info("update_top_tracks")

    manager = UpdateTopTracksManager()
    manager.run()

    logger.info("Top tracks updated")

@shared_task
def update_top_artists():
    logger.info("update_top_artists")

    manager = UpdateTopArtistsManager()
    manager.run()

    logger.info("Top artists updated")