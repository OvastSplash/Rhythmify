from typing import List, Dict
from collections import defaultdict

from Rhythmify.settings import STATIC_URL
from SpotifyController.models.models import Track, Artist, Playlist


class ConvertSpotifyDataBaseService:
    @staticmethod
    def convert_tracks_to_ids(tracks: List[Track]) -> List[str]:
        return [track.spotify_id for track in tracks]

    @staticmethod
    def convert_ids_to_tracks(spotify_ids: List[str]) -> List[Track]:
        tracks = {track.spotify_id: track for track in Track.objects.filter(spotify_id__in=spotify_ids)}
        return [tracks[spotify_id] for spotify_id in spotify_ids if spotify_id in tracks]

    @staticmethod
    def convert_ids_to_playlists(spotify_ids: List[str]) -> List[Playlist]:
        return [Playlist.objects.filter(spotify_id=spotify_id).first() for spotify_id in spotify_ids]

    @staticmethod
    def convert_user_statistic(user_statistic_data: Dict):
        converted_user_statistic = defaultdict(
            lambda: {
                "total_listen_ms": 0,
                "total_tracks_count": 0,
                "tracks": [],
                "artists": [],
                "genres": []
            }
        )

        last_date_str = None
        total_listen_ms: int = 0
        total_tracks_count = 0

        for track_data in user_statistic_data["tracks"]:
            date = track_data['month_year']

            if last_date_str and date != last_date_str:
                converted_user_statistic[last_date_str]['total_listen_ms'] = total_listen_ms
                converted_user_statistic[last_date_str]['total_tracks_count'] = total_tracks_count
                total_listen_ms = 0
                total_tracks_count = 0

            last_date_str = date

            spotify_id = track_data["track__spotify_id"]
            most_popular_period = track_data["most_popular_period"]

            played_count = track_data["play_count"]
            total_tracks_count += int(played_count)

            listen_ms = track_data["total_listen_ms"]
            total_listen_ms += int(listen_ms)

            track = Track.objects.get(spotify_id=spotify_id)
            converted_user_statistic[date]["tracks"].append({
                "track": track,
                "count": played_count,
                "period": most_popular_period,
                'listen_ms': listen_ms
            })

        # Set total_listen_ms and total_tracks_count for the last month
        if last_date_str:
            converted_user_statistic[last_date_str]['total_listen_ms'] = total_listen_ms
            converted_user_statistic[last_date_str]['total_tracks_count'] = total_tracks_count

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