from django.shortcuts import render


# Create your views here.
def visiteur_index(request):
    return render(request, "visiteur/visiteur_index.html")

def temperature_salles(request):
    return render(request, "visiteur/temperature_salles.html")

def liste_salles(request):
    return render(request, "visiteur/liste_salles.html")

def poubelles_vides(request):
    return render(request, "visiteur/poubelles_vides.html")

def ordi_dispo(request):
    return render(request, "visiteur/ordi_dispo.html")