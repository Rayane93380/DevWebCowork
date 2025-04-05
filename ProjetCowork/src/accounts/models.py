from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError

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
    capacite = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Salle {self.nom}"

class Thermostat(models.Model):
    salle = models.OneToOneField(Salle, on_delete=models.CASCADE)
    id_unique = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    temperature_courante = models.FloatField(default=21.0)
    temperature_cible = models.FloatField(default=23.0)
    mode = models.CharField(max_length=50, choices=[('automatique', 'Automatique'), ('manuel', 'Manuel')],
                            default='automatique')
    connectivite = models.CharField(max_length=100, default="Wi-Fi, signal fort")
    etat_batterie = models.IntegerField(default=100)
    derniere_interaction = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thermostat {self.nom} - {self.id_unique}"

class Poubelle(models.Model):
    TYPE_DECHET_CHOICES = [
        ('plastique', 'Plastique'),
        ('carton', 'Carton'),
        ('alimentaire', 'Alimentaire'),
        ('papier', 'Papier'),
    ]
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    id_unique = models.CharField(max_length=50, unique=True)
    type_dechet = models.CharField(max_length=50, choices=TYPE_DECHET_CHOICES)

    # Couleur de la poubelle, qui dépend du type de déchet
    couleur = models.CharField(max_length=50)

    # Capacité maximale de la poubelle
    capacite_maximale = models.FloatField()  # Capacité en litres (par exemple)

    # Quantité actuelle dans la poubelle
    quantite_present = models.FloatField(default=0)  # Quantité en litres

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y ait pas plus de 4 poubelles (une de chaque type) par salle
        if Poubelle.objects.filter(salle=self.salle, type_dechet=self.type_dechet).exists():
            raise ValueError("Il ne peut y avoir qu'une poubelle de chaque type dans une salle.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Poubelle {self.id_unique} - {self.type_dechet} ({self.salle.nom})"

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
# models.py
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

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Utilise AUTH_USER_MODEL
    objet_type = models.CharField(max_length=50, choices=[('imprimante', 'Imprimante'), ('ordinateur', 'Ordinateur')])
    objet_id = models.IntegerField()  # ID de l'objet réservé (Imprimante ou Ordinateur)
    date_reservation = models.DateTimeField(default=datetime.now)  # Date de la réservation

    def __str__(self):
        return f"Réservation de {self.objet_type} par {self.user.username} le {self.date_reservation}"

