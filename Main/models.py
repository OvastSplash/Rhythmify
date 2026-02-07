from django.db import models
from SpotifyController.models.models import Track, Artist, Album, Playlist
from User.models import CustomUser

# Create your models here.

class TopTrack(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.track.name

    class Meta:
        unique_together = ('track', 'position')

class TopArtist(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.artist.name

    class Meta:
        unique_together = ('artist', 'position')

class PlayedTodayTrack(models.Model):
    track = models.ForeignKey(verbose_name="Track", to=Track, on_delete=models.CASCADE)
    play_count = models.PositiveIntegerField(verbose_name="Play Count", default=0)
    users = models.ManyToManyField(verbose_name="Users", to=CustomUser, related_name="played_tracks")

    def __str__(self):
        return f"{self.track.name} --- {self.play_count}"

class RecentlyReplayedTrack(models.Model):
    track = models.ForeignKey(verbose_name="Track", to=Track, on_delete=models.CASCADE)
    replayed_count = models.PositiveIntegerField(verbose_name="Replayed Count", default=0)
    user = models.ForeignKey(verbose_name="User", to=CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.track.name} --- {self.user.username}"

class FreshPlaylist(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.playlist.name} --- {self.playlist.user.username}"