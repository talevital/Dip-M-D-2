from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, LoginAttempt


# Étendre l'admin User par défaut
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'


class ExtendedUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_role', 'get_phone', 'get_organization')
    
    def get_role(self, obj):
        try:
            return obj.profile.role
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_role.short_description = 'Rôle'
    
    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_phone.short_description = 'Téléphone'
    
    def get_organization(self, obj):
        try:
            return obj.profile.organization
        except UserProfile.DoesNotExist:
            return 'N/A'
    get_organization.short_description = 'Organisation'


# Désinscrire l'admin User par défaut et réinscrire avec notre version étendue
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle UserProfile
    """
    list_display = [
        'user', 'role', 'phone', 'organization', 'language', 'timezone', 'currency', 'theme',
        'email_notifications', 'created_at'
    ]
    list_filter = ['role', 'language', 'timezone', 'currency', 'theme', 'email_notifications']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone', 'organization']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Utilisateur', {'fields': ('user',)}),
        ('Informations', {
            'fields': ('role', 'phone', 'organization', 'is_verified')
        }),
        ('Préférences', {
            'fields': ('language', 'timezone', 'currency', 'theme')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'push_notifications', 'weekly_reports', 'monthly_reports')
        }),
        ('Profil', {
            'fields': ('bio', 'avatar')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle LoginAttempt
    """
    list_display = [
        'email', 'user', 'ip_address', 'success', 'failure_reason', 'attempted_at'
    ]
    list_filter = ['success', 'attempted_at']
    search_fields = ['email', 'ip_address', 'user__email']
    ordering = ['-attempted_at']
    readonly_fields = ['attempted_at']
    
    fieldsets = (
        ('Tentative de connexion', {
            'fields': ('user', 'email', 'ip_address', 'user_agent')
        }),
        ('Résultat', {
            'fields': ('success', 'failure_reason')
        }),
        ('Date', {
            'fields': ('attempted_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Empêcher l'ajout manuel de tentatives de connexion
        return False
    
    def has_change_permission(self, request, obj=None):
        # Empêcher la modification des tentatives de connexion
        return False


# Personnalisation de l'interface admin
admin.site.site_header = "Administration DIP"
admin.site.site_title = "DIP Admin"
admin.site.index_title = "Tableau de bord DIP"