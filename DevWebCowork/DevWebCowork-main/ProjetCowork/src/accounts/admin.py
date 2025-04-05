from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Poubelle, CapteurPresence, Imprimante, Ordinateur, Salle, Thermostat # Import du modèle personnalisé

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



class ThermostatInline(admin.StackedInline):
    model = Thermostat
    extra = 1  # Permet d'ajouter un thermostat directement dans la page de la salle

class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'capacite', 'disponible']
    search_fields = ['nom']
    inlines = [ThermostatInline]  # Permet d'ajouter un thermostat à partir de la page de la salle

class ThermostatAdmin(admin.ModelAdmin):
    list_display = ['id_unique', 'nom', 'temperature_courante', 'temperature_cible', 'mode', 'connectivite', 'etat_batterie', 'derniere_interaction']
    search_fields = ['nom', 'id_unique']  # Recherche par le nom du thermostat ou son ID unique

class PoubelleAdmin(admin.ModelAdmin):
    list_display = ['id_unique', 'type_dechet', 'couleur', 'capacite_maximale', 'quantite_present', 'salle']
    search_fields = ['id_unique', 'type_dechet', 'salle__nom']
    list_filter = ['type_dechet', 'salle']  # Pour filtrer par type de déchet et salle

class CapteurPresenceAdmin(admin.ModelAdmin):
    list_display = ['salle', 'compteur']
    search_fields = ['salle__nom']

class ImprimanteAdmin(admin.ModelAdmin):
    list_display = ['modele', 'etat', 'connectivite', 'reservable', 'salle']
    search_fields = ['modele', 'salle__nom']
    list_filter = ['etat', 'reservable', 'salle']

class OrdinateurAdmin(admin.ModelAdmin):
    list_display = ['marque', 'modele', 'etat', 'reservable', 'salle']
    search_fields = ['marque', 'modele', 'salle__nom']
    list_filter = ['etat', 'reservable', 'salle']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Salle, SalleAdmin)
admin.site.register(CapteurPresence, CapteurPresenceAdmin)
admin.site.register(Poubelle, PoubelleAdmin)
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(Imprimante, ImprimanteAdmin)
admin.site.register(Ordinateur, OrdinateurAdmin)
