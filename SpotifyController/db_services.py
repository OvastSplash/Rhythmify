from .models import Artist, Track, FavoriteUserTracks, Genre, RecommendationTracks
from .spotify_data_service import ArtistClass, TrackClass, GenreClass
from typing import List, Type
from User.models import CustomUser
from User.services import UserService
from .spotify_data_service import CheckSpotifyDataService
from django.db.models import Count, Model

class SpotifyDatabaseService:
    @staticmethod
    def get_or_create_genre(genre: GenreClass) -> Genre:
        genre, _ = Genre.objects.get_or_create(name=genre)
        return genre

    @staticmethod
    def create_or_update_artist(artist_data: ArtistClass) -> Artist:
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data.spotify_id,
            defaults={
                'name': artist_data.name,
                'spotify_url': artist_data.spotify_url,
            }
        )

        new_genres = [
            SpotifyDatabaseService.get_or_create_genre(genre)
            for genre in artist_data.genres
            if genre
        ]

        if set(artist.genres.all()) != set(new_genres):
            artist.genres.set(new_genres)
            print(f"New genre was created for {artist.name} --- {', '.join(genre.name for genre in artist.genres.all())}")

        updated = False

        if not created and artist.name != artist_data.name:
            print(f"Artist name {artist.name} changed to {artist_data.name}")
            artist.name = artist_data.name
            updated = True

        if artist_data.image_url and CheckSpotifyDataService.artist_image_update(artist, artist_data.image_url):
            artist.image = UserService.update_object_image(
                artist,
                artist_data.image_url,
                save=False
            ) if artist_data.image_url else None

            updated = True
            print(f"Image was created or updated for {artist.name} --- Image Name: {artist.image}")

        if updated:
            artist.save()

        return artist

    @staticmethod
    def create_track(constructed_tracks: List[TrackClass]) -> List[Track]:
        tracks: List[Track] = []
        for track in constructed_tracks:

            new_track, created = Track.objects.get_or_create(
                name=track.name,
                defaults={
                    'url': track.url,
                    'spotify_id': track.spotify_id,
                    'release_date': track.release_date
                }
            )

            if track.artists:
                artists: List[Artist] = [SpotifyDatabaseService.create_or_update_artist(artist) for artist in track.artists]

                if artists:
                    for artist in artists:
                        artist.track_list.add(new_track)

            tracks.append(new_track)

        return tracks

    @staticmethod
    def save_tracks_to_user_list(model: Type[Model], tracks: List[Track], user: CustomUser):
        tracks_ids: List[str] = [track.spotify_id for track in tracks]
        print(tracks_ids)
        to_delete = model.objects.exclude(track__spotify_id__in=tracks_ids, user=user)
        existing_ids = list(to_delete.values_list("track__spotify_id", flat=True))
        to_delete.delete()
        existing_ids = set(existing_ids)

        tracks = [track for track in tracks if track.spotify_id not in existing_ids]
        recommended_objects: List[model] = [model(track=track, user=user) for track in tracks]
        model.objects.bulk_create(recommended_objects)


class GetSpotifyInfoFromDatabase:
    @staticmethod
    def get_user_top_tracks(user: CustomUser, count: int = 5) -> List[Track]:
        return list(
            Track.objects
            .filter(favorite_users__user=user)
            .prefetch_related("favorite_users", "artists")
        )[:count]

    @staticmethod
    def get_user_top_artists(user: CustomUser, count: int = 5) -> List[Artist]:
        return list(
            Artist.objects
            .filter(track_list__favorite_users__user=user)
            .annotate(user_count=Count('spotify_id'))
            .order_by("-user_count")
        )[:count]

    @staticmethod
    def get_user_top_genres(user: CustomUser, count: int = 5) -> List[str]:
        return list(
            Genre.objects
            .filter(artists__track_list__favorite_users__user=user)
            .annotate(artist_count=Count('artists'))
            .order_by("-artist_count")
            .values_list("name", flat=True)
        )[:count]

    @staticmethod
    def get_user_recommend_tracks(user: CustomUser) -> List[Track]:
        return list(
            Track.objects
            .filter(recommendations__user=user)
        )