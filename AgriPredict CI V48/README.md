# AgriPredict CI — Version 17

Application Flask d'accompagnement du producteur, du suivi de campagne à la préparation de la vente.

## Fonctionnalités

- Page d'accueil et tableau de bord du producteur.
- Gestion des exploitations, parcelles et tâches indicatives de campagne.
- Rappels affichés à la connexion pour les tâches dont l'échéance est arrivée ou dépassée.
- Consultation des prix importés avec leur date et leur source.
- Prévision indicative des prix à partir des observations datées réellement importées ; les résultats ne garantissent pas le prix futur.
- Marché agricole : annonces de récoltes publiées par les utilisateurs, filtrage par produit et mise à jour du statut de ses propres annonces.
- Simulateur de vente tenant compte des prix présents en base, du transport et du stockage.
- Conseiller agricole génératif via Gemini, avec contexte producteur et signalement explicite des erreurs de configuration ou d’API.

## Installation et lancement

1. Installez Python 3.10 ou plus récent.
2. Dans ce dossier, exécutez :
   ```bash
   python -m venv .venv
   # Windows : .venv\\Scripts\\activate
   # Linux/macOS : source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copiez `.env.example` en `.env`, puis configurez une valeur aléatoire pour `SECRET_KEY`. Pour activer Gemini, ajoutez `GEMINI_API_KEY` et vérifiez le nom du modèle dans `GEMINI_MODEL`. Ne partagez jamais le fichier `.env`.
4. Lancez `python app.py` puis ouvrez `http://127.0.0.1:5000`.

La base SQLite est initialisée au démarrage. Faites une copie de sauvegarde de `agripredict.db` avant les mises à jour.

## Importer des observations de prix

Connectez-vous avec un compte administrateur puis ouvrez la page d'import des prix (`/administration/import-prix`). Le CSV doit contenir les colonnes :

`date,produit,marche,region,prix_fcfa_kg`

N'importez que des observations dont la provenance et les dates peuvent être vérifiées. Le site n'extrait pas encore automatiquement les prix des marchés ; les annonces publiées par les utilisateurs sont distinctes des observations historiques.

## Marché agricole

Dans « Vendre / Acheter », un producteur connecté peut publier le produit, la quantité, le prix demandé, la région et un contact. Le contact est affiché publiquement dans l'annonce : ne renseignez que les coordonnées que vous souhaitez partager. Les annonces sont déclaratives et ne sont pas des transactions garanties ni des vendeurs vérifiés.

## Limites et déploiement

- Les calendriers de culture sont indicatifs et doivent être validés localement selon la variété, le climat et les pratiques.
- Les prévisions reposent uniquement sur les prix présents en base ; elles ne doivent pas être présentées comme des prédictions agricoles validées.
- Les rappels apparaissent dans l'interface après connexion ; l'envoi de SMS, WhatsApp, e-mail ou notifications push n'est pas encore configuré.
- Avant un déploiement public, ajouter une protection CSRF, une validation renforcée des contacts et des annonces, des contrôles anti-abus, des sauvegardes et une configuration de production (`debug=False`).


## Évolution architecture — bibliothèque de données

Cette version ajoute :
- `/donnees` : catalogue filtrable des observations de prix présentes dans SQLite ;
- `/donnees/export.csv` : export CSV avec les filtres actifs ;
- `/a-propos` : page décrivant la mission et les règles de transparence ;
- des entrées de menu vers la bibliothèque de données et la page À propos.

### État des modules selon l'architecture cible
- Présents dans l'application actuelle : accueil, prix, exploitations, parcelles/campagne, simulateur, vente/achat, prévision exploratoire, conseiller, import des prix.
- Ajoutés dans cette version : bibliothèque de données filtrable, export CSV, page À propos.
- À construire dans une prochaine étape : tables normalisées `produit`, `pays`, `marche`, `source`, `serie`, `inflation`, `prevision`, `calendrier`, `note`; administration complète avec contrôle de complétude; routes JSON `/api/...`; graphiques Chart.js réutilisables; comparateur de marchés basé sur un coût de transport fixe documenté; tests automatisés de prévision et simulateur; export Excel.
- **Prévision et conseiller IA :** leur logique n'a pas été remaniée dans cette version, conformément à la décision de les traiter ultérieurement. Ne pas interpréter la prévision actuelle comme un modèle agronomique validé.

