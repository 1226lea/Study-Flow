from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
]
