from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, date
from django.contrib import messages
from .models import Imprimante, Ordinateur, CapteurPresence, Thermostat, Poubelle, Salle, ReservationSalle, ReservationOrdinateur, Signalement
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.conf import settings
from email.utils import formataddr
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

User = get_user_model()
NIVEAU_MINIMUM_RESERVATION = 2
NIVEAU_MINIMUM_TEMPERATURE = 3

def calculer_age(date_naissance):
    today = date.today()
    return today.year - date_naissance.year - ((today.month, today.day) < (date_naissance.month, date_naissance.day))


def modifier_profil(request):
    user = request.user

    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username')  # Récupérer le nouveau nom d'utilisateur
        if username != user.username:  # Vérifier si le nom d'utilisateur a changé
            if User.objects.filter(username=username).exists():  # Vérifier si le nom d'utilisateur existe déjà
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return redirect('modifier_profil')

            user.username = username  # Mettre à jour le nom d'utilisateur

        # Récupérer et mettre à jour d'autres informations
        user.nom = request.POST.get('nom')
        user.prenom = request.POST.get('prenom')
        user.age = request.POST.get('age')
        user.genre = request.POST.get('genre')

        # Gérer la mise à jour du mot de passe
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('password')

        if current_password and new_password:
            if check_password(current_password, user.password):  # Vérifier le mot de passe actuel
                user.password = make_password(new_password)  # Hacher le nouveau mot de passe
                update_session_auth_hash(request, user)  # Pour garder l'utilisateur connecté après changement
                messages.success(request, "Votre mot de passe a été mis à jour.")
            else:
                messages.error(request, "Le mot de passe actuel est incorrect.")
                return redirect('modifier_profil')

        # Mettre à jour la date de naissance
        date_naissance_str = request.POST.get('date_naissance')
        if date_naissance_str:
            try:
                user.date_de_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "La date de naissance n'est pas valide.")
                return redirect('modifier_profil')

        # Gérer la photo de profil si envoyé
        if 'photo_profil' in request.FILES:
            user.photo_profil = request.FILES['photo_profil']

        # Sauvegarder les modifications dans la base de données
        user.save()

        # Message de succès
        messages.success(request, "Votre profil a été modifié avec succès.")
        return redirect('modifier_profil')  # Rediriger vers la page de modification après sauvegarde

    # Pré-remplir le formulaire pour la méthode GET
    return render(request, 'accounts/modifier_profil.html', {'user': user})

def activateEmail(request, user, to_email):
    mail_subject = "Activez votre compte"
    message = render_to_string("accounts/template_activation_email.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(
        subject=mail_subject,
        body=message,
        from_email=formataddr(("Votre espace CoWorking", settings.EMAIL_HOST_USER)),
        to=[to_email]
    )
    email.content_subtype = "html"
    email.send()

    messages.success(
        request,
        f"Merci <b>{user.username}</b> pour votre inscription ! Un e-mail de confirmation a été envoyé à "
        f"<b>{to_email}</b>. Veuillez vérifier votre boîte de réception (ainsi que vos spams) pour activer votre compte."
    )


def signup(request):
    if request.method == "POST":
        # Traiter le formulaire
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        date_naissance_str = request.POST.get("date_naissance")
        genre = request.POST.get("genre")

        try:
            date_naissance = datetime.strptime(date_naissance_str, "%Y-%m-%d").date()
            age = calculer_age(date_naissance)
        except ValueError:
            messages.error(request, "Veuillez entrer une date de naissance valide.")
            return render(request, "accounts/signup.html")

            # Vérifier si l'âge est entre 18 et 25 ans
        if age < 18 or age > 25:
            messages.error(request, "L'inscription est réservée aux personnes entre 18 et 25 ans.")
            return render(request, "accounts/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.")
            return render(request, "accounts/signup.html")

            # Vérification si l'email est déjà utilisé (optionnel mais recommandé)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé. Utilisez un autre email.")
            return render(request, "accounts/signup.html")
        user = User.objects.create_user(username=username,
                                 password=password,
                                 email=email,
                                 nom=nom,
                                 prenom=prenom,
                                 age=int(age) if age else None,  # Convertir en entier si non vide
                                 date_de_naissance=date_naissance if date_naissance else None,
                                 genre=genre
                                 )
        user.is_active = False  # Ne pas activer le compte tout de suite
        user.save()

        # Envoi du mail de confirmation
        activateEmail(request, user, email)

        return redirect("email_verification_sent")

    return render(request, "accounts/signup.html")

def email_verification_sent(request):
    return render(request, "accounts/email_verification_sent.html")

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('login')  # Redirige vers ta page de connexion
    else:
        messages.error(request, "Le lien d'activation est invalide ou expiré.")
        return redirect('signup')  # Ou autre page de ton choix

