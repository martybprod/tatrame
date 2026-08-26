"""Les rappels du jour — préférences et contenu des notifications push.

Un profil peut activer jusqu'à deux rappels quotidiens, à heures FIXES : le
matin (le miroir — l'observation du jour) et le soir (le geste — l'action
concrète). Mêmes heures pour tout le monde, aucun envoi « optimisé » pour
maximiser les ouvertures — cohérent avec le reste d'Align : zéro hasard, zéro
manipulation.

⚠️ Stockage DÉLIBÉRÉMENT séparé de `data/profils/*.json` : ce dernier est
reconstruit intégralement à chaque sauvegarde d'identité (`_construire()` dans
app.py) — un abonnement push qui y vivrait serait écrasé en silence à la
prochaine édition du nom ou de la date de naissance. Un abonnement est une
donnée opérationnelle (un appareil, une permission navigateur), pas une donnée
d'identité ; son cycle de vie est différent, son fichier aussi.

Comme partout dans Align : ici on calcule (quel créneau, quel contenu), le
texte vient du corpus, lu par app.py via le routeur — ce module ne connaît
aucun texte, seulement la mécanique.
"""
import json
import pathlib
import zoneinfo

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "data" / "notifications"

#: Les deux créneaux possibles, et le champ du `titre` du jour qu'ils lisent.
#: Heures FIXES et assumées — un réglage qui bouge tout seul ne serait plus
#: déterministe. Faciles à changer ici, un seul endroit.
CRENEAUX = {
    "matin": {"heure": 8, "minute": 0, "champ": "miroir"},
    "soir": {"heure": 17, "minute": 0, "champ": "geste"},
}

DEFAUT = {
    "actif": False,
    "subscription": None,
    "fuseau_notif": None,
    "dernier_envoi": {"matin": None, "soir": None},
}


def _chemin(profil_id):
    sur = "".join(c for c in profil_id if c.isalnum() or c in "-_")
    if not sur:
        raise ValueError("identifiant de profil invalide")
    return DOSSIER / f"{sur}.json"


def lire(profil_id):
    """Les préférences d'un profil, ou les valeurs par défaut si jamais réglées."""
    chemin = _chemin(profil_id)
    if not chemin.exists():
        return dict(DEFAUT, dernier_envoi=dict(DEFAUT["dernier_envoi"]))
    return json.loads(chemin.read_text(encoding="utf-8"))


def ecrire(profil_id, prefs):
    """Écriture atomique (tmp + replace) — même geste que `_ecrire()` dans app.py,
    dupliqué ici pour que ce module reste indépendant de app.py."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    chemin = _chemin(profil_id)
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(json.dumps(prefs, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(chemin)


def contenu_notification(titre, moment):
    """Le texte à envoyer pour ce créneau, ou None si le corpus manque ce jour-là.

    `titre` est le dict déjà renvoyé par `_titre_du_jour` (app.py) : `{"source",
    "miroir", "geste", ...}`. Un aspect natal sans texte de corpus, ou une
    relation chinoise sans geste, laissent le champ à None — on ne fabrique
    jamais une notification vide ou bancale, on saute ce créneau en silence.
    """
    if not titre:
        return None
    champ = CRENEAUX[moment]["champ"]
    return titre.get(champ) or None


def _heure_locale(instant_utc, fuseau_notif):
    """L'instant converti dans le fuseau de l'utilisateur, ou None si le fuseau
    est absent/invalide. Partagé par `creneau_courant` et `date_locale` — une
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


def creneau_courant(instant_utc, fuseau_notif, tolerance_min=10):
    """Quel créneau (« matin », « soir », ou None) correspond à MAINTENANT,
    dans le fuseau de l'utilisateur — pas celui de son lieu de naissance.

    Le scheduler tourne par intervalles (toutes les 5-15 min), jamais pile à
    l'heure : `tolerance_min` absorbe ce décalage. Une fenêtre de 10 minutes
    après l'heure pile, jamais avant — un rappel du matin ne doit pas arriver
    la veille au soir à cause d'un fuseau mal réglé.
    """
    local = _heure_locale(instant_utc, fuseau_notif)
    if local is None:
        return None
    minute_du_jour = local.hour * 60 + local.minute
    for nom, c in CRENEAUX.items():
        cible = c["heure"] * 60 + c["minute"]
        if cible <= minute_du_jour < cible + tolerance_min:
            return nom
    return None


def deja_envoye_aujourdhui(prefs, moment, date_iso):
    return prefs.get("dernier_envoi", {}).get(moment) == date_iso


def marquer_envoye(prefs, moment, date_iso):
    """Renvoie une COPIE des préférences avec ce créneau marqué envoyé —
    jamais de mutation en place, comme partout ailleurs dans le moteur."""
    maj = dict(prefs)
    maj["dernier_envoi"] = {**prefs.get("dernier_envoi", {}), moment: date_iso}
    return maj


def profils_actifs():
    """Les identifiants de profils ayant activé les rappels — pour le scheduler,
    qui n'a pas besoin de connaître le format du fichier, juste qui suivre."""
    if not DOSSIER.exists():
        return []
    out = []
    for f in sorted(DOSSIER.glob("*.json")):
        prefs = json.loads(f.read_text(encoding="utf-8"))
        if prefs.get("actif") and prefs.get("subscription"):
            out.append(f.stem)
    return out
