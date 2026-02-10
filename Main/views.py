from django.shortcuts import render
from django.views import View

from Main.services.cache import MainCache
from Main.services.database.repositories import fresh_playlist, played_today_track, top_artists, top_tracks
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService
from SpotifyController.services.user_cache import UserCacheService


# Create your views here.
class MainView(View):
    cache_service = MainCache()

    top_artists_register = top_artists.TopArtistsRegister()
    top_tracks_register = top_tracks.TopTrackRegister()
    fresh_playlist_register = fresh_playlist.FreshPlaylistRegister()
    played_today_track_register = played_today_track.PlayedTodayTrackRegister()

    user_cache = UserCacheService(user_id=5)

    @property
    def _top_tracks(self):
        tracks_ids = self.cache_service.get_top_tracks()
        return ConvertSpotifyDataBaseService.convert_ids_to_tracks(tracks_ids)

    @property
    def _top_artists(self):
        artists_ids = self.cache_service.get_top_artists()
        return ConvertSpotifyDataBaseService.convert_ids_to_artists(artists_ids)

    @property
    def _fresh_playlist(self):
        playlists_ids = self.cache_service.get_fresh_playlists()
        return ConvertSpotifyDataBaseService.convert_ids_to_playlists(playlists_ids)

    @property
    def _most_played_today(self):
        return self.played_today_track_register.get_most_played_tracks()

    @property
    def _user_playlists(self):
        playlists_ids = self.user_cache.get_user_playlists()
        return ConvertSpotifyDataBaseService.convert_ids_to_playlists(playlists_ids)

    def get(self, request, *args, **kwargs):
        context = {
            "top_tracks": self._top_tracks,
            "top_artists": self._top_artists,
            "fresh_playlists": self._fresh_playlist,
            "most_played_today": self._most_played_today,
            "user_playlists": self._user_playlists,
        }

        return render(request, "Main/main.html", context)