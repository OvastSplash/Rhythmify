from django.shortcuts import render
from django.views import View

from User.models import CustomUser

from SpotifyController.services.user_cache import UserCacheService
from SpotifyController.services.database.convert_data import ConvertSpotifyDataBaseService

class ProfileView(View):
    def get(self, request, user_id):
        user:CustomUser = request.user

        context = {
            "user": user,
        }

        #TODO: Добавить создание хэша историю прослушиваний при регистрации, сделать проверку на исключение если пользователь ещё не слушал треки

        #TODO: переделать сохранение хэша рекомендованных треков и топ треков, что бы сохранялись айдишки а не объекты треков, как в user listen history
        #TODO: сделать сохранение обложки трека, а не его автора

        if user.spotify_id:
            user_cache_service = UserCacheService(user.id)


            (user_favorite_short_term_tracks, # List[str]
             user_favorite_medium_term_tracks,
             user_favorite_long_term_tracks) = user_cache_service.get_all_user_favorite_tracks()

            user_favorite_short_term_tracks = ConvertSpotifyDataBaseService.convert_ids_to_tracks(user_favorite_short_term_tracks)
            user_favorite_medium_term_tracks = ConvertSpotifyDataBaseService.convert_ids_to_tracks(user_favorite_medium_term_tracks)
            user_favorite_long_term_tracks = ConvertSpotifyDataBaseService.convert_ids_to_tracks(user_favorite_long_term_tracks)


            user_recommended_tracks = user_cache_service.get_user_recommended_tracks()
            user_recommended_tracks = ConvertSpotifyDataBaseService.convert_ids_to_tracks(user_recommended_tracks)

            user_statistics = user_cache_service.get_user_statistics()

            user_statistics_sorted = None
            if user_statistics:
                user_statistics = ConvertSpotifyDataBaseService.convert_user_statistic(user_statistics)
                # Prepare a pre-sorted list of (month, data) tuples to avoid using dictsortreversed in the template
                # Month key format is "YYYY-M"; we sort by numeric (year, month) descending
                def _ym_key(item):
                    month_str = item[0]
                    try:
                        y_str, m_str = month_str.split("-")
                        return (int(y_str), int(m_str))
                    except Exception:
                        return (0, 0)
                user_statistics_sorted = sorted(user_statistics.items(), key=_ym_key, reverse=True)

            context["user_favorite_short_term_tracks"] = user_favorite_short_term_tracks
            context["user_favorite_medium_term_tracks"] = user_favorite_medium_term_tracks
            context["user_favorite_long_term_tracks"] = user_favorite_long_term_tracks

            context["user_recommended_tracks"] = user_recommended_tracks
            context["user_statistics"] = user_statistics
            context["user_statistics_sorted"] = user_statistics_sorted

            print(user_statistics)

        return render(request, "Profile/profile.html", context)