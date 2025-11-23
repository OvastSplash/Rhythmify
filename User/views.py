from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, RegisterForm, ConfirmRegisterForm
from django.contrib.auth import authenticate, login
from SpotifyController.services import SpotifyService
from SpotifyController.DataAggregatorService import AggregatorService

class LoginView(View):
    form = LoginForm

    def get(self, request):
        return render(request, "User/login.html", {"form": self.form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            user_login = form.cleaned_data.get('user_login')
            password = form.cleaned_data.get('password')

            user = authenticate(user_login=user_login, password=password)

            if user and user.is_active:
                login(request, user)
                print(f"User {user_login} logged in {user.id} type {type(user.id)}")
                return redirect("profile", user_id = user.id)

        return render(request, "User/login.html", {"form": form})

class RegisterView(View):
    form = RegisterForm

    def get(self, request):
        return render(request, "User/registration.html", {"form": self.form})

    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            return redirect("profile", user_id = user.id)

        return render(request, "User/registration.html", {"form": self.form})

class ConfirmRegisterView(View):
    form = ConfirmRegisterForm

    def get(self, request):
        spotify_data = request.session.get("spotify_user_info")
        if not spotify_data:
            return redirect("login")

        name, spotify_id, spotify_url, followers, image = SpotifyService.get_user_info(data=spotify_data)

        context = {
            "form": self.form,
            "name": name,
            "image": image,
        }

        return render(request, "User/confirm_register.html", context)

    def post(self, request):
        spotify_data = request.session.get("spotify_user_info")
        form = ConfirmRegisterForm(request.POST)

        if form.is_valid() and spotify_data:
            user = form.save_with_spotify_data(data=spotify_data)

            login(request, user)
            del request.session["spotify_user_info"]

            AggregatorService.update_user_favorite_tracks(users=user, clear_cache=False)
            AggregatorService.update_user_recommendations(users=user, clear_cache=False)

            return redirect("profile", user_id = user.id)

        return render(request, "User/confirm_register.html", {"form": self.form})