"""Comptes utilisateurs de Ta Trame — porté de Manto (utilisateurs.py), pour la mise en ligne.

Un profil existant (data/profils/<id>.json) devient un COMPTE quand on lui ajoute un mot
de passe : le hash vit DANS le fichier profil existant, sous « mdp_hash ». Aucune base de
données, la donnée reste locale, inspectable et archivable à la main — comme partout dans
l'écosystème.

Différences assumées vs Manto (app locale entre amis → app PUBLIQUE sur tatrame.com) :
  - la connexion se fait par SAISIE DU NOM, jamais via une liste publique des profils ;
  - tentative de connexion = {nom_ou_id, mot_de_passe} : le nom saisi est résolu en id
    (slug, comme l'app le fait déjà à la création), sans jamais révéler si le compte existe.

Le reste est porté tel quel de Manto : hachage PBKDF2 épinglé (scrypt, défaut de Werkzeug,
exige hashlib.scrypt absent de certains Python macOS/LibreSSL — PBKDF2 est partout
disponible), écritures atomiques, `sans_secret` (le hash ne quitte jamais le serveur),
session longue durée 365 j (usage PWA : ne pas redemander à chaque visite).
"""
import json
import os
import re
import secrets
import time
import unicodedata

from werkzeug.security import check_password_hash, generate_password_hash

# scrypt (méthode par défaut de Werkzeug) exige hashlib.scrypt — absent sur certains Python
# liés à LibreSSL (macOS system Python). PBKDF2 est partout disponible, tout aussi sûr ici
# (mots de passe de testeurs, pas un service bancaire) — épingler la méthode évite un crash au
# premier hachage selon la machine qui héberge l'app.
_METHODE_HACHAGE = "pbkdf2:sha256"

# Anti-brute-force : public = les noms sont devinables (« martin-boucher »). Après
# ESSAIS_MAX mauvais mots de passe pour un id, on refuse TOUT essai pendant PAUSE_S
# (indépendamment du mot de passe tenté). Compteur en mémoire process — suffisant pour
# une bêta mono-serveur, pas de dépendance externe.
ESSAIS_MAX = 5
PAUSE_S = 60 * 15          # 15 minutes
_tentatives = {}           # id → [nb_essais, timestamp de la première tentative de la fenêtre]


def slug(text):
    """Le même slug que la création de profil de l'app (prénom-nom) — sert à résoudre
    le nom SAISI au moment de la connexion vers l'id de fichier existant."""
    t = unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t


def _path(profils_dir, pid):
    # Garde-fou anti-traversée : un id ne contient que [a-z0-9-]. On re-filtre par sécurité.
    safe = re.sub(r"[^a-z0-9-]+", "", (pid or ""))
    return profils_dir / f"{safe}.json"


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _write_atomic(path, data):
    """Écriture atomique (tmp + os.replace) : jamais de profil à moitié écrit, même si le
    process meurt en plein milieu — portée telle quelle de Manto."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp-{secrets.token_hex(3)}")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def definir_mot_de_passe(profils_dir, pid, mot_de_passe):
    """Fixe (ou change) le mot de passe d'un profil. Refuse SEULEMENT le vide (règle de
    Martin : liberté totale sinon, pas de longueur ni de caractères imposés) — porté tel
    quel de Manto, avec profils_dir en paramètre (Ta Trame n'a pas de config.py)."""
    if not (mot_de_passe or "").strip():
        return False
    data = _read_json(_path(profils_dir, pid))
    if not data:
        return False
    data["mdp_hash"] = generate_password_hash(mot_de_passe, method=_METHODE_HACHAGE)
    _write_atomic(_path(profils_dir, pid), data)
    return True


def verifier_mot_de_passe(profils_dir, pid, mot_de_passe):
    """True si le mot de passe correspond, False sinon (compte inconnu, pas encore de
    mot de passe, mauvais mot de passe — même réponse : on ne révèle rien)."""
    data = _read_json(_path(profils_dir, pid))
    if not data or not data.get("mdp_hash"):
        return False
    return check_password_hash(data["mdp_hash"], mot_de_passe or "")


def a_mdp(profils_dir, pid):
    data = _read_json(_path(profils_dir, pid))
    return bool(data and data.get("mdp_hash"))


def reinitialiser_mot_de_passe(profils_dir, pwd_admin, pid):
    """Efface le mot de passe d'un profil (réinitialisation ADMIN) : au prochain accès,
    la personne est réinvitée à en choisir un nouveau — jamais besoin de connaître
    l'ancien. Porté tel quel de Manto, avec le mot de passe admin en paramètre."""
    if not pwd_admin:
        return False
    data = _read_json(_path(profils_dir, pid))
    if not data:
        return None
    data["mdp_hash"] = None
    _write_atomic(_path(profils_dir, pid), data)
    return True


def _essais(pid):
    """L'état anti-brute-force d'un id, nettoyé des fenêtres expirées."""
    etat = _tentatives.get(pid)
    if etat and time.time() - etat[1] > PAUSE_S:
        _tentatives.pop(pid, None)
        etat = None
    return etat


def bloque(pid):
    """True si cet id est en pause anti-brute-force (trop de mauvais essais)."""
    etat = _essais(pid)
    return bool(etat and etat[0] >= ESSAIS_MAX)


def seconde_restante(pid):
    """Secondes restantes de pause, pour un message honnête (« réessaie dans X min »)."""
    etat = _essais(pid)
    if not etat or etat[0] < ESSAIS_MAX:
        return 0
    return max(0, int(PAUSE_S - (time.time() - etat[1])))


def enregistrer_echec(pid):
    """Un mauvais essai de plus. La fenêtre démarre à la première tentative."""
    etat = _essais(pid)
    if not etat:
        _tentatives[pid] = [1, time.time()]
    else:
        etat[0] += 1


def reinitialiser_echecs(pid):
    """Connexion réussie : le compteur repart de zéro."""
    _tentatives.pop(pid, None)
