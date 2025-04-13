from django.urls import path
from .views import visiteur_index, afficher_objets

urlpatterns = [
    path('', visiteur_index, name='visiteur_index'),
    path('objets/<str:objet_type>/', afficher_objets, name='afficher_objets'),
]