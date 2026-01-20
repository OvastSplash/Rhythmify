from django.db import transaction, IntegrityError
import logging

from typing import List, Tuple

from django.shortcuts import get_object_or_404

from SpotifyController.services.construct_data import (
    TrackClass,
    GenreClass,
    ArtistClass, AlbumClass,
)

from SpotifyController.models.models import (
    Track,
    Artist,
    Genre,
    Album,
    Playlist,
)

from dataclasses import dataclass
from datetime import datetime

from User.services import UserService
from SpotifyController.services.database.check_data import CheckDataService



from Deezer.services import ClientService

logger = logging.getLogger(__name__)

@dataclass
class PlayedTrackDTO:
    track: Track
    played_at: datetime = None

class BuildDataService:
    def __init__(self):
        self.user_service = UserService()
        self.check_service = CheckDataService()
        self.deezer_client = ClientService()

    @staticmethod
    def get_or_create_genre(genre: GenreClass) -> Genre:
        genre, _ = Genre.objects.get_or_create(name=genre)
        return genre

    def _update_artist_genres(self, artist: Artist, genres: List[GenreClass]) -> None:
        new_genres = [self.get_or_create_genre(genre) for genre in genres if genre]

        if set(artist.genres.all()) != set(new_genres):
            artist.genres.set(new_genres)
            logger.debug("Artist genres updated: sid=%s count=%d", artist.spotify_id, len(new_genres))

    def _handle_album_creation(self, album: Album, image_url: str) -> None:
        self.user_service.update_object_image(album, image_url)

    @transaction.atomic
    def create_album(self, constructed_album: AlbumClass) -> Album:
        album, created = Album.objects.get_or_create(
            spotify_id=constructed_album.spotify_id,
            defaults={
                'name': constructed_album.name,
                'total_tracks': constructed_album.total_tracks,
                'release_date': constructed_album.release_date,
                'type': constructed_album.type,
                'spotify_url': constructed_album.spotify_url,
            }
        )

        if created:
            self._handle_album_creation(album, constructed_album.image_url)
            logger.info("Album created: sid=%s name=%s", album.spotify_id, album.name)

            from SpotifyController.tasks.fetch_new_obj import process_new_album_task
            transaction.on_commit(
                lambda : process_new_album_task.delay(album.spotify_id)
            )

        return album

    def create_albums(self, constructed_album: List[AlbumClass]) -> List[Album]:
        return [self.create_album(album) for album in constructed_album]

    def _create_and_associate_album(self, album: AlbumClass, track: Track, artists: List[Artist]) -> Album:
        if album:
            album = self.create_album(album)
            album.tracks.add(track)
            logger.debug("Track linked to album: album_sid=%s track_sid=%s", album.spotify_id, track.spotify_id)

        for artist in artists:
            artist.track_list.add(track)

            if album:
                artist.albums.add(album)

        return album

    @transaction.atomic
    def create_or_update_artist(self, artist_data: ArtistClass) -> Artist:
        logger.debug("Artist get_or_create called: name=%s sid=%s", artist_data.name, artist_data.spotify_id)
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data.spotify_id,
            defaults={
                'name': artist_data.name,
                'spotify_url': artist_data.spotify_url,
                'followers': artist_data.followers,
            }
        )

        self._update_artist_genres(artist, artist_data.genres)

        if created:
            from SpotifyController.tasks.fetch_new_obj import process_new_artist_task
            transaction.on_commit(
                lambda : process_new_artist_task.delay(artist.spotify_id)
            )

        if not created and artist.name != artist_data.name:
            logger.info("Artist renamed: sid=%s old=%s new=%s", artist.spotify_id, artist.name, artist_data.name)
            artist.name = artist_data.name
            artist.save()

        if artist_data.image_url and self.check_service.artist_image_update(artist, artist_data.image_url):
            logger.info("Artist image updating: artist=%s sid=%s", artist.name, artist_data.spotify_id)

            artist.image = self.user_service.update_object_image(
                artist, artist_data.image_url, save=True
            ) if artist_data.image_url else None

        return artist

    def _create_or_update_artists(self, artists: List[ArtistClass]) -> List[Artist]:
        return [self.create_or_update_artist(artist) for artist in artists]

    @transaction.atomic
    def _get_or_create_track(self, track: TrackClass) -> Tuple[Track, bool]:
        try:
            obj, created = Track.objects.get_or_create(
                spotify_id=track.spotify_id,
                defaults={
                    'name': track.name,
                    'url': track.url,
                    'duration_ms': track.duration_ms,
                }
            )
            if created:
                logger.info("Track created: sid=%s name=%s", track.spotify_id, track.name)

            return obj, created
        except IntegrityError:
            logger.warning("Track get_or_create IntegrityError; fetching existing: sid=%s", track.spotify_id)
            return Track.objects.get(spotify_id=track.spotify_id), False

    def _handle_track_creation(self, track: Track, constructed_track: TrackClass) -> None:
        logger.debug("Handle track creation: sid=%s name=%s", track.spotify_id, track.name)
        review = self.deezer_client.get_preview_by_track(track)

        if review:
            track.save_preview(review)

        self.user_service.update_object_image(track, constructed_track.image_url)

    def create_track(self, constructed_track: TrackClass) -> Track:
        track, created = self._get_or_create_track(constructed_track)

        if constructed_track.artists:
            artists: List[Artist] = self._create_or_update_artists(constructed_track.artists)
            self._create_and_associate_album(constructed_track.album, track, artists)
        else:
            raise ValueError(f"Track {track.name} has no artists")

        if created:
            self._handle_track_creation(track, constructed_track)

        return track

    def create_tracks(self, constructed_tracks: List[TrackClass]) -> List[Track]:
        tracks: List[Track] = list()
        for constructed_track in constructed_tracks:
            tracks.append(self.create_track(constructed_track))

        return tracks

    def create_played_at_track(self, track: TrackClass) -> PlayedTrackDTO:
        return PlayedTrackDTO(
            track=self.create_track(track),
            played_at=track.played_at,
        )

    def create_played_at_tracks(self, tracks: List[TrackClass]) -> List[PlayedTrackDTO]:
        return [self.create_played_at_track(track) for track in tracks]


class UpdateDataService:
    def _update_playlist(self, playlist_id: str, track: str, add: bool) -> None:
        """Update playlist with track."""
        try:
            playlist = get_object_or_404(Playlist, spotify_id=playlist_id)
            track = get_object_or_404(Track, spotify_id=track)

            playlist.tracks.add(track) if add else playlist.tracks.remove(track)
            playlist.track_count += 1 if add else -1

            playlist.save()

            if add:
                logger.info("Track added to playlist: pid=%s tid=%s add=%s", playlist_id, track, add)
            else:
                logger.info("Track removed from playlist: pid=%s tid=%s add=%s", playlist_id, track, add)

        except Exception as e:
            logger.error("Track adding error: pid=%s tid=%s add=%s error=%s", playlist_id, track, add, e)
            raise


    def add_track_to_playlist(self, playlist_id: str, track_id: str) -> None:
        """Update playlist with track."""
        self._update_playlist(playlist_id, track_id, True)


    def remove_track_from_playlist(self, playlist_id: str, track_id: str) -> None:
        """Remove track from playlist."""
        self._update_playlist(playlist_id, track_id, False)