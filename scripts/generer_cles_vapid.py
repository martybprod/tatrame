"""Génère la paire de clés VAPID pour les notifications push — À LANCER UNE FOIS.

Écrit `data/vapid/private_key.pem` (gitignoré, comme `data/profils/`). Le
serveur en dérive la clé publique au démarrage — rien d'autre à stocker.

⚠️ Ne JAMAIS régénérer une fois des utilisateurs abonnés : chaque abonnement
push est lié à la clé publique en vigueur au moment de l'inscription. Une
nouvelle paire de clés invaliderait tous les abonnements existants. Ce script
refuse donc d'écraser une clé déjà présente.

Usage : ./venv/bin/python scripts/generer_cles_vapid.py
"""
import pathlib
import sys

from py_vapid import Vapid

RACINE = pathlib.Path(__file__).resolve().parents[1]
CHEMIN_CLE = RACINE / "data" / "vapid" / "private_key.pem"


def main():
    if CHEMIN_CLE.exists():
        print(f"Une clé existe déjà : {CHEMIN_CLE}")
        print("Rien fait — supprime-la toi-même si tu veux vraiment la remplacer "
              "(ça invalidera tous les abonnements push existants).")
        sys.exit(1)

    CHEMIN_CLE.parent.mkdir(parents=True, exist_ok=True)
    v = Vapid()
    v.generate_keys()
    v.save_key(str(CHEMIN_CLE))
    print(f"Clé privée VAPID écrite : {CHEMIN_CLE}")
    print("Le serveur en dérivera la clé publique au démarrage.")


if __name__ == "__main__":
    main()
