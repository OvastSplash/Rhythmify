from .models import Artist, Track, FavoriteUserTracks
from User.models import CustomUser
from .client_services import SpotifyClientService
from User.services import UserService
from datetime import datetime

class SpotifyDatabaseService:
    def __init__(self, tracks_data, user:CustomUser, spotify_client:SpotifyClientService):
        self.tracks_data = tracks_data
        self.user = user
        self.spotify_client = spotify_client

    def get_artist_image_url(self, artist_id):
        try:
            artist_data = self.spotify_client.get_artist_info(artist_id)
            print(artist_data)
            artist_image_url = artist_data.get('images')[0].get('url')
            return artist_image_url

        except:
            return None

    def create_artist(self, artist_data):
        if artist_data:
            artist_id = artist_data.get("id")

            artist = Artist.objects.filter(spotify_id=artist_id).first()
            if artist:
                return artist

            artist = Artist()
            artist.name = artist_data.get('name')
            artist.spotify_id = artist_id

            image_url = self.get_artist_image_url(artist_id)
            artist.image = UserService.update_object_image(artist, image_url, save=False) if image_url else None

            artist.spotify_url = artist_data.get('external_urls').get('spotify')
            return artist

        return None

    def add_track_to_db(self):
        tracks = []
        for track in self.tracks_data:
            track_id = track.get('id')
            track_exists = Track.objects.filter(spotify_id=track_id).first()

            if track_exists:
                if not FavoriteUserTracks.objects.filter(track=track_exists, user=self.user).exists():
                    FavoriteUserTracks.objects.create(
                        track=track_exists,
                        user=self.user,
                    )

                tracks.append(track_exists)
                continue

            artists = [self.create_artist(artist) for artist in track.get("artists", [])]

            new_track = Track()
            new_track.name = track.get("name")
            new_track.url = track.get("external_urls").get("spotify")
            new_track.spotify_id = track_id

            release_date_str = track.get("album").get("release_date")
            new_track.release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            new_track.save()

            if artists:
                for artist in artists:
                    artist.save()
                    print(artist.name)
                    artist.track_list.add(new_track)

            FavoriteUserTracks.objects.create(
                track=new_track,
                user=self.user,
            )

            tracks.append(new_track)

        return tracks