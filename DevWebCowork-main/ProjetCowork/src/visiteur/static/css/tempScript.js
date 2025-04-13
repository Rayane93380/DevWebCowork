function updateTemperatures() {
    // Exemple d'objet pour les températures des salles
    const temperatures = {
        'Salle 101': Math.floor(Math.random() * (25 - 20 + 1)) + 20, // Température aléatoire entre 20°C et 25°C
        'Salle 102': Math.floor(Math.random() * (25 - 20 + 1)) + 20,
        'Salle 103': Math.floor(Math.random() * (25 - 20 + 1)) + 20
    };

    // Mise à jour des températures dans le tableau
    document.getElementById('temp-salle-101').textContent = temperatures['Salle 101'] + "°C";
    document.getElementById('temp-salle-102').textContent = temperatures['Salle 102'] + "°C";
    document.getElementById('temp-salle-103').textContent = temperatures['Salle 103'] + "°C";
}

// Mise à jour des températures toutes les 5 secondes (5000ms)
setInterval(updateTemperatures, 5000);

// Appel initial pour afficher les températures dès le chargement de la page
updateTemperatures();