### Règles de données
Le catalogue affiche les observations enregistrées dans `market_prices`. Il ne crée pas de valeurs de remplacement. Avant d'utiliser les données pour des décisions, vérifier la provenance, la date, l'unité et la couverture géographique.

## Sécurité de l'import des prix

L'import CSV de prix est réservé aux comptes dont `users.role` vaut explicitement `admin`. Les comptes créés normalement restent des producteurs. Pour autoriser un compte de confiance, connectez-vous à la base SQLite avec un outil d'administration et changez son rôle après avoir vérifié son identité. Ne donnez jamais ce rôle à un producteur ordinaire. Le lien Administration n'apparaît qu'à un compte administrateur.

L'import accepte les cultures déjà configurées dans l'application, limite les fichiers à 8 Mo et 100 000 lignes, vérifie les dates et prix positifs, ignore les doublons et signale les lignes ignorées. La provenance du fichier CSV est conservée dans la colonne `source`.

## État de cette révision

- Renforcement de l'accès à l'import : rôle administrateur requis, pas seulement une connexion.
- Contrôles de format, volume, cultures, dates, prix et doublons pour les imports CSV.
- Lien Administration visible uniquement aux administrateurs.
- Le modèle de prévision et le Conseiller IA n'ont pas été modifiés.
- Vérification syntaxique Python effectuée. Le test de démarrage Flask n'a pas pu être exécuté dans l'environnement de travail, car Flask n'y est pas installé ; le fonctionnement complet doit donc encore être testé après installation de `requirements.txt`.


## Accès administrateur et sécurité des inscriptions

Les inscriptions publiques créent toujours des comptes producteurs. Une adresse inscrite dans `ADMIN_EMAILS` ne devient pas automatiquement administratrice : cela empêcherait un tiers de réclamer un compte administrateur en saisissant simplement l'adresse d'une autre personne.

1. Dans `.env`, inscrivez les adresses administratives autorisées : `ADMIN_EMAILS=adresse1@domaine.ci,adresse2@domaine.ci`.
2. Chaque personne crée son compte normalement.
3. Après vérification de son identité par l'exploitant, promouvez son compte depuis le dossier du projet avec `python promote_admin.py adresse1@domaine.ci`.
4. Répétez l'opération pour la seconde adresse.

La route d'import vérifie à la fois le rôle `admin` enregistré dans la base et la présence de l'adresse dans `ADMIN_EMAILS`. Retirer une adresse de `.env` bloque immédiatement ses accès administrateur. Gardez `.env` privé et ne publiez jamais les mots de passe ou les clés API.

## Repères agricoles EAA 2024-2025

Une page publique `/donnees-agricoles` présente des indicateurs agrégés du rapport d'analyse de l'Enquête Agricole Annuelle 2024-2025. Elle sert de contexte descriptif uniquement : ces chiffres nationaux ne sont pas des prix de marché et ne sont pas utilisés par le modèle de prévision.

