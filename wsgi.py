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
from app import app, _demarrer_scheduler

# Un seul worker (cf. avertissement ci-dessus) : ce démarrage a donc lieu une fois.
_demarrer_scheduler()
