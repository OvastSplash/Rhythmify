from django.shortcuts import render
from django.views import View
from User.models import CustomUser
from SpotifyController.client_services import SpotifyClientService
from django.shortcuts import redirect

class ProfileView(View):
    def get(self, request, user_id):
        user:CustomUser = request.user
        if user.spotify_id:
            spotify_service = SpotifyClientService(user.access_token, request.user)
            top_tracks = spotify_service.get_user_top_tracks(commit=True)

            for track in top_tracks:
                print(f"Track: {track.name} --- Artists: {track.artists.all()[0].name}")

        return render(request, "Profile/profile.html")