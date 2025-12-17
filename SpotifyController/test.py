import os
import sys


# 1) Добавляем корень проекта в PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 2) Указываем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Rhythmify.settings")

# 3) Инициализируем Django
import django
django.setup()

# 4) Теперь можно импортировать модели и сервисы
from SpotifyController.services.client_services import PublicClient, UserClient
from SpotifyController.models.models import Track
from Deezer.services import ClientService
from User.models import CustomUser

def update_all_track_datas():
    tracks = Track.objects.all()[:50]
    deezer_client = ClientService()

    for track in tracks[:5]:
        public_client = PublicClient()
        track_data = public_client.get_track_info(track.spotify_id)
        preview_url = deezer_client.get_preview_by_track(track)
        print(preview_url)
        # print(finder.get("results")[0]["previewUrl"])
        # UserService.update_object_image(track, track_data.image_url)

def test():
    user = CustomUser.objects.filter(id=14).first()
    client = UserClient(user=user)
    client.get_user_data()
    print(client.get_user_short_term_top_tracks(limit=20))

update_all_track_datas()
