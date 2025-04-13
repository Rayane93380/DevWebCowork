from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Poubelle, CapteurPresence, Imprimante, Ordinateur, Salle, Thermostat, Signalement # Import du modèle personnalisé

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
    list_display = ('nom', 'capacite_max', 'description', 'disponible')

class SignalementAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'objet_type', 'objet_id', 'statut', 'raison', 'date_signalement')

admin.site.register(Signalement, SignalementAdmin)

class ThermostatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'temperature_courante', 'temperature_cible', 'en_maintenance', 'date_maintenance')
    list_filter = ('en_maintenance',)
    actions = ['mettre_en_maintenance', 'retirer_de_maintenance']

    def mettre_en_maintenance(self, request, queryset):
        for thermostat in queryset:
            thermostat.set_en_maintenance()
    mettre_en_maintenance.short_description = "Mettre les thermostats sélectionnés en maintenance"

    def retirer_de_maintenance(self, request, queryset):
        for thermostat in queryset:
            thermostat.en_maintenance = False
            thermostat.save()
    retirer_de_maintenance.short_description = "Retirer les thermostats sélectionnés de la maintenance"

class PoubelleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite_max', 'quantite_present', 'couleur', 'en_maintenance', 'date_maintenance', 'salle')
    list_filter = ('en_maintenance', 'salle')
    actions = ['mettre_en_maintenance', 'retirer_de_maintenance']

    def mettre_en_maintenance(self, request, queryset):
        for poubelle in queryset:
            poubelle.set_en_maintenance()
    mettre_en_maintenance.short_description = "Mettre les poubelles sélectionnées en maintenance"

    def retirer_de_maintenance(self, request, queryset):
        for poubelle in queryset:
            poubelle.en_maintenance = False
            poubelle.save()
    retirer_de_maintenance.short_description = "Retirer les poubelles sélectionnées de la maintenance"

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
