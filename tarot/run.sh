#!/bin/zsh
# Tarot — app de tirage déterministe (port 5089)
#
# Vibe Station cherche un run.sh en PREMIER (avant le chemin app.py), et
# c'est la convention de l'écosystème. `exec` remplace le shell par Python :
# le PID vu par Vibe est donc celui du vrai serveur, pas d'un wrapper — sinon
# le « Stop » tuerait le shell en laissant l'app orpheline sur le port.
cd "$(dirname "$0")"

# Le venv est autonome : on neutralise le PYTHONPATH injecté par la Vibe (3.9).
unset PYTHONPATH

# Les variables d'environnement locales (.env) : TAROT_ALBUM_MDP (le mot de
# passe d'édition de l'album), TAROT_SECRET (clé de session)…
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Premier lancement : venv + dépendances (Flask seul, bibliothèque standard ensuite).
if [ ! -x ./venv/bin/python3 ]; then
  python3 -m venv venv
  ./venv/bin/pip install --quiet --upgrade pip
fi
./venv/bin/python3 -c "import flask" 2>/dev/null || ./venv/bin/pip install --quiet -r requirements.txt

exec ./venv/bin/python3 app.py
