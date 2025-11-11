from django.db import models
from User.models import CustomUser

class Track(models.Model):
    name = models.CharField(verbose_name="Track Name", max_length=200, null=False)
    url = models.URLField(verbose_name="Track Url", max_length=250, null=False)
    release_date = models.DateField(verbose_name="Release Date", null=False)
    spotify_id = models.CharField(verbose_name="Spotify id", max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(verbose_name="Name", max_length=200, null=False)
    image = models.ImageField(verbose_name="Image", upload_to='artists/', null=True)
    spotify_id = models.CharField(verbose_name="Spotify id", max_length=100, unique=True, null=False)
    spotify_url = models.URLField(verbose_name="Artist Url", max_length=250, null=False)
    track_list = models.ManyToManyField(Track, verbose_name="Track List", related_name="artists", blank=True)

    def __str__(self):
        return self.name

class FavoriteUserTracks(models.Model):
    track = models.ForeignKey(Track, verbose_name="Track", related_name="favorite_users", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name="User",  related_name="favorite_tracks_links", on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name="Add Time", auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.track.name}"