from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Import du modèle personnalisé

class CustomUserAdmin(UserAdmin):
    list_display = ("username", "nom", "prenom", "email", "age", "date_de_naissance", "genre", "niveau", "points","photo_profil")
    search_fields = ("username", "nom", "prenom", "email")
    list_filter = ("niveau", "genre")

    fieldsets = (
        ("Informations de connexion", {"fields": ("username", "password")}),
        ("Informations personnelles", {"fields": ("nom", "prenom", "email", "age", "date_de_naissance", "genre", "photo_profil")}),
        ("Statistiques", {"fields": ("niveau", "points")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        ("Nouvel utilisateur", {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "nom", "prenom", "email", "age", "date_de_naissance", "genre"),
        }),
    )

# Enregistre directement la nouvelle configuration
admin.site.register(User, CustomUserAdmin)
