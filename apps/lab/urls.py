from django.urls import path
from .views import dev_lab_view

app_name = "lab"

urlpatterns = [
    # Secret dev-only endpoints — remove or gate behind admin before shipping
    path("dev/", dev_lab_view, name="dev_lab"),
    path("dev/<slug:lab_slug>/", dev_lab_view, name="dev_lab_slug"),
]
