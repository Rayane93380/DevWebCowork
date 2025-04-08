from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    points = models.IntegerField(default=0)
    niveau = models.IntegerField(default=1)
    nom = models.CharField(max_length=150, default="Inconnu")
    prenom = models.CharField(max_length=150, default="Inconnu")
    age = models.IntegerField(null=True, blank=True)
    genre = models.CharField(
        max_length=10,
        choices=[("Homme", "Homme"), ("Femme", "Femme"), ("Autre", "Autre")],
        null=True,
        blank=True
    )
    date_de_naissance = models.DateField(null=True, blank=True)
    photo_profil = models.ImageField(upload_to="photos_profil/", null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.nom} {self.prenom} - Niveau {self.niveau} - Points {self.points}"

# Create your models here.


class Salle(models.Model):
    nom = models.CharField(max_length=100)
    capacite_max = models.IntegerField()
    description = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)  # Ajoute ce champ pour vérifier si la salle est disponible

    def __str__(self):
        return self.nom


class Signalement(models.Model):
    SIGNALER_CHOICES = [
        ('objet_non_fonctionnel', 'Objet non fonctionnel'),
        ('autre', 'Autre'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    objet_type = models.CharField(max_length=50)
    objet_id = models.PositiveIntegerField()
    raison = models.CharField(max_length=255, blank=True, null=True)
    statut = models.BooleanField(default=False)
    date_signalement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Signalement de {self.utilisateur.username} pour l'objet {self.objet_id}"

    @property
    def objet(self):
        if self.objet_type == 'imprimante':
            return Imprimante.objects.get(id=self.objet_id)
        elif self.objet_type == 'ordinateur':
            return Ordinateur.objects.get(id=self.objet_id)
        elif self.objet_type == 'thermostat':
            return Thermostat.objects.get(id=self.objet_id)
        elif self.objet_type == 'poubelle':
            return Poubelle.objects.get(id=self.objet_id)
        return None

class Thermostat(models.Model):
    # Champs existants
    nom = models.CharField(max_length=100)
    temperature_courante = models.FloatField(default=21.0)
    temperature_cible = models.FloatField(default=23.0)

    # Champs de maintenance
    en_maintenance = models.BooleanField(default=False)
    date_maintenance = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nom

    def set_en_maintenance(self):
        """Met l'objet en maintenance pour 5 minutes"""
        self.en_maintenance = True
        self.date_maintenance = timezone.now()  # Met à jour l'heure de début de la maintenance
        self.save()

    def is_maintenance_active(self):
        """Vérifie si l'objet est en maintenance (5 minutes)"""
        if not self.en_maintenance:
            return False
        if timezone.now() > self.date_maintenance + timezone.timedelta(minutes=5):
            self.en_maintenance = False
            self.save()
            return False
        return True

class Poubelle(models.Model):
    # Champs existants
    nom = models.CharField(max_length=100, default="Poubelle inconnue")
    capacite_max = models.IntegerField(default=38)
    quantite_present = models.IntegerField(default=12)
    couleur = models.CharField(max_length=50)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name="poubelles")

    # Champs de maintenance
    en_maintenance = models.BooleanField(default=False)
    date_maintenance = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nom

    def set_en_maintenance(self):
        """Met l'objet en maintenance pour 5 minutes"""
        self.en_maintenance = True
        self.date_maintenance = timezone.now()  # Met à jour l'heure de début de la maintenance
        self.save()

    def is_maintenance_active(self):
        """Vérifie si l'objet est en maintenance (5 minutes)"""
        if not self.en_maintenance:
            return False
        if timezone.now() > self.date_maintenance + timezone.timedelta(minutes=5):
            self.en_maintenance = False
            self.save()
            return False
        return True

class CapteurPresence(models.Model):
    salle = models.OneToOneField(Salle, on_delete=models.CASCADE)  # Un capteur par salle
    compteur = models.IntegerField(default=0)  # Compteur de personnes dans la salle

    def __str__(self):
        return f"Capteur de présence pour la salle {self.salle.nom}"

    def entrer(self):
        """Incrémente le compteur lorsqu'une personne entre."""
        if self.compteur < self.salle.capacite_maximale:
            self.compteur += 1
            self.save()
        else:
            raise ValidationError(f"Capacité maximale atteinte pour la salle {self.salle.nom}. L'entrée est interdite.")

    def sortir(self):
        """Décrémente le compteur lorsqu'une personne sort."""
        if self.compteur > 0:
            self.compteur -= 1
            self.save()
        else:
            raise ValidationError(f"Aucune personne dans la salle {self.salle.nom} pour sortir.")

from django.db import models
from datetime import datetime

# models.py

class Imprimante(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    modele = models.CharField(max_length=100)
    connectivite = models.CharField(max_length=100, default="Wi-Fi")
    etat = models.CharField(max_length=50, choices=[('en fonctionnement', 'En fonctionnement'), ('en panne', 'En panne')], default='en fonctionnement')
    reservable = models.BooleanField(default=True)  # Option de réservation (oui/non)
    maintenance_due = models.BooleanField(default=False)  # Maintenance nécessaire (True ou False)
    reservation_count = models.IntegerField(default=0)  # Nombre de réservations

    def __str__(self):
        return f"Imprimante {self.modele} - {self.salle.nom}"

class Ordinateur(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    etat = models.CharField(max_length=50, choices=[('fonctionnel', 'Fonctionnel'), ('en panne', 'En panne')], default='fonctionnel')
    reservable = models.BooleanField(default=True)  # Option de réservation (oui/non)
    maintenance_due = models.BooleanField(default=False)  # Maintenance nécessaire (True ou False)
    reservation_count = models.IntegerField(default=0)  # Nombre de réservations

    def __str__(self):
        return f"Ordinateur {self.marque} {self.modele} - {self.salle.nom}"

# models.py
from django.conf import settings

class ReservationSalle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()

    def __str__(self):
        return f"Réservation de {self.user.username} pour la salle {self.salle.nom} de {self.date_debut} à {self.date_fin}"

class ReservationOrdinateur(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordinateur = models.ForeignKey(Ordinateur, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()

    def __str__(self):
        return f"Réservation de {self.user.username} pour l'ordinateur {self.ordinateur.nom} de {self.date_debut} à {self.date_fin}"
