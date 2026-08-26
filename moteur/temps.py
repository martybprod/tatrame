"""Heure locale de naissance -> instant UTC. La couche la plus piégeuse.

Un décalage d'une heure déplace l'Ascendant d'environ 15°, soit un demi-signe :
c'est ici, pas dans les éphémérides, que se perdent les thèmes.

Trois principes tenus dans ce module :
  1. tzdata est ÉPINGLÉ et FORCÉ. Sans cela, `zoneinfo` lit /usr/share/zoneinfo
     et suit les mises à jour de macOS -> les thèmes dériveraient d'une mise à
     jour système à l'autre, en silence.
  2. Une heure ambiguë ou inexistante n'est JAMAIS devinée : elle est signalée
     à l'appelant, qui fera trancher l'utilisateur.
  3. Les limites historiques connues de tzdata sont AFFICHÉES, pas masquées.
     On ne peut pas les corriger — autant les dire.
"""
import zoneinfo
from datetime import datetime, timedelta, timezone

import tzdata

# ⚠️ Ordre important : vider le TZPATH force zoneinfo à se rabattre sur le
# paquet pip `tzdata` (épinglé) au lieu de /usr/share/zoneinfo (macOS, qui
# bouge). Doit être fait AVANT toute construction de ZoneInfo.
zoneinfo.reset_tzpath(to=[])

VERSION_IANA = tzdata.IANA_VERSION


def fuseau(nom):
    return zoneinfo.ZoneInfo(nom)


# --------------------------------------------------------------- ambiguïtés

def est_ambigue(dt_naif, zone):
    """L'heure existe DEUX fois (recul d'automne) ?"""
    dt = dt_naif.replace(tzinfo=zone)
    return dt.replace(fold=0).utcoffset() != dt.replace(fold=1).utcoffset() \
        and not est_inexistante(dt_naif, zone)


def est_inexistante(dt_naif, zone):
    """L'heure n'existe PAS (avance de printemps) ?

    Une heure sautée ne survit pas à l'aller-retour par UTC : c'est le test
    le plus sûr, et il ne dépend d'aucune table.
    """
    dt = dt_naif.replace(tzinfo=zone)
    return dt != dt.astimezone(timezone.utc).astimezone(zone)


def vers_utc(annee, mois, jour, heure, minute, nom_fuseau, fold=0):
    """Heure civile locale -> UTC, avec diagnostic explicite.

    Renvoie (datetime UTC, avis) où `avis` est None ou un dict décrivant
    l'ambiguïté. On applique un défaut (`fold`) pour pouvoir continuer, mais
    on REMONTE toujours le doute : Python, lui, choisirait en silence.
    """
    zone = fuseau(nom_fuseau)
    naif = datetime(annee, mois, jour, heure, minute)
    avis = None

    if est_inexistante(naif, zone):
        avis = {
            "type": "heure_inexistante",
            "message": (
                f"{naif:%d/%m/%Y %H:%M} n'existe pas à {nom_fuseau} : "
                "l'horloge a sauté cette heure-là (passage à l'heure d'été). "
                "Vérifier l'heure inscrite sur l'acte de naissance."
            ),
        }
    elif est_ambigue(naif, zone):
        zero = naif.replace(tzinfo=zone, fold=0)
        un = naif.replace(tzinfo=zone, fold=1)
        avis = {
            "type": "heure_ambigue",
            "message": (
                f"{naif:%d/%m/%Y %H:%M} a eu lieu DEUX fois à {nom_fuseau} "
                "(retour à l'heure normale). Les deux lectures diffèrent d'une "
                "heure, soit environ 15° d'Ascendant — un demi-signe."
            ),
            "choix": [
                {"fold": 0, "decalage": str(zero.utcoffset()), "libelle": "avant le changement"},
                {"fold": 1, "decalage": str(un.utcoffset()), "libelle": "après le changement"},
            ],
        }

    local = naif.replace(tzinfo=zone, fold=fold)
    return local.astimezone(timezone.utc), avis


