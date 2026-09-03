# Image de production de Ta Trame. Servie par gunicorn (voir wsgi.py), jamais app.run.
#
# Python 3.11 : la version du venv local. On la fige pour que le conteneur calcule les
# thèmes exactement comme la machine de dev (même discipline que requirements.txt).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl + unzip : nécessaires UNIQUEMENT au build pour récupérer les données de référence
# (éphémérides JPL, dumps GeoNames). Nettoyés dans la même couche.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl unzip \
    && rm -rf /var/lib/apt/lists/*

# --- Dépendances Python -------------------------------------------------------
# Couche isolée : ne se réinstalle que si requirements bouge → builds de code rapides.
COPY requirements.txt requirements-prod.txt ./
RUN pip install -r requirements-prod.txt

# --- Éphémérides JPL (de440s.bsp, ~32 Mo, statique, identique pour tous) -------
# Couche isolée : retéléchargée seulement si cette instruction change. Le hash est
# vérifié au chargement par moteur/ephemerides.py — un téléchargement corrompu échoue
# au démarrage, jamais en silence.
RUN mkdir -p data/ephem \
    && curl -fsSL -o data/ephem/de440s.bsp \
       https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp

# --- Base des lieux (lieux.sqlite, construite depuis GeoNames, ~15 Mo) ---------
# On RÉUTILISE le script existant plutôt que d'embarquer un binaire. Couche keyée sur
# le seul construire_geo.py (stdlib pure) : reconstruite uniquement s'il change, pas à
# chaque push de code. Les dumps bruts sont supprimés après build (seul le .sqlite sert
# au runtime).
COPY outils/construire_geo.py outils/construire_geo.py
RUN mkdir -p data/geo \
    && curl -fsSL -o data/geo/CA.zip https://download.geonames.org/export/dump/CA.zip \
    && curl -fsSL -o data/geo/FR.zip https://download.geonames.org/export/dump/FR.zip \
    && (cd data/geo && unzip -o CA.zip && unzip -o FR.zip) \
    && python outils/construire_geo.py \
    && rm -f data/geo/CA.zip data/geo/FR.zip data/geo/CA.txt data/geo/FR.txt \
             data/geo/readme.txt

# --- Code applicatif ----------------------------------------------------------
# Dernière couche : la seule qui se reconstruit à chaque `git push`. Le .dockerignore
# tient dehors venv, .git, .env, les données de référence (recréées ci-dessus) et les
# données utilisateur (montées en volume). data/corpus, versionné, entre bien ici.
COPY . .

# Les données utilisateur MUTABLES (data/profils, data/contacts, data/vapid,
# data/notifications, data/activite, data/commentaires, data/journal) doivent être
# montées en VOLUMES PERSISTANTS dans Coolify — sur ces sous-dossiers précis, PAS sur
# /app/data (ce qui masquerait data/corpus versionné et les données de référence
# construites ci-dessus). Sans ces volumes, chaque redéploiement efface profils et
# abonnements push. Voir DEPLOIEMENT.md.

EXPOSE 8000

# 1 worker (contrainte de correction, cf. wsgi.py), plusieurs threads pour encaisser
# quelques requêtes simultanées ; timeout large car le 1er calcul de thème peut être lent.
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--timeout", "120", \
     "--bind", "0.0.0.0:8000", "--access-logfile", "-", "wsgi:app"]
