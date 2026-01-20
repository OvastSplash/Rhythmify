from typing import List

from SpotifyController.models.models import (Track, Artist, Album, Genre, Playlist)
from dataclasses import dataclass
from django.shortcuts import get_object_or_404


class GetArtistDataService:
    @dataclass
    class ArtistData:
        artist: Artist
        tracks: List[Track]
        albums: List[Album]
        genres: List[str]

    def __init__(self, artist_id: int) -> None:
        self.artist = get_object_or_404(Artist, pk=artist_id)

    def __enter__(self):
        return self.ArtistData(
            artist=self.get_artist_data(),
            tracks=self.get_artist_sorted_tracks(),
            albums=self.get_artist_albums(),
            genres=self.get_artist_genres(),
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


    def get_artist_data(self) -> Artist:
        return self.artist

    def get_artists_top_tracks(self) -> List[Track]:
        return list(self.artist.top_tracks.all())

    def get_artist_tracks(self) -> List[Track]:
        return list(self.artist.track_list.all())

    def get_artist_sorted_tracks(self) -> List[Track]:
        top_tracks = self.get_artists_top_tracks()
        all_tracks = self.get_artist_tracks()

        sorted_tracks = top_tracks
        tracks_name = [track.name for track in all_tracks]

        for track in all_tracks:
            if track not in sorted_tracks and track.name not in tracks_name:
                tracks_name.append(track.name)
                sorted_tracks.append(track)

        del tracks_name

        return sorted_tracks

    def get_artist_albums(self) -> List[Album]:
        return list(self.artist.albums.all())

    def get_artist_genres(self) -> List[str]:
        return [genre.name for genre in self.artist.genres.all()]


class GetAlbumDataService:
    @dataclass
    class AlbumData:
        album: Album
        tracks: List[Track]

    def __init__(self, album_id: int) -> None:
        self.album = get_object_or_404(Album, pk=album_id)

    def __enter__(self):
        return self.AlbumData(
            album=self.album,
            tracks=self.get_album_tracks()
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False



    def get_album_data(self) -> Album:
        return self.album

    def get_album_tracks(self) -> List[Track]:
        return list(self.album.tracks.all())


class GetGenreDataService:
    @dataclass
    class GenreData:
        genre: Genre
        artists: List[Artist]

    def __init__(self, genre_name) -> None:
        self.genre = get_object_or_404(Genre, name=genre_name)

    def __enter__(self):
        return self.GenreData(
            genre=self.genre,
            artists=self.get_genre_artists()
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def get_genre_artists(self) -> List[Artist]:
        return list(Artist.objects.filter(genres__in=[self.genre]))

class GetTrackDataService:
    @dataclass
    class TrackData:
        track: Track
        artists: List[Artist]
        albums: List[Album]

    def __init__(self, track_id: int) -> None:
        self.track = get_object_or_404(Track, pk=track_id)

    def __enter__(self):
        return self.TrackData(
            track=self.track,
            artists=list(self.track.artists.all()),
            albums=list(self.track.albums.all())
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @staticmethod
    def get_track_by_sid(sid: str) -> Track | None:
        try:
            return Track.objects.get(spotify_id=sid)
        except Track.DoesNotExist:
            return None


class GetPlaylistDataService:
    @staticmethod
    def get_playlist_by_sid(sid: str) -> Playlist | None:
        try:
            return Playlist.objects.get(spotify_id=sid)
        except Playlist.DoesNotExist:
            return None
