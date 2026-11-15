"""Point d'entrée WSGI pour la production du Tarot (gunicorn : `gunicorn wsgi:app`,
ou `python wsgi.py` en local, ce qui imite le conteneur).

En local, `run.sh` lance `app.py` directement (serveur de dev). En conteneur, gunicorn
importe simplement `app` : ce fichier existe pour que le déploiement ait une entrée
explicite et pour poser les réglages qui ne valent qu'en ligne.

Aucun état en mémoire n'est nécessaire : le Tarot est 100 % déterministe et sans
session (hors album, dont le cookie est signé par TAROT_SECRET).
"""
import os

from app import app  # noqa: F401  (gunicorn wsgi:app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
