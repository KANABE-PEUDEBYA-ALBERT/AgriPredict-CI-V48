"""Programmes pratiques par culture. Les périodes sont indicatives et doivent être adaptées au climat, à la variété et au système de culture."""

CROP_PROGRAMS = {
    "Riz": {
        "cycle": "Environ 3 à 6 mois selon la variété, la zone et le mode de culture.",
        "before": [
            ("4 à 6 semaines avant", "Choisir la parcelle", "Privilégier une parcelle adaptée au système choisi (pluvial ou irrigué), accessible et avec une maîtrise suffisante de l'eau. Observer les risques d'inondation et de drainage."),
            ("3 à 4 semaines avant", "Défricher et préparer", "Débroussailler, retirer les obstacles et organiser l'évacuation des résidus. Labourer selon l'état du sol et les pratiques locales."),
            ("1 à 2 semaines avant", "Préparer le sol et les semences", "Pour une parcelle irriguée, préparer le nivellement et les diguettes si nécessaire. Choisir des semences saines et adaptées à la zone. Prévoir pépinière ou semis direct.")
        ],
        "during": [
            ("Semis / repiquage", "Installer la culture", "Respecter les recommandations de la variété et du mode de culture. En pépinière, repiquer des plants vigoureux au stade recommandé localement."),
            ("7 à 15 jours après installation", "Contrôler la reprise", "Vérifier la levée ou la reprise, les manques, l'eau et les dégâts éventuels. Remplacer les manques lorsque cela reste pertinent."),
            ("15 à 30 jours", "Premier désherbage", "Désherber tôt, avant que les adventices ne concurrencent fortement le riz. La date dépend du semis direct ou du repiquage."),
            ("30 à 60 jours", "Suivre la croissance", "Observer chaque semaine les feuilles, les tiges, les adventices et l'état hydrique. Appliquer la fertilisation uniquement selon les recommandations locales et l'état de la parcelle."),
            ("Montaison et floraison", "Protéger la période sensible", "Éviter les stress hydriques. Surveiller les symptômes inhabituels et faire confirmer toute maladie ou attaque avant intervention."),
            ("Maturation", "Préparer la récolte", "Surveiller le remplissage et la maturité des grains. Organiser la main-d'œuvre, le transport, l'aire de séchage et le stockage.")
        ],
        "harvest": "Récolter lorsque la majorité des grains a atteint la maturité recommandée pour la variété. Sécher proprement, réduire les impuretés et stocker à l'abri de l'humidité et des ravageurs.",
        "watch": "Adventices, manque ou excès d'eau, jaunissement, dégâts sur feuilles et tiges, oiseaux et qualité du séchage. Faire identifier localement les symptômes avant tout traitement."
    },
    "Maïs": {
        "cycle": "Environ 3 à 5 mois selon la variété et la saison.",
        "before": [
            ("2 à 4 semaines avant", "Choisir la parcelle", "Choisir un terrain bien drainé, accessible et adapté à la saison. Éviter les zones où l'eau stagne durablement."),
            ("1 à 3 semaines avant", "Défricher et labourer", "Défricher, retirer les obstacles et ameublir le sol selon les pratiques locales. Prévoir l'écoulement de l'eau."),
            ("Juste avant le semis", "Préparer les semences", "Choisir une variété adaptée à la zone et à la durée de la saison. Utiliser des semences saines et prévoir les besoins en intrants après conseil local.")
        ],
        "during": [
            ("Jour du semis", "Semer", "Semer lorsque l'humidité du sol est suffisante et que la période est favorable. Respecter l'espacement et la profondeur recommandés pour la variété."),
            ("5 à 10 jours", "Vérifier la levée", "Compter les plants levés, repérer les manques et vérifier les dégâts d'oiseaux, d'insectes ou de ruissellement."),
            ("2 à 3 semaines", "Premier sarclage", "Sarcler tôt pour limiter la concurrence des mauvaises herbes. Éviter de blesser les racines."),
            ("4 à 6 semaines", "Deuxième entretien", "Reprendre le désherbage si nécessaire, observer la vigueur et l'état nutritionnel. Toute fertilisation doit suivre les recommandations locales."),
            ("Avant et pendant la floraison", "Surveiller les plants", "Observer les feuilles, la tige et les panicules. Maintenir une humidité suffisante sans engorgement et surveiller les chenilles et autres ravageurs."),
            ("Remplissage des grains", "Préparer la récolte", "Surveiller le dessèchement des spathes et l'état des épis. Préparer le séchage et un stockage propre.")
        ],
        "harvest": "Récolter lorsque les épis sont mûrs et les grains suffisamment secs pour la méthode de stockage prévue. Sécher sur une surface propre et protéger contre l'humidité.",
        "watch": "Mauvaise levée, adventices, chenilles, feuilles décolorées, verse, humidité excessive et moisissures après récolte."
    },
    "Manioc": {
        "cycle": "Souvent 8 à 18 mois ou davantage selon la variété, l'usage et la zone.",
        "before": [
            ("2 à 4 semaines avant", "Choisir la parcelle", "Choisir un sol profond, meuble et bien drainé. Éviter les zones inondables et les sols très compactés."),
            ("1 à 3 semaines avant", "Défricher et préparer le terrain", "Défricher, retirer les souches gênantes et labourer ou ameublir selon le terrain. Former des buttes ou billons si cela convient au sol et au drainage."),
            ("Avant plantation", "Préparer les boutures", "Sélectionner des tiges saines, vigoureuses et provenant de plants sans symptômes. Préparer des boutures de longueur et d'âge adaptés aux recommandations locales.")
        ],
        "during": [
            ("Jour de plantation", "Planter les boutures", "Planter selon l'orientation et l'espacement recommandés localement. Éviter les boutures desséchées ou abîmées."),
            ("2 à 4 semaines", "Contrôler la reprise", "Vérifier le démarrage des bourgeons et remplacer les manques si nécessaire."),
            ("1 à 3 mois", "Sarcler et entretenir", "Désherber régulièrement pendant l'installation. Les premières semaines sont importantes pour limiter la concurrence des adventices."),
            ("3 à 6 mois", "Suivre la croissance", "Observer la vigueur, le feuillage et les symptômes de mosaïque ou de déformation. Maintenir la parcelle propre et limiter les blessures aux tiges."),
            ("6 mois et plus", "Suivre le développement des racines", "Contrôler l'état général et adapter l'entretien à la pression des adventices et aux besoins de la parcelle."),
            ("Avant récolte", "Vérifier la maturité", "Tenir compte de la variété, de l'objectif de vente ou de transformation et des débouchés. Échelonner la récolte si nécessaire.")
        ],
        "harvest": "Récolter à l'âge adapté à la variété et à l'utilisation prévue. Limiter les blessures, trier les racines et organiser rapidement le transport ou la transformation.",
        "watch": "Mosaïque, déformations, pourritures, cochenilles, acariens, boutures non vigoureuses et mauvais drainage. Faire confirmer les maladies avant toute intervention."
    },
    "Arachide": {
        "cycle": "Environ 3 à 5 mois selon la variété.",
        "before": [
            ("2 à 4 semaines avant", "Choisir la parcelle", "Préférer un sol meuble, bien drainé et facile à récolter. Éviter les sols très lourds et les zones engorgées."),
            ("1 à 3 semaines avant", "Préparer le terrain", "Défricher et ameublir le sol. Éviter les grosses mottes qui gênent la levée et le développement des gousses."),
            ("Avant semis", "Préparer les graines", "Choisir des graines saines, non moisies et adaptées à la zone. Conserver les graines à l'abri de l'humidité.")
        ],
        "during": [
            ("Jour du semis", "Semer", "Semer dans un sol suffisamment humide, à la profondeur et à l'espacement recommandés pour la variété."),
            ("5 à 10 jours", "Vérifier la levée", "Repérer les manques, les attaques et les dégâts de ruissellement."),
            ("2 à 3 semaines", "Sarcler", "Désherber tôt et avec précaution pour ne pas déraciner les jeunes plants."),
            ("4 à 6 semaines", "Entretenir", "Surveiller la floraison, la formation des gynophores et l'état du sol. Éviter les travaux qui perturbent la zone de formation des gousses."),
            ("Formation des gousses", "Surveiller la parcelle", "Observer les feuilles, les taches et l'humidité. Adapter l'entretien aux recommandations locales."),
            ("Fin de cycle", "Préparer l'arrachage", "Vérifier la maturité des gousses sur plusieurs plants avant de programmer la récolte.")
        ],
        "harvest": "Arracher au stade de maturité adapté, laisser sécher dans de bonnes conditions, trier et stocker au sec. Éviter les moisissures et l'humidité qui favorisent les aflatoxines.",
        "watch": "Taches foliaires, mauvaises herbes, sécheresse, pourriture des gousses et moisissures au séchage ou au stockage."
    },
    "Oignon": {
        "cycle": "Environ 3 à 5 mois après semis, selon la variété et le mode de production.",
        "before": [
            ("4 à 6 semaines avant repiquage", "Préparer la pépinière", "Choisir un emplacement ensoleillé, drainé et proche d'une source d'eau. Préparer un lit fin et propre."),
            ("3 à 4 semaines avant", "Préparer le champ", "Défricher, ameublir et niveler le sol. Prévoir des planches ou billons adaptés au drainage et à l'irrigation."),
            ("Avant repiquage", "Sélectionner les plants", "Retenir des plants sains et homogènes. Écarter ceux qui présentent des symptômes ou sont trop faibles.")
        ],
        "during": [
            ("Semis en pépinière", "Installer les semences", "Semer régulièrement et maintenir une humidité adaptée sans détremper le sol."),
            ("Après levée", "Entretenir la pépinière", "Désherber délicatement et surveiller les maladies. Préparer le champ avant que les plants soient prêts."),
            ("Repiquage", "Installer les plants", "Repiquer dans un sol humide, en respectant les espacements conseillés pour la variété."),
            ("1 à 3 semaines après repiquage", "Contrôler la reprise", "Vérifier les plants morts ou manquants, l'arrosage et les adventices."),
            ("Croissance des feuilles", "Désherber et arroser", "Désherber régulièrement. Maintenir une humidité régulière sans excès d'eau. Éviter de mouiller inutilement le feuillage."),
            ("Formation des bulbes", "Suivre les bulbes", "Observer le grossissement, l'état des feuilles et les signes de maladies. Adapter l'arrosage selon le stade et le sol."),
            ("Maturation", "Réduire l'eau et préparer", "Suivre le couchage naturel des feuilles et les signes de maturité. Préparer un lieu de séchage ventilé.")
        ],
        "harvest": "Récolter lorsque les bulbes sont mûrs selon la variété. Sécher ou ressuyer dans un endroit propre, sec et ventilé avant le stockage.",
        "watch": "Fonte des semis, thrips, taches foliaires, pourritures, arrosage excessif et mauvaise conservation."
    },
    "Mil": {
        "cycle": "Environ 3 à 5 mois selon la variété et la zone.",
        "before": [
            ("2 à 4 semaines avant", "Choisir la parcelle", "Choisir un terrain adapté à la saison des pluies, bien drainé et accessible."),
            ("1 à 3 semaines avant", "Défricher et préparer", "Défricher, ameublir le sol et organiser les lignes ou poquets selon les pratiques locales."),
            ("Avant semis", "Choisir les semences", "Utiliser une variété adaptée à la durée de la saison et des semences saines.")
        ],
        "during": [
            ("Jour du semis", "Semer", "Semer après une pluie suffisante et régulière, en respectant les recommandations locales."),
            ("5 à 10 jours", "Vérifier la levée", "Repérer les manques et les dégâts d'oiseaux ou d'insectes."),
            ("2 à 3 semaines", "Sarcler et éclaircir", "Désherber tôt et éclaircir si le peuplement est trop dense, selon le mode de semis."),
            ("4 à 6 semaines", "Deuxième entretien", "Contrôler les adventices et la vigueur des plants. Éviter les blessures aux racines."),
            ("Montaison et épiaison", "Surveiller les épis", "Observer les feuilles et les épis, surveiller les ravageurs et le stress hydrique."),
            ("Maturation", "Préparer la récolte", "Protéger les épis des oiseaux et préparer le séchage et le stockage.")
        ],
        "harvest": "Récolter à maturité, sécher soigneusement les épis ou grains et stocker dans un lieu sec et protégé.",
        "watch": "Oiseaux, adventices, chenilles, stress hydrique, moisissures et insectes de stockage."
    },
    "Cacao": {
        "cycle": "Culture pérenne : calendrier d'entretien organisé sur toute l'année, pas en jours après semis.",
        "before": [
            ("Avant installation", "Choisir le site", "Vérifier le sol, le drainage, l'accès à l'eau et l'adaptation de la zone. Prévoir l'ombrage et les arbres associés."),
            ("Avant plantation", "Préparer la parcelle", "Défricher sélectivement sans dégrader inutilement le couvert. Prévoir les lignes, les plants et les espèces d'ombrage."),
            ("Plantation", "Installer les jeunes cacaoyers", "Utiliser des plants sains et adaptés. Planter au début d'une période favorable en humidité, selon le calendrier local.")
        ],
        "during": [
            ("Premiers mois", "Suivre la reprise", "Remplacer les plants morts, protéger les jeunes plants et maintenir un ombrage adapté."),
            ("Tous les 1 à 2 mois", "Désherber et entretenir", "Contrôler les herbes concurrentes sans blesser les jeunes cacaoyers. Entretenir les accès et les zones de travail."),
            ("Toute l'année", "Gérer l'ombrage", "Éviter un ombrage excessif ou insuffisant. Adapter progressivement les arbres d'ombrage à la croissance des cacaoyers."),
            ("Chaque mois", "Observer les arbres", "Inspecter feuilles, troncs, fleurs et cabosses. Retirer les cabosses malades ou momifiées selon les pratiques recommandées."),
            ("Périodes de récolte", "Récolter les cabosses mûres", "Passer régulièrement, récolter les cabosses mûres et éviter de blesser les coussinets floraux."),
            ("Après récolte", "Fermenter et sécher", "Fermenter selon le volume et le protocole de qualité adopté, puis sécher uniformément sur une aire propre.")
        ],
        "harvest": "Récolter régulièrement les cabosses mûres. Respecter les étapes de fermentation et de séchage pour obtenir des fèves de bonne qualité.",
        "watch": "Pourriture brune, mirides, dessèchement, mauvais ombrage, cabosses malades et défauts de fermentation ou de séchage. Faire confirmer les problèmes par un conseiller local."
    }
}

