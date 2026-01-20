from django.db import models
from SpotifyController.models.models import Track, Artist, Album, Playlist
# Create your models here.

class TopTracks(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.track.name

    class Meta:
        unique_together = ('track', 'position')

class TopArtists(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.artist.name

    class Meta:
        unique_together = ('artist', 'position')

class TopAlbums(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.album.name

    class Meta:
        unique_together = ('album', 'position')

class RecommendationPlaylist(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    def __str__(self):
        return self.playlist.name