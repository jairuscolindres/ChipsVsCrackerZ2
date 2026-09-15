from django.urls import path
from .views import login_view

app_name = "login"

url_patterns = [
        path("", login_view, name="login"),
        ]
