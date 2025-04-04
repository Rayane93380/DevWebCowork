from django.urls import path
from .views import visiteur_index, temperature_salles, liste_salles, poubelles_vides, ordi_dispo

urlpatterns = [
    path('', visiteur_index, name='visiteur_index'),
    path('temperature_salles/', temperature_salles, name='temperature_salles'),
    path('liste_salles/', liste_salles, name='liste_salles'),
    path('poubelles_vides/', poubelles_vides, name='poubelles_vides'),
    path('ordi_dispo/', ordi_dispo, name='ordi_dispo')
]