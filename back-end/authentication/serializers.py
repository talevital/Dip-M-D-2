from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, LoginAttempt


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'inscription des utilisateurs
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    organization = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.CharField(write_only=True, required=False, default='user')
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'password', 'password_confirm', 'phone', 'organization', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Un utilisateur avec ce nom d'utilisateur existe déjà.")
        return value
    
    def create(self, validated_data):
        try:
            # Extraire les données du profil
            phone = validated_data.pop('phone', '')
            organization = validated_data.pop('organization', '')
            role = validated_data.pop('role', 'user')
            password_confirm = validated_data.pop('password_confirm')
            password = validated_data.pop('password')
            
            # Créer l'utilisateur avec les données validées
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            
            # Créer le profil utilisateur avec les données supplémentaires
            UserProfile.objects.create(
                user=user,
                phone=phone,
                organization=organization,
                role=role
            )
            
            return user
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            raise serializers.ValidationError(f"Erreur lors de la création du compte: {str(e)}")


class UserLoginSerializer(serializers.Serializer):
    """
    Sérialiseur pour la connexion des utilisateurs
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Email ou mot de passe incorrect.")
            if not user.is_active:
                raise serializers.ValidationError("Ce compte utilisateur est désactivé.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email et mot de passe requis.")
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les informations utilisateur
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'role', 'phone', 'organization', 'is_active', 
            'is_verified', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_role(self, obj):
        try:
            return obj.profile.role
        except UserProfile.DoesNotExist:
            return 'user'
    
    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except UserProfile.DoesNotExist:
            return ''
    
    def get_organization(self, obj):
        try:
            return obj.profile.organization
        except UserProfile.DoesNotExist:
            return ''
    
    def get_is_verified(self, obj):
        try:
            return obj.profile.is_verified
        except UserProfile.DoesNotExist:
            return False
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le profil utilisateur
    """
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'language', 'timezone', 'currency', 'theme',
            'email_notifications', 'push_notifications', 'weekly_reports', 
            'monthly_reports', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour des informations utilisateur
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'organization']
    
    def validate_email(self, value):
        if self.instance and User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Sérialiseur pour le changement de mot de passe
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return attrs


class LoginAttemptSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les tentatives de connexion (lecture seule)
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'user', 'user_name', 'email', 'ip_address', 
            'success', 'failure_reason', 'attempted_at'
        ]
        read_only_fields = '__all__'
