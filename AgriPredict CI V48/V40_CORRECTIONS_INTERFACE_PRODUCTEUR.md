# V40 — corrections de l'interface et de l'espace producteur

## Navigation
- Barre verte étendue à 100 % de la largeur, sans marge horizontale ni espace supérieur.
- Suppression de la mise en évidence permanente de l'onglet supérieur Accueil.
- Ajout d'un état vert temporaire au clic sur les boutons Retour et Accueil.

## Localisation des exploitations
- Ajout de champs distincts : région, département, ville/commune/village et quartier/hameau.
- Ajout de listes dépendantes alimentées par les localités déjà enregistrées dans le compte.
- Possibilité de saisir manuellement une localité absente des suggestions.
- Ajout de colonnes SQLite `department` et `neighborhood` via migration additive, sans supprimer les données existantes.
- Les informations département et quartier sont désormais enregistrées et réaffichées.

Limite importante : le dépôt ne contenait pas de référentiel national vérifié de tous les départements, villes, villages et quartiers de Côte d'Ivoire. Les suggestions sont donc basées sur les localités déjà saisies par l'utilisateur ; elles ne constituent pas un catalogue administratif exhaustif.

## Tableau de bord producteur
- Ajout d'une visualisation en barres de la répartition des cultures par superficie.
- Affichage du nombre de parcelles et de la superficie par culture.
- Les états sans parcelle restent informatifs.

## Préservé depuis V38/V39
- Distinction exploitation / parcelle.
- Doses de semences et d'engrais facultatives dans le simulateur.
- Une entrée d'estimation dans Prévisions, Production conservant le suivi producteur.
- Liaison carte/superficie déjà présente dans le code V39.

## Vérifications
- 14 fichiers Python compilés.
- 18 tests automatisés réussis.
- Analyse syntaxique Jinja réussie pour les principaux templates.
- Test d'initialisation réel de Flask/SQLite non exécuté dans cet environnement : Flask n'y est pas installé.
- Aucun test navigateur réel effectué.
