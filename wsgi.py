"""Point d'entrée WSGI pour la production (gunicorn : `gunicorn wsgi:app`).

En local, `app.py` se lance seul : son bloc `if __name__ == "__main__"` démarre le
serveur de dev ET le scheduler des rappels. En conteneur, gunicorn se contente
d'IMPORTER `app` — ce bloc ne s'exécute donc jamais, et sans ce fichier le scheduler
des rappels push ne démarrerait pas. On rétablit ici ce que le mode conteneur exige.

⚠️ gunicorn DOIT tourner avec --workers 1 (voir Dockerfile). Le scheduler
(_demarrer_scheduler) et le compteur anti-brute-force (auth._tentatives) sont
in-process : plusieurs workers = rappels envoyés en double + limite de tentatives
éclatée par worker. Pour la charge d'une bêta (<20 personnes), 1 worker + quelques
threads suffit très largement.
"""
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app import app, _demarrer_scheduler, completer_journal_retro

# Un seul worker (cf. avertissement ci-dessus) : ce démarrage a donc lieu une fois.
_demarrer_scheduler()
# Rattrapage rétroactif du journal (notes d'avant le 2026-11-25 : regreffer le
# miroir manquant) — idempotent, il ne fait rien au boot suivant.
completer_journal_retro()

# ── L'app sœur Tarot, montée sous /tarot (bêta) ──────────────────────────
# Elle vit dans tarot/ de ce dépôt et sait tourner seule (voir tarot/app.py) :
# supprimer ce montage et le dossier rend l'intégration réversible, sans rien
# toucher d'autre. Un échec d'import ne doit JAMAIS empêcher Ta Trame de servir.
try:
    from tarot.app import app as tarot_app
    application = DispatcherMiddleware(app, {"/tarot": tarot_app})
except Exception:  # pragma: no cover - garde-fou de production
    application = app
