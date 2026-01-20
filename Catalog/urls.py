from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("artist/<int:artist_id>", views.ArtistView.as_view(), name="artist"),
    path("album/<int:album_id>", views.AlbumView.as_view(), name="album"),
    path("genre/<str:genre_name>", views.GenreView.as_view(), name="genre"),
    path("track/<int:track_id>", views.TrackView.as_view(), name="track"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)