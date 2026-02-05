from django.shortcuts import render, get_object_or_404
from django.views import View
import logging
import json

from django.shortcuts import HttpResponse

from SpotifyController.services.client_services import UserClient
from SpotifyController.services.database.check_data import CheckDataService
from User.models import CustomUser

from SpotifyController.services.view.collect_user_data import CollectUserDataService

logger = logging.getLogger("SpotifyController")

class ProfileView(View):
    def get(self, request, user_id):
        user: CustomUser = get_object_or_404(CustomUser, pk=user_id)

        context = {
            "user": user,
        }

        #TODO: Добавить создание хэша историю прослушиваний при регистрации, сделать проверку на исключение если пользователь ещё не слушал треки
        #TODO: Отдельно потом добавить юзера который зашел на страничку другого пользователя через request, что бы плейлисты были правильные

        if user.spotify_id:
            collect_data = CollectUserDataService(user.id)

            (user_favorite_short_term_tracks, # List[str]
             user_favorite_medium_term_tracks,
             user_favorite_long_term_tracks) = collect_data.get_favorite_tracks()

            user_playlists = collect_data.get_playlists()

            user_recommended_tracks = collect_data.get_recommended_tracks()

            (user_statistics,
             user_statistics_sorted) = collect_data.get_statistics()

            context["user_favorite_short_term_tracks"] = user_favorite_short_term_tracks
            context["user_favorite_medium_term_tracks"] = user_favorite_medium_term_tracks
            context["user_favorite_long_term_tracks"] = user_favorite_long_term_tracks

            context["user_playlists"] = user_playlists

            context["user_recommended_tracks"] = user_recommended_tracks
            context["user_statistics"] = user_statistics
            context["user_statistics_sorted"] = user_statistics_sorted

            logger.info("User statistics loaded: has_stats=%s", bool(user_statistics))
            logger.info("User playlists loaded: has_stats=%s", bool(user_playlists))

        return render(request, "Profile/profile.html", context)


class AddTrackToPlaylistView(View):
    def post(self, request, *args, **kwargs):
        """Add/Remove track to/from playlist(s)."""
        try:
            data = json.loads(request.body)
            track_id = data.get("track_id")
            
            # For backward compatibility and mixed use
            playlists_ids = data.get("add_to", [])

            # Compatibility with old single 'playlist_id' or 'playlist_ids' (default to add)
            if not playlists_ids:
                playlist_ids = data.get("playlist_ids", [])
                if not playlist_ids:
                    playlist_id = data.get("playlist_id")
                    if playlist_id:
                        playlist_ids = [playlist_id]
                playlists_ids = playlist_ids

            logger.info("Track playlist update: track_id=%s playlists=%s", track_id, playlists_ids)

            if not track_id:
                return HttpResponse("Missing track_id", status=400)
            
            user = request.user
            if not user.is_authenticated:
                return HttpResponse("Unauthorized", status=401)

            user_client = UserClient(user)
            
            for pid in playlists_ids:
                user_client.sync_track_to_playlist(pid, track_id)

            return HttpResponse(json.dumps({"status": "success"}), content_type="application/json")

        except Exception as e:
            logger.exception("Track playlist update error: %s", e)
            return HttpResponse(status=500)

