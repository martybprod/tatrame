"""Positions écliptiques géocentriques apparentes — Skyfield + DE440s.

Licence : Skyfield est MIT, DE440s est du domaine public (JPL/NASA). Aucune
contamination AGPL, aucune redevance, jamais. C'est tout l'intérêt de ce
module par rapport à pyswisseph. Voir PROPOSITION.md §6.

Déterminisme :
  - le fichier d'éphémérides est VENDORISÉ et vérifié par empreinte au
    chargement (jamais téléchargé à la volée : ce serait à la fois du réseau
    au runtime et une source de dérive silencieuse) ;
  - aucun `datetime.now()` : l'instant est toujours un paramètre ;
  - les vitesses sont calculées par différences finies centrées à pas fixe.
"""
import hashlib
import pathlib

from skyfield.api import Loader, load_file
from skyfield.framelib import ecliptic_frame
from skyfield.nutationlib import iau2000b

RACINE = pathlib.Path(__file__).resolve().parents[1]
FICHIER_EPHEMERIDE = RACINE / "data" / "ephem" / "de440s.bsp"

# Empreinte du de440s.bsp téléchargé le 2026-07-15 depuis
# https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp
# Couverture 1849-2150. Vérifiée au chargement : un fichier différent
# donnerait des positions différentes, donc un thème différent, en silence.
SHA256_ATTENDU = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"

# DE440s ne contient que les barycentres pour Mars et au-delà. Pour Mercure et
# Vénus, barycentre == centre (aucune lune). Pour les géantes, l'écart
# barycentre/centre vu de la Terre est très inférieur à la minute d'arc :
# c'est l'usage courant, et le filet golden le mesure au lieu de le supposer.
CORPS = {
    "soleil": "sun",
    "lune": "moon",
    "mercure": "mercury",
    "venus": "venus",
    "mars": "mars barycenter",
    "jupiter": "jupiter barycenter",
    "saturne": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluton": "pluto barycenter",
}

# Pas des différences finies centrées, en jours. Compromis : trop grand ->
# erreur de troncature sur la Lune (13°/j) ; trop petit -> bruit d'annulation
# en flottant. Mesuré contre l'oracle dans tests/test_ephemerides.py.
PAS_VITESSE = 0.02


