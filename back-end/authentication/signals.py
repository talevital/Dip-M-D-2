from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Créer automatiquement un profil utilisateur lors de la création d'un utilisateur
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarder le profil utilisateur lors de la sauvegarde de l'utilisateur
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

