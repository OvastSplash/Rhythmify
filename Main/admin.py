from django.contrib import admin

from Main.models import TopTrack, TopArtist, RecentlyReplayedTrack, PlayedTodayTrack

# Register your models here.
admin.site.register(TopTrack)
admin.site.register(TopArtist)
admin.site.register(PlayedTodayTrack)
admin.site.register(RecentlyReplayedTrack)