def login_user(request):
    if request.method == "POST":
        # Connecter l'utilisateur
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            user.points += 1

            for level, threshold in LEVEL_THRESHOLDS.items():
                if user.points >= threshold:
                    user.niveau = level

            if user.niveau == 4:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                return redirect('/admin/')

            user.save()
            return redirect('visiteur_index2')

    return render(request, "accounts/login.html")

# Create your views here.
from django.http import HttpResponse

# Create your views here.

def visiteur_index2(request):
    return render(request, "accounts/visiteur_index2.html")


@login_required
def reserver_PC(request):
    user = request.user  # Récupérer l'utilisateur connecté

    if user.niveau < NIVEAU_MINIMUM_RESERVATION:
        messages.error(request, "Vous n'avez pas le niveau requis pour réserver un PC.")
        return redirect("ordi_dispo2")  # Redirige vers la liste des PC

    # Ici, ajouter la logique pour enregistrer la réservation en base de données

    return render(request, "accounts/reserver_PC.html") # Redirection après réservation

@login_required
def modifier_temp(request, thermostat_id):
    thermostat = get_object_or_404(Thermostat, id=thermostat_id)
    if request.method == 'POST':
        nouvelle_temperature = request.POST.get('temperature')

        if nouvelle_temperature:
            try:
                nouvelle_temperature = float(nouvelle_temperature)
                thermostat.temperature_courante = nouvelle_temperature
                thermostat.save()

                # Incrémentation de l'action pour maintenance
                thermostat.set_en_maintenance()
                messages.success(request, "Température modifiée et l'objet est désormais en maintenance.")

            except ValueError:
                messages.error(request, "Veuillez entrer une valeur numérique valide.")
        else:
            messages.error(request, "La température est requise.")
        return redirect('afficher_objets', objet_type='thermostat')

    return render(request, 'accounts/modifier_temp.html', {'thermostat': thermostat})

def logout_user(request):
    logout(request)
    return redirect('index')

@login_required
def signaler_objet(request, objet_type, objet_id):
    """
    Permet aux utilisateurs de signaler un objet comme non fonctionnel ou pour une autre raison.
    """
    if request.method == 'POST':
        raison = request.POST.get('raison', '')

        # Créer un signalement pour l'objet signalé
        signalement = Signalement.objects.create(
            utilisateur=request.user,
            objet_type=objet_type,
            objet_id=objet_id,
            raison=raison
        )

        messages.success(request, "L'objet a été signalé. L'administrateur sera informé.")
        return redirect('afficher_objets', objet_type=objet_type)  # Redirection vers la page d'objets

    return render(request, 'accounts/signaler_objet.html', {'objet_type': objet_type, 'objet_id': objet_id})



LEVEL_THRESHOLDS = {
    1: 0,
    2: 5,
    3: 10,
    4: 15,
}


def get_objects_for_type(objet_type):
    if objet_type == 'salle':
        return Salle.objects.all()
    elif objet_type == 'thermostat':
        return Thermostat.objects.all()
    elif objet_type == 'ordinateur':
        return Ordinateur.objects.all()
    elif objet_type == 'imprimante':
        return Imprimante.objects.all()
    elif objet_type == 'poubelle':
        return Poubelle.objects.all()
    else:
        return []


@login_required
def annuler_reservation_salle(request, reservation_id):
    reservation = get_object_or_404(ReservationSalle, id=reservation_id)

    if reservation.user != request.user:
        messages.error(request, "Vous ne pouvez annuler que vos propres réservations.")
        return redirect('afficher_objets', objet_type='salle')


    salle = reservation.salle
    reservation.delete()


    salle.disponible = True
    salle.save()

    messages.success(request, "Votre réservation a été annulée avec succès. La salle est maintenant disponible.")


    return redirect('afficher_objets', objet_type='salle')


@login_required
def afficher_objets(request, objet_type):
    # Afficher les objets
    if objet_type == 'salle':
        objets = Salle.objects.all()
    else:
        # Autres objets (imprimantes, thermostats, etc.)
        objets = get_objects_for_type(objet_type)

    context = {
        'objets': objets,
        'objet_type': objet_type,
    }
    return render(request, 'accounts/afficher_objets.html', context)

@login_required
def afficher_reservations(request):
    reservations = ReservationSalle.objects.filter(user=request.user)
    return render(request, 'accounts/afficher_reservations.html', {'reservations': reservations})

