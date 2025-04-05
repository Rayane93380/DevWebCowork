from django.urls import path
from .views import modifier_profil, signup, login_user, logout_user, visiteur_index2, temperature_salles2, liste_salles2, poubelles_vides2, ordi_dispo2, reserver_salle, reserver_PC, modifier_temp, afficher_objets, reserver_objet, dashboard, activate, email_verification_sent




urlpatterns = [
    path('', signup, name='signup'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('visiteur_index2', visiteur_index2, name="visiteur_index2"),
    path('temperature_salles2/', temperature_salles2, name='temperature_salles2'),
    path('liste_salles2/', liste_salles2, name='liste_salles2'),
    path('poubelles_vides2/', poubelles_vides2, name='poubelles_vides2'),
    path('ordi_dispo2/', ordi_dispo2, name='ordi_dispo2'),
    path('reserver_salle/', reserver_salle, name='reserver_salle'),
    path('reserver_PC/', reserver_PC, name='reserver_PC'),
    path('temperature_salles2/modifier_temp/', modifier_temp, name='modifier_temp'),
    path('modifier-profil/', modifier_profil, name='modifier_profil'),
    path('objets_connectes/<str:objet_type>/', afficher_objets, name='afficher_objets'),
    path('reserver/<str:objet_type>/<int:objet_id>/', reserver_objet, name='reserver_objet'),
    path('dashboard/', dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path("email-verification-sent/", email_verification_sent, name="email_verification_sent"),
]
