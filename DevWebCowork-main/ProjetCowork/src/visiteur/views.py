from django.shortcuts import render


# Create your views here.
def visiteur_index(request):
    return render(request, "visiteur/visiteur_index.html")

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