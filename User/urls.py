from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register", views.RegisterView.as_view(), name="register"),
    path("confirm_register", views.ConfirmRegisterView.as_view(), name="confirm_register"),

    path('', lambda request: redirect('login')),
]