# Déploiement de Ta Trame (bêta — conteneur / Coolify)

Ce mémo ne couvre QUE ce qui est particulier au passage en conteneur. Le plan complet
(Hetzner, DNS, PWA, Loi 25…) vit à part. Ici : les 4 choses qu'il ne faut pas rater et
le flux « je développe en local → je pousse → c'est en ligne ».

## Comment l'app tourne selon l'environnement

| | Local (dev) | Conteneur (prod) |
|---|---|---|
| Serveur | `app.run` via `run.sh` (port 5073) | gunicorn `wsgi:app` (port 8000) |
| Démarrage scheduler | bloc `__main__` de `app.py` | `wsgi.py` |
| Secrets | générés + écrits dans `.env` | **variables d'env obligatoires** |
| Cookies session | normaux (http local) | `Secure` + `SameSite=Lax` + ProxyFix |

Bascule pilotée par une seule variable : **`TATRAME_ENV=prod`** (absente/`dev` en local).

## 1. Variables d'environnement à définir dans Coolify

Générer chaque secret UNE fois, le coller dans Coolify, ne jamais le committer.

```
TATRAME_ENV=prod
SECRET_KEY=<64 hexa>          # python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_PASSWORD=<au choix>     # mot de passe admin (réinit. des comptes testeurs)
CODE_INVITATION=<au choix>    # code partagé pour créer un compte (bêta fermée)
```

Sans `SECRET_KEY`/`ADMIN_PASSWORD`/`CODE_INVITATION` en prod, l'app **refuse de démarrer**
avec un message clair (pour les secrets : au lieu d'en fabriquer un différent à chaque
déploiement, ce qui déconnecterait toutes les sessions ; pour le code : pour ne jamais
ouvrir la bêta sans porte par accident). C'est voulu. Révoquer/renouveler l'accès à la
bêta = changer `CODE_INVITATION` et redéployer.

⚠️ En prod, `SECRET_KEY`/`ADMIN_PASSWORD` viennent de l'environnement et RIEN d'autre.
Changer le mot de passe admin via `/admin/mot-de-passe` en conteneur n'est pas durable
(le `.env` du conteneur est éphémère) : le modifier dans Coolify + redéployer.

## 2. Volumes persistants (LE piège n°1)

Le conteneur a un système de fichiers **éphémère** : sans volumes, chaque redéploiement
efface profils et abonnements push. Monter des volumes persistants sur ces sous-dossiers
**précis** (surtout PAS sur `/app/data`, qui masquerait le corpus versionné et les
données de référence construites dans l'image) :

```
/app/data/profils
/app/data/contacts
/app/data/vapid
/app/data/notifications
```

## 3. Clés VAPID (notifications push)

Elles vivent dans le volume `/app/data/vapid`. Les générer une fois puis déposer le
`.pem` dans le volume (sinon les rappels sont simplement indisponibles, sans casser le
reste) :

```
python scripts/generer_cles_vapid.py   # produit data/vapid/private_key.pem
```

Et remplacer le placeholder `VAPID_CLAIMS = mailto:contact@example.com` dans `app.py`
par un vrai contact avant diffusion.

## 4. Avant la première mise en ligne — drapeaux de dev à repasser

- `DEV_MARTIN_VOIT_TOUS_LES_THEMES = True` → **False** (sinon un compte `martin-boucher`
  verrait les données de naissance de toute la famille). Un rappel s'affiche au démarrage.
- `PHASE_AMIS = True` : acceptable en bêta fermée (le 1er mot de passe saisi adopte le
  compte). À repasser à `False` avant une diffusion plus large.

## Tester l'image en local (avant de toucher à Hetzner)

```
docker build -t tatrame .
docker run --rm -p 8000:8000 \
  -e TATRAME_ENV=prod -e SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") \
  -e ADMIN_PASSWORD=test1234 \
  -v tatrame_profils:/app/data/profils \
  -v tatrame_contacts:/app/data/contacts \
  -v tatrame_vapid:/app/data/vapid \
  -v tatrame_notifications:/app/data/notifications \
  tatrame
# puis http://localhost:8000/health
```

Le 1er build télécharge les éphémérides JPL (~32 Mo) et les dumps GeoNames (~100 Mo) pour
construire `lieux.sqlite` : c'est long UNE fois, puis mis en cache (les `git push` de code
ne le refont pas).

## Flux dev → prod (continuer à développer, transférer facilement)

Le principe : **le code vient de git, les données vivent dans les volumes ; les deux ne se
touchent jamais.** C'est ce qui rend les mises à jour triviales et sûres.

1. Développer en local comme d'habitude (`run.sh`, port 5073) — rien ne change.
2. Committer, `git push` sur la branche que Coolify surveille (`main`).
3. Coolify rebuild + redéploie automatiquement. Les volumes (profils des testeurs) ne
   bougent pas ; tes profils de test locaux (`data/profils`, gitignoré) ne partent jamais
   en prod.
4. Reproduire un bug sur des données réelles : copier le volume prod vers le local
   (`scp`/`rsync` depuis le VPS) — flux à sens unique, aucun risque d'écraser la prod.

Prérequis one-shot : ajouter un remote git (GitHub privé) — le dépôt est local pour
l'instant — et y connecter Coolify.
