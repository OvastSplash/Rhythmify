from django.urls import path
from .views import SpotifyLoginView, SpotifyCallbackView
urlpatterns = [
    path('auth/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback', SpotifyCallbackView.as_view(), name='spotify_callback'),
]