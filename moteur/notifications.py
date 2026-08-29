"""Les rappels du jour — préférences et planification des notifications push.

Un profil peut activer jusqu'à TROIS rappels quotidiens, chacun indépendant
(on/off séparé, heure de base réglable) :

  - matin  → « Message du jour » (le miroir) ; envoyé SEULEMENT si l'app n'a
             pas déjà été ouverte aujourd'hui (anti-redondance — voir app.py).
  - midi   → « Le fil du jour », sur un domaine CHOISI par l'utilisateur.
  - soir   → « À méditer ».

⚠️ HEURE VARIABLE MAIS DÉTERMINISTE (choix assumé de Martin, 2026-08-28). Le
rappel ne tombe pas pile à la même minute chaque jour : sa minute exacte est
un décalage de 0 à 59 min DÉRIVÉ (hash) du profil, du créneau et de la date.
Ça bouge donc d'un jour à l'autre — mais ce n'est JAMAIS un tirage au sort :
même (profil, créneau, jour) ⇒ même minute, reproductible. Fidèle à Align :
zéro hasard, zéro manipulation, seulement une heure qui respire.

⚠️ Stockage DÉLIBÉRÉMENT séparé de `data/profils/*.json` : ce dernier est
reconstruit intégralement à chaque sauvegarde d'identité (`_construire()` dans
app.py) — un abonnement push qui y vivrait serait écrasé en silence à la
prochaine édition du nom ou de la date de naissance. Un abonnement est une
donnée opérationnelle (un appareil, une permission navigateur), pas une donnée
d'identité ; son cycle de vie est différent, son fichier aussi.

Comme partout dans Align : ici on calcule (quel créneau, quand, quel TYPE de
carte) ; le texte, lui, vient du corpus et est composé par app.py. Ce module
ne connaît aucun texte, seulement la mécanique.
"""
import datetime as dt
import hashlib
import json
import pathlib
import zoneinfo

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "data" / "notifications"

#: Les trois créneaux, dans l'ordre. Un seul endroit à changer.
CRENEAUX = ("matin", "midi", "soir")

#: Le TYPE de carte que chaque créneau fait apparaître en plein écran. Pas le
#: texte (app.py le compose), juste le contrat créneau → carte, partagé par le
#: scheduler ET le lien profond (`/?carte=…`) du service worker.
CARTE = {"matin": "jour", "midi": "domaine", "soir": "mediter"}

#: Heures de base par défaut (heure locale de l'utilisateur). Réglables par profil.
HEURE_DEFAUT = {"matin": 8, "midi": 12, "soir": 20}

#: Le domaine du « fil du jour » montré à midi si l'utilisateur n'a rien choisi.
#: « soi » (Toi) — le plus universel des douze.
DOMAINE_DEFAUT = "soi"

#: Largeur de la fenêtre déterministe : l'offset appartient à [0, FENETRE_MIN[.
#: 60 min ⇒ un rappel réglé sur 8 h tombe entre 8 h 00 et 8 h 59.
FENETRE_MIN = 60


def _creneaux_defaut():
    return {
        "matin": {"actif": True, "heure": HEURE_DEFAUT["matin"]},
        "midi": {"actif": True, "heure": HEURE_DEFAUT["midi"], "domaine": DOMAINE_DEFAUT},
        "soir": {"actif": False, "heure": HEURE_DEFAUT["soir"]},
    }


def defaut():
    """Les préférences d'un profil qui n'a jamais rien réglé. Une fonction (pas
    une constante partagée) pour qu'aucun appelant ne puisse muter le défaut des
    autres via les sous-dictionnaires."""
    return {
        "subscription": None,
        "fuseau_notif": None,
        "creneaux": _creneaux_defaut(),
        "dernier_envoi": {c: None for c in CRENEAUX},
    }


