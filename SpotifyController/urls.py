from django.urls import path
from .views import SpotifyLoginView, SpotifyCallbackView, CreateSpotifyPlaylistView, CreateSpotifyPlaylistTopTracksView
urlpatterns = [
    path('auth/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('create/playlist/', CreateSpotifyPlaylistView.as_view(), name='create_spotify_playlist'),
    path('create/playlist/top_tracks', CreateSpotifyPlaylistTopTracksView.as_view(), name='create_spotify_playlist_top_tracks')
]