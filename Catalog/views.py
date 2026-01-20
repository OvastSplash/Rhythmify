from django.shortcuts import render
from django.views import View
from SpotifyController.services.database.get_spotify_data import GetGenreDataService, GetAlbumDataService, GetArtistDataService, GetTrackDataService
from SpotifyController.services.view.collect_user_data import CollectUserDataService

# Create your views here.
class TrackView(View):
    def get(self, request, track_id):
        with GetTrackDataService(track_id) as track_data:
            user_playlists = []
            if request.user.is_authenticated:
                collect_data = CollectUserDataService(request.user.id)
                user_playlists = collect_data.get_playlists()

            context = {
                "track": track_data,
                "user_playlists": user_playlists,
            }
            return render(request, "Catalog/track.html", context)


class ArtistView(View):
    def get(self, request, artist_id):
        with GetArtistDataService(artist_id) as artist_data:
            user_playlists = []
            if request.user.is_authenticated:
                collect_data = CollectUserDataService(request.user.id)
                user_playlists = collect_data.get_playlists()

            context = {
                "artist": artist_data,
                "user_playlists": user_playlists,
            }
            return render(request, "Catalog/artist.html", context)


class AlbumView(View):
    def get(self, request, album_id):
        with GetAlbumDataService(album_id) as album_data:
            user_playlists = []
            if request.user.is_authenticated:
                collect_data = CollectUserDataService(request.user.id)
                user_playlists = collect_data.get_playlists()

            context = {
                "album": album_data,
                "user_playlists": user_playlists,
            }
            return render(request, "Catalog/album.html", context)

class GenreView(View):
    def get(self, request, genre_name):
        with GetGenreDataService(genre_name) as genre_data:
            return render(request, "Catalog/genre.html", {"genre": genre_data})