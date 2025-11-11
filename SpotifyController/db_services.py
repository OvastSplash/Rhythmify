from .models import Artist, Track, FavoriteUserTracks
from .spotify_data_service import Artist as ArtistClass
from .spotify_data_service import Track as TrackClass
from typing import List
from User.models import CustomUser
from User.services import UserService

class SpotifyDatabaseService:
    @staticmethod
    def create_artist(artist_data: ArtistClass) -> Artist:
        artist, _ = Artist.objects.get_or_create(
            name=artist_data.name,
            defaults={
                'spotify_id': artist_data.spotify_id,
                'spotify_url': artist_data.spotify_url,
            }
        )
        image_exists = bool(artist.image)
        artist_current_image_name = artist.image.url.split('/')[-1].replace('.jpg', "") if image_exists else None
        new_image_name = artist_data.image_url.split('/')[-1] if artist_data.image_url else None

        if not image_exists or artist_current_image_name != new_image_name:
            artist.image = UserService.update_object_image(
                artist,
                artist_data.image_url,
            ) if artist_data.image_url else None

            print(f"Image was created or updated for {artist.name} --- Image Name: {artist.image}")

        return artist

    @staticmethod
    def create_track(constructed_tracks: List[TrackClass]) -> List[Track]:
        tracks: List[Track] = []
        for track in constructed_tracks:

            new_track, created = Track.objects.get_or_create(
                name=track.name,
                defaults={
                    'url': track.url,
                    'spotify_id': track.spotify_id,
                    'release_date': track.release_date
                }
            )

            if track.artists:
                artists: List[Artist] = [SpotifyDatabaseService.create_artist(artist) for artist in track.artists]

                if artists:
                    for artist in artists:
                        artist.track_list.add(new_track)

            tracks.append(new_track)

        return tracks

    @staticmethod
    def save_tracks_to_user_favorite_list(tracks: List[Track], user: CustomUser) -> List[Track]:
        for track in tracks:
            FavoriteUserTracks.objects.create(
                track=track,
                user=user,
            )