def _chemin(profil_id):
    sur = "".join(c for c in profil_id if c.isalnum() or c in "-_")
    if not sur:
        raise ValueError("identifiant de profil invalide")
    return DOSSIER / f"{sur}.json"


def _migrer(data):
    """Ramène un fichier au format courant, quel que soit son âge.

    Ancien format (2 créneaux à heures fixes) : `{actif, subscription,
    fuseau_notif, dernier_envoi:{matin, soir}}`. On préserve l'abonnement, le
    fuseau et l'historique d'envoi ; l'ancien `actif` global décidait matin ET
    soir, on le reporte donc sur ces deux créneaux. Le midi est nouveau : au
    défaut. Ne JAMAIS perdre un `subscription` en migrant — le reperdre forcerait
    l'utilisateur à réautoriser les notifications sans le savoir.
    """
    if "creneaux" in data:
        # Format courant : on garantit juste que les trois créneaux existent.
        base = _creneaux_defaut()
        base.update(data.get("creneaux") or {})
        data["creneaux"] = base
        data.setdefault("subscription", None)
        data.setdefault("fuseau_notif", None)
        envoi = data.get("dernier_envoi") or {}
        data["dernier_envoi"] = {c: envoi.get(c) for c in CRENEAUX}
        return data

    ancien_actif = bool(data.get("actif"))
    creneaux = _creneaux_defaut()
    creneaux["matin"]["actif"] = ancien_actif
    creneaux["soir"]["actif"] = ancien_actif
    envoi = data.get("dernier_envoi") or {}
    return {
        "subscription": data.get("subscription"),
        "fuseau_notif": data.get("fuseau_notif"),
        "creneaux": creneaux,
        "dernier_envoi": {c: envoi.get(c) for c in CRENEAUX},
    }


def lire(profil_id):
    """Les préférences d'un profil, au format courant (anciens fichiers migrés à
    la lecture), ou les valeurs par défaut si jamais réglées."""
    chemin = _chemin(profil_id)
    if not chemin.exists():
        return defaut()
    return _migrer(json.loads(chemin.read_text(encoding="utf-8")))


def ecrire(profil_id, prefs):
    """Écriture atomique (tmp + replace) — même geste que `_ecrire()` dans app.py,
    dupliqué ici pour que ce module reste indépendant de app.py."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    chemin = _chemin(profil_id)
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(json.dumps(prefs, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(chemin)


def domaine_midi(prefs):
    """Le domaine du « fil du jour » choisi pour le rappel de midi, ou le défaut."""
    return (prefs.get("creneaux", {}).get("midi", {}).get("domaine")) or DOMAINE_DEFAUT


# ------------------------------------------------- heure locale & date

def _heure_locale(instant_utc, fuseau_notif):
    """L'instant converti dans le fuseau de l'utilisateur, ou None si le fuseau
    est absent/invalide. Partagé par la planification et `date_locale` — une
    seule conversion, jamais deux logiques qui pourraient diverger."""
    if not fuseau_notif:
        return None
    try:
        return instant_utc.astimezone(zoneinfo.ZoneInfo(fuseau_notif))
    except zoneinfo.ZoneInfoNotFoundError:
        return None


def date_locale(instant_utc, fuseau_notif):
    """Le jour calendaire, dans le fuseau de l'utilisateur.

    Important au moment d'envoyer : « aujourd'hui » doit être calculé côté
    utilisateur, pas en UTC — sinon un envoi juste après minuit UTC pourrait
    calculer le titre de la MAUVAISE journée pour quelqu'un dont le fuseau est
    en retard sur UTC (ce serait encore hier, chez lui).
    """
    local = _heure_locale(instant_utc, fuseau_notif)
    return local.date() if local else None


# ------------------------------------------------- fenêtre déterministe

def offset_minutes(profil_id, creneau, date_iso, largeur=FENETRE_MIN):
    """Le décalage (0..largeur-1) qui fait « respirer » l'heure d'un rappel.

    Déterministe et reproductible : même (profil, créneau, jour) ⇒ même minute.

    ⚠️ On utilise `hashlib`, PAS le `hash()` natif de Python : `hash()` des
    chaînes est salé par process (PYTHONHASHSEED) et changerait donc à CHAQUE
    redémarrage du serveur — l'heure d'envoi d'un même jour sauterait d'un
    déploiement à l'autre. sha256 est stable pour toujours.
    """
    graine = f"{profil_id}|{creneau}|{date_iso}".encode("utf-8")
    n = int.from_bytes(hashlib.sha256(graine).digest()[:4], "big")
    return n % largeur


def minute_cible(profil_id, prefs, creneau, date_iso):
    """La minute-du-jour à laquelle ce créneau doit partir, pour ce profil, ce
    jour-là : heure de base réglée + décalage déterministe."""
    heure = prefs["creneaux"][creneau].get("heure", HEURE_DEFAUT[creneau])
    return heure * 60 + offset_minutes(profil_id, creneau, date_iso)


def creneaux_a_envoyer(profil_id, prefs, instant_utc, tolerance_min=10):
    """Quels créneaux doivent partir MAINTENANT, à l'heure locale de l'utilisateur.

    Un créneau est retenu s'il est actif, que sa minute-cible du jour tombe dans
    la fenêtre [cible, cible+tolerance[, et qu'il n'a pas déjà été envoyé
    aujourd'hui. Ne juge PAS la condition « app déjà ouverte » du matin : ça
    dépend du journal d'activité, que seul app.py connaît — il filtre ensuite.

    Couverture garantie : le scheduler tourne toutes les 10 min et la tolérance
    fait 10 min ; des ticks espacés de 10 min et une fenêtre demi-ouverte de
    10 min ⇒ exactement un tick tombe dans chaque fenêtre (au plus ~10 min de
    retard, jamais d'oubli, quelle que soit la phase des ticks). La fenêtre ne
    s'ouvre JAMAIS avant l'heure cible — un rappel du matin ne peut pas arriver
    la veille au soir à cause d'un fuseau mal réglé.
    """
    local = _heure_locale(instant_utc, prefs.get("fuseau_notif"))
    if local is None:
        return []
    date_iso = local.date().isoformat()
    minute_du_jour = local.hour * 60 + local.minute
    a_envoyer = []
    for creneau in CRENEAUX:
        if not prefs["creneaux"].get(creneau, {}).get("actif"):
            continue
        if deja_envoye_aujourdhui(prefs, creneau, date_iso):
            continue
        cible = minute_cible(profil_id, prefs, creneau, date_iso)
        if cible <= minute_du_jour < cible + tolerance_min:
            a_envoyer.append(creneau)
    return a_envoyer


# ------------------------------------------------- suivi d'envoi (anti-doublon)

def deja_envoye_aujourdhui(prefs, creneau, date_iso):
    return prefs.get("dernier_envoi", {}).get(creneau) == date_iso


def marquer_envoye(prefs, creneau, date_iso):
    """Renvoie une COPIE des préférences avec ce créneau marqué envoyé — jamais
    de mutation en place, comme partout ailleurs dans le moteur."""
    maj = dict(prefs)
    maj["dernier_envoi"] = {**prefs.get("dernier_envoi", {}), creneau: date_iso}
    return maj


def profils_actifs():
    """Les identifiants de profils à suivre par le scheduler : un abonnement
    valide ET au moins un créneau actif. Un profil qui a tout désactivé (mais
    garde son abonnement) n'a rien à recevoir — on ne le parcourt pas."""
    if not DOSSIER.exists():
        return []
    out = []
    for f in sorted(DOSSIER.glob("*.json")):
        prefs = _migrer(json.loads(f.read_text(encoding="utf-8")))
        if not prefs.get("subscription"):
            continue
        if any(prefs["creneaux"].get(c, {}).get("actif") for c in CRENEAUX):
            out.append(f.stem)
    return out
