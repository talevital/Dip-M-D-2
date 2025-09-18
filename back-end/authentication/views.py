from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from django.utils import timezone
from django.db import transaction
import logging

from .models import User, UserProfile, LoginAttempt
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserProfileSerializer,
    LoginAttemptSerializer
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_login_attempt(request, user, success, failure_reason=None):
    """Enregistre une tentative de connexion"""
    try:
        LoginAttempt.objects.create(
            user=user if success else None,
            email=request.data.get('email', ''),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            failure_reason=failure_reason
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la tentative de connexion: {e}")


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'obtention des tokens JWT
    """
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Générer les tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Mettre à jour la dernière connexion
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Enregistrer la tentative de connexion réussie
            log_login_attempt(request, user, True)
            
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            # Enregistrer la tentative de connexion échouée
            email = request.data.get('email', '')
            failure_reason = 'Email ou mot de passe incorrect'
            log_login_attempt(request, None, False, failure_reason)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Endpoint pour l'inscription d'un nouvel utilisateur
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                
                # Générer les tokens pour le nouvel utilisateur
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                logger.info(f"Nouvel utilisateur inscrit: {user.email}")
                
                return Response({
                    'message': 'Utilisateur créé avec succès',
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            return Response({
                'error': 'Erreur lors de la création du compte'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """
    Endpoint pour récupérer le profil de l'utilisateur connecté
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """
    Endpoint pour mettre à jour le profil de l'utilisateur connecté
    """
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès',
            'user': UserSerializer(request.user).data
        })
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Endpoint pour changer le mot de passe de l'utilisateur connecté
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"Mot de passe changé pour l'utilisateur: {user.email}")
        
        return Response({
            'message': 'Mot de passe changé avec succès'
        })
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile_details(request):
    """
    Endpoint pour récupérer les détails du profil utilisateur
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profil utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile_details(request):
    """
    Endpoint pour mettre à jour les détails du profil utilisateur
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profil mis à jour avec succès',
                'profile': serializer.data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profil utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_login_history(request):
    """
    Endpoint pour récupérer l'historique des connexions de l'utilisateur
    """
    if not request.user.is_admin():
        return Response({
            'error': 'Accès non autorisé'
        }, status=status.HTTP_403_FORBIDDEN)
    
    attempts = LoginAttempt.objects.filter(user=request.user).order_by('-attempted_at')[:50]
    serializer = LoginAttemptSerializer(attempts, many=True)
    
    return Response({
        'attempts': serializer.data,
        'total': attempts.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    Endpoint pour déconnecter l'utilisateur (blacklister le refresh token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        logger.info(f"Utilisateur déconnecté: {request.user.email}")
        
        return Response({
            'message': 'Déconnexion réussie'
        })
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return Response({
            'error': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_400_BAD_REQUEST)


# Vues génériques pour les administrateurs
class UserListAPIView(generics.ListAPIView):
    """
    Vue pour lister tous les utilisateurs (admin seulement)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return User.objects.all()
        return User.objects.none()


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vue pour gérer un utilisateur spécifique (admin seulement)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return User.objects.all()
        return User.objects.none()