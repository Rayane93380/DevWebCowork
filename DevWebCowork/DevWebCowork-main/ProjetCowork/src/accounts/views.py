from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, date
from django.contrib import messages
from .models import Imprimante, Ordinateur, CapteurPresence, Thermostat, Poubelle, Reservation
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,  urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.conf import settings
from email.utils import formataddr
from django.contrib.auth.decorators import login_required


User = get_user_model()
NIVEAU_MINIMUM_RESERVATION = 2
NIVEAU_MINIMUM_TEMPERATURE = 3

def calculer_age(date_naissance):
    today = date.today()
    return today.year - date_naissance.year - ((today.month, today.day) < (date_naissance.month, date_naissance.day))


def modifier_profil(request):
    # Récupérer l'utilisateur connecté
    user = request.user

    if request.method == 'POST':
        # Récupérer les données du formulaire
        user.nom = request.POST.get('nom')
        user.prenom = request.POST.get('prenom')
        user.age = request.POST.get('age')
        user.genre = request.POST.get('genre')

        # Récupérer le mot de passe actuel et le nouveau mot de passe
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('password')

        # Validation et mise à jour du mot de passe
        if current_password and new_password:
            if check_password(current_password, user.password):  # Vérifier le mot de passe actuel
                user.password = make_password(new_password)  # Hacher le nouveau mot de passe
                update_session_auth_hash(request, user)  # Pour garder l'utilisateur connecté après changement
                messages.success(request, "Votre mot de passe a été mis à jour.")
            else:
                messages.error(request, "Le mot de passe actuel est incorrect.")
                return redirect('modifier_profil')

        # Conversion de la date de naissance au format correct
        date_naissance_str = request.POST.get('date_naissance')
        if date_naissance_str:
            try:
                user.date_de_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "La date de naissance n'est pas valide. Veuillez réessayer.")
                return redirect('modifier_profil')

        # Gérer la photo de profil si elle est envoyée
        if 'photo_profil' in request.FILES:
            user.photo_profil = request.FILES['photo_profil']

        # Sauvegarder les modifications dans la base de données
        user.save()

        # Message de succès
        messages.success(request, "Votre profil a été modifié avec succès.")
        return redirect('modifier_profil')  # Rediriger vers la page de modification après sauvegarde

    # Si la requête est GET, pré-remplir les champs avec les informations actuelles
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

            if user.niveau == 4 and not user.is_superuser:
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

def temperature_salles2(request):
    return render(request, "accounts/temperature_salles2.html")

def liste_salles2(request):
    return render(request, "accounts/liste_salles2.html")

def poubelles_vides2(request):
    return render(request, "accounts/poubelles_vides2.html")

def ordi_dispo2(request):
    return render(request, "accounts/ordi_dispo2.html")

def reserver_salle(request):
    return render(request, "accounts/reserver_salle.html")





@login_required
def reserver_PC(request):
    user = request.user  # Récupérer l'utilisateur connecté

    if user.niveau < NIVEAU_MINIMUM_RESERVATION:
        messages.error(request, "Vous n'avez pas le niveau requis pour réserver un PC.")
        return redirect("ordi_dispo2")  # Redirige vers la liste des PC

    # Ici, ajouter la logique pour enregistrer la réservation en base de données

    return render(request, "accounts/reserver_PC.html") # Redirection après réservation

@login_required()
def modifier_temp(request):
    user = request.user

    if user.niveau < NIVEAU_MINIMUM_TEMPERATURE:
        messages.error(request, "Vous n'avez pas le niveau requis pour modifier la température")
        return render(request, "accounts/temperature_salles2.html")


    return render(request, 'accounts/modifier_temp.html')

def logout_user(request):
    logout(request)
    return redirect('index')


LEVEL_THRESHOLDS = {
    1: 0,
    2: 5,
    3: 10,
    4: 15,
}

@login_required
def afficher_objets(request, objet_type):
    """
    Affiche les objets connectés d'un type spécifique (imprimante, ordinateur, thermostat, etc.)
    """
    if objet_type == 'capteurpresence':
        objets = CapteurPresence.objects.all()
    elif objet_type == 'thermostat':
        objets = Thermostat.objects.all()
    elif objet_type == 'poubelle':
        objets = Poubelle.objects.all()
    elif objet_type == 'imprimante':
        objets = Imprimante.objects.all()
    elif objet_type == 'ordinateur':
        objets = Ordinateur.objects.all()
    else:
        return redirect('dashbord')  # Redirection si le type d'objet n'est pas valide

    context = {
        'objets': objets,
        'objet_type': objet_type,
    }
    return render(request, 'accounts/afficher_objets.html', context)



@login_required
def reserver_objet(request, objet_type, objet_id):
    """
    Gérer la réservation d'un objet (imprimante ou ordinateur)
    """
    if objet_type == 'imprimante':
        objet = Imprimante.objects.get(id=objet_id)
    elif objet_type == 'ordinateur':
        objet = Ordinateur.objects.get(id=objet_id)
    else:
        return redirect('afficher_objets')

    # Vérification si l'objet est réservable
    if not objet.reservable or objet.maintenance_due:
        return render(request, 'error.html', {'message': 'Cet objet n\'est pas disponible pour réservation.'})

    # Créer une nouvelle réservation
    reservation = Reservation.objects.create(user=request.user, objet_type=objet_type, objet_id=objet.id)

    # Incrémenter le compteur de réservations
    objet.reservation_count += 1
    if objet.reservation_count >= 4:
        # Si l'objet atteint 4 réservations, mettre à jour le champ maintenance_due
        objet.maintenance_due = True
        objet.reservable = False  # Marquer l'objet comme non réservable
    objet.save()

    return redirect('afficher_objets')


@login_required
def annuler_reservation(request, reservation_id):
    """
    Annuler une réservation existante
    """
    reservation = Reservation.objects.get(id=reservation_id)

    if reservation.user != request.user:
        return redirect(
            'afficher_objets')  # Si l'utilisateur essaie de modifier une réservation qui n'est pas la sienne

    # Supprimer la réservation
    reservation.delete()

    # Récupérer l'objet réservé
    if reservation.objet_type == 'imprimante':
        objet = Imprimante.objects.get(id=reservation.objet_id)
    elif reservation.objet_type == 'ordinateur':
        objet = Ordinateur.objects.get(id=reservation.objet_id)

    # Décrémenter le compteur de réservations
    objet.reservation_count -= 1
    if objet.reservation_count < 4:
        # Si le nombre de réservations est inférieur à 4, remettre l'objet en état réservable
        objet.maintenance_due = False
        objet.reservable = True
    objet.save()

    return redirect('afficher_objets')


def dashboard(request):
    # Récupérer les objets connectés
    return render(request, 'accounts/dashboard.html')