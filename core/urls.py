from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),

    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register_view, name='register'),
    path('upload/', views.upload_resource, name='upload_resource'),
    path('profile/', views.profile_view, name='profile'),
    path('resource/<int:resource_id>/save/', views.toggle_save_resource, name='toggle_save_resource'),
    path('resource/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
    path('resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
]
