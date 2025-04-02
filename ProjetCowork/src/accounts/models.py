from django.contrib.auth.models import AbstractUser
from django.db import models

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
