import logging

from celery import shared_task

from Main.services.handlers.handle_update_top_tracks import UpdateTopTracksHandler
from Main.services.handlers.handle_update_top_artists import UpdateTopArtistsManager

from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService

from Main.services.database.repositories.played_today_track import PlayedTodayTrackRegister
from Main.services.database.repositories.fresh_playlist import FreshPlaylistRegister

from Main.services.cache import MainCache

logger = logging.getLogger(__name__)


@shared_task
def update_top_tracks():
    logger.info("update_top_tracks")

    handler = UpdateTopTracksHandler()
    top_tracks = handler.run()

    logger.info("Top tracks updated: tracks=%s", top_tracks)

@shared_task
def update_top_artists():
    logger.info("update_top_artists")

    handler = UpdateTopArtistsManager()
    top_artists = handler.run()


    logger.info("Top artists updated: artists=%s", top_artists)

@shared_task
def update_recently_replayed_tracks():
    logger.info("update_recently_replayed_tracks")

    replayed_tracks = PlayedTodayTrackRegister.get_replayed_tracks()
    tracks_ids = ConvertSpotifyDataBaseService.convert_tracks_to_ids(
        tracks=[replayed.track for replayed in replayed_tracks]
    )

    cache = MainCache()
    cache.set_recently_replayed_tracks(tracks_ids)

    logger.info("Recently replayed tracks updated")

@shared_task
def update_fresh_playlists():
    logger.info("update_fresh_playlists")

    fresh_playlists = FreshPlaylistRegister.get_fresh_playlists()
    playlists_ids = ConvertSpotifyDataBaseService.convert_playlists_to_ids(
        [fresh.playlist for fresh in fresh_playlists]
    )

    cache = MainCache()
    cache.set_fresh_playlists(playlists_ids)

    logger.info("Fresh playlists updated")