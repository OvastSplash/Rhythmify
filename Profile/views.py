from django.shortcuts import render
from django.views import View
from User.models import CustomUser
from SpotifyController.client_services import SpotifyClientService
from SpotifyController.db_services import SpotifyDatabaseService
from typing import List

class ProfileView(View):
    def get(self, request, user_id):
        user:CustomUser = request.user
        
        if user.spotify_id:
            if user.top_tracks.exists():
                user_favorite_tracks = user.top_tracks.all()

            else:
                spotify_service = SpotifyClientService(user.access_token)
                constructed_data = spotify_service.get_user_top_tracks()
                user_favorite_tracks = SpotifyDatabaseService.create_track(constructed_data)
                SpotifyDatabaseService.save_tracks_to_user_favorite_list(user_favorite_tracks, user)

            for track in user_favorite_tracks:
                print(f"Track: {track.name} --- Artists: {', '.join(artist.name for artist in track.artists.all())}")

        return render(request, "Profile/profile.html")