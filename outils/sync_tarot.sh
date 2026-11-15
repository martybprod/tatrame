#!/bin/sh
# Miroir du Tarot dans le dépôt de Ta Trame (bêta).
#
# La SOURCE de développement reste ATRO_PLUS/TAROT_APP (port 5089, services.json).
# On la copie ici avant de committer, pour que l'image contienne exactement ce
# qu'on a testé. Quand le Tarot redeviendra une app séparée : supprimer tarot/,
# le montage de wsgi.py et ce script — rien d'autre n'en dépend.
set -e
cd "$(dirname "$0")/.."
rsync -a --delete \
  --exclude 'venv' --exclude '.env' --exclude '__pycache__' \
  --exclude '.pytest_cache' --exclude '.openchamber' \
  ../TAROT_APP/ tarot/
echo "tarot/ synchronisé depuis ../TAROT_APP"
