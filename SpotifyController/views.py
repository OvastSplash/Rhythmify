from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect
from SpotifyController.services.spotify_auth import AuthService
from User.services import UserService
from SpotifyController.services.client_services import UserClient

class SpotifyLoginView(View):
    @staticmethod
    def get(request):
        sp_oauth = AuthService.oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

class SpotifyCallbackView(View):
    @staticmethod
    def get(request):
        code = request.GET.get('code')

        sp_oauth = AuthService.oauth()
        token_info = sp_oauth.get_access_token(code)
        access_token, refresh_token, expires_at = AuthService.get_tokens(token_info)

        user = request.user
        user_logged_in = user if user.is_authenticated else None

        result = UserService.spotify_update_user(
            access_token,
            refresh_token,
            expires_at,
            user_logged_in
        )

        if result.error:
            messages.error(request, result.error)
            return redirect("login")

        if not result.is_existing and result.data:
            request.session['spotify_user_info'] = result.data
            return redirect("confirm_register")

        if not user_logged_in:
            login(request, result.user)
            print(f"user {result.user.user_login} is logged in")

        print(result.user.id)

        return redirect('profile', user_id = result.user.id)

class CreateSpotifyPlaylistView(View):
    @staticmethod
    def post(request):
        user = request.user
        sp_client = UserClient(user=user)
        sp_client.create_user_recommendation_playlist(user)
        return HttpResponse(status=200)