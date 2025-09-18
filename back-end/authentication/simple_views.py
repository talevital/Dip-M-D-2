from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def simple_register(request):
    """
    Inscription simple et fonctionnelle
    """
    try:
        data = json.loads(request.body)
        
        # Validation basique
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not email or not username or not password:
            return Response({
                'error': 'Email, username et password sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Un utilisateur avec cet email existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Un utilisateur avec ce nom existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Créer le profil (utiliser get_or_create pour éviter les conflits)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': data.get('phone', ''),
                'organization': data.get('organization', ''),
                'role': data.get('role', 'user')
            }
        )
        
        # Générer les tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la création: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def simple_login(request):
    """
    Connexion simple et fonctionnelle
    """
    try:
        data = json.loads(request.body)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et password sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authentifier l'utilisateur (essayer d'abord avec l'email comme username)
        user = authenticate(username=email, password=password)
        
        # Si ça ne marche pas, essayer de trouver l'utilisateur par email
        if user is None:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is None:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Générer les tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la connexion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