@login_required
def reserver_salle(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)

    # Vérifier la disponibilité de la salle
    if not salle.disponible:
        messages.error(request, "Cette salle n'est pas disponible.")
        return redirect('afficher_objets', objet_type='salle')

    # Définir une date de début par défaut à maintenant
    date_debut_default = timezone.now()
    date_fin_default = date_debut_default + timedelta(hours=1)

    if request.method == 'POST':
        date_debut = request.POST.get('date_debut', date_debut_default)
        date_fin = request.POST.get('date_fin', date_fin_default)

        try:
            date_debut = timezone.datetime.strptime(date_debut, "%Y-%m-%dT%H:%M")
            date_fin = timezone.datetime.strptime(date_fin, "%Y-%m-%dT%H:%M")

            if date_debut >= date_fin:
                messages.error(request, "La date de début doit être avant la date de fin.")
                return redirect('reserver_salle', salle_id=salle.id)

            # Créer la réservation pour la salle
            reservation = ReservationSalle(
                user=request.user,
                salle=salle,
                date_debut=date_debut,
                date_fin=date_fin
            )
            reservation.save()

            # Mettre à jour la disponibilité de la salle
            salle.disponible = False  # La salle devient indisponible après la réservation
            salle.save()

            messages.success(request, "Votre réservation a été confirmée.")
            return redirect('afficher_objets', objet_type='salle')

        except ValueError:
            messages.error(request, "Les dates de réservation sont invalides.")
            return redirect('reserver_salle', salle_id=salle.id)

    return render(request, 'accounts/reserver_salle.html', {'salle': salle, 'date_debut_default': date_debut_default, 'date_fin_default': date_fin_default})

@login_required
def reserver_PC(request, ordinateur_id):
    ordinateur = get_object_or_404(Ordinateur, id=ordinateur_id)

    # Vérifier la disponibilité de l'ordinateur
    if not ordinateur.disponible:
        messages.error(request, "Cet ordinateur n'est pas disponible.")
        return redirect('afficher_objets', objet_type='ordinateur')

    # Définir une date de début par défaut à maintenant
    date_debut_default = timezone.now()
    date_fin_default = date_debut_default + timedelta(hours=1)

    if request.method == 'POST':
        date_debut = request.POST.get('date_debut', date_debut_default)
        date_fin = request.POST.get('date_fin', date_fin_default)

        try:
            date_debut = timezone.datetime.strptime(date_debut, "%Y-%m-%dT%H:%M")
            date_fin = timezone.datetime.strptime(date_fin, "%Y-%m-%dT%H:%M")

            if date_debut >= date_fin:
                messages.error(request, "La date de début doit être avant la date de fin.")
                return redirect('reserver_PC', ordinateur_id=ordinateur.id)

            # Créer la réservation pour l'ordinateur
            reservation = ReservationOrdinateur(
                user=request.user,
                ordinateur=ordinateur,
                date_debut=date_debut,
                date_fin=date_fin
            )
            reservation.save()

            # Mettre à jour la disponibilité de l'ordinateur
            ordinateur.disponible = False  # L'ordinateur devient indisponible après la réservation
            ordinateur.save()

            messages.success(request, "Votre réservation a été confirmée.")
            return redirect('afficher_objets', objet_type='ordinateur')

        except ValueError:
            messages.error(request, "Les dates de réservation sont invalides.")
            return redirect('reserver_PC', ordinateur_id=ordinateur.id)

    return render(request, 'accounts/reserver_PC.html', {'ordinateur': ordinateur, 'date_debut_default': date_debut_default, 'date_fin_default': date_fin_default})


@login_required
def vider_poubelle(request, poubelle_id):
    poubelle = get_object_or_404(Poubelle, id=poubelle_id)
    if request.method == 'POST':
        # Vider la poubelle
        poubelle.quantite_present = 0
        poubelle.save()

        # Incrémentation de l'action pour maintenance
        poubelle.set_en_maintenance()
        messages.success(request, "La poubelle a été vidée et l'objet est désormais en maintenance.")
        return redirect('afficher_objets', objet_type='poubelle')

    return render(request, 'accounts/vider_poubelle.html', {'poubelle': poubelle})



@login_required
def recherche_profils(request):
    query = request.GET.get('q', '')
    utilisateurs = []

    if query:
        utilisateurs = User.objects.filter(
            Q(username__icontains=query) |
            Q(nom__icontains=query) |
            Q(prenom__icontains=query)
        )

    context = {
        'utilisateurs': utilisateurs,
        'query': query
    }
    return render(request, 'accounts/resultats_recherche.html', context)

@login_required
def profil_detail(request, user_id):
    profil = User.objects.get(id=user_id)
    is_admin = request.user.is_superuser or request.user == profil

    return render(request, 'accounts/profil_detail.html', {
        'profil': profil,
        'is_admin': is_admin
    })


from django.urls import reverse

def filtrer_objets(request):
    type_objet = request.GET.get("type")
    etat = request.GET.get("etat")

    if type_objet == "salles":
        return redirect(reverse('afficher_objets', args=['salle']))
    elif type_objet == "ordinateurs":
        return redirect(reverse('afficher_objets', args=['ordinateur']))
    elif type_objet == "poubelles":
        return redirect(reverse('afficher_objets', args=['poubelle']))
    elif type_objet == "temperature":
        return redirect(reverse('afficher_objets', args=['thermostat']))

    return redirect("/")
