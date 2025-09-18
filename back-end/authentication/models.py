from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    """
    Profil utilisateur étendu pour le système DIP
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('user', 'Utilisateur'),
        ('guest', 'Invité'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name="Rôle"
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Téléphone"
    )
    organization = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Organisation"
    )
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    
    # Préférences utilisateur
    bio = models.TextField(blank=True, null=True, verbose_name="Biographie")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    language = models.CharField(max_length=5, default='fr', verbose_name="Langue")
    timezone = models.CharField(max_length=50, default='Africa/Abidjan', verbose_name="Fuseau horaire")
    currency = models.CharField(max_length=3, default='XOF', verbose_name="Devise")
    theme = models.CharField(max_length=10, default='light', verbose_name="Thème")
    
    # Préférences de notification
    email_notifications = models.BooleanField(default=True, verbose_name="Notifications email")
    push_notifications = models.BooleanField(default=False, verbose_name="Notifications push")
    weekly_reports = models.BooleanField(default=True, verbose_name="Rapports hebdomadaires")
    monthly_reports = models.BooleanField(default=False, verbose_name="Rapports mensuels")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser
    
    def is_regular_user(self):
        return self.role == 'user'
    
    def is_guest(self):
        return self.role == 'guest'


class LoginAttempt(models.Model):
    """
    Modèle pour enregistrer les tentatives de connexion
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts', null=True, blank=True)
    email = models.EmailField(verbose_name="Email")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    success = models.BooleanField(verbose_name="Succès")
    failure_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name="Raison de l'échec")
    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Tentative le")
    
    class Meta:
        verbose_name = "Tentative de connexion"
        verbose_name_plural = "Tentatives de connexion"
        ordering = ['-attempted_at']
    
    def __str__(self):
        status = "Succès" if self.success else "Échec"
        return f"{self.email} - {status} - {self.attempted_at}"