class Ephemerides:
    """Fournisseur de positions. Instancier une fois, réutiliser."""

    #: Les corps disponibles. Exposé sur la classe pour que les appelants
    #: n'aient pas à importer la constante de module séparément.
    CORPS = tuple(CORPS)

    def __init__(self, fichier=FICHIER_EPHEMERIDE, verifier_empreinte=True):
        if not fichier.exists():
            raise FileNotFoundError(
                f"Éphémérides absentes : {fichier}\n"
                f"  curl -o {fichier} https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"
            )
        if verifier_empreinte:
            self._verifier(fichier)
        # load_file lit le fichier local tel quel ; le Loader ne sert qu'à
        # l'échelle de temps, en `builtin=True` pour qu'il n'aille RIEN
        # chercher sur le réseau (contrainte « zéro réseau au runtime »).
        self.eph = load_file(str(fichier))
        self.ts = Loader(str(fichier.parent)).timescale(builtin=True)
        self.terre = self.eph["earth"]

    @staticmethod
    def _verifier(fichier):
        h = hashlib.sha256()
        with open(fichier, "rb") as f:
            for bloc in iter(lambda: f.read(1 << 20), b""):
                h.update(bloc)
        obtenu = h.hexdigest()
        if obtenu != SHA256_ATTENDU:
            raise RuntimeError(
                "Empreinte des éphémérides inattendue — refus de démarrer.\n"
                f"  attendu : {SHA256_ATTENDU}\n  obtenu   : {obtenu}\n"
                "Un fichier différent produirait des thèmes différents en silence."
            )

    # ------------------------------------------------------------ instants

    def instant(self, annee, mois, jour, heure=0, minute=0, seconde=0):
        """Instant Skyfield depuis une date/heure UTC explicite."""
        return self.ts.utc(annee, mois, jour, heure, minute, seconde)

    def instant_depuis_jd(self, jd_ut):
        return self.ts.ut1_jd(jd_ut)

    # ------------------------------------------------------------ positions

    def longitude(self, corps, t):
        """Longitude écliptique géocentrique APPARENTE, vraie équinoxe de la date.

        C'est exactement le zodiaque tropical : `ecliptic_frame` est le repère
        de l'écliptique et de l'équinoxe VRAIS de la date (précession +
        nutation incluses), et `.apparent()` ajoute l'aberration et la
        déflexion relativiste.
        """
        cible = self.eph[CORPS[corps]]
        pos = self.terre.at(t).observe(cible).apparent()
        lat, lon, _ = pos.frame_latlon(ecliptic_frame)
        # float() explicite : Skyfield renvoie des scalaires numpy, qui
        # fuiraient jusque dans le JSON (non sérialisable) et dont le repr
        # diffère. Le moteur ne rend que des types Python natifs.
        return float(lon.degrees) % 360.0, float(lat.degrees)

    def position(self, corps, t):
        """Longitude, latitude, vitesse en longitude (°/jour) et rétrogradation.

        Vitesse par différences finies centrées : Skyfield n'expose pas de
        dérivée de longitude écliptique. Le signe de la vitesse EST la
        rétrogradation.
        """
        lon, lat = self.longitude(corps, t)
        avant, _ = self.longitude(corps, self.ts.tt_jd(t.tt - PAS_VITESSE))
        apres, _ = self.longitude(corps, self.ts.tt_jd(t.tt + PAS_VITESSE))
        # écart le plus court, pour survivre au passage par 0°/360°
        delta = (apres - avant + 180.0) % 360.0 - 180.0
        vitesse = delta / (2.0 * PAS_VITESSE)
        return {
            "lon": lon,
            "lat": lat,
            "vitesse_lon": vitesse,
            "retrograde": vitesse < 0.0,
        }

    def theme_positions(self, t):
        return {nom: self.position(nom, t) for nom in CORPS}

    # ------------------------------------------- points calculés, sans éphéméride

    @staticmethod
    def noeud_moyen(t):
        """Nœud lunaire moyen ascendant, rapporté à l'équinoxe VRAI de la date.

        Skyfield ne le fournit pas (`almanac.moon_nodes` donne les INSTANTS de
        passage par le plan de l'écliptique, pas la longitude du nœud).
        Purement analytique : aucun fichier d'éphéméride n'intervient.

        Le polynôme de Meeus (ch. 47) donne le nœud rapporté à l'équinoxe
        MOYEN. Toutes les autres longitudes de ce module sont rapportées à
        l'équinoxe VRAI (repère `ecliptic_frame`, nutation comprise) : sans
        la correction ci-dessous, le nœud serait dans un repère différent de
        celui des planètes, avec un décalage allant jusqu'à ±17". Vérifié
        contre l'oracle : l'écart résiduel valait exactement Δψ.
        """
        T = (t.tt - 2451545.0) / 36525.0
        omega = (125.0445479
                 - 1934.1362891 * T
                 + 0.0020754 * T ** 2
                 + T ** 3 / 467441.0
                 - T ** 4 / 60616000.0)
        d_psi, _ = iau2000b(t.tt)          # en 0,1 microarcsecondes
        return float(omega + d_psi / 1e7 / 3600.0) % 360.0

    @staticmethod
    def obliquite(t):
        """Obliquité VRAIE de l'écliptique (moyenne + nutation), en degrés."""
        d_psi, d_eps = iau2000b(t.tt)          # en 0,1 microarcsecondes
        T = (t.tt - 2451545.0) / 36525.0
        # IAU 1980/2006, en secondes d'arc
        eps_moyen = (84381.406
                     - 46.836769 * T
                     - 0.0001831 * T ** 2
                     + 0.00200340 * T ** 3
                     - 0.000000576 * T ** 4
                     - 0.0000000434 * T ** 5)
        return float(eps_moyen + d_eps / 1e7) / 3600.0

    @staticmethod
    def armc(t, longitude_est):
        """ARMC = temps sidéral APPARENT local, en degrés.

        `t.gast` est le temps sidéral apparent de Greenwich en heures ; la
        longitude est comptée positive vers l'est.
        """
        return (float(t.gast) * 15.0 + longitude_est) % 360.0
