from django.db import transaction

from typing import List, Tuple, Dict, DefaultDict
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
)

from dataclasses import dataclass
from datetime import datetime
from User.services import UserService
from SpotifyController.services.database.check_data import CheckDataService

from Deezer.services import ClientService

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

    def _handle_album_creation(self, album: Album, image_url: str) -> None:
        self.user_service.update_object_image(album, image_url)

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

        return album

    @transaction.atomic
    def create_albums(self, constructed_album: List[AlbumClass]) -> List[Album]:
        return [self.create_album(album) for album in constructed_album]

    def _create_and_associate_album(self, album: AlbumClass, track: Track, artists: List[Artist]) -> Album:
        if album:
            album = self.create_album(album)
            album.tracks.add(track)

        for artist in artists:
            artist.track_list.add(track)

            if album:
                artist.albums.add(album)

        return album

    def create_or_update_artist(self, artist_data: ArtistClass) -> Artist:
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data.spotify_id,
            defaults={
                'name': artist_data.name,
                'spotify_url': artist_data.spotify_url,
                'followers': artist_data.followers,
            }
        )

        if created:
            print(f"Artist has been created --- Artist Name: {artist.name}")

        self._update_artist_genres(artist, artist_data.genres)

        if not created and artist.name != artist_data.name:
            print(f"Artist name {artist.name} changed to {artist_data.name}")
            artist.name = artist_data.name
            artist.save()

        if artist_data.image_url and self.check_service.artist_image_update(artist, artist_data.image_url):
            artist.image = self.user_service.update_object_image(
                artist, artist_data.image_url, save=True
            ) if artist_data.image_url else None

        return artist

    def _create_or_update_artists(self, artists: List[ArtistClass]) -> List[Artist]:
        return [self.create_or_update_artist(artist) for artist in artists]

    def _get_or_create_track(self, track: TrackClass) -> Tuple[Track, bool]:
        return Track.objects.get_or_create(
            spotify_id=track.spotify_id,
            defaults={
                'name': track.name,
                'url': track.url,
                'duration_ms': track.duration_ms,
            }
        )

    def _handle_track_creation(self, track: Track, constructed_track: TrackClass) -> None:
        print(f"Track was created --- Track Name: {track.name}")
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

    @transaction.atomic
    def create_tracks(self, constructed_tracks: List[TrackClass]) -> List[Track]:
        tracks: List[Track] = list()
        for constructed_track in constructed_tracks:
            tracks.append(self.create_track(constructed_track))

        return tracks

    def create_artists_top_track(self, constructed_tracks: TrackClass, artist: Artist) -> Track:
        track = self.create_track(constructed_tracks)

        if not artist.top_tracks.filter(spotify_id=track.spotify_id).exists():
            artist.top_tracks.add(track)
            print(f"Track successfully added to artist's top tracks --- Track Name: {track.name} --- Artist Name: {artist.name}")

        return track

    @transaction.atomic
    def create_artists_top_tracks(self, tracks: List[TrackClass], artist: Artist) -> List[Track]:
        return [self.create_artists_top_track(track, artist) for track in tracks]

    def create_played_at_track(self, track: TrackClass) -> PlayedTrackDTO:
        return PlayedTrackDTO(
            track=self.create_track(track),
            played_at=track.played_at,
        )

    @transaction.atomic
    def create_played_at_tracks(self, tracks: List[TrackClass]) -> List[PlayedTrackDTO]:
        return [self.create_played_at_track(track) for track in tracks]