# Compléments agronomiques documentés pour la Côte d'Ivoire.
# Les doses d'engrais ne sont volontairement pas uniformisées : elles dépendent
# du sol, de la variété, du précédent cultural et du système de production.
# Cultures supplémentaires présentes dans le catalogue agricole du projet.
CROP_PROGRAMS.setdefault("Igname", {
    "cycle": "Variable selon l'espèce, la variété et la date de plantation.",
    "before": [], "during": [],
    "harvest": "Récolter à maturité, manipuler sans blesser les tubercules et conserver dans un local ventilé.",
    "watch": "Pourritures, cochenilles, symptômes viraux et blessures des tubercules."
})
CROP_PROGRAMS.setdefault("Plantain", {
    "cycle": "Variable selon le matériel végétal, la variété, la saison et la conduite de la parcelle.",
    "before": [], "during": [],
    "harvest": "Récolter au stade adapté au marché et au transport. Éviter les chocs et organiser rapidement l'écoulement.",
    "watch": "Nématodes, cercosporiose, charançons, déficit hydrique et excès d'eau."
})

TECHNICAL_DETAILS = {
    "Riz": {
        "nutrition": [
            ("Fumure de fond", "Un engrais composé NPK adapté au riz peut apporter phosphore et potassium au démarrage. La formule et la quantité doivent suivre l'analyse du sol ou le conseil technique local."),
            ("Azote : urée", "L'urée est une source d'azote, mais elle ne convient pas automatiquement à toutes les parcelles. Le choix du produit et toute décision d'application doivent être confirmés par un conseiller agricole à partir du type de riz, de la variété et du diagnostic du sol."),
            ("Matière organique", "Le compost mûr et les résidus végétaux bien gérés contribuent à entretenir la matière organique du sol. Éviter d'enfouir des résidus mal décomposés juste avant l'installation.")
        ],
        "protection": [
            ("Adventices", "Désherber tôt et contrôler de nouveau avant que les mauvaises herbes ne montent en graines."),
            ("Pyriculariose et autres maladies", "Observer les lésions sur feuilles et panicules. Utiliser des semences saines, une variété adaptée et faire confirmer le diagnostic avant toute intervention."),
            ("Ravageurs", "Surveiller les dégâts sur feuilles, tiges et panicules. Préserver les ennemis naturels et demander un diagnostic local avant tout traitement phytosanitaire.")
        ],
        "sources": [("CNRA – Bien fertiliser le riz pluvial en Côte d'Ivoire", "https://cnra.ci/download/bien-fertiliser-le-riz-pluvial-en-cote-divoire/"), ("CNRA – Fiches techniques riz", "https://cnra.ci/nos-fiches-techniques/"), ("AfricaRice – RiceAdvice", "https://www.africarice.org/fr/innovations/riceadvice")]
    },
    "Maïs": {
        "nutrition": [
            ("Avant le semis", "Maintenir la matière organique avec du compost mûr et raisonner la fumure de fond à partir de la fertilité du sol."),
            ("Engrais composé NPK", "Le maïs a besoin d'azote, de phosphore et de potassium. Un engrais composé adapté peut être utilisé au démarrage selon les recommandations locales et l'analyse du sol."),
            ("Urée (azote)", "L'urée peut compléter les besoins en azote pendant la croissance, en particulier avant les phases de forte demande. Ne pas appliquer automatiquement la même quantité sur toutes les parcelles : le précédent cultural, le sol et la variété changent le besoin.")
        ],
        "protection": [
            ("Chenille légionnaire d'automne", "Inspecter régulièrement le cœur des jeunes plants et repérer les dégâts frais. Favoriser la surveillance précoce et faire confirmer l'identification."),
            ("Striga et adventices", "Pratiquer la rotation, éviter de laisser les adventices produire des graines et maintenir une parcelle propre au début du cycle."),
            ("Maladies et stockage", "Écarter les épis malades, sécher correctement les grains et stocker dans un lieu propre, sec et ventilé.")
        ],
        "sources": [("CNRA – Bien cultiver le maïs en Côte d'Ivoire", "https://cnra.ci/download/bien-cultiver-le-mais-en-cote-divoire/"), ("CNRA – Fiches techniques", "https://cnra.ci/nos-fiches-techniques/")]
    },
    "Manioc": {
        "nutrition": [
            ("Matière organique", "Le compost mûr et la restitution raisonnée des résidus aident à entretenir la fertilité et la structure du sol."),
            ("Azote et potassium", "Les travaux relayés par le FIRCA indiquent que la réponse du manioc à une fertilisation azotée et potassique dépend de la fertilité initiale. Un diagnostic du sol est donc nécessaire avant de choisir un engrais."),
            ("Phosphore", "Ne pas choisir une formule NPK au hasard : vérifier les besoins du sol et privilégier une recommandation tenant compte du potassium, de l'azote et du phosphore disponibles.")
        ],
        "protection": [
            ("Matériel végétal", "Utiliser des boutures issues de pieds sains et éviter de multiplier des plants présentant des symptômes de mosaïque ou de déformation."),
            ("Mosaïque et maladies", "Repérer les feuilles déformées ou panachées et retirer du circuit de multiplication les plants suspects. Faire confirmer le diagnostic."),
            ("Entretien", "Désherber pendant l'installation et surveiller les cochenilles, acariens et pourritures. Éviter les blessures inutiles aux tiges et aux racines.")
        ],
        "sources": [("CNRA – Fiches techniques manioc", "https://cnra.ci/nos-fiches-techniques/"), ("FIRCA – Filières banane plantain, igname et manioc", "https://firca.ci/wp-content/uploads/2026/05/FIRCA-et-les-Filieres-banane-plantain-Igname-et-Manioc.pdf")]
    },
    "Arachide": {
        "nutrition": [
            ("Avant semis", "Privilégier un sol meuble, bien drainé et suffisamment pourvu en calcium dans la zone de formation des gousses."),
            ("Phosphore et calcium", "Ces éléments sont importants pour la formation des gousses. La correction éventuelle dépend du pH et de l'analyse du sol ; ne pas appliquer une formule universelle."),
            ("Azote", "L'arachide est une légumineuse pouvant fixer une partie de l'azote grâce à ses nodosités. Éviter de décider d'un apport important d'azote sans diagnostic de la parcelle.")
        ],
        "protection": [
            ("Maladies foliaires", "Observer les taches sur feuilles et leur progression. Retirer les résidus fortement atteints et alterner les cultures lorsque c'est possible."),
            ("Formation des gousses", "Limiter les sarclages profonds après le début de la formation des gousses pour ne pas les endommager."),
            ("Aflatoxines", "Sécher rapidement et complètement les gousses, trier les produits moisis et conserver au sec. Ne pas mélanger les lots suspects aux lots sains.")
        ],
        "sources": [("CNRA – Fiches techniques arachide", "https://cnra.ci/nos-fiches-techniques/")]
    },
    "Oignon": {
        "nutrition": [
            ("Préparation du sol", "Incorporer de la matière organique bien décomposée avant l'installation. Éviter les apports de fumier frais au contact des plants."),
            ("Engrais composé", "L'oignon demande une nutrition équilibrée pendant l'installation et la formation du bulbe. Choisir une formule NPK adaptée au sol et à la variété avec un conseiller agricole."),
            ("Azote et potassium", "Le fractionnement des apports nutritifs peut être nécessaire selon le cycle et le mode d'irrigation. Un excès d'azote tardif peut retarder la maturation et nuire à la conservation.")
        ],
        "protection": [
            ("Thrips", "Inspecter le feuillage, surtout les jeunes feuilles, et surveiller les plages argentées ou déformations."),
            ("Maladies foliaires", "Espacer correctement les plants, limiter l'humidité persistante sur le feuillage et retirer les plants très atteints."),
            ("Pourritures", "Éviter les sols engorgés, réduire progressivement l'irrigation à l'approche de la maturité et bien ressuyer les bulbes avant stockage.")
        ],
        "sources": [("FIRCA – Filière oignon", "https://firca.ci/filieres-agricoles/oignon/"), ("FIRCA – Guides et manuels", "https://firca.ci/publications/guides-et-manuels/")]
    },
    "Mil": {
        "nutrition": [
            ("Matière organique", "Entretenir la fertilité par le compost mûr, les résidus végétaux et la rotation avec des légumineuses lorsque cela convient au système."),
            ("Engrais minéral", "Les besoins en azote et en phosphore varient selon la variété, le sol et le précédent cultural. Faire établir la formule et la quantité à partir d'un diagnostic local plutôt que reprendre une dose standard."),
            ("Suivi de la culture", "Surveiller la couleur et la vigueur des plants, mais confirmer toute carence par un diagnostic : un jaunissement peut aussi venir de l'eau, des racines ou d'une maladie.")
        ],
        "protection": [
            ("Striga et adventices", "Arracher les foyers de Striga avant la production de graines et pratiquer la rotation culturale."),
            ("Maladies", "Surveiller les symptômes foliaires et les épis, utiliser des semences saines et choisir des variétés adaptées à la zone."),
            ("Oiseaux et stockage", "Organiser la surveillance à l'approche de la maturité, sécher les grains et protéger le stock de l'humidité et des insectes.")
        ],
        "sources": [("CNRA – Fiches techniques mil et sorgho", "https://cnra.ci/nos-fiches-techniques/")]
    },
    "Cacao": {
        "nutrition": [
            ("Jeunes cacaoyers", "Prioriser l'installation, l'ombrage temporaire adapté, le paillage et la protection des racines. La fertilisation doit tenir compte de l'âge des plants."),
            ("Cacaoyers adultes", "Le CNRA dispose d'une fiche spécifique sur la fertilisation du cacaoyer adulte. Les formules doivent être choisies selon le diagnostic du sol et le contexte pédo-climatique ; une recette unique pour toutes les plantations serait inadaptée."),
            ("Matière organique", "Conserver les feuilles et résidus sains au sol et utiliser du compost mûr lorsque disponible. Éviter d'accumuler des cabosses malades dans la plantation.")
        ],
        "protection": [
            ("Pourriture brune", "Passer régulièrement dans la plantation, repérer les cabosses atteintes et appliquer les mesures d'assainissement recommandées par le conseil agricole local."),
            ("Mirides et insectes", "Observer les jeunes pousses, les rameaux et les cabosses. Faire identifier l'insecte avant de choisir une méthode de lutte."),
            ("Cocoa swollen shoot", "Surveiller les symptômes inhabituels et demander rapidement un diagnostic. Ne pas déplacer de matériel végétal provenant d'arbres suspects.")
        ],
        "sources": [("CNRA – Bien fertiliser le cacaoyer adulte", "https://cnra.ci/download/bien-fertiliser-le-cacaoyer-adulte-en-cote-divoire/"), ("CNRA – Fiches techniques cacao", "https://cnra.ci/nos-fiches-techniques/"), ("CIRAD – Fertilisation minérale du cacaoyer en Côte d'Ivoire", "https://publications.cirad.fr/une_notice.php?dk=564558")]
    },
    "Igname": {
        "cycle": "Le cycle dépend fortement de l'espèce, de la variété et de la date de plantation ; la fiche locale de variété doit primer.",
        "before": [
            ("Avant plantation", "Choisir la parcelle", "Choisir un sol profond, meuble et bien drainé. Prévoir des buttes adaptées au type de sol et à la variété."),
            ("Avant plantation", "Préparer les semenceaux", "Utiliser des semenceaux sains, homogènes et issus d'une source fiable. Écarter ceux qui présentent des signes de pourriture ou de maladie."),
            ("Mise en place", "Préparer les buttes", "Former les buttes ou billons selon les pratiques adaptées à la zone et organiser la plantation au début d'une période favorable en humidité.")
        ],
        "during": [
            ("Après levée", "Contrôler la reprise", "Vérifier la levée, remplacer les manques si cela reste possible et installer les tuteurs lorsque le type d'igname le nécessite."),
            ("Début de croissance", "Désherber", "Contrôler régulièrement les adventices sans blesser les tiges ni les racines."),
            ("Croissance", "Conduire les tiges", "Guider les tiges sur les supports et éviter qu'elles ne s'entremêlent au sol."),
            ("Tout le cycle", "Suivre la fertilité", "Maintenir la matière organique et adapter la fertilisation organique ou minérale à la parcelle."),
            ("Fin de cycle", "Préparer la récolte", "Observer le jaunissement et le dessèchement du feuillage, puis vérifier la maturité avant de récolter.")
        ],
        "nutrition": [
            ("Fumure organique", "Le compost mûr et les amendements organiques contribuent à la structure du sol et à l'alimentation de la culture."),
            ("Fertilisation minérale", "Le FIRCA rapporte des travaux sur l'optimisation de la nutrition azotée et potassique de l'igname. Le choix de la formule doit être précédé d'un diagnostic de fertilité."),
            ("Semenceaux", "La qualité sanitaire et la conservation des semenceaux sont aussi importantes que la fertilisation pour obtenir une bonne implantation.")
        ],
        "protection": [
            ("Semenceaux sains", "Sélectionner des semenceaux sains et éviter de replanter du matériel présentant des symptômes viraux ou des pourritures."),
            ("Cochenilles et maladies", "Surveiller les tiges et les tubercules, pratiquer l'assainissement du matériel végétal et faire confirmer les symptômes."),
            ("Adventices", "Désherber régulièrement pendant la phase d'installation et limiter la concurrence au début du cycle.")
        ],
        "harvest": "Récolter lorsque la maturité est atteinte et que le feuillage entre en sénescence. Manipuler les tubercules sans les blesser, ressuyer et conserver dans un local ventilé, à l'abri de l'humidité.",
        "watch": "Pourritures, cochenilles, symptômes viraux, blessures des tubercules et mauvaise conservation.",
        "sources": [("CNRA – Fiches techniques igname", "https://cnra.ci/nos-fiches-techniques/"), ("FIRCA – Filières banane plantain, igname et manioc", "https://firca.ci/wp-content/uploads/2026/05/FIRCA-et-les-Filieres-banane-plantain-Igname-et-Manioc.pdf")]
    },
    "Plantain": {
        "cycle": "Le délai entre plantation et première récolte varie selon le matériel végétal, la variété, la saison et la conduite de la parcelle.",
        "before": [
            ("Avant plantation", "Choisir le terrain", "Choisir un sol profond, fertile et bien drainé, avec une disponibilité en eau suffisante. Éviter les zones durablement inondées."),
            ("Avant plantation", "Choisir les plants", "Privilégier des rejets vigoureux et sains ou des vitroplants acclimatés provenant d'une pépinière fiable."),
            ("Installation", "Préparer la parcelle", "Préparer les trous et organiser l'espacement selon la variété, le matériel végétal et le système de culture.")
        ],
        "during": [
            ("Après plantation", "Contrôler la reprise", "Vérifier la reprise des plants, remplacer les plants morts et maintenir le sol propre."),
            ("Croissance", "Gérer les rejets", "Conserver les rejets nécessaires au renouvellement du pied et supprimer les rejets excédentaires selon le système de production."),
            ("Toute la croissance", "Entretenir le sol", "Pailler avec des résidus sains, maintenir la matière organique et éviter la concurrence des adventices."),
            ("Floraison", "Suivre le régime", "Surveiller le développement du régime, maintenir une alimentation hydrique régulière et éviter les blessures du pseudo-tronc."),
            ("Avant récolte", "Préparer la coupe", "Repérer le stade de maturité demandé par le marché et organiser la manutention pour limiter les chocs.")
        ],
        "nutrition": [
            ("Matière organique", "Le bananier plantain répond à une bonne gestion de la fertilité. Entretenir la matière organique du sol avec des résidus sains et du compost mûr."),
            ("Engrais minéral", "La fumure doit tenir compte de la densité de plantation, du type de plant, du sol et de la disponibilité en eau. Le FIRCA indique que les doses ont été étudiées pour des systèmes précis de haute densité : elles ne doivent pas être transposées automatiquement."),
            ("Eau et nutrition", "Une nutrition équilibrée ne compense pas un stress hydrique. Adapter l'irrigation à la saison, au sol et au stade de la plante.")
        ],
        "protection": [
            ("Nématodes", "Utiliser du matériel végétal sain, éviter de déplacer de la terre contaminée et surveiller l'état des racines et la vigueur des pieds."),
            ("Cercosporiose", "Observer les feuilles, retirer les feuilles très atteintes selon les pratiques locales et maintenir une bonne aération de la plantation."),
            ("Charançons et pourritures", "Surveiller les bases des plants et les résidus en décomposition. Faire confirmer le ravageur ou la maladie avant toute intervention.")
        ],
        "harvest": "Récolter au stade de maturité adapté au marché et au transport. Éviter les chocs, protéger les régimes et organiser rapidement l'écoulement.",
        "watch": "Nématodes, cercosporiose, charançons, déficit hydrique, excès d'eau et blessures des régimes.",
        "sources": [("CNRA – Bien cultiver la banane plantain en Côte d'Ivoire", "https://cnra.ci/nos-fiches-techniques/"), ("FIRCA – Filière banane plantain", "https://firca.ci/filieres-agricoles/banane-plantain/"), ("FIRCA – Filières banane plantain, igname et manioc", "https://firca.ci/wp-content/uploads/2026/05/FIRCA-et-les-Filieres-banane-plantain-Igname-et-Manioc.pdf")]
    }
}

for _crop, _details in TECHNICAL_DETAILS.items():
    CROP_PROGRAMS[_crop].update(_details)

# Références et rubriques nutrition/protection des cultures sans dose universelle.
for _crop, _guide in CROP_PROGRAMS.items():
    _guide.setdefault("nutrition", [("Fertilité du sol", "Faire analyser le sol et adapter les apports de matière organique et d'engrais aux besoins réels de la culture.")])
    _guide.setdefault("protection", [("Surveillance", "Observer régulièrement la parcelle, identifier précisément le problème et demander un diagnostic avant toute intervention phytosanitaire.")])
    _guide.setdefault("sources", [("CNRA – Fiches techniques", "https://cnra.ci/nos-fiches-techniques/")])