Source : [Archive nationale des données statistiques — EAA 2024-2025](https://nada.anstat.ci/index.php/catalog/34/). Rapport d'analyse des résultats, janvier 2026. Les chiffres sont transcrits dans `app.py` et doivent être revérifiés à chaque mise à jour du rapport.

## Module de prévision de récolte

- Route : `/prevision-recolte` (connexion requise).
- Cultures proposées : maïs, riz, manioc, igname, plantain et cacao.
- Le fichier `data_agricole_simulee.xlsx` sert uniquement aux essais techniques ; il n'est jamais utilisé pour calculer une prévision affichée à un producteur.
- Le module dispose d’un corpus intégré de 100 000 observations simulées pour le mode expérimental. Les résultats sont explicitement signalés comme artificiels et non validés sur le terrain. Dès que `data/observations_reelles_recoltes.csv` contient au moins 100 observations réelles contrôlées, le mode réel devient prioritaire.
- Le module est séparé de la prévision des prix et du conseiller agricole Gemini.


## Assistant agricole Gemini

L’onglet **Assistant agricole** accompagne le producteur sur les cultures, les tâches de campagne, la prévention des problèmes phytosanitaires et la préparation de la vente. Lorsqu’un producteur est connecté, le serveur transmet au modèle les informations utiles déjà enregistrées pour ses parcelles, ses tâches et les prix de la culture sélectionnée. L’assistant ne doit pas inventer de prix et rappelle les limites des conseils agronomiques.

Pour activer Gemini, copiez `.env.example` vers `.env`, puis renseignez `GEMINI_API_KEY` avec une clé obtenue auprès de Google AI Studio. La clé reste uniquement côté serveur ; ne la placez jamais dans un template HTML ou un fichier JavaScript. `GEMINI_MODEL` peut être modifié selon les modèles accessibles à votre compte. Sans clé valide ou en cas d’indisponibilité de Gemini, le site affiche un message explicite et ne génère aucune réponse locale de remplacement. Les questions ne sont pas tronquées par une limite applicative arbitraire ; la taille maximale d’une requête HTTP reste déterminée par la configuration serveur.

Le prototype de prévision de récolte utilise des données simulées : ses résultats ne sont pas des garanties de rendement réel.


## Carte agricole AgriMap Africa

Le module `/carte-agricole` est réservé aux producteurs connectés. Il propose un fond OpenStreetMap et un fond satellite Esri, la géolocalisation navigateur après autorisation, l'enregistrement d'un point GPS et le dessin facultatif d'un polygone GeoJSON. Les coordonnées et contours sont associés aux parcelles existantes. La migration SQLite ajoute les colonnes nécessaires sans supprimer les données antérieures.

Le GPS nécessite généralement HTTPS (ou localhost). Les tuiles cartographiques et la géolocalisation exigent une connexion Internet. La superficie calculée à partir du contour est une approximation géodésique et ne remplace pas un relevé cadastral. La détection automatique fiable des régions nécessite l'ajout d'un jeu de limites administratives GeoJSON officiel ; dans cette version, la région déclarée dans l'exploitation reste conservée et aucune frontière administrative n'est inventée. La carte n'effectue pas encore de prédiction agricole à partir des coordonnées seules : il faut d'abord connecter des données climatiques, pédologiques et agricoles observées, puis valider les modèles.


## Historique — structure agronomique et assistant Gemini

- Migration SQLite additive `migrations/agricultural_core.py`, lancée par `init_db()` au démarrage.
- Sauvegardez `agripredict.db` avant toute mise à jour ; la migration ajoute des tables sans supprimer les anciennes tables ni leurs enregistrements.
- Nouvelles tables : catalogue des cultures, variétés, campagnes, phases culturales, observations de phases, analyses de sol, observations climatiques, pratiques agricoles, résultats de récolte, sources et lots d’import.
- Cultures prioritaires identifiées dans le catalogue : riz, maïs, manioc et cacao. Les cultures historiques sont conservées.
- Traçabilité de la provenance : observations réelles, simulées, externes ou déclarées par le producteur. Une donnée manquante n’est jamais assimilée à zéro.
- Assistant : suppression de la limite fixe de longueur, suppression de toute réponse locale de secours, messages explicites si Gemini n’est pas configuré ou indisponible.
- Les données synthétiques du fichier Excel restent expérimentales et ne constituent pas une validation sur le terrain.

### Configuration Gemini

Créer un fichier `.env` à partir de `.env.example`, renseigner `GEMINI_API_KEY`, puis redémarrer le serveur. Ne jamais publier `.env`.

## Module de Machine Learning — rendements agricoles

Le module `ml_harvest.py` compare six approches : baseline médiane, Ridge, Random Forest, Extra Trees, Gradient Boosting et HistGradientBoosting. Les variables explicatives sont contrôlées : culture, région, sol, semences, irrigation, pratique agricole, pluviométrie et engrais. L'identifiant d'exploitation, la production totale (qui dépend mathématiquement du rendement et de la superficie), la campagne codée et la provenance ne sont pas utilisées comme variables prédictives.

### Données simulées : mode expérimental clairement signalé

Le fichier `data/recoltes_simulees_100000.csv` contient 100 000 lignes artificielles. Il permet au producteur de parcourir et tester le module d'estimation lorsque l'historique réel contrôlé n'est pas encore disponible. Les résultats sont systématiquement présentés comme des estimations expérimentales issues de données simulées ; ils ne sont pas des performances agronomiques réelles et ne constituent pas une prévision validée pour un champ. Le fichier historique `data_agricole_simulee.xlsx` reste réservé au benchmark technique.

### Activer les prédictions réelles

Ajouter les observations vérifiées dans `data/observations_reelles_recoltes.csv`, en reprenant l'en-tête du fichier `data/observations_reelles_recoltes_exemple.csv`. Une ligne correspond à une parcelle/campagne récoltée ; `rendement_t_ha` doit être calculé à partir de la production réellement pesée et de la superficie réellement récoltée. Les données doivent être issues d'observations documentées, sans valeurs inventées pour compléter les cases.

Le mode réel exige au moins 100 observations réelles valides. Il compare les algorithmes sur un test indépendant, utilise une validation croisée sur le train, puis réentraîne le meilleur modèle sur l’ensemble des observations réelles. Si ces données ne sont pas disponibles, le module utilise le corpus intégré `data/recoltes_simulees_100000.csv` et affiche un avertissement visible : ce mode expérimental ne mesure pas la performance sur des exploitations réelles.

### Limites méthodologiques

Le protocole actuel est une première base sérieuse, pas une validation scientifique finale. Avant mise en production agricole, il faudra accumuler plusieurs campagnes et régions, réaliser une validation temporelle (entraîner sur les campagnes anciennes et tester sur une campagne ultérieure), contrôler les biais de collecte et publier des résultats par culture. Une validation croisée aléatoire ne remplace pas ce test temporel.


## Version 17 — corrections et contrôles

- Ajout d'une migration additive des anciennes bases SQLite : les colonnes manquantes des tables historiques (`plots`, `farms`, `tasks`, `market_prices`, `users`) sont ajoutées sans effacer les enregistrements existants.
- Les inscriptions publiques attribuent uniquement le rôle producteur. La promotion administrateur est une opération explicite après vérification de l'identité, avec `promote_admin.py`, et l'accès reste limité aux adresses listées dans `ADMIN_EMAILS`.
- Correction de la lecture des fichiers Excel de récoltes réelles : le contrôle de provenance fonctionne désormais pour CSV et Excel.
- Sécurisation du découpage apprentissage/test lorsque le nombre de cultures rend une stratification impossible.
- Vérifications réalisées : compilation Python, tests unitaires, analyse de syntaxe des 19 modèles HTML, contrôle des destinations de navigation, syntaxe JavaScript et test ZIP.
- Le lancement Flask complet doit être confirmé sur un poste disposant des dépendances du fichier `requirements.txt` ; l'environnement de contrôle utilisé pour cette révision ne disposait pas de Flask ni du SDK Gemini et ne pouvait pas accéder à Internet pour les installer.


## Configuration de Gemini

Dans le fichier `.env`, renseignez `GEMINI_API_KEY`, puis utilisez `GEMINI_MODEL=gemini-3.5-flash-lite`. Le service essaie automatiquement `gemini-3.7-flash` si le modèle prioritaire échoue. Le délai maximal par appel est réglable avec `GEMINI_TIMEOUT_SECONDS` (25 secondes par défaut). Les modèles doivent être disponibles pour le projet Google AI Studio associé à la clé.
