from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from SpotifyController.services.database.post_save.album import PostSaveAlbum
from SpotifyController.services.database.post_save.artist import ArtistPostSave


class Track(models.Model):
    name = models.CharField(verbose_name="Track Name", max_length=200, null=False)
    url = models.URLField(verbose_name="Track Url", max_length=250, null=False)
    spotify_id = models.CharField(verbose_name="Spotify id", max_length=100, unique=True, null=False)
    duration_ms = models.IntegerField(verbose_name="Duration in ms", null=True)

    image = models.ImageField(verbose_name="Track Image", upload_to='tracks/', null=True)
    preview = models.FileField(verbose_name="Preview Mp3", upload_to="previews/", max_length=250, null=True)

    def save_preview(self, review_mp3):
        filename = f"{self.spotify_id}.mp3"
        self.preview.save(
            filename,
            ContentFile(review_mp3),
            save=True
        )

        return self.preview.url


    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(verbose_name="Genre Name", max_length=200, null=False, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(verbose_name="Album Name", max_length=200, null=False)
    image = models.ImageField(verbose_name="Album Image", upload_to='albums/', null=True)
    spotify_id = models.CharField(verbose_name="Spotify id", max_length=100, unique=True, null=False)
    spotify_url = models.URLField(verbose_name="Album Url", max_length=250, null=True)

    total_tracks = models.IntegerField(verbose_name="Total Tracks", default=0)
    release_date = models.DateField(verbose_name="Release Date", null=True)
    type = models.CharField(verbose_name="Album Type", max_length=200, null=True)

    tracks = models.ManyToManyField(Track, verbose_name="Tracks", related_name="albums", blank=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Album)
def post_save_album(sender, instance, created, **kwargs):
    if created:
        post_save_service = PostSaveAlbum(instance)
        post_save_service.handle()

#TODO: при создании добавить автосоздание странички артиста, топ треки, альбомы
#TODO: добавить модель альбома в котором храняться треки
class Artist(models.Model):
    name = models.CharField(verbose_name="Name", max_length=200, null=False)
    image = models.ImageField(verbose_name="Image", upload_to='artists/', null=True)
    spotify_id = models.CharField(verbose_name="Spotify id", max_length=100, unique=True, null=False)
    spotify_url = models.URLField(verbose_name="Artist Url", max_length=250, null=False)
    followers = models.IntegerField(verbose_name="Flowers", default=0)

    genres = models.ManyToManyField(Genre, verbose_name="Genres", related_name="artists", default=None)

    track_list = models.ManyToManyField(Track, verbose_name="Track List", related_name="artists", blank=True)
    top_tracks = models.ManyToManyField(Track, verbose_name="Top Tracks", related_name="top_artist_tracks", blank=True)
    albums = models.ManyToManyField(Album, verbose_name="Albums", related_name="artists", blank=True)


    def __str__(self):
        return self.name

@receiver(post_save, sender=Artist)
def post_save_artist(sender, instance, created, **kwargs):
    if created:
        post_save_service = ArtistPostSave(instance)

        post_save_service.handle_top_tracks()
        post_save_service.handle_albums()