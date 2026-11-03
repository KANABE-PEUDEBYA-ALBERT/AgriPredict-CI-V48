"""Calculs simples et contrôles du simulateur de production AgriPredict CI."""
import math

MAX_AREA_HA = 1000.0

def validate_area(area_ha):
    area = float(area_ha)
    if not math.isfinite(area) or not (0.01 <= area <= MAX_AREA_HA):
        raise ValueError("La superficie doit être comprise entre 0,01 et 1 000 hectares.")
    return area

def validate_rate(value, label, maximum):
    rate = float(value)
    if not math.isfinite(rate) or rate < 0 or rate > maximum:
        raise ValueError(f"La dose de {label} doit être comprise entre 0 et {maximum:g} kg/ha.")
    return rate

def calculate_input_totals(area_ha, seed_kg_ha, fertilizer_kg_ha):
    """Retourne les besoins totaux calculés à partir des doses par hectare."""
    area = validate_area(area_ha)
    seed_rate = validate_rate(seed_kg_ha, "semences", 500)
    fertilizer_rate = validate_rate(fertilizer_kg_ha, "engrais", 2000)
    return {
        "area_ha": area,
        "seed_rate_kg_ha": seed_rate,
        "fertilizer_rate_kg_ha": fertilizer_rate,
        "seed_total_kg": round(area * seed_rate, 1),
        "fertilizer_total_kg": round(area * fertilizer_rate, 1),
    }


def polygon_area_ha(geometry):
    """Calcule la superficie d'un polygone GeoJSON sur une sphère (hectares)."""
    if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
        raise ValueError("La parcelle sélectionnée doit être un polygone valide.")
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates or not isinstance(coordinates[0], list):
        raise ValueError("Le contour de la parcelle est incomplet.")
    ring = coordinates[0]
    if len(ring) < 4 or len(ring) > 500:
        raise ValueError("Le contour doit comporter au moins trois sommets et rester raisonnable.")
    points = []
    for pair in ring:
        if not isinstance(pair, (list, tuple)) or len(pair) < 2:
            raise ValueError("Coordonnées de parcelle invalides.")
        lon, lat = float(pair[0]), float(pair[1])
        if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("Coordonnées GPS hors limites.")
        points.append((math.radians(lon), math.radians(lat)))
    if points[0] != points[-1]:
        raise ValueError("Le contour de la parcelle doit être fermé.")
    radius = 6371008.8
    total = 0.0
    for i in range(len(points) - 1):
        lon1, lat1 = points[i]
        lon2, lat2 = points[i + 1]
        total += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
    area = abs(total * radius * radius / 2) / 10000
    if not math.isfinite(area) or not (0.001 <= area <= 100000):
        raise ValueError("La superficie calculée sur la carte est invalide.")
    return area
