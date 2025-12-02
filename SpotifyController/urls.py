from django.urls import path
from .views import SpotifyLoginView, SpotifyCallbackView, CreateSpotifyPlaylistView
urlpatterns = [
    path('auth/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('create_playlist', CreateSpotifyPlaylistView.as_view(), name='create_spotify_playlist'),
]