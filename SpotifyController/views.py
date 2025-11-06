from django.contrib import messages
from django.views import View
from django.shortcuts import redirect
from .services import SpotifyService
from User.services import UserService

class SpotifyLoginView(View):
    @staticmethod
    def get(request):
        sp_oauth = SpotifyService.oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

class SpotifyCallbackView(View):
    @staticmethod
    def get(request):
        code = request.GET.get('code')
        if not code:
            print("code is none")

        sp_oauth = SpotifyService.oauth()
        token_info = sp_oauth.get_access_token(code)
        access_token, refresh_token, expires_at = SpotifyService.get_tokens(token_info)

        user = request.user
        data, user_updated, error = UserService.spotify_update_user(
            access_token,
            refresh_token,
            expires_at,
            user if user.is_authenticated else None
        )

        if error is not None:
            messages.error(request, error)
            return redirect("login")

        if not user_updated:
            request.session['spotify_user_info'] = data
            return redirect("confirm_register")

        #сделать редирект на страницу пользователя
        return redirect('/')
