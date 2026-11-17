from django.urls import path
from labs import views

app_name = 'labs'

urlpatterns = [
    path('', views.lab_list_view, name='lab_list'),
    path('editor/', views.challenge_editor_view, name='challenge_editor'),
    path('<slug:slug>/', views.lab_interface_view, name='lab_interface'),
]
