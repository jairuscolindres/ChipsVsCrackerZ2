from django.urls import path
from .views import home_view, logout_view, leaderboard_view

app_name = "home"
urlpatterns = [
    path("", home_view, name="home"),
    path("leaderboard/", leaderboard_view, name="leaderboard"),
    path("logout/", logout_view, name="logout"),
]
