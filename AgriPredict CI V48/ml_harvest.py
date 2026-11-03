"""Evaluation honnête et prédiction des rendements agricoles.

Le corpus synthétique intégré alimente uniquement le mode expérimental, clairement signalé.
Le mode réel reste prioritaire dès que 100 observations contrôlées sont disponibles.
"""
from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import TransformedTargetRegressor

BASE_DIR = Path(__file__).resolve().parent
SYNTHETIC_FILE = BASE_DIR / "data" / "recoltes_simulees_100000.csv"
REAL_FILE = BASE_DIR / "data" / "observations_reelles_recoltes.csv"
TARGET = "rendement_t_ha"
CATEGORICAL = ["culture", "region", "type_sol", "type_semences", "irrigation", "pratique_agricole"]
NUMERIC = ["pluviometrie_mm", "engrais_kg_ha"]
FEATURES = CATEGORICAL + NUMERIC
REQUIRED = FEATURES + [TARGET]
MIN_REAL_ROWS = 100

def _pipeline(model, scale=False):
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    prep = ColumnTransformer([
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CATEGORICAL),
        ("num", Pipeline(numeric_steps), NUMERIC),
    ])
    return Pipeline([("preparation", prep), ("modele", model)])

def candidate_models():
    return {
        "Baseline médiane": _pipeline(DummyRegressor(strategy="median")),
        "Ridge": _pipeline(Ridge(alpha=10.0), scale=True),
        "Random Forest": _pipeline(RandomForestRegressor(n_estimators=120, min_samples_leaf=3, max_features=0.8, random_state=2026, n_jobs=-1)),
        "Extra Trees": _pipeline(ExtraTreesRegressor(n_estimators=120, min_samples_leaf=3, max_features=0.8, random_state=2026, n_jobs=-1)),
        "Gradient Boosting": _pipeline(GradientBoostingRegressor(n_estimators=100, learning_rate=0.04, max_depth=2, loss="huber", random_state=2026)),
        "HistGradientBoosting": _pipeline(HistGradientBoostingRegressor(max_iter=100, learning_rate=0.05, l2_regularization=2.0, random_state=2026)),
    }

def load_dataset(path: Path, *, source: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fichier absent : {path}")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        raw = pd.read_excel(path, sheet_name="DONNEES_SIMULEES" if source == "synthetic" else 0)
    else:
        raw = pd.read_csv(path)
    if source == "real" and "origine_donnees" in raw.columns:
        origins = raw["origine_donnees"].fillna("").astype(str).str.lower()
        if origins.str.contains(r"simul|synthet|synthetiq", regex=True).any():
            raise ValueError("Le fichier réel contient une provenance simulée : entraînement opérationnel refusé.")
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError("Colonnes obligatoires absentes : " + ", ".join(missing))
    df = raw[REQUIRED].copy()
    for col in NUMERIC + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[TARGET])
    df = df[df[TARGET].between(0.05, 40)]
    if source == "real":
        if len(df) < MIN_REAL_ROWS:
            raise ValueError(f"Seulement {len(df)} récoltes réelles valides. Il en faut au moins {MIN_REAL_ROWS} pour commencer une évaluation prudente.")
    if df.empty:
        raise ValueError("Aucune observation valide après contrôle qualité.")
    return df

def evaluate_models(df: pd.DataFrame, *, seed=2026):
    """Test indépendant + CV sur le train. Aucun identifiant/production totale en entrée."""
    X, y = df[FEATURES], df[TARGET]
    # Test séparé par culture pour préserver la représentation de chaque groupe.
    class_counts = df["culture"].astype(str).value_counts()
    test_size = max(1, int(np.ceil(len(df) * 0.20)))
    train_size = len(df) - test_size
    can_stratify = (
        len(class_counts) > 1
        and int(class_counts.min()) >= 2
        and test_size >= len(class_counts)
        and train_size >= len(class_counts)
    )
    strat = df["culture"].astype(str) if can_stratify else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=seed, stratify=strat)
    n_splits = 3
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    rows, fitted, crop_rows = [], {}, []
    for name, model in candidate_models().items():
        cv_mae = -cross_val_score(model, X_train, y_train, cv=cv, scoring="neg_mean_absolute_error", n_jobs=None).mean()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        rows.append({"modele": name, "MAE_test": mean_absolute_error(y_test, pred), "RMSE_test": mean_squared_error(y_test, pred) ** 0.5, "R2_test": r2_score(y_test, pred), "MAE_CV_train": cv_mae})
        fitted[name] = model
        test_frame = X_test.copy()
        test_frame["_culture"] = test_frame["culture"].astype(str)
        for crop, indexes in test_frame.groupby("_culture").groups.items():
            crop_y = y_test.loc[indexes]
            crop_pred = model.predict(X_test.loc[indexes])
            crop_rows.append({"modele": name, "culture": crop, "n_test": len(indexes),
                              "MAE_test": mean_absolute_error(crop_y, crop_pred),
                              "RMSE_test": mean_squared_error(crop_y, crop_pred) ** 0.5,
                              "R2_test": r2_score(crop_y, crop_pred) if len(indexes) > 1 else np.nan})
    report = pd.DataFrame(rows).sort_values(["MAE_test", "RMSE_test"]).reset_index(drop=True)
    by_crop = pd.DataFrame(crop_rows)
    return report, by_crop, fitted, (X_train, X_test, y_train, y_test)

