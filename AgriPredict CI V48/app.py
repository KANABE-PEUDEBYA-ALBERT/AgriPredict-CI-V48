"""AgriPredict CI — première version fonctionnelle et extensible."""
from __future__ import annotations

import csv
import math as _math
import os
import sqlite3
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from ml_harvest import predict_harvest_estimate
from production_simulator import calculate_input_totals, polygon_area_ha
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from agronomy import CAMPAIGN_TASKS, CROP_GUIDES
from assistant_service import validate_question, build_prompt, ask_gemini
from crop_programs import CROP_PROGRAMS
from migrations.agricultural_core import migrate as migrate_agricultural_core
from migrations.legacy_schema import ensure_legacy_columns

BASE_DIR = Path(__file__).resolve().parent
print(f"[AgriPredict CI] Fichier app.py chargé : {Path(__file__).resolve()}")
load_dotenv(BASE_DIR / ".env")
DB_PATH = BASE_DIR / "agripredict.db"
PRODUCTS = ["Riz", "Maïs", "Mil", "Manioc", "Arachide", "Oignon", "Cacao"]
HARVEST_CROPS = ["Maïs", "Riz", "Manioc", "Igname", "Plantain", "Cacao"]
HARVEST_REGIONS = ["Haut-Sassandra", "Gbêkê", "Poro", "Gôh", "Indénié-Djuablin", "Tchologo", "Nawa", "La Mé", "Bélier", "Sud-Comoé"]
HARVEST_SOILS = ["Sableux", "Argileux", "Limoneux", "Ferralitique"]
HARVEST_SEEDS = ["Locale", "Améliorée", "Certifiée"]

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "agri-dev-change-me")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # limite d’import : 8 Mo


def db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    connection = g.pop("db", None)
    if connection:
        connection.close()


