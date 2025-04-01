from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    points = models.IntegerField(default=0)
    niveau = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.username} - Niveau {self.niveau} - Points {self.points}"


# Create your models here.
