from django.contrib import admin

from SpotifyController.models.models import (
    Track,
    Artist,
    Genre, Album, Playlist,
)
from SpotifyController.models.through import FavoriteUserTracks, RecommendationTracks, UsersListenHistory


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "spotify_id")
    search_fields = ("name", "spotify_id")


admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(FavoriteUserTracks)
admin.site.register(Genre)
admin.site.register(RecommendationTracks)
admin.site.register(UsersListenHistory)
admin.site.register(Playlist)