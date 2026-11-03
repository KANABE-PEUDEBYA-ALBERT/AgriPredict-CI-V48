from production_simulator import calculate_input_totals, validate_area
import pytest

def test_totals_are_area_times_per_hectare_rates():
    result = calculate_input_totals(12, 18.5, 150)
    assert result["seed_total_kg"] == 222.0
    assert result["fertilizer_total_kg"] == 1800.0

def test_maximum_area_is_1000_hectares():
    assert validate_area(1000) == 1000.0

@pytest.mark.parametrize("area", [0, -1, 1000.01, float("inf"), float("nan")])
def test_invalid_area_is_rejected(area):
    with pytest.raises(ValueError):
        validate_area(area)

def test_zero_fertilizer_is_allowed():
    result = calculate_input_totals(2, 10, 0)
    assert result["fertilizer_total_kg"] == 0


def test_polygon_area_ha_for_one_hectare_square():
    from production_simulator import polygon_area_ha
    # Carré d'environ 100 m x 100 m près de l'équateur.
    geometry = {"type": "Polygon", "coordinates": [[[0, 0], [0.0008983, 0], [0.0008983, 0.0008983], [0, 0.0008983], [0, 0]]]}
    area = polygon_area_ha(geometry)
    assert 0.98 <= area <= 1.02


def test_polygon_area_rejects_open_ring():
    import pytest
    from production_simulator import polygon_area_ha
    geometry = {"type": "Polygon", "coordinates": [[[0, 0], [0.001, 0], [0.001, 0.001], [0, 0.001]]]}
    with pytest.raises(ValueError):
        polygon_area_ha(geometry)
