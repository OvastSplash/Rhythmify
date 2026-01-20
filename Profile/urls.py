from django.urls import path

import Search.views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("<int:user_id>", views.ProfileView.as_view(), name="profile"),
    path("add_track/", views.AddTrackToPlaylistView.as_view(), name="add_track_to_playlist"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)