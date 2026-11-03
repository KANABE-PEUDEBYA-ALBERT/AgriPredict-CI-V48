"""Promouvoir explicitement un compte existant en administrateur.

Utilisation : python promote_admin.py adresse@example.com
L'adresse doit déjà exister dans la base et figurer dans ADMIN_EMAILS du .env.
"""
import os
import sqlite3
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DB_PATH = BASE_DIR / "agripredict.db"


def main():
    if len(sys.argv) != 2:
        print("Utilisation : python promote_admin.py adresse@example.com")
        return 2
    email = sys.argv[1].strip().casefold()
    allowed = {item.strip().casefold() for item in os.getenv("ADMIN_EMAILS", "").split(",") if item.strip()}
    if not email or email not in allowed:
        print("Refus : cette adresse ne figure pas dans ADMIN_EMAILS du fichier .env.")
        return 1
    if not DB_PATH.exists():
        print("Base de données introuvable. Lancez d'abord l'application.")
        return 1
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("UPDATE users SET role='admin' WHERE lower(email)=?", (email,))
        if cursor.rowcount != 1:
            print("Compte introuvable. La personne doit d'abord créer son compte.")
            return 1
    print(f"Le compte {email} est maintenant administrateur.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
