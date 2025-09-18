from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .simple_views import simple_register, simple_login

app_name = 'authentication'

urlpatterns = [
    # Authentification SIMPLE et FONCTIONNELLE
    path('simple/register/', simple_register, name='simple_register'),
    path('simple/login/', simple_login, name='simple_login'),
    
    # Authentification originale (pour compatibilité)
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profil utilisateur
    path('profile/', views.get_user_profile, name='user_profile'),
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
    path('profile/details/', views.get_user_profile_details, name='profile_details'),
    path('profile/details/update/', views.update_user_profile_details, name='update_profile_details'),
    
    # Sécurité
    path('change-password/', views.change_password, name='change_password'),
    path('login-history/', views.get_login_history, name='login_history'),
    
    # Gestion des utilisateurs (admin)
    path('users/', views.UserListAPIView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailAPIView.as_view(), name='user_detail'),
]
