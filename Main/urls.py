from django.urls import path
from Main import views

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
]