from django.contrib import admin
from .models import CustomUser
from SpotifyController.models import (
    FavoriteUserTracks,
    RecommendationTracks,
    UsersListenHistory,
)


class FavoriteUserTracksInline(admin.TabularInline):
    model = FavoriteUserTracks
    extra = 0
    autocomplete_fields = ("track",)


class RecommendationTracksInline(admin.TabularInline):
    model = RecommendationTracks
    extra = 0
    autocomplete_fields = ("track",)


class UsersListenHistoryInline(admin.TabularInline):
    model = UsersListenHistory
    extra = 0
    autocomplete_fields = ("track",)
    ordering = ("-played_at",)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "user_login", "spotify_id", "is_staff", "is_active")
    search_fields = ("username", "user_login", "spotify_id")
    inlines = (
        FavoriteUserTracksInline,
        RecommendationTracksInline,
        UsersListenHistoryInline,
    )