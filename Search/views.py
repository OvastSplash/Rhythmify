import json
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from Search.services.search import SearchService
from SpotifyController.services.view.collect_user_data import CollectUserDataService
from typing import List

logger = logging.getLogger(__name__)

# Create your views here.
class SearchView(View):
    """
    Search data by name.
    Returns a list of users.
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body) if request.body else {}
            name = data.get("name") or request.POST.get("name")
            logger.info("Searching: name=%s", name)

            logger.error(data)

            if not name:
                logger.error("Empty name")
                return HttpResponse(json.dumps({
                    "data": {
                        "users": [],
                        "artists": [],
                        "tracks": [],
                        "albums": [],
                        "genres": []
                    }
                }), content_type="application/json", status=400)

            search_results = self._search_data(name)
            
            # Pre-fetch artists and albums for tracks to avoid N+1 and get related data
            for track in search_results["tracks"]:
                track.artists_list = list(track.artists.all())
                track.albums_list = list(track.albums.all())

            serialized_data = {
                "users": [
                    {"id": u.id, "name": u.username, "image_url": u.image.url if u.image else None}
                    for u in search_results["users"]
                ],
                "artists": [
                    {"id": a.id, "name": a.name, "image_url": a.image.url if a.image else None}
                    for a in search_results["artists"]
                ],
                "tracks": [
                    {
                        "id": t.id, 
                        "name": t.name, 
                        "image_url": t.image.url if t.image else None,
                        "preview_url": t.preview.url if t.preview else None,
                        "spotify_id": t.spotify_id,
                        "artist_name": t.artists_list[0].name if t.artists_list else "Unknown Artist",
                        "album_id": t.albums_list[0].id if t.albums_list else None
                    }
                    for t in search_results["tracks"]
                ],
                "albums": [
                    {"id": al.id, "name": al.name, "image_url": al.image.url if al.image else None}
                    for al in search_results["albums"]
                ],
                "genres": [
                    {"id": g.id, "name": g.name}
                    for g in search_results["genres"]
                ],
            }

            return HttpResponse(json.dumps({"data": serialized_data}), content_type="application/json")

        except Exception as e:
            logger.exception("Search error: error=%s", e)
            return HttpResponse(json.dumps({"data": {}}), content_type="application/json", status=500)

    def _search_data(self, name: str) -> dict:
        search_service = SearchService(name)
        return search_service.search()

    def get(self, request, name=None, *args, **kwargs):
        try:
            if not name:
                name = request.GET.get("name")

            if not name:
                logger.error("Empty name")
                return HttpResponse("Empty name", status=400)

            logger.info("Searching data: name=%s", name)

            search_results = self._search_data(name)

            user_playlists = []
            if request.user.is_authenticated:
                collect_data = CollectUserDataService(request.user.id)
                user_playlists = collect_data.get_playlists()

            context = {
                "search_results": search_results,
                "query": name,
                "user_playlists": user_playlists,
            }

            return render(request, "Search/search_users.html", context)

        except Exception as e:
            logger.exception("Search error: error=%s", e)
            return HttpResponse(status=500)