def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'producer', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS farms (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT NOT NULL,
          region TEXT NOT NULL, locality TEXT, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS plots (
          id INTEGER PRIMARY KEY, farm_id INTEGER NOT NULL, name TEXT NOT NULL,
          area_ha REAL NOT NULL, product TEXT NOT NULL, planting_date TEXT,
          latitude REAL, longitude REAL, geometry_geojson TEXT, area_gps_ha REAL, gps_accuracy REAL, location_updated_at TEXT,
          FOREIGN KEY(farm_id) REFERENCES farms(id)
        );
        CREATE TABLE IF NOT EXISTS tasks (
          id INTEGER PRIMARY KEY, plot_id INTEGER NOT NULL, title TEXT NOT NULL,
          due_date TEXT, status TEXT NOT NULL DEFAULT 'À faire', FOREIGN KEY(plot_id) REFERENCES plots(id)
        );
        CREATE TABLE IF NOT EXISTS market_prices (
          id INTEGER PRIMARY KEY, observed_on TEXT NOT NULL, product TEXT NOT NULL,
          market TEXT NOT NULL, region TEXT, price_fcfa_kg REAL NOT NULL, source TEXT NOT NULL DEFAULT 'Import utilisateur'
        );
        CREATE TABLE IF NOT EXISTS sale_listings (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, product TEXT NOT NULL,
          quantity_kg REAL NOT NULL, asking_price_fcfa_kg REAL NOT NULL, region TEXT NOT NULL,
          locality TEXT, description TEXT, contact TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'Disponible', created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    ensure_legacy_columns(connection)
    farm_columns = {row[1] for row in connection.execute("PRAGMA table_info(farms)").fetchall()}
    if "department" not in farm_columns:
        connection.execute("ALTER TABLE farms ADD COLUMN department TEXT")
    if "neighborhood" not in farm_columns:
        connection.execute("ALTER TABLE farms ADD COLUMN neighborhood TEXT")
    connection.commit()
    connection.close()
    migrate_agricultural_core(DB_PATH)


def generate_campaign_tasks(connection: sqlite3.Connection, plot_id: int, product: str, planting_date: str) -> int:
    """Create indicative tasks once for a plot and planting date."""
    try:
        start = date.fromisoformat(planting_date)
    except (TypeError, ValueError):
        return 0
    existing = connection.execute("SELECT COUNT(*) FROM tasks WHERE plot_id=?", (plot_id,)).fetchone()[0]
    if existing:
        return 0
    schedule = CAMPAIGN_TASKS.get(product, [])
    for offset_days, title in schedule:
        due = (start + timedelta(days=offset_days)).isoformat()
        connection.execute(
            "INSERT INTO tasks(plot_id,title,due_date,status) VALUES(?,?,?,'À faire')",
            (plot_id, title, due),
        )
    return len(schedule)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Connectez-vous pour accéder à cet espace.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


def authorized_admin_emails() -> set[str]:
    """Adresses autorisées à utiliser les fonctions d'administration."""
    emails = os.getenv("ADMIN_EMAILS", "")
    return {
        email.strip().casefold()
        for email in emails.split(",")
        if email.strip()
    }


def admin_required(view):
    """Réserve les opérations d'administration aux comptes explicitement administrateurs."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Connectez-vous avec un compte administrateur.", "warning")
            return redirect(url_for("login"))
        allowed_emails = authorized_admin_emails()
        if not allowed_emails or user["email"].casefold() not in allowed_emails or user["role"] != "admin":
            flash("Accès réservé aux deux comptes autorisés de l’équipe AgriPredict CI.", "danger")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"current_user": current_user(), "products": PRODUCTS}


def predict_harvest(values: dict) -> tuple[float, float, dict]:
    """Estimation réelle si disponible, sinon estimation expérimentale simulée."""
    estimate, metadata = predict_harvest_estimate(values)
    production = estimate * float(values["superficie_ha"])
    return estimate, production, metadata


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name, email, password = request.form["name"].strip(), request.form["email"].lower().strip(), request.form["password"]
        if not name or not email or len(password) < 8:
            flash("Indiquez un nom, un e-mail et un mot de passe d'au moins 8 caractères.", "danger")
        else:
            try:
                # Une inscription publique ne peut jamais créer un administrateur.
                # La promotion d'un compte autorisé se fait séparément par l'exploitant.
                role = "producer"
                cursor = db().execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)", (name, email, generate_password_hash(password), role, datetime.now().isoformat()))
                db().commit(); session["user_id"] = cursor.lastrowid
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("Cet e-mail est déjà utilisé.", "danger")
    return render_template("register.html")


@app.route("/connexion", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db().execute("SELECT * FROM users WHERE email = ?", (request.form["email"].lower().strip(),)).fetchone()
        if user and check_password_hash(user["password_hash"], request.form["password"]):
            # Le rôle est attribué par l'exploitant, jamais automatiquement à la connexion.
            # admin_required vérifie aussi que l'adresse figure dans ADMIN_EMAILS.
            session["user_id"] = user["id"]
            upcoming = db().execute("""SELECT t.title, t.due_date, p.name FROM tasks t
                JOIN plots p ON p.id=t.plot_id JOIN farms f ON f.id=p.farm_id
                WHERE f.user_id=? AND t.status!='Terminée' AND t.due_date<=?
                ORDER BY t.due_date LIMIT 3""", (user["id"], date.today().isoformat())).fetchall()
            for task in upcoming:
                flash(f"Rappel de campagne — {task['name']} : {task['title']} (échéance {task['due_date']}).", "warning")
            return redirect(url_for("dashboard"))
        flash("E-mail ou mot de passe incorrect.", "danger")
    return render_template("login.html")


@app.route("/deconnexion")
def logout():
    session.clear(); return redirect(url_for("index"))


@app.route("/tableau-de-bord")
@login_required
def dashboard():
    user_id = session["user_id"]
    connection = db()
    farms = connection.execute(
        """
        SELECT f.*,
               COUNT(DISTINCT p.id) AS plot_count,
               COALESCE(SUM(p.area_ha), 0) AS total_area_ha
        FROM farms f
        LEFT JOIN plots p ON p.farm_id = f.id
        WHERE f.user_id = ?
        GROUP BY f.id
        ORDER BY f.name
        """,
        (user_id,),
    ).fetchall()
    plots = connection.execute(
        """
        SELECT p.*, f.name AS farm_name
        FROM plots p
        JOIN farms f ON f.id = p.farm_id
        WHERE f.user_id = ?
        ORDER BY f.name, p.name
        """,
        (user_id,),
    ).fetchall()
    tasks = connection.execute(
        """
        SELECT t.*, p.name AS plot_name, p.id AS plot_id, f.name AS farm_name
        FROM tasks t
        JOIN plots p ON p.id = t.plot_id
        JOIN farms f ON f.id = p.farm_id
        WHERE f.user_id = ? AND t.status != 'Terminée'
        ORDER BY t.due_date
        LIMIT 8
        """,
        (user_id,),
    ).fetchall()
    total_area = sum(float(f["total_area_ha"] or 0) for f in farms)
    crop_rows = connection.execute(
        """SELECT p.product AS crop, COUNT(*) AS plot_count,
                  COALESCE(SUM(p.area_ha), 0) AS area_ha
           FROM plots p JOIN farms f ON f.id=p.farm_id
           WHERE f.user_id=? GROUP BY p.product ORDER BY area_ha DESC, crop""",
        (user_id,),
    ).fetchall()
    max_crop_area = max((float(row["area_ha"] or 0) for row in crop_rows), default=0)
    return render_template("dashboard.html", farms=farms, plots=plots, tasks=tasks,
                           total_area=total_area, crop_rows=crop_rows,
                           max_crop_area=max_crop_area)


@app.route("/exploitation", methods=["GET", "POST"])
@login_required
def farm():
    connection = db(); user_id = session["user_id"]
    if request.method == "POST":
        connection.execute(
            "INSERT INTO farms(user_id,name,region,locality,department,neighborhood) VALUES(?,?,?,?,?,?)",
            (user_id, request.form["name"].strip(), request.form["region"].strip(),
             request.form.get("locality", "").strip() or None,
             request.form.get("department", "").strip() or None,
             request.form.get("neighborhood", "").strip() or None),
        )
        connection.commit(); flash("Exploitation ajoutée.", "success")
        return redirect(url_for("farm"))
    farms = connection.execute(
        """
        SELECT f.*, COUNT(p.id) AS plot_count,
               COALESCE(SUM(p.area_ha), 0) AS total_area_ha
        FROM farms f
        LEFT JOIN plots p ON p.farm_id = f.id
        WHERE f.user_id = ?
        GROUP BY f.id
        ORDER BY f.name
        """,
        (user_id,),
    ).fetchall()
    location_rows = connection.execute(
        "SELECT DISTINCT region, department, locality, neighborhood FROM farms WHERE user_id=?",
        (user_id,),
    ).fetchall()
    known_regions = sorted({row["region"] for row in location_rows if row["region"]})
    location_catalog = [
        {"region": row["region"] or "", "department": row["department"] or "",
         "locality": row["locality"] or "", "neighborhood": row["neighborhood"] or ""}
        for row in location_rows
    ]
    return render_template("farm.html", farms=farms,
                           known_regions=known_regions,
                           geo_regions=HARVEST_REGIONS,
                           location_catalog=location_catalog)


@app.route("/parcelles", methods=["GET", "POST"])
@login_required
def plots():
    connection = db(); user_id = session["user_id"]
    farms = connection.execute("SELECT * FROM farms WHERE user_id=? ORDER BY name", (user_id,)).fetchall()
    if request.method == "POST":
        try:
            farm_id = int(request.form["farm_id"])
            name = request.form.get("name", "").strip()
            area_ha = float(request.form.get("area_ha", "0"))
            product = request.form.get("product", "")
            planting_date = request.form.get("planting_date", "").strip() or None
            owned_farm = connection.execute("SELECT id FROM farms WHERE id=? AND user_id=?", (farm_id, user_id)).fetchone()
            if not owned_farm:
                raise ValueError("Choisissez une exploitation qui vous appartient.")
            if not name or area_ha <= 0 or product not in PRODUCTS:
                raise ValueError("Vérifiez le nom, la superficie et la culture de la parcelle.")
            if planting_date:
                date.fromisoformat(planting_date)
            cursor = connection.execute("INSERT INTO plots(farm_id,name,area_ha,product,planting_date) VALUES(?,?,?,?,?)", (farm_id, name, area_ha, product, planting_date))
            plot_id = cursor.lastrowid
            generated = generate_campaign_tasks(connection, plot_id, product, planting_date) if planting_date else 0
            connection.commit()
            if generated:
                flash(f"Parcelle ajoutée : {generated} tâches indicatives ont été créées dans le calendrier.", "success")
            elif planting_date:
                flash("Parcelle ajoutée. Aucun calendrier standard n'est défini pour cette culture.", "warning")
            else:
                flash("Parcelle ajoutée. Ajoutez une date de semis/plantation pour générer son calendrier.", "success")
            return redirect(url_for("campaign", plot_id=plot_id) if generated else url_for("plots"))
        except (ValueError, TypeError):
            connection.rollback()
            flash("Impossible d'ajouter la parcelle. Vérifiez les informations saisies.", "danger")
    rows = connection.execute("SELECT p.*, f.name AS farm_name FROM plots p JOIN farms f ON f.id=p.farm_id WHERE f.user_id=? ORDER BY p.id DESC", (user_id,)).fetchall()
    return render_template("plots.html", farms=farms, plots=rows)


@app.route("/parcelles/<int:plot_id>/date-campagne", methods=["POST"])
@login_required
def set_campaign_date(plot_id: int):
    connection = db()
    plot = connection.execute(
        "SELECT p.* FROM plots p JOIN farms f ON f.id=p.farm_id WHERE p.id=? AND f.user_id=?",
        (plot_id, session["user_id"]),
    ).fetchone()
    if not plot:
        flash("Cette parcelle est introuvable ou ne vous appartient pas.", "danger")
        return redirect(url_for("plots"))
    planting_date = request.form.get("planting_date", "").strip()
    try:
        date.fromisoformat(planting_date)
    except ValueError:
        flash("Indiquez une date de semis ou de plantation valide.", "danger")
        return redirect(url_for("plots"))
    existing_tasks = connection.execute("SELECT COUNT(*) FROM tasks WHERE plot_id=?", (plot_id,)).fetchone()[0]
    if existing_tasks and plot["planting_date"] and plot["planting_date"] != planting_date:
        flash("Cette campagne possède déjà des tâches. Pour éviter de déplacer silencieusement les échéances, contactez l'administrateur avant de modifier sa date.", "warning")
        return redirect(url_for("campaign", plot_id=plot_id))
    connection.execute("UPDATE plots SET planting_date=? WHERE id=?", (planting_date, plot_id))
    generated = generate_campaign_tasks(connection, plot_id, plot["product"], planting_date)
    connection.commit()
    flash(f"Date enregistrée et {generated} tâches indicatives générées." if generated else "Date de campagne enregistrée.", "success")
    return redirect(url_for("campaign", plot_id=plot_id))


@app.route("/campagne/<int:plot_id>", methods=["GET", "POST"])
@login_required
def campaign(plot_id: int):
    connection = db()
    plot = connection.execute(
        "SELECT p.*, f.name AS farm_name, f.region, f.locality FROM plots p "
        "JOIN farms f ON f.id=p.farm_id WHERE p.id=? AND f.user_id=?",
        (plot_id, session["user_id"]),
    ).fetchone()
    if not plot:
        flash("Cette parcelle est introuvable ou ne vous appartient pas.", "danger")
        return redirect(url_for("plots"))
    if request.method == "POST":
        task_id = request.form.get("task_id", type=int)
        status = request.form.get("status", "")
        allowed = {"À faire", "En cours", "Terminée"}
        if status not in allowed or task_id is None:
            flash("Mise à jour de tâche invalide.", "danger")
        else:
            cursor = connection.execute(
                "UPDATE tasks SET status=? WHERE id=? AND plot_id=?",
                (status, task_id, plot_id),
            )
            connection.commit()
            flash("Statut de la tâche mis à jour." if cursor.rowcount else "Tâche introuvable.", "success" if cursor.rowcount else "warning")
        return redirect(url_for("campaign", plot_id=plot_id))
    tasks = connection.execute(
        "SELECT * FROM tasks WHERE plot_id=? ORDER BY due_date, id", (plot_id,)
    ).fetchall()
    completed = sum(1 for task in tasks if task["status"] == "Terminée")
    progress = round(100 * completed / len(tasks)) if tasks else 0
    guide = CROP_GUIDES.get(plot["product"], {})
    return render_template("campaign.html", plot=plot, tasks=tasks, progress=progress,
                           guide=guide, today=date.today().isoformat())


@app.route("/campagne/<int:plot_id>/generer", methods=["POST"])
@login_required
def regenerate_campaign(plot_id: int):
    connection = db()
    plot = connection.execute(
        "SELECT p.* FROM plots p JOIN farms f ON f.id=p.farm_id WHERE p.id=? AND f.user_id=?",
        (plot_id, session["user_id"]),
    ).fetchone()
    if not plot:
        flash("Cette parcelle est introuvable ou ne vous appartient pas.", "danger")
        return redirect(url_for("plots"))
    if not plot["planting_date"]:
        flash("Enregistrez d'abord la date de semis ou de plantation.", "warning")
    elif connection.execute("SELECT COUNT(*) FROM tasks WHERE plot_id=?", (plot_id,)).fetchone()[0]:
        flash("Un calendrier existe déjà. Les tâches existantes ont été conservées.", "warning")
    else:
        count = generate_campaign_tasks(connection, plot_id, plot["product"], plot["planting_date"])
        connection.commit()
        flash(f"{count} tâches indicatives ajoutées." if count else "Aucun calendrier standard n'est défini pour cette culture.", "success" if count else "warning")
    return redirect(url_for("campaign", plot_id=plot_id))


@app.route("/prix", methods=["GET", "POST"])
def prices():
    flash('La rubrique des prix agricoles est désactivée : AgriPredict CI se concentre désormais sur la production.', "info")
    return redirect(url_for("index"))
    product = request.values.get("product", PRODUCTS[0])
    rows = db().execute("SELECT * FROM market_prices WHERE product=? ORDER BY observed_on", (product,)).fetchall()
    return render_template("prices.html", product=product, rows=rows, chart_labels=[r["observed_on"] for r in rows], chart_values=[r["price_fcfa_kg"] for r in rows])


@app.route("/simulateur", methods=["GET", "POST"])
@login_required
def simulator():
    """Simulateur agronomique : besoins en intrants et estimation expérimentale de récolte."""
    prediction, error = None, None
    form = {
        "culture": request.values.get("culture", "Maïs"),
        "region": request.values.get("region", "Haut-Sassandra"),
        "superficie_ha": request.values.get("superficie_ha", "1"),
        "map_geometry": request.values.get("map_geometry", ""),
        "map_plot_id": request.values.get("map_plot_id", ""),
        "map_region": request.values.get("map_region", ""),
        "pluviometrie_mm": request.values.get("pluviometrie_mm", ""),
        "type_sol": request.values.get("type_sol", "Ferralitique"),
        "type_semences": request.values.get("type_semences", "Améliorée"),
        "semences_kg_ha": request.values.get("semences_kg_ha", ""),
        "type_engrais": request.values.get("type_engrais", "NPK"),
        "engrais_kg_ha": request.values.get("engrais_kg_ha", ""),
        "irrigation": request.values.get("irrigation", "Non"),
        "pratique_agricole": request.values.get("pratique_agricole", "Améliorée"),
    }
    if request.method == "POST":
        try:
            if form["culture"] not in HARVEST_CROPS:
                raise ValueError("Choisissez une culture disponible.")
            if form["region"] not in HARVEST_REGIONS:
                raise ValueError("Choisissez une région de Côte d'Ivoire.")
            if form["type_sol"] not in HARVEST_SOILS or form["type_semences"] not in HARVEST_SEEDS:
                raise ValueError("Vérifiez le type de sol et les semences.")
            if form["type_engrais"] not in {"NPK", "Urée", "Compost", "Fumure organique", "Autre / non précisé"}:
                raise ValueError("Choisissez un type d'engrais valide.")
            if form["irrigation"] not in {"Oui", "Non"} or form["pratique_agricole"] not in {"Traditionnelle", "Améliorée"}:
                raise ValueError("Vérifiez les pratiques agricoles renseignées.")
            # Si une parcelle est choisie sur la carte, son polygone fait foi :
            # la superficie saisie par le navigateur n'est jamais utilisée comme référence.
            if form["map_geometry"]:
                import json
                area = polygon_area_ha(json.loads(form["map_geometry"]))
                form["superficie_ha"] = f"{area:.4f}"
            else:
                area = float(form["superficie_ha"])
            rain = float(form["pluviometrie_mm"])
            fertilizer_rate = float(form["engrais_kg_ha"] or 0)
            if not _math.isfinite(rain) or not (0 <= rain <= 5000):
                raise ValueError("La pluviométrie doit être comprise entre 0 et 5 000 mm.")
            input_totals = calculate_input_totals(area, form["semences_kg_ha"] or 0, fertilizer_rate)
            area = input_totals["area_ha"]
            seed_rate = input_totals["seed_rate_kg_ha"]
            fertilizer_rate = input_totals["fertilizer_rate_kg_ha"]
            model_values = {
                "culture": form["culture"], "region": form["region"],
                "superficie_ha": area, "pluviometrie_mm": rain,
                "type_sol": form["type_sol"], "type_semences": form["type_semences"],
                "engrais_kg_ha": fertilizer_rate, "irrigation": form["irrigation"],
                "pratique_agricole": form["pratique_agricole"],
                "campagne_agricole": date.today().strftime("%Y"),
            }
            yield_t_ha, production_t, model_info = predict_harvest(model_values)
            prediction = {
                "culture": form["culture"], "region": form["region"],
                "area_ha": area, "yield_t_ha": round(yield_t_ha, 2),
                "production_t": round(production_t, 2),
                "production_kg": round(production_t * 1000, 0),
                "seed_total_kg": input_totals["seed_total_kg"],
                "seed_rate": seed_rate,
                "fertilizer_total_kg": input_totals["fertilizer_total_kg"],
                "fertilizer_rate": fertilizer_rate,
                "fertilizer_type": form["type_engrais"],
                "seed_rate_provided": bool(form["semences_kg_ha"].strip()),
                "fertilizer_rate_provided": bool(form["engrais_kg_ha"].strip()),
                "rainfall_mm": rain, "model_info": model_info,
                "map_selected": bool(form["map_geometry"]),
                "map_plot_id": form["map_plot_id"],
            }
        except (ValueError, TypeError, OverflowError, FileNotFoundError) as exc:
            error = str(exc) or "Impossible de calculer une estimation avec ces données."
        except Exception:
            app.logger.exception("Erreur dans le simulateur de production")
            error = "Le calcul a échoué. Vérifiez les informations et réessayez."
    return render_template(
        "simulator.html", prediction=prediction, error=error, form=form,
        harvest_crops=HARVEST_CROPS, harvest_regions=HARVEST_REGIONS,
        harvest_soils=HARVEST_SOILS, harvest_seeds=HARVEST_SEEDS,
    )

@app.route("/vente", methods=["GET", "POST"])
def marketplace():
    flash('La mise en relation commerciale est désactivée sur AgriPredict CI.', "info")
    return redirect(url_for("index"))
    """Marketplace d'annonces producteur; les annonces sont publiées par leurs auteurs."""
    if request.method == "POST":
        if "user_id" not in session:
            flash("Connectez-vous pour publier une annonce de vente.", "warning")
            return redirect(url_for("login"))
        try:
            product = request.form.get("product", "").strip()
            quantity = float(request.form.get("quantity_kg", "0"))
            price = float(request.form.get("asking_price_fcfa_kg", "0"))
            region = request.form.get("region", "").strip()
            locality = request.form.get("locality", "").strip()
            description = request.form.get("description", "").strip()
            contact = request.form.get("contact", "").strip()
            if product not in PRODUCTS or quantity <= 0 or price <= 0 or not region or not contact:
                raise ValueError("Vérifiez la culture, la quantité, le prix, la région et le contact.")
            db().execute("""INSERT INTO sale_listings(user_id,product,quantity_kg,asking_price_fcfa_kg,region,locality,description,contact,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""", (session["user_id"], product, quantity, price, region, locality, description, contact, datetime.now().isoformat(timespec="minutes")))
            db().commit()
            flash("Votre annonce est publiée. Le prix demandé est celui que vous avez saisi, pas un prix officiel vérifié.", "success")
            return redirect(url_for("marketplace"))
        except (ValueError, TypeError):
            flash("Annonce non publiée : vérifiez les champs et saisissez des valeurs positives.", "danger")
    product_filter = request.args.get("product", "")
    query = "SELECT s.*, u.name AS seller_name FROM sale_listings s JOIN users u ON u.id=s.user_id WHERE s.status='Disponible'"
    params = []
    if product_filter in PRODUCTS:
        query += " AND s.product=?"; params.append(product_filter)
    query += " ORDER BY s.created_at DESC LIMIT 100"
    listings = db().execute(query, params).fetchall()
    suggestions = db().execute("SELECT product, AVG(price_fcfa_kg) AS avg_price, COUNT(*) AS n, MAX(observed_on) AS latest FROM market_prices GROUP BY product").fetchall()
    suggestion_map = {r["product"]: dict(r) for r in suggestions}
    return render_template("marketplace.html", listings=listings, product_filter=product_filter, suggestions=suggestion_map)


@app.route("/vente/<int:listing_id>/statut", methods=["POST"])
@login_required
def update_listing_status(listing_id: int):
    flash("Les fonctions de vente et de transaction sont désactivées sur AgriPredict CI.", "info")
    return redirect(url_for("index"))
    status = request.form.get("status", "")
    if status not in {"Disponible", "Vendu", "Retiré"}:
        flash("Statut invalide.", "danger")
    else:
        cursor = db().execute("UPDATE sale_listings SET status=? WHERE id=? AND user_id=?", (status, listing_id, session["user_id"]))
        db().commit()
        flash("Statut de l'annonce mis à jour." if cursor.rowcount else "Annonce introuvable ou non autorisée.", "success" if cursor.rowcount else "warning")
    return redirect(url_for("marketplace"))


@app.route("/prevision", methods=["GET", "POST"])
def forecast():
    flash('Les prévisions de prix sont désactivées. Utilisez les prévisions de récolte.', "info")
    return redirect(url_for("index"))
    """Prévision exploratoire sur les seules observations de prix importées."""
    product = request.values.get("product", PRODUCTS[0])
    prediction = None
    mae = None
    test_count = 0
    message = None
    rows = db().execute(
        "SELECT observed_on, price_fcfa_kg FROM market_prices WHERE product=? ORDER BY observed_on, id",
        (product,),
    ).fetchall()
    count = len(rows)
    if count >= 8:
        frame = pd.DataFrame([dict(r) for r in rows])
        frame["observed_on"] = pd.to_datetime(frame["observed_on"], errors="coerce")
        frame["price_fcfa_kg"] = pd.to_numeric(frame["price_fcfa_kg"], errors="coerce")
        frame = frame.dropna().sort_values("observed_on")
        # Agréger les observations d'une même date afin d'éviter de tester sur le même jour.
        frame = frame.groupby("observed_on", as_index=False)["price_fcfa_kg"].mean()
        if len(frame) >= 8:
            origin = frame["observed_on"].min()
            x = (frame["observed_on"] - origin).dt.days.to_numpy().reshape(-1, 1)
            y = frame["price_fcfa_kg"].to_numpy()
            split = max(5, int(len(frame) * 0.8))
            if split < len(frame):
                test_model = LinearRegression().fit(x[:split], y[:split])
                test_predictions = test_model.predict(x[split:])
                mae = round(float((abs(y[split:] - test_predictions)).mean()), 2)
                test_count = len(y[split:])
            final_model = LinearRegression().fit(x, y)
            future_day = (pd.Timestamp.today().normalize() + pd.Timedelta(days=14) - origin).days
            prediction = round(max(0.0, float(final_model.predict([[future_day]])[0])), 2)
            message = "Estimation expérimentale à 14 jours par régression linéaire sur les prix importés. La validation utilise une séparation chronologique ; elle ne garantit pas le prix futur."
        else:
            message = "Les données contiennent moins de 8 dates distinctes valides. Aucune prévision n'est affichée."
    else:
        message = "Il faut au moins 8 observations réelles pour évaluer puis ajuster ce modèle. Importez un historique daté et vérifiable."
    return render_template("forecast.html", product=product, prediction=prediction, message=message,
                           count=count, mae=mae, test_count=test_count)


@app.route("/prevision-recolte", methods=["GET", "POST"])
@login_required
def harvest_forecast():
    """Ancienne URL conservée pour compatibilité : redirige vers le simulateur unique."""
    return redirect(url_for("simulator"))

@app.route("/administration/import-prix", methods=["GET", "POST"])
@admin_required
def import_prices():
    flash('L’importation de prix est désactivée sur AgriPredict CI.', "info")
    return redirect(url_for("index"))
    if request.method == "POST":
        upload = request.files.get("file")
        if not upload or not upload.filename or not upload.filename.lower().endswith(".csv"):
            flash("Importez un fichier CSV valide.", "danger")
            return redirect(url_for("import_prices"))
        try:
            data = pd.read_csv(upload, dtype={"produit": "string", "marche": "string", "region": "string"})
        except (ValueError, UnicodeDecodeError, pd.errors.ParserError):
            flash("Le fichier CSV est illisible. Vérifiez son encodage et son séparateur.", "danger")
            return redirect(url_for("import_prices"))
        expected = {"date", "produit", "marche", "region", "prix_fcfa_kg"}
        if not expected.issubset(data.columns):
            flash("Colonnes requises : date, produit, marche, region, prix_fcfa_kg.", "danger")
            return redirect(url_for("import_prices"))
        if len(data) > 100000:
            flash("Le fichier dépasse la limite de 100 000 lignes par import.", "danger")
            return redirect(url_for("import_prices"))
        connection = db()
        imported = skipped = 0
        seen = set()
        for row in data[["date", "produit", "marche", "region", "prix_fcfa_kg"]].itertuples(index=False, name=None):
            observed_on, product, market, region, price = row
            try:
                observed = date.fromisoformat(str(observed_on)[:10])
                product = str(product).strip()
                market = str(market).strip()
                region = "" if pd.isna(region) else str(region).strip()
                numeric_price = float(price)
                if not product or product not in PRODUCTS or not market or numeric_price <= 0 or not pd.notna(numeric_price):
                    raise ValueError("valeur invalide")
            except (ValueError, TypeError, OverflowError):
                skipped += 1
                continue
            key = (observed.isoformat(), product.casefold(), market.casefold(), region.casefold(), numeric_price)
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            duplicate = connection.execute(
                "SELECT 1 FROM market_prices WHERE observed_on=? AND lower(product)=lower(?) AND lower(market)=lower(?) AND coalesce(lower(region),'')=lower(?) AND price_fcfa_kg=? LIMIT 1",
                (observed.isoformat(), product, market, region, numeric_price),
            ).fetchone()
            if duplicate:
                skipped += 1
                continue
            connection.execute(
                "INSERT INTO market_prices(observed_on,product,market,region,price_fcfa_kg,source) VALUES(?,?,?,?,?,?)",
                (observed.isoformat(), product, market, region, numeric_price, upload.filename[:180]),
            )
            imported += 1
        connection.commit()
        flash(f"Import terminé : {imported} prix ajoutés, {skipped} ligne(s) ignorée(s) (invalides ou déjà présentes).", "success" if imported else "warning")
        return redirect(url_for("prices"))
    return render_template("import_prices.html")


@app.route("/conseiller")
@login_required
def advisor():
    return render_template("advisor.html")


@app.route("/guide-cultures", methods=["GET"])
@login_required
def crop_guide():
    """Fiches techniques par culture."""
    selected_product = request.args.get("product", "Riz")
    if selected_product not in CROP_PROGRAMS:
        selected_product = "Riz"
    return render_template(
        "crop_guide.html",
        products=list(CROP_PROGRAMS.keys()),
        selected_product=selected_product,
        guide=CROP_PROGRAMS[selected_product],
    )

@app.route("/assistant-ia", methods=["GET", "POST"])
@login_required
def general_ai():
    """Chat Gemini général, sans sélection ni contexte imposé de culture."""
    question = ""
    answer = None
    assistant_status = None
    if request.method == "POST":
        try:
            question = validate_question(request.form.get("question", ""))
            prompt = (
                "Tu es un assistant IA généraliste, utile et polyvalent, intégré à AgriPredict CI. "
                "Réponds en français clair et naturellement, avec le niveau de détail demandé. "
                "Tu peux traiter des sujets variés : études, sciences, informatique, rédaction, "
                "organisation, vie quotidienne et agriculture. Ne demande pas de choisir une culture "
                "et ne ramène pas automatiquement les questions à l'agriculture. "
                "N'invente pas de faits, de sources ou de données. Signale brièvement les incertitudes "
                "lorsqu'elles sont importantes. Pour les traitements phytosanitaires et les doses, "
                "ne prescris pas de produit ni de dosage et recommande une validation locale. "
                "Formate tes réponses en Markdown lisible : titres avec ##, listes avec -, tableaux si utiles, "
                "et texte en gras avec **...**. IMPORTANT : toute formule mathématique ou chimique doit être "
                "entourée de délimiteurs LaTeX complets. Dans une phrase, écris exactement \\( ... \\) ; "
                "pour une équation seule, écris exactement \\[ ... \\] sur des lignes séparées. "
                "N'écris jamais une formule LaTeX nue et n'utilise pas de simples crochets [ ... ] à la place "
                "de \\[ ... \\]. Pour les mathématiques, utilise \\frac{}{}, \\sqrt{}, \\sum, "
                "indices, exposants, intégrales et matrices selon le besoin. Pour le code, utilise des blocs "
                "clôturés avec le langage indiqué (```python, ```r, ```sql, etc.) et fournis du code complet "
                "et commenté lorsque demandé. Pour la chimie, écris les espèces avec indices corrects, par "
                "exemple \\(\\mathrm{Ca(OH)_2}\\), et les réactions avec une flèche ; tu peux utiliser "
                "la notation mhchem \\(\\ce{CO2 + Ca(OH)2 -> CaCO3 + H2O}\\) lorsqu'elle convient. "
                "Équilibre les réactions lorsque c'est demandé. N'entoure pas les réponses ordinaires "
                "d'astérisques isolés et n'écris pas les balises Markdown comme du texte brut."
            )
            answer = ask_gemini(question, prompt)
            assistant_status = "ok"
        except ValueError as error:
            answer = str(error)
            assistant_status = "error"
        except RuntimeError as error:
            answer = ("L'assistant IA n'est pas configuré." if str(error) == "GEMINI_NOT_CONFIGURED"
                      else "Impossible d'obtenir une réponse pour le moment.")
            assistant_status = "error"
        except Exception:
            answer = "Impossible de joindre l'assistant IA pour le moment."
            assistant_status = "error"
    return render_template("general_ai.html", question=question, answer=answer,
                           assistant_status=assistant_status)


@app.route("/donnees")
def data_library():
    flash('La bibliothèque des prix est désactivée sur AgriPredict CI.', "info")
    return redirect(url_for("index"))
    """Catalogue simple des observations de prix actuellement disponibles dans SQLite."""
    product = request.args.get("product", "").strip()
    region = request.args.get("region", "").strip()
    source = request.args.get("source", "").strip()
    start_date = request.args.get("debut", "").strip()
    end_date = request.args.get("fin", "").strip()
    clauses, params = [], []
    for field, value in [("product", product), ("region", region), ("source", source)]:
        if value:
            clauses.append(f"{field} LIKE ?")
            params.append(f"%{value}%")
    if start_date:
        clauses.append("observed_on >= ?"); params.append(start_date)
    if end_date:
        clauses.append("observed_on <= ?"); params.append(end_date)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = db().execute("SELECT observed_on, product, market, region, price_fcfa_kg, source FROM market_prices" + where + " ORDER BY observed_on DESC LIMIT 1000", params).fetchall()
    products = [r["product"] for r in db().execute("SELECT DISTINCT product FROM market_prices ORDER BY product")]
    regions = [r["region"] for r in db().execute("SELECT DISTINCT region FROM market_prices WHERE region IS NOT NULL AND region != '' ORDER BY region")]
    sources = [r["source"] for r in db().execute("SELECT DISTINCT source FROM market_prices ORDER BY source")]
    return render_template("data_library.html", rows=rows, products=products, regions=regions, sources=sources,
                           filters={"product": product, "region": region, "source": source, "debut": start_date, "fin": end_date})

@app.route("/donnees/export.csv")
def export_data_csv():
    flash('L’export des données de prix est désactivé sur AgriPredict CI.', "info")
    return redirect(url_for("index"))
    """Export des observations filtrées, limité aux données réellement présentes en base."""
    import io
    from flask import Response
    product = request.args.get("product", "").strip()
    region = request.args.get("region", "").strip()
    source = request.args.get("source", "").strip()
    start_date = request.args.get("debut", "").strip()
    end_date = request.args.get("fin", "").strip()
    clauses, params = [], []
    for field, value in [("product", product), ("region", region), ("source", source)]:
        if value:
            clauses.append(f"{field} LIKE ?"); params.append(f"%{value}%")
    if start_date:
        clauses.append("observed_on >= ?"); params.append(start_date)
    if end_date:
        clauses.append("observed_on <= ?"); params.append(end_date)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = db().execute("SELECT observed_on, product, market, region, price_fcfa_kg, source FROM market_prices" + where + " ORDER BY observed_on", params).fetchall()
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["date_observation", "produit", "marche", "region", "prix_fcfa_kg", "source"])
    for row in rows:
        writer.writerow([row["observed_on"], row["product"], row["market"], row["region"], row["price_fcfa_kg"], row["source"]])
    return Response("\\ufeff" + stream.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=agripredict_observations_prix.csv"})

@app.route("/donnees-agricoles")
def agricultural_insights():
    """Indicateurs agrégés issus du rapport officiel EAA 2024-2025.

    Ces agrégats décrivent le contexte agricole national. Ils ne sont pas des prix
    de marché et ne sont jamais injectés dans le modèle de prévision des prix.
    """
    indicators = [
        {"label": "Ménages agricoles", "value": "1 734 942", "detail": "dont 1 109 780 ménages ruraux"},
        {"label": "Population agricole en âge de travailler", "value": "5 282 168", "detail": "Indicateur national"},
        {"label": "Superficie moyenne par ménage", "value": "3,4 ha", "detail": "Moyenne des parcelles par ménage agricole"},
        {"label": "Ménages pratiquant la culture végétale", "value": "1 574 970", "detail": "Ménages agricoles"},
    ]
    food_crops = [
        ("Manioc", 7392519), ("Igname", 6963767), ("Banane plantain", 2270901),
        ("Maïs", 1829263), ("Riz pluvial de bas-fond", 1162864),
        ("Riz pluvial de plateau", 570408), ("Arachide", 393973),
    ]
    cash_crops = [
        ("Cacao", 1658145), ("Palmier à huile", 1530284), ("Hévéa", 1076658),
        ("Noix de cajou", 831593), ("Coton", 384466), ("Café", 80384),
    ]
    return render_template("agricultural_insights.html", indicators=indicators,
                           food_crops=food_crops, cash_crops=cash_crops)


@app.route("/carte-agricole")
@login_required
def agricultural_map():
    user_plots = db().execute("""SELECT p.id,p.name,p.product,p.area_ha,p.latitude,p.longitude,p.geometry_geojson,p.area_gps_ha,
        f.name AS farm_name,f.region,f.locality FROM plots p JOIN farms f ON f.id=p.farm_id
        WHERE f.user_id=? ORDER BY p.id DESC""", (session["user_id"],)).fetchall()
    return render_template("agricultural_map.html", plots=user_plots, select_for=request.args.get("select_for") == "simulator")


@app.route("/api/parcelles/<int:plot_id>/geolocalisation", methods=["POST"])
@login_required
def save_plot_geolocation(plot_id):
    payload = request.get_json(silent=True) or {}
    try:
        lat, lon = float(payload["latitude"]), float(payload["longitude"])
        accuracy = float(payload.get("accuracy") or 0)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
        owned = db().execute("SELECT p.id FROM plots p JOIN farms f ON f.id=p.farm_id WHERE p.id=? AND f.user_id=?", (plot_id, session["user_id"])).fetchone()
        if not owned:
            return {"ok": False, "error": "Parcelle introuvable ou non autorisée."}, 404
        db().execute("UPDATE plots SET latitude=?,longitude=?,gps_accuracy=?,location_updated_at=? WHERE id=?", (lat,lon,accuracy,datetime.utcnow().isoformat(timespec="seconds"),plot_id))
        db().commit()
        return {"ok": True, "latitude": lat, "longitude": lon}
    except (KeyError, TypeError, ValueError):
        return {"ok": False, "error": "Coordonnées GPS invalides."}, 400


@app.route("/api/parcelles/<int:plot_id>/contour", methods=["POST"])
@login_required
def save_plot_contour(plot_id):
    import json, math
    payload = request.get_json(silent=True) or {}
    geometry = payload.get("geometry")
    try:
        if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
            raise ValueError
        ring = geometry["coordinates"][0]
        if len(ring) < 4 or len(ring) > 500:
            raise ValueError
        coords = []
        for pair in ring:
            lon, lat = float(pair[0]), float(pair[1])
            if not (-180 <= lon <= 180 and -90 <= lat <= 90): raise ValueError
            coords.append((lon, lat))
        # Aire géodésique approchée sur sphère, suffisante pour une estimation de superficie.
        radius = 6371008.8
        total = 0.0
        for i in range(len(coords)-1):
            lon1, lat1 = map(math.radians, coords[i]); lon2, lat2 = map(math.radians, coords[i+1])
            total += (lon2-lon1) * (2 + math.sin(lat1) + math.sin(lat2))
        area_ha = abs(total * radius * radius / 2) / 10000
        if not (0.001 <= area_ha <= 100000): raise ValueError
        owned = db().execute("SELECT p.id FROM plots p JOIN farms f ON f.id=p.farm_id WHERE p.id=? AND f.user_id=?", (plot_id, session["user_id"])).fetchone()
        if not owned: return {"ok": False, "error": "Parcelle introuvable ou non autorisée."}, 404
        db().execute("UPDATE plots SET geometry_geojson=?,area_gps_ha=?,location_updated_at=? WHERE id=?", (json.dumps(geometry),area_ha,datetime.utcnow().isoformat(timespec="seconds"),plot_id))
        db().commit()
        return {"ok": True, "area_gps_ha": round(area_ha, 4)}
    except (KeyError, TypeError, ValueError, IndexError):
        return {"ok": False, "error": "Contour invalide. Dessinez un polygone fermé comportant au moins trois sommets."}, 400


@app.route("/a-propos")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
