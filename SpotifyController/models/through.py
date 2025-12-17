from django.db import models
from SpotifyController.models.models import (Track, Album, Artist)
from User.models import CustomUser

class FavoriteUserTracks(models.Model):
    TERM_CHOICES = [
        ('short_term', 'Short Term'),
        ('medium_term', 'Medium Term'),
        ('long_term', 'Long Term'),
    ]

    track = models.ForeignKey(Track, verbose_name="Track", related_name="favorite", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name="User",  related_name="favorite_tracks_links", on_delete=models.CASCADE)

    term = models.CharField(verbose_name="Term", max_length=15, choices=TERM_CHOICES, default='short_term')
    add_time = models.DateTimeField(verbose_name="Add Time", auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.track.name}"


class RecommendationTracks(models.Model):
    track = models.ForeignKey(Track, verbose_name="Track", related_name="recommendations", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name="User", related_name="recommendations_links", on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name="Add Time", auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.track.name}"


class UsersListenHistory(models.Model):
    track = models.ForeignKey(Track, verbose_name="Track", related_name="listen_history", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, verbose_name="User", related_name="listen_history_links", on_delete=models.CASCADE)
    played_at = models.DateTimeField(verbose_name="Played At")

    def __str__(self):
        return f"{self.user.username} - {self.track.name}"
