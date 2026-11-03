# Assistant Gemini — révision 15

- Gemini est le seul moteur de réponse.
- Aucune réponse locale de secours n'est produite.
- Sans clé, l'interface demande de configurer `GEMINI_API_KEY`.
- En cas d'erreur API ou de réponse vide, l'interface signale l'indisponibilité sans inventer de conseil.
- La validation rejette les questions vides, sans imposer de plafond fixe de caractères dans le service.
- La clé reste côté serveur dans `.env`.
- Tests : `python -m unittest discover -s tests -v`.
