from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib import messages
User = get_user_model()

NIVEAU_MINIMUM_RESERVATION = 2
NIVEAU_MINIMUM_TEMPERATURE = 3

def signup(request):
    if request.method == "POST":
        # Traiter le formulaire
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.")
            return render(request, "accounts/signup.html")

            # Vérification si l'email est déjà utilisé (optionnel mais recommandé)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé. Utilisez un autre email.")
            return render(request, "accounts/signup.html")
        user = User.objects.create_user(username=username,
                                 password=password,
                                 email=email)
        login(request, user)
        return redirect("visiteur_index2")
    return render(request, "accounts/signup.html")

def login_user(request):
    if request.method == "POST":
        # Connecter l'utilisateur
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            # 🔥 Ajoute +1 aux points de l'utilisateur
            user.points += 1

            # 🔥 Vérifie si le niveau doit être mis à jour
            for level, threshold in LEVEL_THRESHOLDS.items():
                if user.points >= threshold:
                    user.niveau = level

            user.save()
            return redirect('visiteur_index2')

    return render(request, "accounts/login.html")

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

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

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    1: 0,  # Niveau 1 -> 100 points
    2: 5,  # Niveau 2 -> 200 points
    3: 10,  # Niveau 3 -> 500 points
    4: 15, # Niveau 4 -> 1000 points
}