# --------------------------------------------------------------------- LMT

def utc_depuis_tsm(annee, mois, jour, heure, minute, longitude):
    """Temps solaire moyen LOCAL -> UTC, depuis la longitude du LIEU.

    À utiliser avant l'adoption des fuseaux (~1884 en Amérique du Nord, 1891
    en France). tzdata donne bien un décalage LMT pour ces époques, mais c'est
    celui de la ville DE RÉFÉRENCE de la zone, pas du lieu de naissance :
    Québec vs Toronto ≈ 32 min, Marseille +12 min vs Paris, Brest −27 min.
    D'où le calcul direct : 1° de longitude = 240 secondes.
    """
    naif = datetime(annee, mois, jour, heure, minute)
    return naif - timedelta(seconds=longitude * 240.0)


# ------------------------------------------- limites historiques assumées

def limites_connues(annee, mois, jour, nom_fuseau, longitude=None):
    """Les cas où tzdata est CONNU pour être faux. À afficher, pas à taire.

    Aucune bibliothèque de lat/lon ne résout ces cas : ils tiennent à ce que
    tzdata modélise, et il ne les modélise pas. L'atlas ACS, la référence
    historique du métier, est en faillite et sans équivalent ouvert.
    """
    d = datetime(annee, mois, jour)
    avis = []

    if nom_fuseau in ("America/Montreal", "America/Toronto"):
        if longitude is not None and d < datetime(1884, 1, 1):
            avis.append(
                "Avant 1884, tzdata donne le temps moyen local de TORONTO, pas "
                "celui du lieu (America/Montreal est un simple alias depuis 2015). "
                "Écart ≈ 23 min pour Montréal, soit ≈ 5,8° d'Ascendant. "
                "Utiliser plutôt utc_depuis_tsm() avec la longitude du lieu."
            )
        if datetime(1917, 1, 1) <= d < datetime(1974, 1, 1):
            avis.append(
                "Entre 1917 et 1973, Montréal avait ses PROPRES règles d'heure "
                "d'été, perdues quand tzdata l'a fusionnée avec Toronto. "
                "Écart possible d'une heure pleine — notamment fin octobre et "
                "en novembre 1949 et 1950."
            )
        if datetime(1975, 2, 23) <= d < datetime(1975, 4, 27):
            avis.append(
                "Février-avril 1975 : les États-Unis sont passés à l'heure d'été "
                "le 23 février (loi d'urgence sur l'énergie), le Canada NON — il "
                "est resté à l'heure normale jusqu'au 27 avril. Toute équivalence "
                "« Québec = heure de l'Est américaine » est fausse d'une heure ici."
            )

    if nom_fuseau == "Europe/Paris":
        fenetres = [
            (datetime(1940, 6, 14), datetime(1941, 5, 4)),
            (datetime(1941, 10, 5), datetime(1942, 3, 9)),
        ]
        if any(a <= d < b for a, b in fenetres):
            avis.append(
                "Europe/Paris ne modélise que la ZONE OCCUPÉE : tzdata le dit "
                "lui-même (« The French rules for 1941-1944 were not used in "
                "Paris »). Une naissance en zone libre est décalée d'une heure "
                "sur cette période."
            )
        if datetime(1940, 1, 1) <= d < datetime(1945, 1, 1):
            avis.append(
                "L'Alsace-Moselle, annexée en 1940-44, était à l'heure allemande "
                "et n'est modélisée par AUCUNE zone tzdata."
            )

    if d < datetime(1970, 1, 1):
        avis.append(
            "Avant 1970, tzdata est explicitement « best effort » : sa propre "
            "documentation reconnaît que ces données viennent souvent "
            "« d'ouvrages d'astrologie sans citations, dont les compilateurs ont "
            "manifestement inventé des entrées ». Vérifier contre un atlas ne "
            "constitue donc PAS un contrôle indépendant."
        )
    return avis
