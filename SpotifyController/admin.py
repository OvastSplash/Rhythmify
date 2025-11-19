from django.contrib import admin

from SpotifyController.models import Track, Artist, FavoriteUserTracks, Genre, RecommendationTracks

# Register your models here.
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(FavoriteUserTracks)
admin.site.register(Genre)
admin.site.register(RecommendationTracks)

