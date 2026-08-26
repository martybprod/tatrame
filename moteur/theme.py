"""Assemblage d'un thème natal : le point d'entrée du moteur.

Chaîne complète, 100 % locale et déterministe :
    lieu (SQLite) -> heure locale -> UTC (tzdata épinglé) -> éphémérides
    (Skyfield/DE440s) -> maisons (trigo maison) -> thème.

Aucun LLM, aucun réseau, aucun aléa, aucun `datetime.now()`.
"""
import math

from moteur import maisons
from moteur.ephemerides import Ephemerides
from moteur.temps import limites_connues, vers_utc

SIGNES = [
    "Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge",
    "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons",
]


def signe_de(longitude):
    """Signe, degré et minute d'une longitude écliptique."""
    i = int(longitude // 30) % 12
    reste = longitude % 30
    degre = int(reste)
    minute = int(round((reste - degre) * 60))
    if minute == 60:                      # l'arrondi peut déborder
        minute, degre = 0, degre + 1
    return {"signe": SIGNES[i], "degre": degre, "minute": minute}


def maison_de(longitude, cuspides):
    """Dans quelle maison tombe une longitude.

    Les maisons sont des secteurs de largeur INÉGALE en Placidus, et le
    système enjambe 0° : d'où le raisonnement en écart relatif à la cuspide 1.
    """
    rel = (longitude - cuspides[0]) % 360.0
    bornes = [(c - cuspides[0]) % 360.0 for c in cuspides]
    for i in range(12):
        debut = bornes[i]
        fin = bornes[(i + 1) % 12] if i < 11 else 360.0
        if debut <= rel < fin:
            return i + 1
    return 12


class Moteur:
    def __init__(self):
        self.eph = Ephemerides()

    def theme_natal(self, annee, mois, jour, heure, minute,
                    lat, lon, nom_fuseau, systeme="placidus", fold=0):
        utc, avis_heure = vers_utc(annee, mois, jour, heure, minute, nom_fuseau, fold=fold)
        t = self.eph.instant(utc.year, utc.month, utc.day,
                             utc.hour, utc.minute, utc.second)

        eps = self.eph.obliquite(t)
        armc = self.eph.armc(t, lon)
        cusp, asc, mc, repli = maisons.cuspides(systeme, armc, eps, lat)

        corps = {}
        for nom in self.eph.CORPS:
            p = self.eph.position(nom, t)
            corps[nom] = {
                **p,
                **signe_de(p["lon"]),
                "maison": maison_de(p["lon"], cusp),
            }
        noeud = self.eph.noeud_moyen(t)
        corps["noeud_moyen"] = {
            "lon": noeud, "lat": 0.0, "vitesse_lon": None, "retrograde": True,
            **signe_de(noeud), "maison": maison_de(noeud, cusp),
        }

        return {
            "naissance": {
                "locale": f"{jour:02d}/{mois:02d}/{annee} {heure:02d}h{minute:02d}",
                "utc": utc.isoformat(),
                "fuseau": nom_fuseau,
                "lat": lat, "lon": lon,
            },
            "corps": corps,
            "angles": {"asc": {"lon": asc, **signe_de(asc)},
                       "mc": {"lon": mc, **signe_de(mc)}},
            "maisons": {"systeme": systeme, "cuspides": cusp,
                        "cuspides_signe": [signe_de(c) for c in cusp],
                        "repli": repli},
            "technique": {"armc": armc, "obliquite": eps, "jd_tt": float(t.tt)},
            # Les réserves ne sont pas des notes de bas de page : elles font
            # partie du résultat, et l'app doit les montrer.
            "avis": [a for a in [avis_heure] if a],
            "limites": limites_connues(annee, mois, jour, nom_fuseau, lon),
        }
