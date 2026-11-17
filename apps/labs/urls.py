from django.urls import path
from labs import views

app_name = 'labs'

urlpatterns = [
    path('', views.lab_list_view, name='lab_list'),
    path('<slug:slug>/', views.lab_interface_view, name='lab_interface'),
]
