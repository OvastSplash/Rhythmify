from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, user_login, password=None, **extra_fields):
        if not user_login:
            raise ValueError('Users must have an username')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(user_login=user_login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(user_login, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    user_login = models.CharField(verbose_name="Login", max_length=255, unique=True, null=False, blank=False)
    username = models.CharField(verbose_name="username", max_length=255, null=False, blank=False)
    user_image = models.ImageField(verbose_name="User Image", upload_to='users/%Y/%m', null=True, blank=True)
    spotify_id = models.CharField(verbose_name="Spotify ID", max_length=255, null=True, blank=True)
    followers = models.IntegerField(verbose_name="Followers", default=0, blank=True)
    spotify_url = models.URLField(verbose_name="Spotify Link", null=True, blank=True)
    access_token = models.CharField(verbose_name="Access Token", max_length=255, null=True, blank=True)
    refresh_token = models.CharField(verbose_name="Refresh Token", max_length=255, null=True, blank=True)
    token_expires_at = models.DateTimeField(verbose_name="Token Expires", null=True, blank=True)
    top_tracks_cache = models.JSONField(verbose_name="Top Tracks Cache", null=True, blank=True)

    is_active = models.BooleanField(verbose_name="Is Active", default=True)
    is_staff = models.BooleanField(verbose_name="Is Staff", default=False)
    is_superuser = models.BooleanField(verbose_name="Is Superuser", default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser