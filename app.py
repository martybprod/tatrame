"""Align — serveur Flask.

100 % local, 100 % déterministe : aucun LLM, aucun réseau, aucun aléa.
Même profil + même date -> même réponse, toujours, pour toujours.

Port 5073 (hors liste des ports « unsafe » des navigateurs).
"""
import base64
import datetime as dt
import json
import os
import pathlib
import re
import secrets
import unicodedata

from apscheduler.schedulers.background import BackgroundScheduler
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from flask import (Flask, jsonify, redirect, render_template, render_template_string,
                    request, session)
from py_vapid import Vapid
from pywebpush import webpush

import auth
from moteur import ages
from moteur import aspects as A
from moteur import chinois
from moteur import notifications as notif
from moteur import noeuds as N
from moteur import periodes as PER
from moteur import relations as REL
from moteur import routeur
from moteur import croisement as X
from moteur import jour as J
from moteur import numerologie as NUM
from moteur import tarot as TAR
from moteur import mineurs as MIN
from moteur import synthese
from moteur import temps as TEMPS
from moteur.corpus import Corpus
from moteur.geo import ATTRIBUTION, Lieux
from moteur.numerologie import (annee_personnelle, mois_personnel,
                                annee_universelle, decalage_au_monde, cap as cap_de)
from moteur.tarot import carte_de_l_annee, carte_du_jour
from moteur.theme import Moteur

RACINE = pathlib.Path(__file__).resolve().parent

# Le fuseau de l'AUDIENCE d'Align (Québec/Est canadien), pas celui du serveur.
# `date.today()` suit l'horloge système du processus : sur un poste local
# c'est déjà l'heure du Québec, mais un conteneur déployé tourne en UTC —
# passé 20h locale, il croirait déjà être demain. Voir `_date_demandee()`.
FUSEAU_APP = "America/Toronto"

PROFILS = RACINE / "data" / "profils"
PROFILS.mkdir(parents=True, exist_ok=True)
CONTACTS = RACINE / "data" / "contacts"
CONTACTS.mkdir(parents=True, exist_ok=True)
JOURNAL = RACINE / "data" / "journal"
JOURNAL.mkdir(parents=True, exist_ok=True)

# Les libellés français des 12 domaines du Fil du jour (Explorer). Pure
# présentation : les slugs et leur correspondance aux maisons vivent dans
# moteur/jour.py::MAISON_DOMAINE, seule source de vérité pour le calcul.
DOMAINE_LABELS = {
    "soi": "Toi", "ressources": "Argent", "echanges": "Mots",
    "racines": "Famille", "creation": "Créativité", "quotidien": "Habitudes",
    "autre": "Couple", "traversee": "Traversées", "sens": "Sens",
    "metier": "Métier", "communaute": "Communauté", "retrait": "Solitude",
}

app = Flask(__name__)
moteur = Moteur()
corpus = Corpus()
lieux = Lieux()


# --------------------------------------------------- comptes (mise en ligne)
#
# Secrets persistés au premier démarrage (pattern Manto config.py : jamais codés en
# dur, jamais reperdus au redémarrage). Ta Trame n'a pas de config.py — ils vivent
# ici, lus de .env, sinon générés et ajoutés au fichier.

def _load_dotenv():
    """Mini-chargeur .env sans dépendance (porté de Manto config.py). SANS lui,
    _secret_persiste ne relit jamais le fichier .env au redémarrage : il ne
    voit rien dans os.environ, croit qu'aucun secret n'existe encore, et en
    RÉGÉNÈRE un nouveau à chaque lancement — c'est le bug qui empêchait le mot
    de passe admin de jamais correspondre d'un redémarrage à l'autre."""
    try:
        path = RACINE / ".env"
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except OSError:
        pass


_load_dotenv()

# Mode d'exécution. En conteneur (Coolify), poser TATRAME_ENV=prod dans les variables
# d'environnement : ça durcit les cookies de session et REFUSE de fabriquer un secret
# manquant (voir _secret_persiste). Absent/dev en local : comportement d'origine.
_EST_PROD = os.environ.get("TATRAME_ENV", "dev").strip().lower() == "prod"


def _secret_persiste(cle_env, nb_hex):
    """Valeur secrète lue de .env, générée et PERSISTÉE au premier démarrage sinon."""
    val = os.environ.get(cle_env)
    if val:
        return val
    # En conteneur, le système de fichiers est ÉPHÉMÈRE : générer + écrire dans .env
    # redonnerait un secret DIFFÉRENT à chaque redéploiement (toutes les sessions
    # déconnectées, signatures cassées). En prod on exige donc le secret via
    # l'environnement (variables Coolify) et on échoue clairement s'il manque — plutôt
    # que d'en fabriquer un silencieusement voué à changer au prochain déploiement.
    if _EST_PROD:
        raise RuntimeError(
            f"{cle_env} absent de l'environnement alors que TATRAME_ENV=prod. "
            f"Définir cette variable dans Coolify (ne pas compter sur .env en conteneur)."
        )
    val = secrets.token_hex(nb_hex)
    chemin = RACINE / ".env"
    try:
        with open(chemin, "a", encoding="utf-8") as f:
            f.write(f"\n{cle_env}={val}\n")
    except OSError:
        pass                              # tant pis pour la persistance ; reste utilisable ce run-ci
    os.environ[cle_env] = val
    return val


def _reecrire_env(cle, valeur):
    """Remplace (ou ajoute) une clé dans .env en RÉÉCRIVANT le fichier — contrairement à
    _secret_persiste qui se contente d'ajouter en fin de fichier (donc de ne rien faire
    si la clé existe déjà, même avec une valeur à écarter). Nécessaire pour remplacer un
    mot de passe admin trivial laissé par erreur (ex. "merci" au clavier) : il faut
    ÉCARTER l'ancienne valeur, pas seulement compléter une clé absente."""
    chemin = RACINE / ".env"
    lignes, trouve = [], False
    try:
        if chemin.exists():
            for ligne in chemin.read_text(encoding="utf-8").splitlines():
                if ligne.strip().startswith(f"{cle}="):
                    if not trouve:
                        lignes.append(f"{cle}={valeur}")
                        trouve = True
                    continue                 # dédup : toute autre occurrence de la clé disparaît
                lignes.append(ligne)
        if not trouve:
            lignes.append(f"{cle}={valeur}")
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    except OSError:
        pass                                  # tant pis pour la persistance ; reste utilisable ce run-ci
    os.environ[cle] = valeur


SECRET_KEY = _secret_persiste("SECRET_KEY", 32)
# Mot de passe ADMIN (réinitialisation des comptes des testeurs) — généré au premier
# démarrage si absent, mais Martin peut le CHOISIR lui-même à tout moment depuis
# /admin/commentaires (voir /admin/mot-de-passe) : jamais réécrasé automatiquement une
# fois qu'il l'a changé (une auto-correction ici entrerait en conflit avec son choix).
ADMIN_PASSWORD = _secret_persiste("ADMIN_PASSWORD", 4)

# Le compte d'administration : Martin y accède depuis l'app (une fois connecté
# à SON compte), sans retaper le mot de passe admin. Celui-ci reste un REPLI
# (autre appareil, session non connectée). Voir _est_admin().
COMPTE_ADMIN = "martin-boucher"

# Code d'invitation de la bêta FERMÉE : un secret PARTAGÉ que les proches invités saisissent
# pour créer leur compte (voir api_creer_profil). Volontairement simple — pour <20 personnes,
# un code partagé, révocable en changeant la variable, suffit ; des codes uniques par personne
# seraient l'étape suivante si le besoin apparaît. En prod on l'EXIGE (comme SECRET_KEY) ;
# en dev, absent = pas de porte (confort local).
CODE_INVITATION = os.environ.get("CODE_INVITATION")
if _EST_PROD and not CODE_INVITATION:
    raise RuntimeError(
        "CODE_INVITATION absent de l'environnement alors que TATRAME_ENV=prod. "
        "Définir cette variable dans Coolify (contrôle d'accès de la bêta fermée)."
    )

# Phase « entre amis » (décision de Martin, 2026-08-21) : les personnes qui utilisent
# Ta Trame sont encore des proches invités individuellement, pas des inconnus du grand
# public. Le premier mot de passe saisi pour un profil qui n'en a pas encore devient le
# sien (voir /api/connexion) — sans ça, chaque proche attend que Martin lui pose un mot
# de passe à la main. À repasser à False avant une diffusion plus large (un nom deviné
# pourrait alors réclamer un profil existant avant son propriétaire).
PHASE_AMIS = True

# ⚠️⚠️⚠️ TEMPORAIRE — MODE TEST DEMANDÉ PAR MARTIN (2026-08-22) ⚠️⚠️⚠️
# Le compte martin-boucher voit et peut ouvrir TOUS les thèmes existants, comme s'il
# les avait tous créés comme thèmes secondaires — pour tester Relations/Explorer/etc.
# sans avoir à se connecter séparément à chaque compte de la famille.
#
# Volontairement PAS implémenté en posant "proprietaire": "martin-boucher" sur les
# vrais profils des autres personnes : ça aurait cassé LEUR connexion indépendante
# (un thème secondaire n'est jamais connectable par son propre nom, voir
# /api/connexion) et exposé leurs profils à une suppression en cascade si le compte
# martin-boucher était supprimé un jour. Ce drapeau est une vue élargie de LA
# SESSION de Martin uniquement — aucun fichier profil n'est modifié, aucun autre
# compte n'est affecté.
#
# 🔴 À REPASSER À False avant une mise en ligne ou une diffusion plus large — sinon
# n'importe qui se connectant comme martin-boucher verrait les données de naissance
# de toute la famille. Un rappel s'affiche aussi dans le terminal au démarrage.
DEV_MARTIN_VOIT_TOUS_LES_THEMES = True

app.secret_key = SECRET_KEY
# Session = juste « quels profils ce navigateur a déverrouillés », rien de sensible
# dedans ; longue durée (365 j) pour ne pas redemander le mot de passe à chaque
# visite — indispensable au confort PWA (usage quotiden, écran d'accueil).
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 365

if _EST_PROD:
    # Derrière le reverse proxy de Coolify (Traefik) qui termine le TLS : sans ça Flask
    # se croit en http (il ne voit que le trafic interne du proxy) et n'enverrait pas les
    # cookies marqués Secure. ProxyFix lui fait respecter X-Forwarded-Proto/Host.
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.update(
        SESSION_COOKIE_SECURE=True,     # cookie de session jamais transmis en clair (http)
        SESSION_COOKIE_HTTPONLY=True,   # hors de portée du JS (défaut Flask, explicité)
        SESSION_COOKIE_SAMESITE="Lax",  # limite l'envoi cross-site (protection CSRF de base)
    )

# ------------------------------------------------------- notifications push

VAPID_PRIVATE_KEY_PATH = RACINE / "data" / "vapid" / "private_key.pem"
# ⚠️ Placeholder — à remplacer par un vrai contact avant une mise en ligne
# réelle. Les claims VAPID exigent une adresse (mailto:) ou une URL (https:)
# permettant de joindre l'exploitant en cas d'abus signalé par un fournisseur
# push ; ce n'est pas un secret, juste un point de contact.
VAPID_CLAIMS = {"sub": "mailto:contact@example.com"}


def _vapid():
    """L'instance Vapid, ou None si les clés n'ont pas encore été générées
    (`scripts/generer_cles_vapid.py`) — les rappels restent indisponibles
    sans faire tomber le reste de l'app."""
    if not VAPID_PRIVATE_KEY_PATH.exists():
        return None
    return Vapid.from_file(str(VAPID_PRIVATE_KEY_PATH))


def _cle_publique_navigateur(v):
    """La clé publique VAPID au format attendu par `PushManager.subscribe`
    côté navigateur : le point EC brut non compressé (65 octets), encodé en
    base64 URL-safe sans padding. Différent du PEM que lit `pywebpush`."""
    brute = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return base64.urlsafe_b64encode(brute).rstrip(b"=").decode()


# ------------------------------------------------------------- profils

def _chemin(profil_id):
    sur = "".join(c for c in profil_id if c.isalnum() or c in "-_")
    if not sur:
        raise ValueError("identifiant de profil invalide")
    return PROFILS / f"{sur}.json"


def _ecrire(chemin, donnees):
    """Écriture atomique : tmp + replace. Un profil ne se corrompt pas."""
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(chemin)


@app.after_request
def _pas_de_cache(reponse):
    # Le JS/CSS est servi depuis static/ ; la page, elle, ne doit jamais être
    # mise en cache, sinon un redémarrage semble « ne rien changer ».
    if request.path == "/":
        reponse.headers["Cache-Control"] = "no-store"
    # /sw.js : servi via send_static_file (app.py::service_worker), donc
    # caché par défaut plusieurs heures comme n'importe quel fichier statique.
    # C'est le piège précis vécu par Martin (2026-08-27, « sur mon iPhone, ça
    # ne change rien, même sur Safari ») : le NAVIGATEUR garde sa copie locale
    # du fichier du service worker lui-même, et ne revérifie même pas auprès
    # du serveur avant l'expiration du cache — un ancien service worker
    # (d'une itération antérieure) peut alors rester actif indéfiniment,
    # invisible, et contrôler CHAQUE visite de l'origine (PWA et Safari
    # normal, la portée d'un SW n'est pas limitée au mode standalone).
    # `no-cache` (pas `no-store`) est la pratique standard pour un fichier de
    # service worker : le navigateur revalide via ETag à CHAQUE requête,
    # sans re-télécharger si rien n'a changé — mais il ne peut plus jamais
    # ignorer silencieusement une mise à jour.
    if request.path == "/sw.js":
        reponse.headers["Cache-Control"] = "no-cache"
    return reponse


# ------------------------------------------------ verrou serveur (comptes)
#
# Une seule porte pour tout l'app : avant CHAQUE requête, si l'URL parle d'un
# profil (ou d'un contact, qui est une identité de naissance aussi), on exige
# qu'il soit déverrouillé dans la session de CE navigateur. Un seul point de
# contrôle = aucune route oubliée — la route nouvelle héritera du verrou
# automatiquement (elle porte <profil_id> dans son URL).

_ROUTES_PROTOGEES = re.compile(
    r"^/api/(profil|portrait|jour|explorer|ciel|apercu|relations|notifications)"
)

# Routes de gestion du compte : elles portent <profil_id> mais gèrent JUSTE le
# mot de passe — les verrouiller serait circulaire (changer son mot de passe
# exige d'être déverrouillé… sauf qu'on l'exige aussi pour se déverrouiller).
# Leur propre garde vérifie ce qu'il faut (session, ou mot de passe admin).
_ROUTES_COMPTE = re.compile(r"^/api/profil/[^/]+/(mot-de-passe|reinitialiser-mdp|activer)$")


def _proprietaire_de(pid):
    """Le COMPTE propriétaire d'un profil : lui-même s'il est racine (créé en
    premier, connectable par nom + mot de passe), sinon le compte qui l'a créé
    en second (thème secondaire — « le thème de ma fille », jamais connectable
    séparément, voir champ « proprietaire » posé par api_creer_profil)."""
    d = _charger(pid)
    if not d:
        return None
    return d.get("proprietaire") or pid


def _deverrouille(pid):
    """`session['deverrouilles']` ne contient QUE des comptes racines (jamais
    l'id d'un thème secondaire) — un thème secondaire est déverrouillé dès que
    le compte qui l'a créé l'est, sans jamais figurer lui-même dans la liste.

    ⚠️ TEMPORAIRE (voir DEV_MARTIN_VOIT_TOUS_LES_THEMES) : sur CET appareil
    uniquement, une fois connecté comme martin-boucher, tout profil se
    déverrouille — pour tester sans se reconnecter à chaque compte."""
    dv = session.get("deverrouilles") or []
    if DEV_MARTIN_VOIT_TOUS_LES_THEMES and "martin-boucher" in dv:
        return True
    return _proprietaire_de(pid) in dv


def _deverrouille_pour(pid):
    """Marque ce profil comme déverrouillé POUR CET APPAREIL (session longue durée)."""
    dv = set(session.get("deverrouilles") or [])
    dv.add(pid)
    session["deverrouilles"] = list(dv)
    session.permanent = True


@app.before_request
def _verrou_profils():
    if request.path == "/" or not request.path.startswith("/api/"):
        return None                      # page, service worker, santé : libres
    if _ROUTES_COMPTE.match(request.path):
        return None                      # gestion du mot de passe : garde propre à chaque route
    m = _ROUTES_PROTOGEES.match(request.path)
    if not m:
        return None                      # lieux, lexique, conventions… : données publiques
    # L'id cherché : dernier segment OU celui qui précède un segment non-id
    # (<profil_id>, <profil_id>/<domaine>, <profil_id>/<b_genre>/<b_id>…).
    segments = request.path.strip("/").split("/")
    pid = None
    for i, s in enumerate(segments):
        if s in ("portrait", "jour", "ciel", "apercu") and i + 1 < len(segments):
            pid = segments[i + 1]
            break
        if s in ("profil", "relations", "notifications") and i + 1 < len(segments):
            pid = segments[i + 1]
            break
        if s == "explorer" and i + 1 < len(segments) and segments[i + 1] != "domaines":
            pid = segments[i + 1]
            break
    if pid is None or _deverrouille(pid):
        return None
    return jsonify({"erreur": "verrouille", "a_mdp": auth.a_mdp(PROFILS, pid)}), 401


@app.get("/")
def accueil():
    return render_template("index.html")


@app.get("/api/lieux")
def api_lieux():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])
    return jsonify([
        {"id": l["geonameid"], "nom": l["nom"], "pays": l["pays"],
         "admin1": l["admin1"], "lat": l["lat"], "lon": l["lon"],
         "fuseau": l["fuseau"], "population": l["population"]}
        for l in lieux.chercher(q, limite=8)
    ])


_GENRES = ("f", "m", "x")  # x = préfère ne pas préciser / non binaire


def _valider_genre(d):
    """Le genre, TOUJOURS facultatif. 'x' (non précisé) est un choix respecté,
    pas une erreur — le corpus reste gender-safe (verbes, pas d'accord) tant
    qu'un des deux genres d'un couple est 'x' ou manquant."""
    g = d.get("genre") or "x"
    if g not in _GENRES:
        raise ValueError("Genre invalide.")
    return g


def _construire(d):
    """Valide une saisie et en fait un profil. Lève ValueError si c'est faux.

    La validation vit ici, pas dans le navigateur : un profil mal formé
    donnerait un thème faux plutôt qu'une erreur — le pire des deux mondes.

    L'heure et le lieu de naissance sont FACULTATIFS — même patron que les
    contacts (voir _construire_contact) : sans eux, le profil se crée quand
    même, marqué "complet": False. Ta Trame ne devine jamais une heure ou un
    lieu ; la lecture se limite alors honnêtement aux nombres, aux cartes et
    à l'astrologie chinoise (calculables sur la date seule) plutôt que
    d'inventer un thème faux.
    """
    noms = [p.strip() for p in d.get("prenoms_nom", []) if p.strip()]
    if len(noms) < 2:
        raise ValueError("Il faut au moins un prénom et un nom.")

    an, mo, jo = int(d["annee"]), int(d["mois"]), int(d["jour"])
    try:
        dt.date(an, mo, jo)
    except ValueError:
        raise ValueError(f"Le {jo}/{mo}/{an} n'existe pas au calendrier.")
    if not 1800 <= an <= 2100:
        raise ValueError("L'année doit être comprise entre 1800 et 2100.")

    genre = _valider_genre(d)

    naissance = {"annee": an, "mois": mo, "jour": jo}
    complet = False
    if d.get("lieu_id"):
        lieu = lieux.par_id(int(d["lieu_id"]))
        if not lieu:
            raise ValueError("Ce lieu n'existe pas dans la base.")
        h, mi = int(d.get("heure", 0)), int(d.get("minute", 0))
        if not (0 <= h <= 23 and 0 <= mi <= 59):
            raise ValueError("L'heure doit être entre 00:00 et 23:59.")
        naissance.update({
            "heure": h, "minute": mi,
            "lieu": lieu["nom"], "lieu_id": lieu["geonameid"],
            "pays": lieu["pays"], "admin1": lieu["admin1"],
            "lat": lieu["lat"], "lon": lieu["lon"], "fuseau": lieu["fuseau"],
        })
        complet = True

    return {
        "id": d["id"],
        "nom_affiche": d.get("nom_affiche") or " ".join(noms),
        "prenoms_nom": noms,
        "genre": genre,
        "naissance": naissance,
        "complet": complet,
        "fold": int(d.get("fold", 0)),
    }


@app.post("/api/profil")
def api_creer_profil():
    # Déjà connecté sur cet appareil ? Le nouveau thème est SECONDAIRE — rattaché
    # à ce compte (« le thème de ma fille »), jamais lui-même un compte connectable
    # (voir _deverrouille/_proprietaire_de). Personne d'autre que Martin, décision
    # explicite : « je ne veux pas que chaque thème créé crée un nouveau compte ».
    compte_actuel = (session.get("deverrouilles") or [None])[-1]
    # Bêta fermée : créer un COMPTE racine (le 1er profil de ce navigateur) exige le code
    # d'invitation partagé. Un thème secondaire (compte déjà connecté sur cet appareil) n'en
    # a pas besoin. Vérifié AVANT toute écriture ; porte active seulement si un code est
    # configuré (aucun en dev local). compare_digest : pas de fuite par temps de réponse.
    if not compte_actuel and CODE_INVITATION:
        corps = request.get_json(force=True, silent=True) or {}
        fourni = (corps.get("code_invitation") or "").strip()
        if not secrets.compare_digest(fourni, CODE_INVITATION):
            return jsonify({"erreur": "Code d'invitation invalide."}), 403
    try:
        d = request.get_json(force=True)
        # Anti-collision publique : deux « Martin Boucher » doivent coexister sur
        # tatrame.com (avant, l'id était fabriqué par le navigateur — le second
        # écrasait le premier). L'id reste lisible : slug du nom, ou slug + suffixe
        # court si déjà pris (pattern Manto). La connexion, elle, essaie TOUS les
        # candidats du slug (voir /api/connexion) — jamais un profil secondaire.
        base = auth.slug(" ".join(d.get("prenoms_nom") or [])) or "profil"
        d["id"] = base if not _chemin(base).exists() else f"{base}-{secrets.token_hex(3)}"
        profil = _construire(d)
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"erreur": str(e) or "Saisie incomplète."}), 400
    if compte_actuel:
        profil["proprietaire"] = compte_actuel
    _ecrire(_chemin(profil["id"]), profil)
    if not compte_actuel:
        # Premier profil de ce navigateur : DEVIENT le compte (racine, connectable
        # par nom + mot de passe — voir vueChoisirMotDePasse côté client).
        _deverrouille_pour(profil["id"])
    return jsonify({"ok": True, "profil": profil})


@app.put("/api/profil/<profil_id>")
def api_modifier_profil(profil_id):
    """Modifier un profil existant. L'oubli qui bloquait l'usage.

    L'identifiant ne change pas, même si le nom change : il sert de clé de
    fichier, et le renommer casserait le profil courant du navigateur.
    """
    existant = _charger(profil_id)
    if not existant:
        return jsonify({"erreur": "Profil inconnu."}), 404
    d = {**request.get_json(force=True), "id": profil_id}
    try:
        profil = _construire(d)
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"erreur": str(e) or "Saisie incomplète."}), 400
    # _construire ne connaît pas la propriété (compte racine vs thème secondaire) —
    # elle ne se décide qu'à la création, jamais au fil d'une édition.
    if existant.get("proprietaire"):
        profil["proprietaire"] = existant["proprietaire"]
    _ecrire(_chemin(profil_id), profil)
    return jsonify({"ok": True, "profil": profil})


@app.delete("/api/profil/<profil_id>")
def api_supprimer_profil(profil_id):
    chemin = _chemin(profil_id)
    if not chemin.exists():
        return jsonify({"erreur": "Profil inconnu."}), 404
    # Supprimer un COMPTE (racine) emporte tous ses thèmes secondaires — sinon
    # ils restent orphelins sur le disque, invisibles pour toujours (leur
    # « proprietaire » ne réapparaîtra plus jamais dans une session). Un thème
    # secondaire, lui, n'a jamais d'enfant : rien à cascader en le supprimant.
    for p in PROFILS.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if d.get("proprietaire") == profil_id:
            p.unlink()
    chemin.unlink()
    # Le compte disparaît avec le profil : on le retire aussi des déverrouillés
    # de la session (sinon le sélecteur liste un fantôme au prochain chargement).
    dv = set(session.get("deverrouilles") or [])
    dv.discard(profil_id)
    session["deverrouilles"] = list(dv)
    return jsonify({"ok": True})


def _charger(profil_id):
    chemin = _chemin(profil_id)
    if not chemin.exists():
        return None
    return json.loads(chemin.read_text(encoding="utf-8"))


@app.get("/api/profil/<profil_id>")
def api_lire_profil(profil_id):
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "Profil inconnu."}), 404

    # Les premiers profils ont été écrits sans identifiant de lieu : sans lui,
    # le formulaire de modification n'a rien à renvoyer et le profil devient
    # immodifiable — le blocage même qu'on lève. On le retrouve par les
    # coordonnées, qui, elles, ont toujours été enregistrées.
    n = profil["naissance"]
    if not n.get("lieu_id") and n.get("lat") is not None:
        trouve = lieux.par_coordonnees(n["lat"], n["lon"])
        if trouve:
            n["lieu_id"] = trouve["geonameid"]
    return jsonify(profil)


@app.get("/api/profils")
def api_profils():
    """UNIQUEMENT les profils déverrouillés dans la session de CE navigateur.

    Avant la mise en ligne, cette route listait tous les profils de tout le
    monde — acceptable sur un Mac familial, impensable sur tatrame.com (des
    données de naissance complètes, publiques). La connexion se fait désormais
    par SAISIE DU NOM (voir /api/connexion), jamais via une liste.
    """
    deverrouilles = set(session.get("deverrouilles") or [])
    # ⚠️ TEMPORAIRE (voir DEV_MARTIN_VOIT_TOUS_LES_THEMES) : martin-boucher voit
    # TOUS les thèmes existants, pas seulement les siens, pour tester sans se
    # reconnecter à chaque compte. Aucun fichier profil n'est modifié pour ça.
    voit_tout = DEV_MARTIN_VOIT_TOUS_LES_THEMES and "martin-boucher" in deverrouilles
    out = []
    # Le compte lui-même (racine) ET tous les thèmes secondaires qu'il a créés
    # (proprietaire == ce compte) — un thème secondaire n'est jamais lui-même
    # dans `deverrouilles`, il hérite du déverrouillage de son propriétaire.
    for p in sorted(PROFILS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue                       # un profil corrompu n'empêche pas les autres
        proprio = d.get("proprietaire") or d["id"]
        if not voit_tout and proprio not in deverrouilles:
            continue
        n = d["naissance"]
        out.append({
            "id": d["id"],
            "nom_affiche": d.get("nom_affiche") or " ".join(d["prenoms_nom"]),
            "naissance": f"{n['jour']:02d}/{n['mois']:02d}/{n['annee']}",
            "lieu": n.get("lieu", ""),
            "complet": bool(d.get("complet")),
            "secondaire": bool(d.get("proprietaire")),
            # la RACINE du compte (elle-même pour un compte racine, le compte
            # propriétaire pour un thème) — sert au client à exiger le mot de
            # passe quand on change de compte (voir vueProfils).
            "proprietaire": proprio,
            # le compte racine a-t-il déjà un mot de passe ? (utile à l'écran
            # « changer de compte » pour prévenir qu'un premier mot de passe
            # serait créé, pas vérifié)
            "a_mdp": auth.a_mdp(PROFILS, proprio),
        })
    return jsonify(out)


# ------------------------------------------------------- connexion (comptes)

@app.post("/api/connexion")
def api_connexion():
    """{nom, mot_de_passe} — connecte un profil, ou l'ACTIVE au passage s'il n'a pas
    encore de mot de passe (premier accès).

    Le nom saisi est résolu en slug (« Martin Boucher » → martin-boucher), puis
    on essaie CHAQUE candidat de ce slug (base et suffixés — les homonymes).

    Phase actuelle (PHASE_AMIS=True, décision de Martin) : les utilisateurs de
    Ta Trame sont encore des proches invités individuellement — comme Manto,
    le premier mot de passe saisi pour un profil qui n'en a pas encore devient
    le sien, sans intervention admin. C'est un compromis EXPLICITE : ça permet
    à chacun de créer son mot de passe seul, mais un inconnu qui devine un nom
    pourrait réclamer ce profil avant son propriétaire. À revoir avant une
    diffusion plus large (voir PHASE_AMIS plus haut, et /api/profil/<id>/activer,
    conservé pour la suite : poser un mot de passe SANS passer par un essai de
    connexion, réservé à l'admin).
    """
    body = request.get_json(silent=True) or {}
    nom = (body.get("nom") or "").strip()
    mdp = body.get("mot_de_passe") or ""
    if not nom or not mdp:
        return jsonify({"erreur": "Nom et mot de passe requis."}), 400

    base = auth.slug(nom)
    if auth.bloque(base):
        mn = max(1, auth.seconde_restante(base) // 60)
        return jsonify({"erreur": f"Trop de tentatives. Réessaie dans {mn} minute(s)."}), 429
    # Seuls les comptes RACINES (sans « proprietaire ») sont connectables par nom —
    # un thème secondaire créé par quelqu'un d'autre ne doit jamais se connecter lui-même.
    candidats = [pid for pid in [base] + [p.stem for p in PROFILS.glob(f"{base}-*.json")]
                 if not (_charger(pid) or {}).get("proprietaire")]
    for pid in candidats:
        if auth.a_mdp(PROFILS, pid) and auth.verifier_mot_de_passe(PROFILS, pid, mdp):
            auth.reinitialiser_echecs(base)
            _deverrouille_pour(pid)
            return jsonify({"ok": True, "profil": pid})
    if PHASE_AMIS:
        # Aucun mot de passe posé : premier accès — le mot de passe saisi devient
        # celui du PREMIER candidat existant (s'il y en a un).
        premier = next((pid for pid in candidats if _chemin(pid).exists()), None)
        if premier and not auth.a_mdp(PROFILS, premier):
            if not auth.definir_mot_de_passe(PROFILS, premier, mdp):
                return jsonify({"erreur": "Le mot de passe ne peut pas être vide."}), 400
            auth.reinitialiser_echecs(base)
            _deverrouille_pour(premier)
            return jsonify({"ok": True, "profil": premier, "cree": True})
    auth.enregistrer_echec(base)
    return jsonify({"erreur": "Nom ou mot de passe incorrect."}), 401


@app.post("/api/profil/<profil_id>/activer")
def api_activer_profil(profil_id):
    """{mot_de_passe_admin, mot_de_passe} — réservé à Martin (ADMIN_PASSWORD) : pose le
    mot de passe INITIAL d'un profil créé avant les comptes (les 16 profils existants).
    Distinct de /reinitialiser-mdp (qui EFFACE) — celui-ci POSE, et refuse d'écraser un
    mot de passe déjà choisi par la personne (sinon Martin pourrait reprendre un compte
    déjà activé sans le vouloir)."""
    body = request.get_json(silent=True) or {}
    if body.get("mot_de_passe_admin") != ADMIN_PASSWORD:
        return jsonify({"erreur": "mot de passe administrateur incorrect"}), 403
    if (_charger(profil_id) or {}).get("proprietaire"):
        return jsonify({"erreur": "Un thème secondaire n'a pas de mot de passe."}), 400
    if auth.a_mdp(PROFILS, profil_id):
        return jsonify({"erreur": "Ce profil a déjà un mot de passe."}), 409
    mdp = body.get("mot_de_passe") or ""
    if not auth.definir_mot_de_passe(PROFILS, profil_id, mdp):
        return jsonify({"erreur": "introuvable ou mot de passe vide"}), 400
    return jsonify({"ok": True})


# --------------------------------------------------------------- journal

# L'app suggère souvent d'écrire (les « en action ») — un petit espace perso
# pour le faire, à côté. Zéro corpus, zéro calcul : juste une note horodatée,
# rangée à part du profil pour la même raison que les abonnements push (voir
# moteur/notifications.py) — une donnée opérationnelle, pas une donnée
# d'identité, écrasée sinon à chaque sauvegarde du profil.
MAX_JOURNAL_TEXTE = 8000


def _chemin_journal(profil_id):
    sur = "".join(c for c in profil_id if c.isalnum() or c in "-_")
    if not sur:
        raise ValueError("identifiant de profil invalide")
    return JOURNAL / f"{sur}.json"


def _lire_journal(profil_id):
    chemin = _chemin_journal(profil_id)
    if not chemin.exists():
        return []
    return json.loads(chemin.read_text(encoding="utf-8"))


@app.get("/api/journal/<profil_id>")
def api_journal(profil_id):
    """Les notes du profil, la plus récente d'abord."""
    entrees = _lire_journal(profil_id)
    return jsonify(sorted(entrees, key=lambda e: e["cree_le"], reverse=True))


@app.post("/api/journal/<profil_id>")
def api_journal_ajouter(profil_id):
    texte = ((request.get_json(silent=True) or {}).get("texte") or "").strip()
    if not texte:
        return jsonify({"erreur": "La note ne peut pas être vide."}), 400
    if len(texte) > MAX_JOURNAL_TEXTE:
        return jsonify({"erreur": f"Trop long ({MAX_JOURNAL_TEXTE} caractères maximum)."}), 400
    entrees = _lire_journal(profil_id)
    entree = {
        "id": secrets.token_hex(6),
        "texte": texte,
        # Horodaté dans le fuseau de l'app (Québec), pas celui du serveur —
        # même raison que _date_demandee() : voir FUSEAU_APP plus haut.
        "cree_le": dt.datetime.now(TEMPS.fuseau(FUSEAU_APP)).isoformat(),
    }
    entrees.append(entree)
    _ecrire(_chemin_journal(profil_id), entrees)
    return jsonify(entree)


@app.delete("/api/journal/<profil_id>/<entree_id>")
def api_journal_supprimer(profil_id, entree_id):
    entrees = _lire_journal(profil_id)
    restantes = [e for e in entrees if e["id"] != entree_id]
    if len(restantes) == len(entrees):
        return jsonify({"erreur": "introuvable"}), 404
    _ecrire(_chemin_journal(profil_id), restantes)
    return jsonify({"ok": True})


@app.post("/api/deconnexion")
def api_deconnexion():
    """{profil} — referme CE profil sur cet appareil (les autres restent ouverts)."""
    body = request.get_json(silent=True) or {}
    pid = (body.get("profil") or "").strip()
    dv = set(session.get("deverrouilles") or [])
    dv.discard(pid)
    session["deverrouilles"] = list(dv)
    return jsonify({"ok": True})


@app.post("/api/profil/<profil_id>/mot-de-passe")
def api_definir_mdp(profil_id):
    """{mot_de_passe} — fixe ou change le mot de passe du profil DÉVERROUILLÉ sur cet
    appareil (le flux bêta : création → invitation à en choisir un). Refuse le vide ;
    liberté totale sinon — pas de longueur ni de caractères imposés."""
    if not _deverrouille(profil_id):
        return jsonify({"erreur": "verrouille"}), 401
    if (_charger(profil_id) or {}).get("proprietaire"):
        return jsonify({"erreur": "Un thème secondaire n'a pas de mot de passe — "
                                   "c'est le compte qui l'a créé qui se connecte."}), 400
    mdp = (request.get_json(silent=True) or {}).get("mot_de_passe") or ""
    if not auth.definir_mot_de_passe(PROFILS, profil_id, mdp):
        return jsonify({"erreur": "Le mot de passe ne peut pas être vide."}), 400
    return jsonify({"ok": True})


@app.post("/api/profil/<profil_id>/reinitialiser-mdp")
def api_reinitialiser_mdp(profil_id):
    """{mot_de_passe_admin} — réservé à Martin (ADMIN_PASSWORD dans .env, affiché au
    démarrage) : efface le mot de passe d'un testeur qui l'a oublié ; il sera
    réinvité à en choisir un nouveau à sa prochaine connexion. Ne déverrouille
    PAS lui-même (le testeur repasse par « connexion »)."""
    body = request.get_json(silent=True) or {}
    if body.get("mot_de_passe_admin") != ADMIN_PASSWORD:
        return jsonify({"erreur": "mot de passe administrateur incorrect"}), 403
    if auth.reinitialiser_mot_de_passe(PROFILS, ADMIN_PASSWORD, profil_id) is None:
        return jsonify({"erreur": "introuvable"}), 404
    return jsonify({"ok": True})


# ------------------------------------------------------------- contacts
#
# La personne B d'une lecture Relations : soit un profil existant, soit un
# « contact » léger, stocké séparément pour ne pas polluer le sélecteur de
# profils principaux (data/contacts/). Un contact n'a besoin QUE d'une date
# de naissance — heure et lieu sont optionnels. Align ne devine jamais une
# heure de naissance : sans elle, la lecture se limite honnêtement aux
# nombres et à l'astrologie chinoise (les deux calculables sur la date seule).

def _chemin_contact(contact_id):
    sur = "".join(c for c in contact_id if c.isalnum() or c in "-_")
    if not sur:
        raise ValueError("identifiant de contact invalide")
    return CONTACTS / f"{sur}.json"


def _construire_contact(d):
    noms = [p.strip() for p in d.get("prenoms_nom", []) if p.strip()]
    an, mo, jo = int(d["annee"]), int(d["mois"]), int(d["jour"])
    try:
        dt.date(an, mo, jo)
    except ValueError:
        raise ValueError(f"Le {jo}/{mo}/{an} n'existe pas au calendrier.")
    if not 1800 <= an <= 2100:
        raise ValueError("L'année doit être comprise entre 1800 et 2100.")

    naissance = {"annee": an, "mois": mo, "jour": jo}
    complet = False
    if d.get("lieu_id"):
        lieu = lieux.par_id(int(d["lieu_id"]))
        if not lieu:
            raise ValueError("Ce lieu n'existe pas dans la base.")
        h, mi = int(d.get("heure", 0)), int(d.get("minute", 0))
        if not (0 <= h <= 23 and 0 <= mi <= 59):
            raise ValueError("L'heure doit être entre 00:00 et 23:59.")
        naissance.update({
            "heure": h, "minute": mi,
            "lieu": lieu["nom"], "lieu_id": lieu["geonameid"],
            "pays": lieu["pays"], "admin1": lieu["admin1"],
            "lat": lieu["lat"], "lon": lieu["lon"], "fuseau": lieu["fuseau"],
        })
        complet = True

    return {
        "id": d["id"],
        "nom_affiche": d.get("nom_affiche") or (" ".join(noms) if noms else "Sans nom"),
        "prenoms_nom": noms,
        "genre": _valider_genre(d),
        "naissance": naissance,
        "fold": int(d.get("fold", 0)),
        "contact": True,
        "complet": complet,
    }


@app.post("/api/contact")
def api_creer_contact():
    """Créer un contact exige un profil déverrouillé (le contact appartient à
    ce compte : champ « proprietaire ») — sinon n'importe qui remplit le
    disque du serveur de fichiers anonymes."""
    if not (session.get("deverrouilles") or []):
        return jsonify({"erreur": "verrouille"}), 401
    try:
        c = _construire_contact(request.get_json(force=True))
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"erreur": str(e) or "Saisie incomplète."}), 400
    c["proprietaire"] = session["deverrouilles"][-1]
    _ecrire(_chemin_contact(c["id"]), c)
    return jsonify({"ok": True, "contact": c})


@app.delete("/api/contact/<contact_id>")
def api_supprimer_contact(contact_id):
    """Un contact ne se supprime que par le compte qui l'a créé."""
    chemin = _chemin_contact(contact_id)
    if not chemin.exists():
        return jsonify({"erreur": "Contact inconnu."}), 404
    try:
        proprio = json.loads(chemin.read_text(encoding="utf-8")).get("proprietaire")
    except json.JSONDecodeError:
        proprio = None
    if proprio and proprio not in (session.get("deverrouilles") or []):
        return jsonify({"erreur": "verrouille"}), 401
    chemin.unlink()
    return jsonify({"ok": True})


def _charger_contact(contact_id):
    chemin = _chemin_contact(contact_id)
    if not chemin.exists():
        return None
    return json.loads(chemin.read_text(encoding="utf-8"))


@app.get("/api/contacts")
def api_contacts():
    """Les contacts de CE navigateur uniquement (même règle que /api/profils) :
    une date de naissance, même sans heure, ne devient pas publique parce
    qu'elle a servi à une lecture Relations."""
    deverrouilles = set(session.get("deverrouilles") or [])
    out = []
    for p in sorted(CONTACTS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if d.get("proprietaire") not in deverrouilles:
            continue
        n = d["naissance"]
        out.append({
            "id": d["id"],
            "nom_affiche": d.get("nom_affiche") or " ".join(d.get("prenoms_nom") or ["Sans nom"]),
            "naissance": f"{n['jour']:02d}/{n['mois']:02d}/{n['annee']}",
            "complet": bool(d.get("complet")),
        })
    return jsonify(out)


def _charger_entite(genre, id_):
    return _charger(id_) if genre == "profil" else _charger_contact(id_)


# ------------------------------------------------------------- lectures

def _croisement(profil, annee_courante):
    n = profil["naissance"]
    theme = moteur.theme_natal(
        n["annee"], n["mois"], n["jour"], n["heure"], n["minute"],
        n["lat"], n["lon"], n["fuseau"], fold=profil.get("fold", 0),
    )
    return theme, X.croiser(theme, profil["prenoms_nom"],
                            n["jour"], n["mois"], n["annee"], annee_courante)


def _texte_nombre(nb, cle):
    """Le texte court ET le détail approfondi, chacun dans SA table.

    Un même chiffre ne dit pas la même chose selon le nombre : un 9 en
    Cap (ta direction) n'est pas un 9 en Voix (ton expression) ni en Foyer
    (ton intime). Chaque nombre lit donc sa propre table, jamais celle du
    Cap — sinon on afficherait un texte faux. Une table courte absente
    (la Voix et l'Élan n'en ont pas) renvoie None : le panneau montre
    alors le seul détail, sans jamais emprunter au Cap.
    """
    v = nb[cle]["valeur"]
    return {
        "court": corpus.lire("nombres", cle, v),
        "detail": corpus.lire("nombres_detail", cle, v),
    }


def _textes_heritages(nb):
    # Les héritages présents dans le thème (13/14/16/19), chacun avec son texte.
    # Un héritage est un DRAPEAU partagé par la lignée, pas une note : on l'écrit
    # une fois par nombre-héritage, jamais par (nombre porteur × héritage) — la
    # règle d'addition, encore.
    presents = sorted({h for c in ("cap", "voix", "foyer", "elan")
                       for h in nb[c].get("heritages", [])})
    return {str(h): corpus.lire("heritages_detail", "heritages", h) for h in presents}


def _lois_du_cap(nb):
    # Les lois-leviers (distillées de Millman) qui travaillent ce but de vie.
    # On route par la BASE du Cap (1-9), jamais par sa valeur : un Cap maître
    # (11/22/33) hérite des leviers de sa base réduite — nb['cap']['base'] la
    # porte déjà. Table ADDITIVE : le routage lit lois.json::_routage[base],
    # 2-3 lois, jamais une matrice nombre × loi. Trou de corpus -> liste vide,
    # comme partout (le panneau se cache, l'app ne tombe pas).
    base = nb["cap"]["base"]
    slugs = corpus.lire("lois", "_routage", base, defaut=[]) or []
    lois = []
    for slug in slugs:
        loi = corpus.lire("lois", slug)
        if loi:
            lois.append({"cle": slug, **loi})
    return lois


@app.get("/api/portrait/<profil_id>")
def api_portrait(profil_id):
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "profil inconnu"}), 404

    aujourd_hui = _date_demandee()

    if not profil.get("complet"):
        # Sans heure ni lieu de naissance, pas de thème réel — mais les
        # nombres (prénoms + date) et les cartes (Arrien/Greer, date seule)
        # restent honnêtement calculables, voir _construire(). Pas de « pont »
        # ici (il lit le thème réel pour juger résonance/tension) : la carte
        # garde son seul sens de base, à l'état neutre.
        n = profil["naissance"]
        nb = NUM.portrait(profil["prenoms_nom"], n["jour"], n["mois"], n["annee"])
        cartes = TAR.profil(n["jour"], n["mois"], n["annee"], aujourd_hui.year)
        arcanes = corpus.lire("arcanes", "arcanes", defaut={}) or {}

        def texte_arcane_neutre(numero):
            a = arcanes.get(str(0 if numero == 22 else numero))
            return {**a, "lecture_etat": None} if a else None

        return jsonify({
            "profil": profil,
            "complet": False,
            "nombres": nb,
            "cartes": cartes,
            # Coquilles vides : pas de thème réel pour juger résonance/tension,
            # mais le frontend (chargerPortrait) les attend déjà toutes deux
            # falsy-safe (`if (pont)`, `a ? ... : ''`) — même code, sans branche
            # séparée à entretenir.
            "ponts": {"naissance": None, "fond": None},
            "accords": {},
            "textes": {
                "cap": _texte_nombre(nb, "cap"),
                "voix": _texte_nombre(nb, "voix"),
                "foyer": _texte_nombre(nb, "foyer"),
                "elan": _texte_nombre(nb, "elan"),
                "arcane_naissance": texte_arcane_neutre(cartes["naissance"]["numero"]),
                "arcane_fond": texte_arcane_neutre(cartes["fond"]["numero"]),
                "heritages": _textes_heritages(nb),
                # Les leviers du but de vie ne dépendent que de la date : ils
                # existent même sans heure ni lieu (profil incomplet).
                "lois": _lois_du_cap(nb),
            },
            "attribution": ATTRIBUTION,
        })

    theme, r = _croisement(profil, aujourd_hui.year)
    nb = r["nombres"]
    textes_heritages = _textes_heritages(nb)

    # Personologie : la sous-période du Soleil affine le signe (additif, ne le
    # remplace pas) ; l'axe des nœuds lit « d'où tu viens -> où tu vas » par
    # sous-période (résolution 48, pas 12 signes — origine = nœud sud,
    # destination = nœud nord). Pur calcul déjà fait par le moteur
    # (periodes.periode_de, noeuds.axe) ; ici on ne fait que résoudre les
    # clés de corpus, comme partout ailleurs dans ce fichier.
    cle_periode = PER.periode_de(theme["corps"]["soleil"]["lon"])["cle"]
    texte_periode = corpus.lire("periodes", cle_periode)
    axe_noeuds = N.axe(theme)
    cle_sud = axe_noeuds["sud"]["periode"]["cle"]
    cle_nord = axe_noeuds["nord"]["periode"]["cle"]
    textes_noeuds = {
        "sud": {**axe_noeuds["sud"], "texte": corpus.lire("noeuds", cle_sud, "origine")},
        "nord": {**axe_noeuds["nord"], "texte": corpus.lire("noeuds", cle_nord, "destination")},
    }

    arcanes = corpus.lire("arcanes", "arcanes", defaut={}) or {}

    def texte_arcane(numero, etat):
        a = arcanes.get(str(0 if numero == 22 else numero))
        if not a:
            return None
        return {**a, "lecture_etat": a.get(f"en_{etat}") if etat in ("resonance", "tension") else None}

    return jsonify({
        "profil": profil,
        "complet": True,
        "theme": theme,
        "nombres": nb,
        "cartes": r["cartes"],
        "ponts": r["ponts"],
        "accords": r["accords"],
        "bilan": r["bilan"],
        "stelliums": r["stelliums"],
        "textes": {
            "cap": _texte_nombre(nb, "cap"),
            "voix": _texte_nombre(nb, "voix"),
            "foyer": _texte_nombre(nb, "foyer"),
            "elan": _texte_nombre(nb, "elan"),
            "arcane_naissance": texte_arcane(
                r["cartes"]["naissance"]["numero"],
                (r["ponts"]["naissance"] or {}).get("etat", "neutre")),
            "arcane_fond": texte_arcane(
                r["cartes"]["fond"]["numero"],
                (r["ponts"]["fond"] or {}).get("etat", "neutre")),
            "heritages": textes_heritages,
            "periode_soleil": texte_periode,
            "noeuds": textes_noeuds,
            "lois": _lois_du_cap(nb),
        },
        "attribution": ATTRIBUTION,
    })


# ------------------------------------------------------------- relations
#
# Le lien entre DEUX personnes. Le moteur (moteur/relations.py) calcule des
# AXES sur des primitives (cap, éléments, positions, branches chinoises) ;
# ici, comme partout ailleurs dans ce fichier, on résout les clés qu'il
# produit vers le corpus. Jamais l'inverse : le texte ne guide aucun calcul.

LABEL_ASTRE = {
    "soleil": "Soleil", "lune": "Lune", "mercure": "Mercure", "venus": "Vénus",
    "mars": "Mars", "jupiter": "Jupiter", "saturne": "Saturne",
    "uranus": "Uranus", "neptune": "Neptune", "pluton": "Pluton",
    "asc": "Ascendant", "mc": "Milieu du Ciel",
}


def _personne_relations(entite):
    """Depuis un profil OU un contact -> le dict attendu par moteur.relations.

    Le Cap (date seule) et le pilier chinois d'année (date seule) sont
    TOUJOURS calculables. Les éléments et les positions ne le sont QUE si la
    naissance est complète (heure + lieu) : Align ne devine jamais une heure
    de naissance, il dit honnêtement ce qui manque plutôt que d'approximer.
    """
    n = entite["naissance"]
    jo, mo, an = n["jour"], n["mois"], n["annee"]
    valeur_cap = cap_de(jo, mo, an)["valeur"]
    pilier = chinois.pilier_annee(an, mo, jo)

    complet = all(k in n for k in ("heure", "minute", "lat", "lon", "fuseau"))
    elements, positions = {}, None
    if complet:
        theme = moteur.theme_natal(
            an, mo, jo, n["heure"], n["minute"], n["lat"], n["lon"], n["fuseau"],
            fold=entite.get("fold", 0),
        )
        corps = theme["corps"]
        elements = {
            "soleil": A.ELEMENT_DE[corps["soleil"]["signe"]],
            "lune": A.ELEMENT_DE[corps["lune"]["signe"]],
            "venus": A.ELEMENT_DE[corps["venus"]["signe"]],
            "mars": A.ELEMENT_DE[corps["mars"]["signe"]],
            "asc": A.ELEMENT_DE[theme["angles"]["asc"]["signe"]],
        }
        positions = {nom: c["lon"] for nom, c in corps.items() if nom != "noeud_moyen"}
        positions["asc"] = theme["angles"]["asc"]["lon"]
        positions["mc"] = theme["angles"]["mc"]["lon"]

    personne = {"cap": valeur_cap, "elements": elements,
               "chinois": {"i_branche": pilier["i_branche"], "element": pilier["element"]},
               "positions": positions}
    return personne, complet


_CLIMAT_CLE = {"resonance": "resonance_forte", "tension": "tension_forte",
              "mixte": "mixte", "neutre": "neutre"}


def _texte_pouls(pouls):
    """Le transit du jour sur le composite, résolu vers son corpus. Le message
    se compose : planète du jour + point du « vous » touché + climat de la classe."""
    if not pouls:
        return None
    cadre = corpus.lire("rel_pouls") or {}
    return {
        "cadre": cadre.get("cadre", ""),
        "pied": cadre.get("pied", ""),
        "planete_jour": LABEL_ASTRE.get(pouls["transit"], pouls["transit"]),
        "point": corpus.lire("rel_pouls", "point", pouls["natal"]) or "",
        "climat": corpus.lire("rel_pouls", "classe", pouls["classe"]) or "",
    }


def _prenom(nom):
    """Le prénom (premier mot) pour alléger une section qui répète les noms.
    Garde le libellé complet s'il n'y a rien à découper (ex. « cette personne »)."""
    return nom.split()[0] if nom and nom.split() else nom


def _de(nom):
    """« de Martin » / « d'Arianne » : élision propre devant voyelle ou h muet."""
    return f"d'{nom}" if nom[:1].lower() in "aeiouyéèêàhâî" else f"de {nom}"


_ASPECT_LABEL = {"conjonction": "conjonction", "sextile": "sextile",
                 "carre": "carré", "trigone": "trigone", "opposition": "opposition"}


def _cap(s):
    return s[0].upper() + s[1:] if s else s


def _texte_synastrie(asps, nom_a, nom_b, primaire="a"):
    """La synastrie en registre d'INTERACTION : chaque ligne dit quelle fonction
    de A rencontre quelle fonction de B, et ce que ça produit ENTRE eux — jamais
    un aspect natal en « toi » (qui décrirait une seule personne, à tort).

    Composition déterministe : phrase-fonction (corpus) × gabarit de classe, en
    nommant les personnes. Trois soins de style :
      - même fonction des deux côtés -> pronom de rappel (« l'envie d'agir de X
        et celle de Y »), pas la phrase répétée ;
      - une ouverture déjà vue -> on inverse l'ordre (le verbe est symétrique)
        pour ne pas répéter le même début de ligne ;
      - le tail tourne en round-robin PAR classe.
    Les aspects entre points PERSONNELS d'abord (le cœur du lien), angles ensuite ;
    une poignée, les plus serrés en tête. Chaque ligne porte aussi son `detail`
    technique (pour le tiroir « d'où vient ceci »).
    """
    if not asps:
        return None
    fonctions = corpus.lire("rel_synastrie", "fonctions") or {}
    rappels = corpus.lire("rel_synastrie", "rappels") or {}
    classes = corpus.lire("rel_synastrie", "classe") or {}
    a, b = _prenom(nom_a), _prenom(nom_b)

    ordre = sorted(asps, key=lambda x: (not x["perso"], x["orbe"]))[:6]
    tour = {}      # tails en round-robin par classe
    vues = set()   # ouvertures déjà utilisées, pour ne pas répéter un même début
    lignes = []
    for asp in ordre:
        da, db = asp["de_a"], asp["de_b"]
        fa = fonctions.get(da) or LABEL_ASTRE.get(da, da)
        fb = fonctions.get(db) or LABEL_ASTRE.get(db, db)
        cl = classes.get(asp["classe"]) or {}
        tails = cl.get("tails") or [""]
        i = tour.get(asp["classe"], 0)
        tour[asp["classe"]] = i + 1

        # Chaque fonction est suivie de son astre entre parenthèses (le nom
        # technique reste, discret, dans le texte ; le détail complet est au tiroir).
        def part(fonc, astre, nom, cap=False):
            ph = _cap(fonc) if cap else fonc
            return f"{ph} {_de(nom)} ({LABEL_ASTRE.get(astre, astre)})"

        # Le côté « primaire » mène par défaut : A d'ordinaire, mais le PARENT
        # quand le rôle est connu (le ciel du parent colore celui de l'enfant).
        p = (fb, db, b) if primaire == "b" else (fa, da, a)
        s = (fa, da, a) if primaire == "b" else (fb, db, b)

        if da == db:                       # même fonction des deux côtés
            rap = rappels.get(da, "la même")
            debut = f"{part(*p, cap=True)} et {rap} {_de(s[2])} ({LABEL_ASTRE.get(s[1], s[1])})"
        else:
            ouv_p = part(*p, cap=True)
            ouv_s = part(*s, cap=True)
            if ouv_p in vues and ouv_s not in vues:   # inverse pour ne pas répéter
                debut = f"{ouv_s} et {part(*p)}"
                vues.add(ouv_s)
            else:
                debut = f"{ouv_p} et {part(*s)}"
                vues.add(ouv_p)

        ecart = f"{asp['orbe']:.1f}".replace(".", ",")
        asp_nom = _ASPECT_LABEL.get(asp["aspect"], asp["aspect"])
        lignes.append({
            "texte": f"{debut} {cl.get('verbe', '')}. {tails[i % len(tails)]}",
            "detail": f"{LABEL_ASTRE.get(da, da)} de {a} — {asp_nom} — "
                      f"{LABEL_ASTRE.get(db, db)} {_de(b)} · écart {ecart}°",
            "perso": asp["perso"],
        })
    return lignes


def _texte_composite_aspects(aspects):
    """Les aspects INTERNES du composite, en registre « votre lien » (une seule
    entité, le couple) — jamais les 135 textes natals en « tu ». Deux facettes
    du « nous » qui se parlent : composé depuis les phrases-fonction (partagées
    avec la synastrie) et un gabarit de classe propre au composite. Les deux
    corps sont toujours différents (un point ne s'aspecte pas lui-même), donc pas
    de contraction ; on évite juste de répéter la même ouverture, et le tail
    tourne par classe. Chaque ligne porte son `detail` technique."""
    if not aspects:
        return []
    fonctions = corpus.lire("rel_synastrie", "fonctions") or {}
    classes = corpus.lire("rel_composite", "aspect_interne") or {}
    tour, vues, lignes = {}, set(), []
    for asp in aspects[:4]:
        da, db = asp["corps"]
        fa = fonctions.get(da) or LABEL_ASTRE.get(da, da)
        fb = fonctions.get(db) or LABEL_ASTRE.get(db, db)
        cl = classes.get(asp["classe"]) or {}
        tails = cl.get("tails") or [""]
        i = tour.get(asp["classe"], 0)
        tour[asp["classe"]] = i + 1

        pa = f"{fa} ({LABEL_ASTRE.get(da, da)})"   # minuscule : milieu de phrase
        pb = f"{fb} ({LABEL_ASTRE.get(db, db)})"
        if pa in vues:                          # inverse pour ne pas répéter l'ouverture
            pa, pb = pb, pa
        vues.add(pa)

        ecart = f"{asp['orbe']:.1f}".replace(".", ",")
        asp_nom = _ASPECT_LABEL.get(asp["aspect"], asp["aspect"])
        lignes.append({
            "texte": f"Au cœur de votre lien, {pa} et {pb} {cl.get('verbe', '')}. "
                     f"{_cap(tails[i % len(tails)])}",
            "detail": f"{LABEL_ASTRE.get(da, da)} — {asp_nom} — "
                      f"{LABEL_ASTRE.get(db, db)} · écart {ecart}°",
        })
    return lignes


_ELISION = re.compile(
    r"\b(que|de|ne|se|me|te|je|ce|le|la)\s+(?=[AEIOUYÉÈÀÂÊÎÔÛHaeiouyéèàâêîôûh])",
    re.IGNORECASE)


def _elider(texte):
    """Élide un petit mot devant un prénom à voyelle après substitution :
    « que Arianne » -> « qu'Arianne », « de Arianne » -> « d'Arianne »."""
    return _ELISION.sub(lambda m: m.group(1)[:-1] + "'", texte)


def _texte_elements(par_point, nom_a, nom_b, genre_a="x", genre_b="x"):
    """L'axe éléments, composé au rendu et NOMMÉ (doctrine « langage clair »).

    Chaque point personnel compare l'élément de A et de B. Le template
    rel_elements_v2 (clé `{point}_{cle}`) porte des jetons d'élément
    (`{feu}`/`{terre}`/`{air}`/`{eau}`) qu'on remplace par le prénom de la
    personne qui a CET élément sur ce point ; `{a}`/`{b}` quand les deux ont le
    même élément. Repli sur l'ancien rel_elements (registre « l'un/l'autre »)
    tant que le pilote ne couvre pas toutes les combinaisons — aucun couple
    n'est cassé. Gender-safe : les templates n'emploient que des verbes.

    Jetons de PRONOM (`{il:X}` / `{Il:X}`, X = feu/air/terre/eau ou a/b) : ils ne
    reprennent un « il »/« elle » QUE si les deux genres sont connus ET DIFFÉRENTS
    — un « il » et une « elle » restent toujours distinguables. Deux personnes du
    même sexe (ou un genre inconnu) rendent le pronom ambigu : dans ce cas le
    jeton retombe sur le PRÉNOM (le texte actuel, sans confusion possible). Règle
    d'écriture : `{il:X}` ne sert qu'à REPRENDRE un nom déjà cité, en position sujet."""
    a, b = _prenom(nom_a), _prenom(nom_b)
    # Pronoms actifs seulement si genres connus ET différents (sinon ambigu).
    accord = genre_a in ("f", "m") and genre_b in ("f", "m") and genre_a != genre_b
    out = []
    for pt in par_point:
        etat = pt["etat"]
        tpl = corpus.lire("rel_elements_v2", f"{pt['point']}_{pt['cle']}")
        if tpl and tpl.get("texte"):
            texte = tpl["texte"]
            if pt["element_a"] == pt["element_b"]:
                ids = {"a": (a, genre_a), "b": (b, genre_b)}
            else:
                ids = {pt["element_a"].lower(): (a, genre_a),
                       pt["element_b"].lower(): (b, genre_b)}
            for ident, (nom, genre) in ids.items():
                # pronom si accord possible, sinon le prénom (repli sans confusion)
                pron = ("elle" if genre == "f" else "il") if accord else nom
                texte = texte.replace("{Il:" + ident + "}", pron[0].upper() + pron[1:])
                texte = texte.replace("{il:" + ident + "}", pron)
                texte = texte.replace("{" + ident + "}", nom)
            texte = _elider(texte)         # « que Arianne » -> « qu'Arianne » ; « que il » -> « qu'il »
        else:                              # repli : l'ancien texte symétrique
            vieux = corpus.lire("rel_elements", pt["cle"]) or {}
            texte = f"{vieux.get('en_bref', '')} {vieux.get('texte', '')}".strip()
        out.append({"point": pt["point"], "etat": etat, "texte": texte})
    return out


def _texte_diagnostic(diag, nom_a, nom_b, cadre):
    """La ressemblance du composite (démocratie / féodal / étrangère), résolue
    vers son texte. Le cas féodal nomme le « souverain » et le « vassal » à partir
    de la personne visée par le calcul (aucun jugement : un simple repère)."""
    if not diag:
        return None
    texte = cadre.get(diag["cle"], "")
    if diag["cle"] == "feodal":
        souverain, vassal = (nom_a, nom_b) if diag["souverain"] == "a" else (nom_b, nom_a)
        texte = texte.replace("{souverain}", souverain).replace("{vassal}", vassal)
    return {
        "cle": diag["cle"],
        "amorce": cadre.get("_amorce", ""),
        "texte": texte,
        "pied": cadre.get("_pied", ""),
    }


def _textes_relations(resultat, nom_a, nom_b, pouls=None, parent=None,
                      genre_a="x", genre_b="x"):
    """Résout chaque axe CALCULÉ vers son texte de corpus. Que de la lecture.

    `parent` ('a' | 'b' | None) : dans un lien parent-enfant, qui est le parent.
    Il n'entre PAS dans le calcul (les axes restent symétriques) ; il oriente
    seulement la LECTURE — la synastrie se lit du parent vers l'enfant, et le
    conseil s'adresse au parent ou à l'enfant selon qui consulte (A = profil).

    `genre_a`/`genre_b` ('f'|'m'|'x') : facultatifs, jamais requis. Transportés
    jusqu'aux composeurs pour qu'un futur texte puisse accorder « il »/« elle »
    quand les DEUX genres sont connus. Le corpus actuel (rel_elements_v2) reste
    gender-safe par construction (verbes) : rien ne change tant qu'aucun texte
    n'exploite ces jetons — c'est le socle, pas la réécriture."""
    axes = resultat["axes"]
    type_dict = dict(corpus.lire("rel_types", resultat["type"]) or {})
    # Conseil orienté : si le consultant (A) est l'enfant, on lui parle en enfant.
    if parent == "b" and type_dict.get("conseil_enfant"):
        type_dict["conseil"] = type_dict["conseil_enfant"]
    textes = {"type": type_dict,
             "pouls": _texte_pouls(pouls)}

    nb = axes["nombres"]
    textes["nombres"] = {
        "paire": corpus.lire("rel_nombres", nb["cle"]),
        "harmonique": corpus.lire("rel_harmoniques", nb["harmonique"]),
        # Le composé : le « vous » comme entité (somme des Cap, réduite 1-9).
        # Pendant numérologique du thème composite astral (textes["composite"]).
        "composite": corpus.lire("rel_composite_nombre", nb["composite"]),
    }

    textes["elements"] = _texte_elements(axes["elements"]["par_point"], nom_a, nom_b, genre_a, genre_b)

    ch = axes["chinois"]
    textes["chinois"] = {
        "branche": corpus.lire("rel_chinois", "branches", ch["branche"]),
        "element": corpus.lire("rel_chinois", "elements", ch["element"]),
    }

    syn = axes["synastrie"]
    # La synastrie se lit dans SON registre (l'interaction entre deux personnes),
    # pas en empruntant les textes natals en « toi ». Voir _texte_synastrie.
    # Parent-enfant : le côté PARENT mène (son ciel colore celui de l'enfant),
    # et une intro l'annonce.
    textes["synastrie_intro"] = None
    if syn is not None:
        textes["synastrie"] = _texte_synastrie(
            syn["aspects"], nom_a, nom_b, primaire=(parent or "a"))
        if parent:
            p_nom, e_nom = (nom_a, nom_b) if parent == "a" else (nom_b, nom_a)
            intro = (type_dict.get("synastrie_intro") or "")
            textes["synastrie_intro"] = intro.replace(
                "{parent}", _prenom(p_nom)).replace("{enfant}", _prenom(e_nom))
    else:
        textes["synastrie"] = None

    comp = resultat.get("composite")
    if comp is not None:
        cadre = corpus.lire("rel_composite") or {}
        amorces = cadre.get("amorces", {})
        luminaires = []
        # Soleil, Lune, Vénus et Mars portent un texte (le « vous » en signe) ;
        # l'Ascendant n'a pas d'entrée, comme dans le thème natal, on le nomme
        # sans texte long. Vénus/Mars sont ce qu'un couple a de plus parlant —
        # l'amour et l'élan du lien — alors on les lit aussi, pas seulement les
        # deux luminaires.
        for pt in ("soleil", "lune", "venus", "mars", "asc"):
            c = comp["corps"].get(pt)
            if not c:
                continue
            # Le fond planète-en-signe reprend l'IMAGERIE de l'axe astre_signe,
            # mais re-voix en « vous » (le composite décrit le lien, pas une
            # personne) : corpus dédié rel_composite_signe.
            fond = (corpus.lire("rel_composite_signe", f"{pt}_{_plier_signe(c['signe'])}")
                    if pt != "asc" else None)
            luminaires.append({"point": pt, "signe": c["signe"],
                              "amorce": amorces.get(pt, ""), "fond": fond})
        textes["composite"] = {
            "cadrage": cadre.get("cadrage", ""),
            "amorce_aspect": cadre.get("aspect", ""),
            "pied": cadre.get("pied", ""),
            "luminaires": luminaires,
            "aspects": _texte_composite_aspects(comp["aspects"]),
            "diagnostic": _texte_diagnostic(resultat.get("diagnostic"),
                                            nom_a, nom_b, cadre.get("diagnostic", {})),
        }
    else:
        textes["composite"] = None

    cle_climat = _CLIMAT_CLE[resultat["synthese"]["climat"]]
    textes["synthese"] = {
        "dominante": corpus.lire("rel_synthese", "dominante", cle_climat),
        # Les étiquettes d'axe, pour que la synthèse d'intro NOMME les points
        # forts (top_appui/top_bouscule) ; le contenu précis vient du en_bref.
        "axes": corpus.lire("rel_synthese", "axes") or {},
        "pied": {
            "non_verdict": corpus.lire("rel_synthese", "pied", "non_verdict"),
            "conditions": corpus.lire("rel_synthese", "pied", "conditions"),
            "bidirectionnel": corpus.lire("rel_synthese", "pied", "bidirectionnel"),
        },
    }
    return textes


@app.get("/api/relations/<profil_id>/<b_genre>/<b_id>")
def api_relations(profil_id, b_genre, b_id):
    if b_genre not in ("profil", "contact"):
        return jsonify({"erreur": "Type de personne B invalide."}), 400
    type_relation = request.args.get("type", "amour")
    if type_relation not in REL.LENTILLES:
        return jsonify({"erreur": "Type de relation inconnu."}), 400
    # Le rôle n'a de sens que pour parent-enfant. role=parent -> A (le profil
    # consultant) est le parent ; role=enfant -> A est l'enfant (B est le parent).
    role = request.args.get("role")
    parent = None
    if type_relation == "parent_enfant" and role in ("parent", "enfant"):
        parent = "a" if role == "parent" else "b"

    profil_a = _charger(profil_id)
    if not profil_a:
        return jsonify({"erreur": "Profil A inconnu."}), 404
    # La personne B peut être le PROFIL d'un autre compte (via « Tes profils » du
    # navigateur) ou un contact. Un profil B n'est lisible que s'il est déverrouillé
    # sur CE navigateur (le verrou before_request ne protège que profil_id, le
    # segment A) ; un contact, s'il appartient à un compte déverrouillé.
    if b_genre == "profil" and not _deverrouille(b_id):
        return jsonify({"erreur": "verrouille"}), 401
    entite_b = _charger_entite(b_genre, b_id)
    if not entite_b:
        return jsonify({"erreur": "Personne B inconnue."}), 404
    if b_genre == "contact" and entite_b.get("proprietaire") \
            and entite_b["proprietaire"] not in (session.get("deverrouilles") or []):
        return jsonify({"erreur": "verrouille"}), 401

    pers_a, complet_a = _personne_relations(profil_a)
    pers_b, complet_b = _personne_relations(entite_b)
    resultat = REL.croiser_relation(pers_a, pers_b, type_relation)

    nom_a = profil_a.get("nom_affiche") or " ".join(profil_a["prenoms_nom"])
    nom_b = entite_b.get("nom_affiche") or " ".join(entite_b.get("prenoms_nom") or ["cette personne"])
    genre_a = profil_a.get("genre", "x")
    genre_b = entite_b.get("genre", "x")

    # Le pouls du jour : le transit du ciel réel sur le composite, seulement
    # quand le composite existe. Le ciel se lit à midi UTC de la date demandée
    # (rejouable via ?date=), même instant stable que /api/jour.
    pouls = None
    if resultat["composite"] is not None:
        date = _date_demandee()
        t = moteur.eph.instant(date.year, date.month, date.day, 12, 0, 0)
        ciel = {c: moteur.eph.position(c, t) for c in moteur.eph.CORPS}
        positions = {c: p["lon"] for c, p in ciel.items()}
        vitesses = {c: p["vitesse_lon"] for c, p in ciel.items()}
        pouls = REL.pouls_composite(resultat["composite"], positions, vitesses)

    return jsonify({
        "nom_a": nom_a, "nom_b": nom_b,
        "complet_a": complet_a, "complet_b": complet_b,
        "resultat": resultat,
        "textes": _textes_relations(resultat, nom_a, nom_b, pouls, parent, genre_a, genre_b),
        "types": sorted(REL.LENTILLES),
    })


def _date_demandee():
    """La date lue, jamais devinée dans le moteur.

    `datetime.now()` vit ICI, dans la couche transport — jamais dans le
    moteur, qui reçoit toujours l'instant en paramètre. C'est ce qui rend
    chaque lecture rejouable : `?date=2026-07-16` redonne exactement la même.

    Le « aujourd'hui » par défaut se calcule dans `FUSEAU_APP`, jamais dans
    le fuseau système du processus — `date.today()` suivrait l'UTC du
    conteneur déployé et basculerait au jour suivant 4-5h avant le Québec.
    """
    q = request.args.get("date")
    if q:
        return dt.date.fromisoformat(q)
    return dt.datetime.now(TEMPS.fuseau(FUSEAU_APP)).date()


def bloc_univers(jour, mois, annee_civile):
    """Le croisement de l'année du MONDE avec l'année PERSONNELLE.

    Jusqu'ici rien ne reliait les deux — pourtant l'année personnelle EST
    l'année du monde, décalée par la date de naissance. Le décalage ne dépend
    QUE d'elle : il est donc constant toute la vie. On rend les deux nombres
    concrets (le monde est en tant, toi en tant) plus les deux textes de
    corpus : le climat collectif, et ce que ça fait de courir toujours avec le
    même écart sur son époque. Renvoie None si le corpus manque encore.
    """
    au = annee_universelle(annee_civile)
    d = decalage_au_monde(jour, mois)
    climat = corpus.lire("univers_detail", "univers", au) or {}
    ecart = corpus.lire("univers_detail", "decalage", d) or {}
    if not climat and not ecart:
        return None
    return {
        "annee_civile": annee_civile,
        "universelle": au,
        "en_un_mot": climat.get("en_un_mot"),
        "climat": climat.get("climat"),
        "decalage": d,
        "titre": ecart.get("titre"),
        "texte": ecart.get("texte"),
    }


def _bloc_vie(jour, mois, annee, date):
    """La traversée de la vie — la couche de temps la plus lente, universelle.

    Ne dépend que de l'âge (retour de Saturne à ~29½, opposition d'Uranus à
    ~42…). Renvoie le passage courant plus son texte de corpus, ou None si le
    corpus manque encore. Partagé par le Jour et l'aperçu « Tout ».
    """
    passage = ages.passage_de_vie(jour, mois, annee, date)
    if not passage:
        return None
    return {**passage,
            "corpus": corpus.lire("ages_detail", "passages", passage["passage"])}


def _sans_accent(s):
    """« métal » → « metal », « chèvre » → « chevre ». Les clés de corpus sont
    sans accent, alors que le moteur renvoie l'animal et l'élément accentués."""
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if unicodedata.category(c) != "Mn")


def _chinois_natal(n):
    """Le signe chinois de naissance — l'animal et l'élément, plus leurs textes.

    C'est un axe d'IDENTITÉ (comme les nombres ou le trio du ciel), pas la
    couche du jour : ici on décrit qui tu es (« Singe de Métal »), pas la
    relation du jour à ton animal. Additif : un portrait d'animal + une nuance
    d'élément, jamais 60 combinaisons.
    """
    pa = chinois.pilier_annee(n["annee"], n["mois"], n["jour"])
    animal, element = pa["animal"], pa["element"]
    liaison = "d'" if _sans_accent(element)[0] in "aeiou" else "de "
    return {
        "animal": animal, "element": element, "polarite": pa["polarite"],
        # « Singe de Métal », « Coq d'Eau » — le signe nommé d'un bloc.
        "signe": f"{animal.capitalize()} {liaison}{element.capitalize()}",
        "portrait": corpus.lire("chinois_natal", "animaux", _sans_accent(animal)),
        "nuance": corpus.lire("chinois_natal", "elements", _sans_accent(element)),
    }


# La chèvre est le seul animal féminin de la liste ; le reste prend « le ».
def _avec_article(animal):
    return ("la " if animal == "chèvre" else "le ") + animal.capitalize()


def _sous_titre_chinois(sc):
    """La ligne qui nomme les animaux, calculée (l'app la met, pas le corpus).

    « Le Tigre s'oppose à ton Singe. » Le texte du corpus, lui, ne nomme aucun
    animal : il décrit la dynamique de la relation. Séparation nette entre le
    calcul (ici) et la rédaction (là-bas).
    """
    natal = sc["animal_natal"].capitalize()
    if sc["relation"] == "identique":
        return f"C'est le jour {_avec_article(sc['animal_du_jour']).replace('le ', 'du ').replace('la ', 'de la ')}, le tien."
    verbe = {
        "choc": "s'oppose à",
        "harmonie": "s'allie à",
        "trine": "est en affinité avec",
        "nuisance": "accroche un peu",
    }[sc["relation"]]
    return f"{_avec_article(sc['animal_du_jour'])} {verbe} ton {natal}."


def _titre_du_jour(textes, force_transit, date, ecart_lune, n):
    """Le routeur du titre : quelle voix prend la tête aujourd'hui.

    Quatre saillances comparées (ciel, numéro, lune, chinois). Pour l'instant
    seule la voix CHINOISE peut ravir le titre au ciel ; numéro et lune restent
    des sections de contexte (leur corpus de titre viendra après). Si le chinois
    gagne mais que son corpus manque encore, on retombe proprement sur le ciel.
    """
    sc = chinois.saillance_chinoise(n["annee"], n["mois"], n["jour"], date)
    choix = routeur.router_du_jour(force_transit, date, ecart_lune,
                                   score_chinois=sc["score"])
    tr = textes.get("transit") or {}
    titre = {"source": "ciel", "miroir": tr.get("miroir"), "geste": tr.get("geste")}
    if choix["voix"] == "chinois":
        rel = corpus.lire("chinois_detail", "relations", sc["relation"]) or {}
        if rel.get("miroir"):
            titre = {"source": "chinois", "miroir": rel["miroir"],
                     "geste": rel.get("geste"), "en_bref": rel.get("en_bref"),
                     "sous_titre": _sous_titre_chinois(sc)}
    return titre, {"choix": choix, "chinois": sc}


def _phase_du_transit(dominante):
    """Où en est le contact dans son passage : approche, cœur, ou retrait.

    Dérivée de l'exactitude et du SENS (applicatif) du transit — donc du ciel
    réel, jamais d'un tirage. C'est ce qui permet à un même contact
    (ex. Mercure carré ton Soleil) de ne pas rendre EXACTEMENT le même texte
    à chaque passage : un aspect qui se construit, culmine, ou se referme,
    ce n'est pas la même expérience vécue.

    ⚠️ Le piège de la première version : « cœur » dès exactitude ≥ 0,66. Or un
    aspect serré TIENT à ce rendement pendant plusieurs jours — une station
    rétrograde, une semaine entière. Le texte se gelait sur « cœur » jour après
    jour, et l'utilisateur voyait le même message en boucle. Le sens du transit
    (applicatif) était ignoré tant que l'exactitude restait haute.

    D'où la règle actuelle : « cœur » ne désigne plus qu'une BANDE TRÈS SERRÉE
    autour du pic (le moment quasi exact). Les ailes du passage se distinguent
    par la DIRECTION — ce qui se resserre (applicatif) approche du pic, ce qui
    s'écarte s'en retire. Un passage de plusieurs jours progresse alors
    réellement : approche → cœur → retrait.
    """
    ex = dominante.get("exactitude", 0)
    if ex >= 0.92:
        return "coeur"
    return "approche" if dominante.get("applicatif") else "retrait"


def _resoudre_variantes(entree, dominante):
    """Une entrée du corpus des transits peut être un texte unique
    ({miroir, geste}) ou plusieurs variantes ({approche, coeur, retrait}).

    Les entrées non converties restent lisibles telles quelles — c'est la clé
    "miroir" qui distingue les deux formes.
    """
    if not isinstance(entree, dict) or entree is None or "miroir" in entree:
        return entree
    phase = _phase_du_transit(dominante)
    return entree.get(phase) or entree.get("coeur") or next(iter(entree.values()), None)


# Fenêtre de regard en arrière, en jours. Assez large pour briser les blocs
# de jours identiques (une station rétrograde tient une semaine), assez
# courte pour rester bon marché. DÉTERMINISTE : la fenêtre est une fonction
# fixe de (naissance, date), jamais d'un état — la thèse d'Align est intacte.
FENETRE_RECURRENCE = 7


def _declencheurs_pour(theme, date):
    """Déclencheurs classés par force pour une date — version LÉGÈRE : ni
    corpus, ni cartes, juste `J.transits` filtré. Sert à la fenêtre de regard
    en arrière, où l'on n'a besoin que des forces, pas du message du jour."""
    t = moteur.eph.instant(date.year, date.month, date.day, 12, 0, 0)
    ciel = {c: moteur.eph.position(c, t) for c in moteur.eph.CORPS}
    positions = {c: p["lon"] for c, p in ciel.items()}
    vitesses = {c: p["vitesse_lon"] for c, p in ciel.items()}
    return [x for x in J.transits(theme, positions, vitesses)
            if x["etage"] == "declencheur"]


def _recents_pour(theme, date, fenetre=FENETRE_RECURRENCE):
    """Les clés dominantes des `fenetre` jours précédant `date`, du plus
    ancien au plus récent (recents[-1] = hier).

    On balaie la fenêtre de gauche à droite en appliquant LA MÊME règle de
    sélection (`J.choisir_dominante`), pour que « récent » reflète ce qui a
    vraiment été montré — pas seulement le dominant astronomique. Le bord
    gauche s'amorce en naïf : pas de passé connu, `choisir_dominante`
    départage alors par la force. Cela BORNE le regard en arrière à la
    fenêtre, sans cascade vers le passé lointain.
    """
    dominantes = {}   # offset (négatif) -> clé dominante (récurrence)

    def cle_a(offset):
        if offset in dominantes:
            return dominantes[offset]
        d = date + dt.timedelta(days=offset)
        decl = _declencheurs_pour(theme, d)
        # recents = clés déjà résolues parmi les `fenetre` jours précédents.
        rec = [dominantes[j] for j in range(offset - fenetre, offset)
               if j in dominantes]
        dom = J.choisir_dominante(decl, rec) if decl else None
        dominantes[offset] = dom["cle"] if dom else None
        return dominantes[offset]

    for offset in range(-fenetre, 0):
        cle_a(offset)
    return [dominantes[o] for o in range(-fenetre, 0)]


def _jour_pour(profil, date):
    """Tout le calcul du Jour pour un profil, à une date — factorisé hors de
    la route pour que le scheduler des rappels push (voir `_envoyer_rappels`)
    puisse lire exactement le même `titre` que l'API, EN PROCESS, sans faire
    une requête HTTP vers son propre serveur.
    """
    if not profil.get("complet"):
        # Le Fil du jour, le transit dominant, la Lune du jour : tout lit la
        # maison natale (donc l'ascendant) — sans heure ni lieu de naissance,
        # rien de tout ça n'est honnêtement calculable. Voir _construire.
        return {"complet": False, "date": date.isoformat(), "profil_id": profil["id"]}

    n = profil["naissance"]
    theme, r = _croisement(profil, date.year)

    # Le ciel de ce jour, à midi UTC — un instant stable et explicite.
    # Une seule passe par corps : `position` fait déjà trois évaluations
    # d'éphéméride pour la vitesse, la rappeler doublerait le travail.
    t = moteur.eph.instant(date.year, date.month, date.day, 12, 0, 0)
    ciel = {c: moteur.eph.position(c, t) for c in moteur.eph.CORPS}
    positions = {c: p["lon"] for c, p in ciel.items()}
    vitesses = {c: p["vitesse_lon"] for c, p in ciel.items()}

    # Année CIVILE pour les deux : elles s'affichent sur le même bloc et
    # doivent battre à la même horloge. Voir numerologie.annee_personnelle.
    ap = annee_personnelle(n["jour"], n["mois"], date.year)
    # La saison, entre le chapitre (l'année) et la journée (le ciel).
    mp = mois_personnel(n["jour"], n["mois"], date.year, date.month)
    carte_an = carte_de_l_annee(n["jour"], n["mois"], date.year)
    # Le message de la carte de l'année : la couleur qu'elle donne au chapitre,
    # additive au nombre d'année. Registre de l'ANNÉE, pas du jour. (22 ≡ 0.)
    carte_an["message"] = corpus.lire(
        "arcanes", "arcanes", str(0 if carte_an["numero"] == 22 else carte_an["numero"]),
        "pour_l_annee")
    # La carte du jour : même méthode que la naissance, appliquée à la date du
    # jour. Un arcane-écho calculé qui colorie la journée (le ciel mène toujours).
    carte_jr = carte_du_jour(date.day, date.month, date.year)
    # Son message : une invitation du présent (jamais une prédiction), lue sous
    # le nom quand la carte se dévoile. L'arcane 22 est Le Mat, qui ferme la
    # boucle sur le 0 — on lit donc son texte à la clé « 0 ».
    carte_jr["invitation"] = corpus.lire(
        "arcanes", "arcanes", str(0 if carte_jr["numero"] == 22 else carte_jr["numero"]),
        "invitation")
    # La carte mineure PERSONNELLE : couleur = élément de la Lune transit
    # (partagé, change vite) ; rang = écart Soleil transit -> Ascendant natal
    # (personnel, avance sur l'année). Toujours un calcul, jamais un tirage —
    # voir moteur/mineurs.py pour la convention et le piège mathématique évité.
    carte_min = MIN.carte_mineure(
        positions["lune"], positions["soleil"], theme["angles"]["asc"]["lon"])
    carte_min["invitation"] = corpus.lire("mineurs", carte_min["cle"], "invitation")
    # La fenêtre de regard en arrière : pour que la sélection brise les
    # blocs de jours identiques (un transit serré qui domine toute une
    # semaine). Déterministe — voir `_recents_pour`.
    recents = _recents_pour(theme, date)
    j = J.journee(theme, positions, vitesses, ap, carte_an,
                  carte_jour=carte_jr, mois_perso=mp, recents=recents)

    textes = {}
    for genre, cle in j["cles"]:
        if genre == "annee_perso":
            court = corpus.lire("nombres", "annee_perso", ap)
            detail = corpus.lire("annees_detail", "annee_perso", ap)
            # La couche du MONDE, greffée sur l'année personnelle : le climat
            # collectif et l'écart constant qui te sépare de ton époque.
            univers = bloc_univers(n["jour"], n["mois"], date.year)
            textes[genre] = ({**(court or {}), "detail": detail, "univers": univers}
                             if court else None)
        elif genre == "mois_perso":
            # La saison, entre le chapitre (l'année) et la journée (le ciel).
            # Le court et le détail vivent dans le même bloc ici : le corpus des
            # mois est né après la charte de style, il porte déjà les deux.
            detail = corpus.lire("mois_detail", "mois_perso", mp)
            textes[genre] = {**detail, "detail": detail} if detail else None
        elif genre == "phase":
            textes[genre] = corpus.lire("ciel", "phases", j["phase"]["phase"])
        elif genre == "lune_maison":
            textes[genre] = corpus.lire("ciel", "lune_maison", j["lune"]["maison"])
        elif genre == "transit" and j["dominante"]:
            d = j["dominante"]
            # Deux niveaux, du plus précis au plus général : une entrée dédiée
            # à ce contact exact (ex. « mars carré ton Soleil natal ») si elle
            # existe, sinon l'entrée générique de la planète et de la classe.
            # C'est l'addition de tables plutôt que leur produit : on écrit
            # 30 génériques + N précises, jamais 10×3×12 combinaisons.
            cle_generique = f"{d['transit']}_{d['classe']}"
            entree_precise = corpus.lire("transits", "transits_precis", d["cle"])
            entree_generique = corpus.lire("transits", "transits_generiques", cle_generique)
            brut = entree_precise or entree_generique
            resolu = _resoudre_variantes(brut, d)
            # La pensée du soir (« À méditer ») vit au niveau HAUT de l'entrée,
            # à côté des phases — une seule par transit, indépendante de
            # l'heure et de la phase. `_resoudre_variantes` ne renvoie que la
            # variante de phase (approche/coeur/retrait) et la laisserait
            # tomber ; on la regreffe donc explicitement. Repli en DEUX temps :
            # l'entrée précise si elle en a une, sinon la générique — même
            # logique que `brut` ci-dessus, nécessaire car les précises n'ont
            # pas encore leur pensée écrite (corpus en construction) et ne
            # doivent pas priver le générique de la sienne.
            pensee = ((entree_precise or {}).get("pensee_soir")
                      or (entree_generique or {}).get("pensee_soir"))
            if pensee and isinstance(resolu, dict) and "pensee_soir" not in resolu:
                resolu = {**resolu, "pensee_soir": pensee}
            textes[genre] = resolu
        elif genre == "fil":
            # Le Fil du jour : même pattern que "transit" ci-dessus — le
            # moteur émet les candidates (J._cles_fil), la première servie par
            # le corpus gagne. Ancre = le domaine (maison de la Lune) ; puis le
            # transit dominant (raffinement), puis la phase ou la tonalité (le
            # socle), puis le domaine seul (générique, résout toujours).
            for fcle in J._cles_fil(j["dominante"], j["phase"], j["lune"]):
                textes[genre] = corpus.lire("fil", fcle)
                if textes[genre]:
                    break

    # Deux gestes qui s'ouvrent pareil le même matin s'annulent l'un l'autre.
    # Les tables sont écrites séparément mais lues ensemble : c'est ici, et
    # nulle part ailleurs, qu'on peut le voir. On garde le premier (le plus
    # prioritaire) et on retire le geste du second — son miroir reste, lui.
    for garde, retire, _tete in J.gestes_redondants(textes):
        if isinstance(textes.get(retire), dict):
            textes[retire] = {**textes[retire], "geste": None, "geste_retire": True}

    # Le routeur : quelle voix prend le titre du jour. Le ciel mène par défaut ;
    # la voix chinoise le ravit quand sa relation est plus saillante.
    dom = j.get("dominante")
    force_transit = dom["force"] if dom else 0.0
    titre, routage = _titre_du_jour(textes, force_transit, date,
                                    j["phase"]["ecart"], n)

    return {
        "complet": True,
        "date": date.isoformat(),
        "profil_id": profil["id"],
        "jour": j,
        "textes": textes,
        "titre": titre,
        "routeur": routage,
        "manque": [g for g, _ in j["cles"] if not textes.get(g)],
        "carte_annee": carte_an,
        "carte_jour": carte_jr,
        "carte_min": carte_min,
        # La couche la plus lente : la traversée de la vie, universelle.
        "vie": _bloc_vie(n["jour"], n["mois"], n["annee"], date),
    }


@app.get("/api/jour/<profil_id>")
def api_jour(profil_id):
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "profil inconnu"}), 404
    return jsonify(_jour_pour(profil, _date_demandee()))


@app.get("/api/explorer/<profil_id>/<domaine>")
def api_explorer(profil_id, domaine):
    """Explorer : la personne CHOISIT son domaine (au lieu de subir celui du
    jour, dicté par la maison de la Lune). La perle qui en sort continue de
    tourner avec le ciel réel — même mécanique de résolution que le Fil,
    juste avec le domaine forcé. Zéro corpus supplémentaire : `fil.json` sert
    les deux chemins.
    """
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "profil inconnu"}), 404
    if domaine not in J.MAISON_DOMAINE.values():
        return jsonify({"erreur": "domaine inconnu"}), 404
    if not profil.get("complet"):
        return jsonify({"complet": False, "domaine": domaine, "texte": None})

    d = _jour_pour(profil, _date_demandee())
    j = d["jour"]
    texte = None
    for cle in J._cles_fil_domaine(domaine, j["dominante"], j["phase"]):
        texte = corpus.lire("fil", cle)
        if texte:
            break
    return jsonify({"domaine": domaine, "date": d["date"], "texte": texte})


@app.get("/api/explorer/domaines")
def api_explorer_domaines():
    """Les 12 domaines, dans l'ordre des maisons — pour construire la grille
    d'Explorer. Une seule source de vérité (moteur/jour.py::MAISON_DOMAINE) ;
    les libellés français sont ici, pas dans le moteur (pure présentation)."""
    return jsonify([
        {"maison": m, "domaine": d, "label": DOMAINE_LABELS[d]}
        for m, d in sorted(J.MAISON_DOMAINE.items())
    ])


def _plier_signe(signe):
    """« Gémeaux » → « gemeaux ». Les clés de corpus sont sans accent."""
    s = unicodedata.normalize("NFD", signe.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


@app.get("/api/ciel/<profil_id>")
def api_ciel(profil_id):
    """Le Ciel — l'idée globale d'abord, puis chaque astre en détail.

    « Une idée globale, mais qu'on peut facilement aller en demander plus. »
    Le tableau seul ne disait rien ; ici la synthèse vient en premier, et
    chaque astre porte ses deux lectures ADDITIVES : son signe (comment) et
    sa maison (où). Jamais leur produit — ce serait 120 × 120 entrées.
    """
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "Profil inconnu."}), 404
    if not profil.get("complet"):
        # Le Ciel entier (signes, maisons, aspects) exige l'ascendant — donc
        # l'heure ET le lieu de naissance. Sans eux, rien à montrer ici
        # d'honnête (voir _construire) ; Le Portrait, lui, garde ses nombres.
        return jsonify({"complet": False, "attribution": ATTRIBUTION})

    n = profil["naissance"]
    theme = moteur.theme_natal(
        n["annee"], n["mois"], n["jour"], n["heure"], n["minute"],
        n["lat"], n["lon"], n["fuseau"], fold=profil.get("fold", 0),
    )
    s = synthese.synthetiser(theme)

    def textes_astre(nom, signe, maison):
        """Les deux axes, lus séparément puis additionnés à l'écran.

        Les aspects portent leur texte de corpus quand il existe (paires de
        planètes) ; un aspect à un angle (asc/mc) reste sans texte long et
        garde son rendu court par le lexique côté client.
        """
        cle_signe = f"{nom}_{_plier_signe(signe)}"
        aspects = []
        for a in synthese.aspects_d_un_astre(theme, nom):
            texte = corpus.lire("aspects_paires", a["cle"]) if a.get("cle") else None
            aspects.append({**a, "corpus": texte})
        return {
            "signe": corpus.lire("astre_signe", cle_signe),
            "maison": corpus.lire("astre_maison", f"{nom}_{maison}") if maison else None,
            "aspects": aspects,
        }

    astres = {}
    for nom, c in theme["corps"].items():
        if nom == "noeud_moyen":
            continue
        astres[nom] = {**c, "textes": textes_astre(nom, c["signe"], c["maison"])}
    astres["asc"] = {
        **theme["angles"]["asc"], "maison": 1,
        "textes": textes_astre("asc", theme["angles"]["asc"]["signe"], None),
    }
    astres["mc"] = {
        **theme["angles"]["mc"], "maison": 10,
        "textes": textes_astre("mc", theme["angles"]["mc"]["signe"], None),
    }

    globaux = {}
    for genre, cle in s["cles"]:
        globaux[f"{genre}.{cle}"] = corpus.lire("ciel_global", genre, cle)
    for bloc in ("trio", "maitre", "en_vue", "stellium"):
        globaux[bloc] = corpus.lire("ciel_global", bloc, "intro")

    return jsonify({
        "complet": True,
        "theme": theme,
        "synthese": s,
        "astres": astres,
        "globaux": globaux,
        "manque": [f"{g}.{c}" for g, c in s["cles"]
                   if not corpus.lire("ciel_global", g, c)],
        "attribution": ATTRIBUTION,
    })


@app.get("/api/apercu/<profil_id>")
def api_apercu(profil_id):
    """TOUT le thème d'un coup d'œil — chiffres, astres, cartes, sur un écran.

    « Il faut pouvoir bien comprendre facilement tout son thème, tous ces
    chiffres, numéros, et sa carte du ciel — les éléments importants,
    facilement. »

    Aujourd'hui il faut visiter trois écrans et cliquer partout pour se faire
    une idée. Ici : une seule vue, tout nommé (jamais un nombre nu), tout
    cliquable pour aller plus loin. C'est la carte d'identité du thème.
    """
    profil = _charger(profil_id)
    if not profil:
        return jsonify({"erreur": "Profil inconnu."}), 404
    if not profil.get("complet"):
        # Cet aperçu mélange nombres ET thème astro (asc, maisons) sur un seul
        # écran — sans heure ni lieu de naissance, la moitié manque. Plutôt
        # qu'un aperçu bancal, on renvoie vers Le Portrait (qui, lui, garde
        # honnêtement les nombres) — voir _construire.
        return jsonify({"complet": False, "attribution": ATTRIBUTION})

    date = _date_demandee()
    n = profil["naissance"]
    theme, r = _croisement(profil, date.year)
    s = synthese.synthetiser(theme)
    nb = r["nombres"]

    def nombre(cle):
        d = corpus.lire("nombres_detail", cle, nb[cle]["valeur"]) or {}
        return {
            "valeur": nb[cle]["valeur"],
            "base": nb[cle]["base"],
            "maitre": nb[cle]["maitre"],
            "heritages": nb[cle]["heritages"],
            "en_un_mot": d.get("en_un_mot"),
            "accord": (r["accords"].get(cle) or {}).get("etat"),
        }

    ap = annee_personnelle(n["jour"], n["mois"], date.year)
    mp = mois_personnel(n["jour"], n["mois"], date.year, date.month)

    return jsonify({
        "complet": True,
        # Les profils d'avant l'ajout de `nom_affiche` n'ont que `prenoms_nom` :
        # on retombe dessus plutôt que d'afficher « None ».
        "profil": {"nom": profil.get("nom_affiche") or " ".join(profil["prenoms_nom"]),
                   "naissance": f"{n['jour']:02d}/{n['mois']:02d}/{n['annee']}",
                   "heure": f"{n['heure']:02d}h{n['minute']:02d}",
                   "lieu": n["lieu"]},
        # les nombres, chacun nommé
        "nombres": {c: nombre(c) for c in ("cap", "voix", "foyer", "elan")},
        "chantiers": nb["appuis"]["chantiers"],
        # le ciel, l'essentiel
        "trio": s["trio"],
        "element_dominant": s["equilibres"]["element_dominant"],
        "element_creux": s["equilibres"]["element_creux"],
        "modalite": s["equilibres"]["modalite_dominante"],
        "equilibre": s["equilibres"]["equilibre"],
        "maitre_theme": s["maitre"],
        "en_vue": s["en_vue"],
        "stelliums": s["stelliums"],
        # le signe chinois de naissance — 4e axe d'identité (animal + élément)
        "chinois": _chinois_natal(n),
        # les cartes
        "cartes": r["cartes"],
        "pont": r["ponts"]["naissance"],
        # le temps, quatre échelles de la plus lente à la plus rapide : la vie
        # (l'âge, universel), l'année (le chapitre), le mois (la saison) —
        # la journée, elle, se lit dans le Jour.
        "temps": {
            "vie": _bloc_vie(n["jour"], n["mois"], n["annee"], date),
            "annee": {"valeur": ap,
                      "en_un_mot": (corpus.lire("annees_detail", "annee_perso", ap) or {}).get("en_un_mot"),
                      "carte": r["cartes"].get("annee", {}).get("nom"),
                      "univers": bloc_univers(n["jour"], n["mois"], date.year)},
            "mois": {"valeur": mp,
                     "en_un_mot": (corpus.lire("mois_detail", "mois_perso", mp) or {}).get("en_un_mot")},
        },
        "avis": theme["avis"],
        "limites": theme["limites"],
    })


@app.get("/api/lexique")
def api_lexique():
    """Le lexique de vulgarisation.

    Un nombre nu ne dit rien : « Le Cap 9 », « héritage 19 », « maison 10 »,
    « balsamique » sont opaques à qui n'y connaît rien. Le client s'en sert
    pour ne jamais afficher un terme technique sans son nom en français.
    """
    return jsonify(corpus.tables.get("lexique", {}))


@app.get("/api/corpus")
def api_corpus():
    """Ce que le corpus contient — Phase 1 l'affiche, plutôt que de le cacher."""
    return jsonify(corpus.inventaire())


@app.get("/api/conventions")
def api_conventions():
    """Les règles de calcul d'Align, publiées.

    C'est un angle mort du marché : deux conventions contradictoires coexistent
    en numérologie française (É = 5 comme E, ou é = 1 avec sa valeur propre),
    elles donnent des résultats DIFFÉRENTS pour le même nom, et aucune app ne
    dit laquelle elle applique. Ta Trame publie les siennes — c'est cohérent avec
    « déterministe » : reproductible ET auditable.

    Chaque règle dit sa source : ce qui est IMPRIMÉ dans un ouvrage, et ce
    que Ta Trame a TRANCHÉ là où les sources se taisent.
    """
    return jsonify({
        "accents": {
            "regle": "Transparents. É vaut 5, comme E. Idem è, ê, ë, ç, à, ù, ï.",
            "source": "imprimé",
            "detail": "C'est écrit noir sur blanc dans nos ouvrages de référence "
                      "(« é, è = e · ä = a · ç = c ») et leur propre exemple le confirme : "
                      "STÉPHANE = 34, un total qui n'est atteignable qu'avec É = 5.",
        },
        "trait_union": {
            "regle": "Ne fusionne pas. « Marie-Jeanne » compte pour deux unités "
                     "dont on additionne les totaux.",
            "source": "imprimé",
            "detail": "Spécifié dans nos ouvrages de référence. C'est ce qui fait "
                      "apparaître des sous-nombres qu'un mot unique masquerait.",
        },
        "apostrophes": {
            "regle": "Ignorées. « D'Artagnan » se calcule sur DARTAGNAN, en un seul mot.",
            "source": "tranché par Ta Trame",
            "detail": "Nos ouvrages de référence n'en parlent pas (aucune occurrence "
                      "sur 90 000 mots). L'apostrophe n'est pas un séparateur.",
        },
        "particules": {
            "regle": "Gardées, et soudées au nom qu'elles introduisent : "
                     "« de Gaulle » se calcule sur DEGAULLE.",
            "source": "tranché par Ta Trame",
            "detail": "Nos ouvrages de référence sont muets sur la graphie, mais leur "
                      "principe général tranche : ils exigent l'état civil EXACT — or "
                      "« de Gaulle » est l'état civil, « de » compris. "
                      "Rien n'est jeté. Une particule n'est pas un nom pour "
                      "autant : elle en introduit un, donc elle se soude, et l'unité de "
                      "calcul reste le nom civil entier. C'est la même règle que "
                      "l'apostrophe : élidée ou espacée, une particule se comporte pareil.",
        },
        "annee_personnelle": {
            "regle": "Bascule le 1er janvier, pas à l'anniversaire.",
            "source": "tranché par Ta Trame, appuyé sur les sources",
            "detail": "Une partie de nos ouvrages de référence l'affirme explicitement "
                      "(année civile), l'autre parle de « l'année en cours ». La carte "
                      "de l'année suit la même "
                      "horloge — les deux s'affichent ensemble. Le retour solaire, lui, "
                      "reste à l'anniversaire : c'est de l'astronomie, pas une convention. "
                      "Deux couches, deux horloges, qui s'additionnent sans se contredire.",
        },
        "mois_personnel": {
            "regle": "Ton année personnelle plus le numéro du mois, réduit. "
                     "Il bascule le 1er du mois.",
            "source": "tranché par Ta Trame",
            "detail": "À savoir : nos ouvrages de référence ne documentent pas le mois "
                      "personnel. L'un n'en parle nulle part, l'autre n'a aucun module de "
                      "prévision. La formule vient de la numérologie pythagoricienne "
                      "classique, où elle est standard et unanime. C'est donc un ajout "
                      "de Ta Trame, appuyé sur cette tradition commune plutôt que sur nos "
                      "ouvrages habituels. Le cycle de 9 mois ne se cale pas sur "
                      "les 12 du calendrier : il glisse d'un cran chaque année, donc un "
                      "même mois ne retombe jamais au même endroit.",
        },
        "annee_universelle": {
            "regle": "L'année civile réduite. 2026 vaut 1, comme pour tout le "
                     "monde. Ton écart à elle ne dépend que de ta date de "
                     "naissance, donc il est le même toute ta vie.",
            "source": "tranché par Ta Trame, appuyé sur la tradition commune",
            "detail": "L'année universelle (le climat collectif de l'époque) est "
                      "standard en numérologie pythagoricienne. Le lien avec "
                      "l'année personnelle est arithmétique et exact : l'année "
                      "personnelle est l'année universelle plus un décalage, "
                      "réduit — et ce décalage, réduit(jour + mois de naissance), "
                      "ne bouge jamais. Tu gardes le même nombre de crans "
                      "d'avance (ou de retard) sur ton époque, année après année. "
                      "Nos ouvrages de référence ne croisent pas les "
                      "deux couches : le croisement est un ajout de Ta Trame.",
        },
        "jour_personnel": {
            "regle": "Il n'y en a pas. Le jour vient du ciel.",
            "source": "tranché par Ta Trame",
            "detail": "Beaucoup d'apps proposent un « jour personnel » numérologique. "
                      "Ta Trame n'en a pas, et c'est délibéré : nos ouvrages de référence "
                      "n'en documentent aucun, et l'inventer serait de la doctrine maison. Ce "
                      "que tu lis chaque matin vient du ciel réel, qui bouge tout seul — "
                      "la Lune change de signe tous les deux jours et demi. C'est de là "
                      "que vient la variété, pas d'un calcul de plus.",
        },
        "carte_du_jour": {
            "regle": "La carte de naissance de la journée : quanti + mois + année, réduit vers 22.",
            "source": "tranché par Ta Trame",
            "detail": "Aucune des deux sources ne calcule de carte quotidienne. Ta Trame "
                      "prolonge la méthode de la carte de naissance à la journée — "
                      "exactement comme la carte de l'année la prolonge à l'année. Elle "
                      "change chaque jour, est la même pour tout le monde, toujours par "
                      "le même calcul. Cet arcane ne remplace pas "
                      "le ciel, il le colorie. La voix qui mène la journée reste le ciel "
                      "(voir le routeur) ; la carte du jour est un écho qui s'y ajoute. "
                      "« Le jour vient du ciel » reste vrai — la carte du jour ne le "
                      "contredit pas, elle s'y superpose.",
        },
        "carte_mineure_personnelle": {
            "regle": "Une carte MINEURE (parmi les 56, As et figures inclus) en plus de "
                     "la carte du jour universelle. La couleur (Bâtons/Coupes/Épées/"
                     "Deniers) vient de l'élément du signe où passe la Lune transit du "
                     "jour, partagée par tout le monde. Le rang (As, 2..10, Valet, "
                     "Cavalier, Reine, Roi) vient de l'écart entre le Soleil transit du "
                     "jour et TON Ascendant de naissance, divisé en 14 parts égales.",
            "source": "tranché par Ta Trame, sur une base Golden Dawn (Mathers, Book T, "
                      "1888, domaine public)",
            "detail": "Le Golden Dawn découpe le zodiaque à trois résolutions "
                      "superposées (décans de 10° pour les numérales, bandes de 20° "
                      "pour les figures, éléments pour les As) : un seul degré du ciel "
                      "appartient donc à plusieurs de ces couches à la fois, et aucune "
                      "source ne fournit de règle plate « un degré = une des 56 cartes ». "
                      "Ta Trame tranche avec deux axes, chacun porté par un astre "
                      "différent, pour que les 56 cartes restent toutes atteignables — "
                      "vérifié par calcul, pas supposé (voir moteur/mineurs.py). Cette "
                      "carte est personnelle et différente de la carte du jour "
                      "universelle (qui reste un majeur, calculé sur la date civile "
                      "seule, la même pour tout le monde) : les deux cohabitent, l'une "
                      "colore le climat commun, l'autre ta texture propre — toutes deux "
                      "issues du même calcul.",
        },
        "fil_du_jour": {
            "regle": "Un conseil de vie quotidien, choisi par le ciel. La maison où "
                     "passe la Lune donne le DOMAINE (le couple, l'argent, le travail, "
                     "la présence…) ; le transit dominant et la phase lunaire "
                     "choisissent l'entrée dans ce domaine.",
            "source": "imprimé (maisons) + tranché par Ta Trame (le reste)",
            "detail": "La correspondance maison → domaine de vie est classique et "
                      "imprimée : I = soi, II = ressources et argent, III = échanges et "
                      "communication, IV = foyer et racines, V = création et jeu, VI = "
                      "quotidien, santé et habitudes, VII = l'autre et le couple, VIII = "
                      "traversée et transformation, IX = sens et quête, X = métier, XI = "
                      "communauté, XII = retrait et intérieur. Ce que Ta Trame a TRANCHÉ : "
                      "que trois domaines « à processus » (création, quotidien, métier) "
                      "suivent le cycle des huit phases lunaires, et qu'ailleurs la "
                      "nuance vienne de la tonalité du transit dominant (fluide quand "
                      "l'aspect coule, tension quand il est dur). Les textes sont "
                      "distillés de nombreux ouvrages de développement personnel, "
                      "réécrits dans la voix de Ta Trame : les concepts sont repris, jamais "
                      "leur prose. Comme pour le reste, la variété vient du mouvement "
                      "réel de la Lune, qui change de maison tous les deux jours et "
                      "demi.",
        },
        "personologie": {
            "regle": "Le signe se découpe en 48 sous-périodes (cuspide d'entrée, "
                     "3 semaines, cuspide de sortie) qui l'affinent sans le "
                     "remplacer. L'axe des nœuds lunaires (le nœud sud, l'acquis ; "
                     "le nœud nord, le cap) donne une couche « d'où tu viens, où "
                     "tu vas », lue par signe.",
            "source": "structure reprise d'un système classique, vocabulaire et "
                      "textes tranchés par Ta Trame",
            "detail": "Le découpage de l'année en 48 périodes (12 cuspides de "
                      "±3,5° + 36 semaines de ~7,67°, une convention que Ta Trame "
                      "fixe elle-même) est une idée structurelle ancienne, mais "
                      "aucun nom ni texte d'un ouvrage n'est repris : Ta Trame "
                      "écrit son propre vocabulaire, à partir du sens "
                      "astrologique de chaque position, jamais des textes d'une "
                      "source. L'axe des nœuds est de l'astronomie pure (les "
                      "nœuds moyens de la Lune, déjà calculés dans le thème) : "
                      "le nœud sud n'est jamais présenté comme un défaut à fuir, "
                      "ni le nœud nord comme une obligation — les deux "
                      "s'intègrent, comme tout le reste chez Ta Trame, ils "
                      "s'additionnent.",
        },
        "annee_chinoise": {
            "regle": "Commence à Li Chun (立春, le « début du printemps »), fixé "
                     "au 4 février. Un natif d'avant cette date porte l'animal de "
                     "l'année précédente.",
            "source": "tranché par Ta Trame, appuyé sur Walters",
            "detail": "Le début de l'année chinoise a « autant que cinq choix "
                      "possibles » selon Walters. La majorité des astrologues "
                      "retient le calendrier SOLAIRE (Li Chun, début février), pas "
                      "le Nouvel An lunaire — c'est le choix de Ta Trame. ⚠️ La date "
                      "exacte de Li Chun DÉRIVE entre le 3 et le 5 février selon "
                      "l'année (Walters : ~5 février au début du XXe siècle, ~3 à "
                      "la fin du XXIe). Ta Trame la fixe au 4 février : une "
                      "approximation stable qui ne peut décaler que les natifs à un "
                      "jour près de la frontière. Le pilier du JOUR, lui, est "
                      "vérifié au calendrier de Joey Yap.",
        },
        "maisons": {
            "regle": "Placidus, avec repli sur Porphyry au-delà du cercle polaire.",
            "source": "consensus des ouvrages",
            "detail": "Les angles (Ascendant, Milieu du Ciel) sont identiques dans tous "
                      "les systèmes : seules les cuspides intermédiaires varient. "
                      "Au-delà du cercle polaire, Placidus n'est pas défini "
                      "mathématiquement — le repli est annoncé, jamais silencieux.",
        },
        "ephemerides": {
            "regle": "DE440s (JPL/NASA), positions apparentes, zodiaque tropical.",
            "source": "domaine public",
            "detail": "Le fichier est vendorisé et vérifié par empreinte au démarrage : "
                      "un fichier différent donnerait des thèmes différents, en silence. "
                      "Précision : les angles sont exacts à 0,000001° contre la référence "
                      "du métier, soit très en dessous du seuil astrologique (1 minute d'arc).",
        },
        "determinisme": {
            "regle": "Chaque lecture vient d'un texte écrit à l'avance, pour ton profil "
                     "exact et la date du jour.",
            "source": "conception",
            "detail": "Même profil + même date = même lecture, toujours — sans tirage "
                      "aléatoire, sans modèle de langage, sans appel réseau au moment de "
                      "la lecture. Les textes sont rédigés à l'avance ; l'app ne fait que "
                      "les lire. La variété vient du ciel réel, qui bouge tout seul — la "
                      "Lune change de signe tous les deux jours et demi.",
        },
    })


@app.get("/sw.js")
def service_worker():
    """Servi à la RACINE (pas `/static/sw.js`) : la portée d'un service worker
    est le dossier qui le sert — sous `/static/`, il ne pourrait contrôler que
    `/static/`, jamais l'app elle-même. Le piège classique du service worker
    enregistré avec une portée trop étroite."""
    return app.send_static_file("sw.js")


@app.get("/api/notifications/cle-publique")
def api_notifications_cle_publique():
    v = _vapid()
    if not v:
        return jsonify({"erreur": "clés VAPID non générées (scripts/generer_cles_vapid.py)"}), 503
    return jsonify({"cle": _cle_publique_navigateur(v)})


@app.get("/api/notifications/<profil_id>")
def api_notifications_lire(profil_id):
    """L'état du réglage — jamais l'abonnement brut (le client n'en a pas
    besoin, et ce n'est pas à lui de le revoir)."""
    if not _charger(profil_id):
        return jsonify({"erreur": "profil inconnu"}), 404
    return jsonify({"actif": notif.lire(profil_id)["actif"]})


@app.put("/api/notifications/<profil_id>")
def api_notifications_maj(profil_id):
    """Active/désactive les rappels et stocke l'abonnement push du navigateur.

    Fichier séparé de l'identité du profil (voir `moteur/notifications.py`) —
    une édition du nom ou de la date de naissance ne touche jamais ceci.
    """
    if not _charger(profil_id):
        return jsonify({"erreur": "profil inconnu"}), 404
    d = request.get_json(force=True) or {}
    prefs = notif.lire(profil_id)
    prefs["actif"] = bool(d.get("actif"))
    if prefs["actif"]:
        prefs["subscription"] = d.get("subscription") or prefs.get("subscription")
        prefs["fuseau_notif"] = d.get("fuseau_notif") or prefs.get("fuseau_notif")
    else:
        # Désactivé : on efface l'abonnement plutôt que de le garder inerte —
        # une réactivation redemandera la permission proprement.
        prefs["subscription"] = None
    notif.ecrire(profil_id, prefs)
    return jsonify({"ok": True, "actif": prefs["actif"]})


def _envoyer_push(profil_id, subscription, corps):
    """Envoie une notification, ou désactive proprement l'abonnement en cause.

    ⚠️ `pywebpush` peut échouer de plusieurs façons AVANT même la requête
    réseau (abonnement corrompu, clés mal encodées) — pas seulement via
    `WebPushException` (410 Gone, permission révoquée côté navigateur). On
    attrape large, DÉLIBÉRÉMENT : le job du scheduler itère TOUS les profils
    actifs, et un seul abonnement en mauvais état ne doit jamais empêcher
    l'envoi aux autres.
    """
    v = _vapid()
    if not v:
        return
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps({"titre": "Ta Trame", "corps": corps}, ensure_ascii=False),
            vapid_private_key=v,
            vapid_claims=dict(VAPID_CLAIMS),
        )
    except Exception as e:
        print(f"[notifications] échec d'envoi pour {profil_id!r}, "
              f"abonnement désactivé : {e!r}")
        prefs = notif.lire(profil_id)
        prefs["actif"] = False
        prefs["subscription"] = None
        notif.ecrire(profil_id, prefs)


def _envoyer_rappels():
    """Le job du scheduler : à chaque tick, qui doit recevoir un rappel
    MAINTENANT (à SON heure locale), et qui ne l'a pas déjà eu aujourd'hui.

    Réutilise `_jour_pour` — le même calcul que `/api/jour` — pour que le
    contenu envoyé soit EXACTEMENT celui que l'app afficherait, jamais une
    version divergente calculée en double.
    """
    maintenant = dt.datetime.now(dt.timezone.utc)
    for profil_id in notif.profils_actifs():
        prefs = notif.lire(profil_id)
        fuseau = prefs.get("fuseau_notif")
        creneau = notif.creneau_courant(maintenant, fuseau)
        if not creneau:
            continue
        date_loc = notif.date_locale(maintenant, fuseau)
        date_iso = date_loc.isoformat()
        if notif.deja_envoye_aujourdhui(prefs, creneau, date_iso):
            continue
        profil = _charger(profil_id)
        if not profil or not profil.get("complet"):
            continue
        resultat = _jour_pour(profil, date_loc)
        contenu = notif.contenu_notification(resultat["titre"], creneau)
        if not contenu:
            continue
        _envoyer_push(profil_id, prefs["subscription"], contenu)
        notif.ecrire(profil_id, notif.marquer_envoye(prefs, creneau, date_iso))


def _demarrer_scheduler():
    """Un scheduler IN-PROCESS suffit : le serveur tourne en un seul process
    long-lived (`run.sh` fait `exec`, pas de reloader ni de multi-workers,
    voir `.claude/launch.json`) — pas besoin de cron externe.

    ⚠️ Appelé uniquement depuis `if __name__ == "__main__":`, jamais à
    l'import du module — `tests/test_profils.py` importe `app`, et un import
    ne doit jamais démarrer un thread d'arrière-plan en silence.
    """
    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(_envoyer_rappels, "interval", minutes=10, id="rappels_du_jour")
    sched.start()
    return sched


# --------------------------------------------------------- accès admin
#
# Martin est admin de DEUX façons : (1) connecté à son compte dans l'app
# (COMPTE_ADMIN déverrouillé dans la session — le cas normal, un lien apparaît
# dans l'app), ou (2) le mot de passe admin (REPLI, depuis un appareil où il
# n'est pas connecté — voir la page de login /admin).

def _est_admin():
    if session.get("admin_ok"):
        return True
    return COMPTE_ADMIN in (session.get("deverrouilles") or [])


# --------------------------------------------------------- journal d'activité
#
# Qui se connecte, quand, combien de temps, et quelles SECTIONS sont visitées.
# Données PERSONNELLES (Loi 25) : journal minimal, append-only, à part des
# profils, jamais committé (voir .gitignore). Une ligne JSON par événement :
#   {t, profil, nom, type: 'ouverture'|'nav'|'ping', vue}
# Le frontend l'alimente (journalActivite) : 'ouverture' au démarrage, 'nav' à
# chaque changement de section (pour la popularité des sections), 'ping' toutes
# les 60 s tant que l'app est au premier plan (pour estimer la DURÉE). Le
# serveur horodate et n'accepte que d'une session déverrouillée (pas un
# formulaire ouvert au monde).

ACTIVITE_PATH = RACINE / "data" / "activite.jsonl"
#: Coupure de session : au-delà de ce silence, on considère une NOUVELLE session.
SESSION_TROU_MIN = 5


@app.post("/api/activite")
def api_activite():
    if not (session.get("deverrouilles") or []):
        return ("", 204)                 # pas connecté : on ignore, sans erreur
    body = request.get_json(silent=True) or {}
    type_ = (body.get("type") or "").strip()[:20]
    if type_ not in ("ouverture", "nav", "ping"):
        return ("", 204)
    profil = (body.get("profil") or "").strip()[:80]
    ligne = {
        "t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "profil": profil,
        "nom": (_charger(profil) or {}).get("nom_affiche", "") if profil else "",
        "type": type_,
        "vue": (body.get("vue") or "").strip()[:40],
    }
    try:
        ACTIVITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ACTIVITE_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    except OSError:
        pass                             # jamais bloquer l'app pour du journal
    return ("", 204)


def _lire_activite():
    if not ACTIVITE_PATH.exists():
        return []
    lignes = []
    for l in ACTIVITE_PATH.read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l:
            continue
        try:
            lignes.append(json.loads(l))
        except json.JSONDecodeError:
            continue
    return lignes


def _synthese_activite():
    """Agrège le journal : par testeur (dernière visite, nb de sessions, temps
    total estimé, en ligne ?) + popularité GLOBALE des sections."""
    evts = _lire_activite()
    par_profil = {}
    sections = {}
    for e in evts:
        pid = e.get("profil") or "?"
        par_profil.setdefault(pid, {"nom": e.get("nom") or pid, "ts": []})
        try:
            t = dt.datetime.fromisoformat(e["t"])
        except (KeyError, ValueError):
            continue
        par_profil[pid]["ts"].append(t)
        if e.get("nom"):
            par_profil[pid]["nom"] = e["nom"]
        if e.get("type") == "nav" and e.get("vue"):
            sections[e["vue"]] = sections.get(e["vue"], 0) + 1

    maintenant = dt.datetime.now(dt.timezone.utc)
    trou = dt.timedelta(minutes=SESSION_TROU_MIN)
    testeurs = []
    for pid, d in par_profil.items():
        ts = sorted(d["ts"])
        if not ts:
            continue
        # Découpe en sessions : un trou > SESSION_TROU_MIN ouvre une session.
        sessions, courant = [], [ts[0]]
        for prec, cur in zip(ts, ts[1:]):
            if cur - prec > trou:
                sessions.append(courant); courant = [cur]
            else:
                courant.append(cur)
        sessions.append(courant)
        # Durée d'une session = du 1er au dernier événement (une session d'un
        # seul événement compte comme très courte, arrondie à 1 min).
        total_s = sum(max((s[-1] - s[0]).total_seconds(), 60) for s in sessions)
        derniere = ts[-1]
        testeurs.append({
            "nom": d["nom"], "profil": pid,
            "derniere": derniere, "nb_sessions": len(sessions),
            "total_min": round(total_s / 60),
            "en_ligne": (maintenant - derniere) < dt.timedelta(minutes=2),
        })
    testeurs.sort(key=lambda x: x["derniere"], reverse=True)
    sections_tri = sorted(sections.items(), key=lambda kv: kv[1], reverse=True)
    return testeurs, sections_tri


# --------------------------------------------------------- commentaires bêta
#
# Un mot rapide pour Martin (bug, idée, impression), jamais visible des autres
# utilisateurs — lu uniquement via /admin/commentaires, gardé par le mot de
# passe admin (même secret que /activer et /reinitialiser-mdp).

COMMENTAIRES_PATH = RACINE / "data" / "commentaires.json"


def _lire_commentaires():
    if not COMMENTAIRES_PATH.exists():
        return []
    try:
        return json.loads(COMMENTAIRES_PATH.read_text(encoding="utf-8")).get("entries", [])
    except json.JSONDecodeError:
        return []


def _ecrire_commentaires(entries):
    _ecrire(COMMENTAIRES_PATH, {"entries": entries})


@app.post("/api/commentaire")
def api_commentaire():
    """{texte, profil, nom_affiche, vue} — exige d'être connecté à UN compte
    (n'importe lequel) : pas un formulaire ouvert au monde entier sans lien
    avec l'app, mais aucune vérification de PROPRIÉTÉ du profil déclaré (un
    champ de contexte facultatif, pas une donnée sensible)."""
    if not (session.get("deverrouilles") or []):
        return jsonify({"erreur": "verrouille"}), 401
    body = request.get_json(silent=True) or {}
    texte = (body.get("texte") or "").strip()[:4000]
    if not texte:
        return jsonify({"erreur": "Le commentaire est vide."}), 400
    entries = _lire_commentaires()
    entries.append({
        "id": f"c{len(entries) + 1:04d}-{secrets.token_hex(3)}",
        "texte": texte,
        "profil": (body.get("profil") or "").strip()[:80],
        "nom_affiche": (body.get("nom_affiche") or "").strip()[:120],
        "vue": (body.get("vue") or "").strip()[:40],
        "cree_le": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "lu": False,
    })
    _ecrire_commentaires(entries)
    return jsonify({"ok": True})


_ADMIN_COMMENTAIRES_TPL = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Commentaires — Ta Trame</title>
<style>
body{font-family:-apple-system,sans-serif;max-width:720px;margin:40px auto;padding:0 20px;
  background:#141110;color:#eee}
.c{border:1px solid #333;border-radius:10px;padding:14px 16px;margin-bottom:14px}
.c.non-lu{border-color:#e9d494}
.meta{font-size:12px;color:#999;margin-bottom:8px}
.texte{white-space:pre-wrap;line-height:1.5}
a{color:#e9d494}
input,button{font:inherit;padding:8px 10px;border-radius:6px;border:1px solid #333;
  background:#1c1918;color:#eee}
button{background:#e9d494;color:#141110;border:none;cursor:pointer;padding:8px 12px}
details{margin-bottom:24px;font-size:14px;color:#bbb}
details form{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.ok{color:#9fd49f}
.onglets{margin-bottom:18px}
.onglets a{margin-right:16px}
</style></head><body>
<div class="onglets"><a href="/">← Ta Trame</a> · <a href="/admin">📊 Tableau de bord</a> · <b>Commentaires</b></div>
<h2>Commentaires bêta ({{ entries|length }})</h2>
<details{{ ' open' if maj else '' }}>
  <summary>Changer le mot de passe admin</summary>
  {% if maj %}<p class="ok">Mot de passe changé.</p>{% endif %}
  <form method="post" action="/admin/mot-de-passe">
    <input type="password" name="nouveau_mdp" placeholder="Nouveau mot de passe" autofocus>
    <button>Changer</button>
  </form>
</details>
{% for e in entries %}
<div class="c {{ 'non-lu' if not e.lu else '' }}">
  <div class="meta">{{ e.nom_affiche or e.profil or 'anonyme' }} · {{ e.vue or '?' }} · {{ e.cree_le }}
    {% if not e.lu %} · <a href="?lu={{ e.id }}">marquer lu</a>{% endif %}</div>
  <div class="texte">{{ e.texte }}</div>
</div>
{% else %}
<p>Aucun commentaire pour l'instant.</p>
{% endfor %}
</body></html>"""

_ADMIN_LOGIN_TPL = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Commentaires — Ta Trame</title>
<style>body{font-family:-apple-system,sans-serif;max-width:420px;margin:80px auto;
  padding:0 20px;background:#141110;color:#eee}
input,button{font:inherit;padding:9px 11px;border-radius:6px;border:1px solid #333;
  background:#1c1918;color:#eee;width:100%;margin-top:8px}
button{background:#e9d494;color:#141110;border:none;cursor:pointer}</style>
a{color:#e9d494}</style>
</head><body><p><a href="/">← Retour à Ta Trame</a></p>
<p>Mot de passe admin <small style="color:#999">(inutile si tu es connecté à ton compte)</small></p>
<form method="post"><input type="password" name="mdp" autofocus>
<button>Entrer</button></form></body></html>"""


@app.route("/admin/commentaires", methods=["GET", "POST"])
def admin_commentaires():
    """Réservé à Martin. Connexion par FORMULAIRE POST (le mot de passe ne
    doit jamais apparaître dans l'URL — visible dans l'historique du
    navigateur, les logs serveur, un partage d'écran) : une fois validé, un
    simple drapeau de session (`admin_ok`) tient la porte ouverte, comme la
    connexion normale d'un compte. Rendu server-side, aucun JS : Jinja
    échappe le texte des commentaires automatiquement (auto-escaping par
    défaut) — pas de risque d'injection depuis un mot laissé par un testeur."""
    if request.method == "POST":
        if request.form.get("mdp") == ADMIN_PASSWORD:
            session["admin_ok"] = True
            session.permanent = True
        return redirect("/admin/commentaires")
    if not _est_admin():
        return render_template_string(_ADMIN_LOGIN_TPL), 403
    lu_id = request.args.get("lu")
    entries = _lire_commentaires()
    if lu_id:
        for e in entries:
            if e["id"] == lu_id:
                e["lu"] = True
        _ecrire_commentaires(entries)
        return redirect("/admin/commentaires")
    entries.sort(key=lambda e: e.get("cree_le", ""), reverse=True)
    return render_template_string(_ADMIN_COMMENTAIRES_TPL, entries=entries,
                                   maj=request.args.get("maj"))


_ADMIN_BORD_TPL = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tableau de bord — Ta Trame</title>
<style>
body{font-family:-apple-system,sans-serif;max-width:760px;margin:34px auto;padding:0 20px;
  background:#141110;color:#eee}
a{color:#e9d494}
.onglets{margin-bottom:18px}.onglets a{margin-right:16px}
h2{margin:26px 0 12px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:9px 8px;border-bottom:1px solid #2a2622}
th{color:#999;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
.pastille{display:inline-block;width:8px;height:8px;border-radius:50%;background:#3a352e;margin-right:6px}
.pastille.on{background:#7ac07a;box-shadow:0 0 6px #7ac07a}
.barre{background:#2a2622;border-radius:5px;height:10px;overflow:hidden}
.barre span{display:block;height:100%;background:#e9d494}
.vide{color:#888;margin:20px 0}
.num{color:#cfc6b2;font-variant-numeric:tabular-nums}
</style></head><body>
<div class="onglets"><a href="/">← Ta Trame</a> · <b>Tableau de bord</b> · <a href="/admin/commentaires">💬 Commentaires</a></div>
<h2>Testeurs ({{ testeurs|length }})</h2>
{% if testeurs %}
<table><thead><tr><th>Testeur</th><th>Dernière visite</th><th class="num">Sessions</th><th class="num">Temps total</th></tr></thead>
<tbody>
{% for t in testeurs %}
<tr>
  <td><span class="pastille {{ 'on' if t.en_ligne else '' }}"></span>{{ t.nom }}</td>
  <td>{{ t.derniere_txt }}</td>
  <td class="num">{{ t.nb_sessions }}</td>
  <td class="num">{{ t.total_txt }}</td>
</tr>
{% endfor %}
</tbody></table>
{% else %}<p class="vide">Aucune activité enregistrée pour l'instant.</p>{% endif %}

<h2>Sections les plus visitées</h2>
{% if sections %}
<table><tbody>
{% for nom, n, pct in sections %}
<tr>
  <td style="width:30%">{{ nom }}</td>
  <td><div class="barre"><span style="width:{{ pct }}%"></span></div></td>
  <td class="num" style="width:60px;text-align:right">{{ n }}</td>
</tr>
{% endfor %}
</tbody></table>
{% else %}<p class="vide">Aucune navigation enregistrée pour l'instant.</p>{% endif %}
</body></html>"""


def _fmt_duree(minutes):
    if minutes >= 60:
        h, m = divmod(minutes, 60)
        return f"{h} h {m:02d}" if m else f"{h} h"
    return f"{minutes} min"


def _fmt_depuis(quand):
    """« il y a 3 min », « il y a 2 h », « hier », « il y a 4 j »."""
    delta = dt.datetime.now(dt.timezone.utc) - quand
    s = delta.total_seconds()
    if s < 120:
        return "à l'instant"
    if s < 3600:
        return f"il y a {int(s // 60)} min"
    if s < 86400:
        return f"il y a {int(s // 3600)} h"
    j = int(s // 86400)
    return "hier" if j == 1 else f"il y a {j} j"


# Noms lisibles des sections (les `data-vue` techniques -> libellés de la nav).
_LIBELLES_VUE = {
    "jour": "Le Jour", "apercu": "Tout", "portrait": "Le Portrait",
    "ciel": "Le Ciel", "relations": "Relations", "regles": "Les Règles",
    "profils": "Profils",
}


@app.get("/admin")
def admin_bord():
    """Tableau de bord d'activité — réservé à l'admin (compte de Martin, ou mot
    de passe admin en repli via /admin/commentaires)."""
    if not _est_admin():
        return redirect("/admin/commentaires")
    testeurs, sections = _synthese_activite()
    for t in testeurs:
        t["derniere_txt"] = _fmt_depuis(t["derniere"])
        t["total_txt"] = _fmt_duree(t["total_min"])
    maxi = sections[0][1] if sections else 1
    sections_v = [(_LIBELLES_VUE.get(v, v), n, round(100 * n / maxi))
                  for v, n in sections]
    return render_template_string(_ADMIN_BORD_TPL, testeurs=testeurs,
                                   sections=sections_v)


@app.post("/admin/mot-de-passe")
def admin_changer_mdp():
    """Change le mot de passe admin depuis la page elle-même — le seul moyen VOULU
    de le fixer (le générer au hasard n'était qu'un repli au tout premier démarrage).
    Réservé à qui est déjà connecté comme admin (même garde que la liste elle-même) :
    changer ce mot de passe SANS déjà être admin serait la faille qu'on referme partout
    ailleurs dans l'app. Liberté totale sur le mot de passe choisi ; seul le vide est
    refusé (même règle que les mots de passe des comptes)."""
    global ADMIN_PASSWORD
    if not session.get("admin_ok"):
        return jsonify({"erreur": "verrouille"}), 401
    nouveau = (request.form.get("nouveau_mdp") or "").strip()
    if not nouveau:
        return redirect("/admin/commentaires")
    ADMIN_PASSWORD = nouveau
    _reecrire_env("ADMIN_PASSWORD", nouveau)
    return redirect("/admin/commentaires?maj=1")


@app.get("/health")
def health():
    """Contrat écosystème : 200 tant que le process vit."""
    inv = corpus.inventaire()
    total = sum(inv.values())
    return jsonify({
        "service": "align", "name": "Ta Trame", "port": 5073,
        "status": "ok" if total else "degraded",
        "detail": f"{total} entrées de corpus" if total else "corpus vide",
    })


if __name__ == "__main__":
    # Affiché une fois au démarrage — la seule fois où Martin doit aller le lire
    # (pattern Manto) : nécessaire pour activer les 16 profils créés avant les
    # comptes (/api/profil/<id>/activer) et pour réinitialiser un mot de passe oublié.
    print(f"[admin] mot de passe administrateur : {ADMIN_PASSWORD}")
    if DEV_MARTIN_VOIT_TOUS_LES_THEMES:
        print("[dev] ⚠️  martin-boucher voit TOUS les thèmes (mode test) — "
              "repasser DEV_MARTIN_VOIT_TOUS_LES_THEMES à False avant mise en ligne.")
    _demarrer_scheduler()
    app.run(host="0.0.0.0", port=5073, debug=False)
