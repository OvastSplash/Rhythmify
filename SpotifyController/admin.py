from django.contrib import admin

from SpotifyController.models import (
    Track,
    Artist,
    FavoriteUserTracks,
    Genre,
    RecommendationTracks,
    UsersListenHistory,
)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "spotify_id", "release_date")
    search_fields = ("name", "spotify_id")


admin.site.register(Artist)
admin.site.register(FavoriteUserTracks)
admin.site.register(Genre)
admin.site.register(RecommendationTracks)
admin.site.register(UsersListenHistory)
