import logging
from celery import shared_task

from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister
from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister
from Main.services.database.repositories.top_tracks import TopTrackRegister
from Main.services.database.repositories.top_artists import TopArtistsRegister

logger = logging.getLogger(__name__)


@shared_task
def clear_all_data():
    logger.info("clear_all_data")

    top_track = TopTrackRegister()
    top_artist = TopArtistsRegister()
    played_today_track_register = PlayedTodayTrackRegister()
    fresh_playlist_register = FreshPlaylistRegister()

    top_track.clear_top_tracks()
    top_artist.clear_top_artists()
    played_today_track_register.clear_played_tracks()
    fresh_playlist_register.clear_fresh_playlists()

    logger.info("Cleared today's data")

