from django.shortcuts import render
from django.views import View
from User.models import CustomUser
from SpotifyController.CacheService import UserCacheService
from SpotifyController.DataAggregatorService import AggregatorService
from SpotifyController.db_services import GetSpotifyInfoFromDatabase

class ProfileView(View):
    def get(self, request, user_id):
        user:CustomUser = request.user

        context = {
            "user": user,
        }

        #TODO: Добавить сюда историю прослушиваний с хэша
        #TODO: Добавить создание хэша историю прослушиваний при регистрации, сделать проверку на исключение если пользователь ещё не слушал треки

        if user.spotify_id:
            user_favorite_tracks = UserCacheService.get_user_favorite_tracks(user.id)
            user_recommended_tracks = UserCacheService.get_user_recommended_tracks(user.id)
            user_statistics = UserCacheService.get_user_statistics(user.id)
            user_statistics_sorted = None
            if user_statistics:
                user_statistics = GetSpotifyInfoFromDatabase.convert_user_statistic(user_statistics)
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

            if not user_recommended_tracks:
                print("user_recommended_tracks is None")
                AggregatorService.update_user_recommendations(user)
                user_recommended_tracks = UserCacheService.get_user_recommended_tracks(user.id)

            if not user_favorite_tracks:
                AggregatorService.update_user_favorite_tracks(user)
                user_favorite_tracks = UserCacheService.get_user_favorite_tracks(user.id)

            context["user_favorite_tracks"] = user_favorite_tracks
            context["user_recommended_tracks"] = user_recommended_tracks
            context["user_statistics"] = user_statistics
            context["user_statistics_sorted"] = user_statistics_sorted

            print(user_statistics)

        return render(request, "Profile/profile.html", context)