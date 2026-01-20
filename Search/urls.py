from django.urls import path
from Search import views

urlpatterns = [
    path("<str:name>", views.SearchView.as_view(), name="search_user"),
    path("", views.SearchView.as_view(), name="search_user_post"),
]