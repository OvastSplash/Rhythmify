from time import sleep

from SpotifyController.services.database.post_save.artist import ArtistPostSave
from SpotifyController.services.database.post_save.album import PostSaveAlbum

from SpotifyController.services.client_services import UserClient
from SpotifyController.models.models import Artist, Album, Playlist

from celery import shared_task

import logging

logger = logging.getLogger(__name__)

@shared_task
def process_new_album_task(album_id):
    sleep(5)
    album = Album.objects.get(spotify_id=album_id)
    logger.info("Process album: %s", album.name)

    post_save_service = PostSaveAlbum(album)
    post_save_service.handle()

    logger.info("Album successfully processed: %s", album.name)

@shared_task
def process_new_artist_task(artist_id):
    sleep(5)
    artist = Artist.objects.get(spotify_id=artist_id)
    logger.info("Process artist: %s", artist.name)

    post_save_service = ArtistPostSave(artist)
    post_save_service.handle_top_tracks()
    post_save_service.handle_albums()

    logger.info("Artist successfully processed: %s", artist.name)

@shared_task
def process_new_playlist_task(playlist_id):
    sleep(5)
    playlist = Playlist.objects.get(spotify_id=playlist_id)
    logger.info("Process playlist: %s", playlist.name)

    client = UserClient(playlist.user)
    tracks = client.get_playlist_tracks(playlist.spotify_id)

    playlist.tracks.add(*tracks)
    playlist.track_count = len(tracks)
    playlist.save()

    logger.info("Playlist successfully processed: %s", playlist.name)