def run_synthetic_benchmark(output_dir: Path | None = None) -> pd.DataFrame:
    """Benchmark de démonstration uniquement : ne produit aucun modèle de production."""
    df = load_dataset(SYNTHETIC_FILE, source="synthetic")
    report, by_crop, _, _ = evaluate_models(df)
    report.insert(0, "statut_donnees", "SIMULÉES — TEST TECHNIQUE UNIQUEMENT")
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        report.to_csv(output_dir / "comparaison_modeles_donnees_simulees.csv", index=False)
        by_crop.to_csv(output_dir / "performances_par_culture_donnees_simulees.csv", index=False)
        (output_dir / "avertissement.txt").write_text("Résultats issus exclusivement de données synthétiques. Ils ne mesurent pas la performance sur des exploitations réelles et ne doivent pas servir à annoncer une précision agronomique.\n", encoding="utf-8")
    return report

def train_real_model():
    """Entraîne le modèle gagnant sur des récoltes réelles contrôlées seulement."""
    df = load_dataset(REAL_FILE, source="real")
    report, by_crop, fitted, _ = evaluate_models(df)
    winner = str(report.iloc[0]["modele"])
    # Réentraînement final sur toutes les observations réelles après évaluation.
    model = candidate_models()[winner]
    model.fit(df[FEATURES], df[TARGET])
    return model, report, len(df), winner

def predict_real_harvest(values: dict) -> tuple[float, dict]:
    model, report, n, winner = train_real_model()
    x = pd.DataFrame([{k: values.get(k) for k in FEATURES}])
    estimate = max(0.0, float(model.predict(x)[0]))
    best = report.iloc[0]
    metadata = {"modele": winner, "observations_reelles": n, "mae_test": round(float(best["MAE_test"]), 3), "rmse_test": round(float(best["RMSE_test"]), 3), "r2_test": round(float(best["R2_test"]), 3)}
    return estimate, metadata

@lru_cache(maxsize=1)
def train_synthetic_model():
    """Entraîne une fois le modèle de démonstration sur le corpus synthétique intégré."""
    df = load_dataset(SYNTHETIC_FILE, source="synthetic")
    model = _pipeline(RandomForestRegressor(
        n_estimators=180, min_samples_leaf=8, max_features=0.85,
        random_state=2026, n_jobs=-1
    ))
    model.fit(df[FEATURES], df[TARGET])
    return model, len(df)

def predict_synthetic_harvest(values: dict) -> tuple[float, dict]:
    """Estimation de démonstration. Le résultat n'est jamais une observation réelle."""
    model, n = train_synthetic_model()
    x = pd.DataFrame([{k: values.get(k) for k in FEATURES}])
    estimate = max(0.0, float(model.predict(x)[0]))
    metadata = {
        "modele": "Random Forest (mode expérimental)",
        "source_donnees": "SIMULÉES",
        "observations_simulees": n,
        "avertissement": "Estimation expérimentale issue de données artificielles ; elle ne constitue pas une prévision agronomique validée sur le terrain."
    }
    return estimate, metadata

def predict_harvest_estimate(values: dict) -> tuple[float, dict]:
    """Priorité aux récoltes réelles contrôlées ; sinon, bascule explicite en mode simulé."""
    if REAL_FILE.exists():
        try:
            return predict_real_harvest(values)
        except (ValueError, FileNotFoundError):
            # Le jeu simulé intégré permet de tester l'interface sans prétendre à une validation réelle.
            pass
    return predict_synthetic_harvest(values)

if __name__ == "__main__":
    result = run_synthetic_benchmark(BASE_DIR / "rapports_ml")
    print(result.to_string(index=False))
    print("\nATTENTION : benchmark synthétique uniquement, aucune prédiction réelle n'est activée.")
