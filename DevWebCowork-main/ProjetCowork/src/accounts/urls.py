from django.urls import path
from .views import modifier_profil, signup, login_user, logout_user, visiteur_index2, reserver_salle, reserver_PC, modifier_temp, afficher_objets, activate, email_verification_sent, recherche_profils, profil_detail, vider_poubelle, filtrer_objets, annuler_reservation_salle, afficher_reservations,signaler_objet


urlpatterns = [
    path('', signup, name='signup'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('visiteur_index2', visiteur_index2, name="visiteur_index2"),
    path('objets/<str:objet_type>/', afficher_objets, name='afficher_objets'),
    path('login/reserver_salle/<int:salle_id>/', reserver_salle, name='reserver_salle'),
    path('login/annuler_reservation_salle/<int:reservation_id>/', annuler_reservation_salle, name='annuler_reservation_salle'),
    path('reserver_salle/<int:salle_id>/', reserver_salle, name='reserver_salle'),
    path('afficher_salles/', afficher_objets, name='afficher_salles'),
    path('login/mes_reservations/', afficher_reservations, name='afficher_reservations'),
    path('modifier_temp/<int:thermostat_id>/', modifier_temp, name='modifier_temp'),
    path('vider_poubelle/<int:poubelle_id>/', vider_poubelle, name='vider_poubelle'),
    path('signaler/<str:objet_type>/<int:objet_id>/', signaler_objet, name='signaler_objet'),
    path('login/reserver_PC/<int:ordinateur_id>/', reserver_PC, name='reserver_PC'),
    path('temperature_salles2/modifier_temp/', modifier_temp, name='modifier_temp'),
    path('modifier-profil/', modifier_profil, name='modifier_profil'),
    path('objets_connectes/<str:objet_type>/', afficher_objets, name='afficher_objets'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path("email-verification-sent/", email_verification_sent, name="email_verification_sent"),
    path('recherche-profils/', recherche_profils, name='recherche_profils'),
    path('profil/<int:user_id>/', profil_detail, name='profil_detail'),
    path("filtrer/", filtrer_objets, name="filtrer_objets"),
]
