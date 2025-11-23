from django.shortcuts import render
from django.views import View
from User.models import CustomUser
from SpotifyController.CacheService import UserCacheService
from SpotifyController.DataAggregatorService import AggregatorService

class ProfileView(View):
    def get(self, request, user_id):
        user:CustomUser = request.user

        if user.spotify_id:
            user_favorite_tracks = UserCacheService.get_user_favorite_tracks(user.id)
            user_recommended_tracks = UserCacheService.get_user_recommended_tracks(user.id)

            if user_recommended_tracks is None:
                AggregatorService.update_user_recommendations(user)
                user_recommended_tracks = UserCacheService.get_user_recommended_tracks(user.id)

            if user_favorite_tracks is None:
                AggregatorService.update_user_favorite_tracks(user)
                user_favorite_tracks = UserCacheService.get_user_favorite_tracks(user.id)

            context = {
                "user_favorite_tracks": user_favorite_tracks,
                "user_recommended_tracks": user_recommended_tracks,
                "user": user,
            }

            return render(request, "Profile/profile.html", context)

        return render(request, "Profile/profile.html")