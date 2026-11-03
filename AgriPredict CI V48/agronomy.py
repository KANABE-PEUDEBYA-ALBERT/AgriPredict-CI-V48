"""Connaissances de départ validables : elles complètent l'IA, sans la remplacer."""

CROP_GUIDES = {
    "Riz": {"etapes": ["Préparer et niveler la parcelle", "Utiliser des semences adaptées et saines", "Semer ou repiquer", "Suivre l'eau et désherber tôt", "Observer les ravageurs chaque semaine", "Récolter à maturité puis sécher avant stockage"], "risques": "Surveillez les feuilles jaunissantes, les dégâts de tiges et les adventices. Vérifiez d'abord l'eau, le sol et les symptômes avant tout traitement."},
    "Maïs": {"etapes": ["Préparer le sol", "Semer avec un espacement régulier", "Désherber tôt", "Suivre la croissance et les ravageurs", "Récolter puis sécher correctement"], "risques": "Inspectez les feuilles et le cœur des plants pour détecter tôt les dégâts d'insectes."},
    "Manioc": {"etapes": ["Choisir des boutures saines", "Préparer le terrain", "Planter à espacement régulier", "Désherber pendant l'installation", "Récolter selon la variété"], "risques": "Écartez les boutures présentant des symptômes et demandez un avis technique en cas de mosaïque ou de déformation."},
    "Arachide": {"etapes": ["Préparer un sol meuble", "Semer des graines saines", "Désherber tôt", "Surveiller l'humidité", "Récolter et sécher soigneusement"], "risques": "Le séchage et le stockage sont essentiels pour éviter les pertes et les moisissures."},
    "Oignon": {"etapes": ["Préparer la pépinière", "Repiquer", "Arroser régulièrement sans excès", "Désherber", "Récolter puis sécher les bulbes"], "risques": "Surveillez les taches sur feuilles et évitez l'humidité excessive."},
    "Mil": {"etapes": ["Préparer le sol", "Semer au début de la saison adaptée", "Désherber précocement", "Surveiller les ravageurs", "Récolter et sécher les épis"], "risques": "L'observation précoce des feuilles et épis permet d'agir avant une perte importante."},
    "Cacao": {"etapes": ["Entretenir les arbres et l'ombrage", "Assainir la parcelle", "Surveiller cabosses et feuilles", "Récolter les cabosses mûres", "Fermenter et sécher correctement"], "risques": "Les maladies et ravageurs doivent être confirmés localement avant toute intervention."},
}

# Jours indicatifs après semis/plantation. Les échéances pourront ensuite être
# ajustées par région ou par un conseiller agronome partenaire.
CAMPAIGN_TASKS = {
    "Riz": [(0, "Préparer la parcelle et vérifier les semences"), (7, "Vérifier la levée et l'eau"), (21, "Désherber et observer les ravageurs"), (45, "Contrôler l'état nutritionnel et sanitaire"), (90, "Préparer la récolte et le séchage")],
    "Maïs": [(0, "Vérifier le semis et la levée"), (15, "Premier désherbage"), (35, "Observer feuilles et cœur des plants"), (70, "Préparer la récolte et le séchage")],
    "Mil": [(0, "Vérifier la levée"), (18, "Désherber précocement"), (40, "Observer les épis et ravageurs"), (85, "Préparer récolte et séchage")],
    "Manioc": [(0, "Vérifier la reprise des boutures"), (30, "Désherber la parcelle"), (90, "Observer les symptômes sur feuilles"), (270, "Évaluer la maturité avant récolte")],
    "Arachide": [(0, "Vérifier la levée"), (20, "Désherber tôt"), (45, "Contrôler l'humidité et les feuilles"), (100, "Préparer récolte et séchage")],
    "Oignon": [(0, "Surveiller la reprise après repiquage"), (14, "Désherber et vérifier l'arrosage"), (35, "Observer les feuilles"), (85, "Préparer récolte et séchage des bulbes")],
    "Cacao": [(0, "Assainir la parcelle et vérifier l'ombrage"), (30, "Observer cabosses et feuilles"), (60, "Ramasser les cabosses mûres"), (65, "Organiser fermentation et séchage")],
}


def local_answer(product: str | None) -> str:
    guide = CROP_GUIDES.get(product or "")
    if not guide:
        return "Choisissez une culture afin de recevoir ses étapes générales."
    return (f"Pour le {product} : " + " ; ".join(guide["etapes"]) + ".\n\n" + guide["risques"] + "\n\nPour les pesticides ou engrais : ne choisissez ni dose ni marque sans diagnostic local, étiquette officielle et conseil d'un agent agricole.")
