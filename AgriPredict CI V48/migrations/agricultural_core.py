"""Migration additive du noyau agronomique AgriPredict CI.
Conserve les tables et lignes historiques. Exécution idempotente.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "agripredict.db"

CROPS = [
    ("riz", "Riz", 1, "annuelle"),
    ("mais", "Maïs", 1, "annuelle"),
    ("manioc", "Manioc", 1, "pluriannuelle_courte"),
    ("cacao", "Cacao", 1, "perenne"),
    ("mil", "Mil", 0, "annuelle"),
    ("arachide", "Arachide", 0, "annuelle"),
    ("oignon", "Oignon", 0, "annuelle"),
    ("igname", "Igname", 0, "annuelle"),
    ("plantain", "Plantain", 0, "pluriannuelle"),
]

PHASES = {
    "riz": [("preparation", "Préparation du terrain"), ("semis", "Semis ou repiquage"), ("croissance", "Croissance végétative"), ("reproduction", "Montaison et floraison"), ("maturation", "Maturation"), ("recolte", "Récolte")],
    "mais": [("preparation", "Préparation du terrain"), ("semis", "Semis"), ("croissance", "Croissance végétative"), ("floraison", "Floraison"), ("remplissage", "Remplissage des grains"), ("recolte", "Récolte")],
    "manioc": [("preparation", "Préparation du terrain"), ("plantation", "Plantation des boutures"), ("reprise", "Reprise et installation"), ("croissance", "Développement des racines"), ("recolte", "Récolte")],
    "cacao": [("installation", "Installation de la cacaoyère"), ("croissance", "Croissance et entretien"), ("floraison", "Floraison et nouaison"), ("fructification", "Développement des cabosses"), ("recolte", "Récolte et écabossage"), ("post_recolte", "Fermentation et séchage")],
}


def slug(value: str) -> str:
    value = value.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ô", "o").replace("ï", "i")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_") or "culture"


def migrate(db_path: Path = DB_PATH) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Base SQLite introuvable : {db_path}")
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY, applied_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY, source_type TEXT NOT NULL CHECK(source_type IN ('observed','simulated','external','user_declared')),
            name TEXT NOT NULL, organization TEXT, reference_url TEXT, description TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS crop_catalog (
            id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL UNIQUE,
            is_priority INTEGER NOT NULL DEFAULT 0 CHECK(is_priority IN (0,1)), crop_cycle TEXT
        );
        CREATE TABLE IF NOT EXISTS crop_varieties (
            id INTEGER PRIMARY KEY, crop_id INTEGER NOT NULL, name TEXT NOT NULL,
            maturity_days INTEGER CHECK(maturity_days IS NULL OR maturity_days > 0), description TEXT,
            source_id INTEGER, UNIQUE(crop_id,name),
            FOREIGN KEY(crop_id) REFERENCES crop_catalog(id),
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY, plot_id INTEGER NOT NULL, crop_id INTEGER NOT NULL,
            variety_id INTEGER, campaign_name TEXT NOT NULL, start_date TEXT, expected_harvest_date TEXT,
            cultivated_area_ha REAL NOT NULL CHECK(cultivated_area_ha > 0), production_system TEXT,
            status TEXT NOT NULL DEFAULT 'planned' CHECK(status IN ('planned','active','completed','cancelled')),
            source_id INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(plot_id) REFERENCES plots(id) ON DELETE CASCADE,
            FOREIGN KEY(crop_id) REFERENCES crop_catalog(id),
            FOREIGN KEY(variety_id) REFERENCES crop_varieties(id),
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS crop_phases (
            id INTEGER PRIMARY KEY, crop_id INTEGER NOT NULL, phase_code TEXT NOT NULL,
            phase_name TEXT NOT NULL, sequence_no INTEGER NOT NULL,
            UNIQUE(crop_id,phase_code), UNIQUE(crop_id,sequence_no),
            FOREIGN KEY(crop_id) REFERENCES crop_catalog(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS phase_observations (
            id INTEGER PRIMARY KEY, campaign_id INTEGER NOT NULL, phase_id INTEGER NOT NULL,
            observed_on TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'observed', notes TEXT,
            source_id INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
            FOREIGN KEY(phase_id) REFERENCES crop_phases(id),
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS soil_analyses (
            id INTEGER PRIMARY KEY, plot_id INTEGER NOT NULL, sampled_on TEXT NOT NULL,
            soil_type TEXT, ph REAL CHECK(ph IS NULL OR (ph >= 0 AND ph <= 14)),
            organic_matter_pct REAL, nitrogen_mg_kg REAL, phosphorus_mg_kg REAL, potassium_mg_kg REAL,
            laboratory TEXT, notes TEXT, source_id INTEGER,
            FOREIGN KEY(plot_id) REFERENCES plots(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS climate_observations (
            id INTEGER PRIMARY KEY, campaign_id INTEGER, plot_id INTEGER, observed_at TEXT NOT NULL,
            rainfall_mm REAL CHECK(rainfall_mm IS NULL OR rainfall_mm >= 0),
            temperature_min_c REAL, temperature_max_c REAL, humidity_pct REAL CHECK(humidity_pct IS NULL OR (humidity_pct BETWEEN 0 AND 100)),
            source_id INTEGER, notes TEXT,
            CHECK(campaign_id IS NOT NULL OR plot_id IS NOT NULL),
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
            FOREIGN KEY(plot_id) REFERENCES plots(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS agricultural_practices (
            id INTEGER PRIMARY KEY, campaign_id INTEGER NOT NULL, phase_observation_id INTEGER,
            practiced_on TEXT NOT NULL, practice_type TEXT NOT NULL, description TEXT,
            input_name TEXT, input_quantity REAL, input_unit TEXT, labor_days REAL,
            irrigation_used INTEGER CHECK(irrigation_used IS NULL OR irrigation_used IN (0,1)),
            source_id INTEGER,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
            FOREIGN KEY(phase_observation_id) REFERENCES phase_observations(id),
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS harvest_results (
            id INTEGER PRIMARY KEY, campaign_id INTEGER NOT NULL UNIQUE, harvested_on TEXT NOT NULL,
            harvested_area_ha REAL NOT NULL CHECK(harvested_area_ha > 0), production_kg REAL NOT NULL CHECK(production_kg >= 0),
            quality_grade TEXT, losses_kg REAL CHECK(losses_kg IS NULL OR losses_kg >= 0),
            source_id INTEGER, notes TEXT,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
            FOREIGN KEY(source_id) REFERENCES data_sources(id)
        );
        CREATE TABLE IF NOT EXISTS import_batches (
            id INTEGER PRIMARY KEY, file_name TEXT NOT NULL, file_format TEXT NOT NULL,
            imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, imported_by INTEGER,
            row_count INTEGER NOT NULL DEFAULT 0, accepted_count INTEGER NOT NULL DEFAULT 0,
            rejected_count INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'completed',
            FOREIGN KEY(imported_by) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_campaigns_plot ON campaigns(plot_id);
        CREATE INDEX IF NOT EXISTS idx_phase_obs_campaign ON phase_observations(campaign_id, observed_on);
        CREATE INDEX IF NOT EXISTS idx_climate_campaign_date ON climate_observations(campaign_id, observed_at);
        CREATE INDEX IF NOT EXISTS idx_soil_plot_date ON soil_analyses(plot_id, sampled_on);
        CREATE INDEX IF NOT EXISTS idx_harvest_date ON harvest_results(harvested_on);
        """)
        for code, name, priority, cycle in CROPS:
            connection.execute("INSERT OR IGNORE INTO crop_catalog(code,name,is_priority,crop_cycle) VALUES(?,?,?,?)", (code,name,priority,cycle))
        # Reprend aussi les cultures historiques présentes dans les parcelles, sans supprimer ni renommer leur texte.
        try:
            old_products = connection.execute("SELECT DISTINCT product FROM plots WHERE product IS NOT NULL AND TRIM(product) <> ''").fetchall()
        except sqlite3.OperationalError:
            old_products = []
        for (name,) in old_products:
            connection.execute("INSERT OR IGNORE INTO crop_catalog(code,name,is_priority,crop_cycle) VALUES(?,?,0,'non_precise')", (slug(name), name))
        for crop_code, phases in PHASES.items():
            crop = connection.execute("SELECT id FROM crop_catalog WHERE code=?", (crop_code,)).fetchone()
            for order, (phase_code, phase_name) in enumerate(phases, start=1):
                connection.execute("INSERT OR IGNORE INTO crop_phases(crop_id,phase_code,phase_name,sequence_no) VALUES(?,?,?,?)", (crop[0],phase_code,phase_name,order))
        connection.execute("INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(?,?)", ("001_agricultural_core", datetime.utcnow().isoformat(timespec="seconds")))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
    print("Migration 001_agricultural_core appliquée.")
