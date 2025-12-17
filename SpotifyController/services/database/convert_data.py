from typing import List, Dict
from collections import defaultdict
from SpotifyController.models.models import Track, Artist

class ConvertSpotifyDataBaseService:
    @staticmethod
    def convert_tracks_to_ids(tracks: List[Track]) -> List[str]:
        return [track.spotify_id for track in tracks]

    @staticmethod
    def convert_ids_to_tracks(spotify_ids: List[str]) -> List[Track]:
        tracks = {track.spotify_id: track for track in Track.objects.filter(spotify_id__in=spotify_ids)}
        return [tracks[spotify_id] for spotify_id in spotify_ids if spotify_id in tracks]

    @staticmethod
    def convert_user_statistic(user_statistic_data: Dict):
        converted_user_statistic = defaultdict(lambda: {"tracks": [], "artists": [], "genres": []})

        for track_data in user_statistic_data["tracks"]:
            date = track_data['month_year']
            spotify_id = track_data["track__spotify_id"]
            played_count = track_data["play_count"]
            most_popular_period = track_data["most_popular_period"]

            track = Track.objects.get(spotify_id=spotify_id)
            converted_user_statistic[date]["tracks"].append({
                "track": track,
                "count": played_count,
                "period": most_popular_period
            })

        for artist_data in user_statistic_data["artists"]:
            spotify_id = artist_data["track__artists__spotify_id"]
            arist_in_count = artist_data["artists_count"]
            most_popular_period = artist_data["most_popular_period"]

            artist = Artist.objects.get(spotify_id=spotify_id)

            date = artist_data['month_year']

            converted_user_statistic[date]["artists"].append({
                "artist": artist,
                "count": arist_in_count,
                "period": most_popular_period
            })

        for genre_data in user_statistic_data["genres"]:
            date = genre_data['month_year']
            genre = genre_data['track__artists__genres__name']
            genre_in_count = genre_data['genres_count']
            most_popular_period = genre_data["most_popular_period"]

            converted_user_statistic[date]["genres"].append({
                "genre": genre,
                "count": genre_in_count,
                "period": most_popular_period
            })

        return converted_user_statistic