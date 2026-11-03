"""Ajoute les colonnes attendues par l'application aux anciennes bases SQLite."""

REQUIRED_COLUMNS = {
    "users": {"role": "TEXT NOT NULL DEFAULT 'producer'", "created_at": "TEXT NOT NULL DEFAULT ''"},
    "farms": {"locality": "TEXT"},
    "plots": {
        "planting_date": "TEXT",
        "latitude": "REAL",
        "longitude": "REAL",
        "geometry_geojson": "TEXT",
        "area_gps_ha": "REAL",
        "gps_accuracy": "REAL",
        "location_updated_at": "TEXT",
    },
    "tasks": {"due_date": "TEXT", "status": "TEXT NOT NULL DEFAULT 'À faire'"},
    "market_prices": {"region": "TEXT", "source": "TEXT NOT NULL DEFAULT 'Import utilisateur'"},
}


def ensure_legacy_columns(connection):
    """Complète les tables existantes sans toucher aux données déjà enregistrées."""
    for table, columns in REQUIRED_COLUMNS.items():
        existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if not existing:
            continue
        for column, definition in columns.items():
            if column not in existing:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
