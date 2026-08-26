"""Recherche du lieu de naissance — SQLite local, zéro réseau.

Le fuseau vient du champ 18 de GeoNames : quand l'utilisateur choisit une
ville de la base, `timezonefinder` (~90 Mo + numpy + h3 + une compilation
CFFI faute de wheel macOS) est superflu.

Données GeoNames, CC BY 4.0 : l'attribution doit rester visible dans l'app.
"""
import pathlib
import sqlite3
import threading
import unicodedata

RACINE = pathlib.Path(__file__).resolve().parents[1]
BASE = RACINE / "data" / "geo" / "lieux.sqlite"

ATTRIBUTION = "Lieux : GeoNames (geonames.org), licence CC BY 4.0"

# Une même commune apparaît souvent deux fois : en PPL (localité) et en ADM3
# (municipalité officielle). On préfère PPL, dont les coordonnées visent le
# centre habité plutôt que le centroïde administratif — plus proche du lieu
# de naissance réel. Écart mesuré sur Baie-Saint-Paul : ~0,17° de longitude,
# soit ~40 s de temps solaire. Marginal, mais autant viser juste.
RANG_CODE = {"PPLC": 0, "PPLA": 1, "PPLA2": 2, "PPLA3": 3, "PPL": 4, "ADM3": 5, "ADM4": 6}


def plier(s):
    """Même normalisation qu'à la construction de la base."""
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class Lieux:
    """Une connexion PAR THREAD.

    Flask sert chaque requête dans un thread différent, et sqlite3 refuse
    qu'une connexion voyage d'un thread à l'autre. Le stockage thread-local
    est plus sûr que `check_same_thread=False` : celui-ci laisserait passer
    des accès concurrents sur la même connexion.

    Ouvrir en lecture seule ne coûte presque rien (la base est un fichier de
    16 Mo, lu par mmap), et garantit qu'aucune requête ne l'écrira jamais.
    """

    def __init__(self, base=BASE):
        if not base.exists():
            raise FileNotFoundError(
                f"Base des lieux absente : {base}\n"
                "  python outils/construire_geo.py"
            )
        self.base = base
        self._local = threading.local()

    @property
    def con(self):
        if not hasattr(self._local, "con"):
            c = sqlite3.connect(f"file:{self.base}?mode=ro", uri=True)
            c.row_factory = sqlite3.Row
            self._local.con = c
        return self._local.con

    def chercher(self, nom, pays=None, limite=20):
        """Cherche un lieu par nom. Renvoie les candidats, les meilleurs d'abord.

        Ne devine JAMAIS : les homonymes sont réels (trois « Saint-Fabien »,
        dont un au Nouveau-Brunswick et deux au Québec) et un mauvais choix
        déplace l'Ascendant. C'est à l'utilisateur de trancher.
        """
        sql = "SELECT * FROM lieux WHERE recherche = ?"
        args = [plier(nom)]
        if pays:
            sql += " AND pays = ?"
            args.append(pays)
        lignes = self.con.execute(sql, args).fetchall()
        if not lignes:
            sql = sql.replace("recherche = ?", "recherche LIKE ?")
            args[0] = plier(nom) + "%"
            lignes = self.con.execute(sql + " LIMIT 200", args).fetchall()

        candidats = [dict(r) for r in lignes]
        candidats.sort(key=lambda r: (RANG_CODE.get(r["code"], 9), -r["population"], r["nom"]))
        return candidats[:limite]

    def par_id(self, geonameid):
        r = self.con.execute("SELECT * FROM lieux WHERE geonameid = ?", (geonameid,)).fetchone()
        return dict(r) if r else None

    def par_coordonnees(self, lat, lon, tolerance=0.02):
        """Retrouve un lieu par ses coordonnées — filet pour les vieux profils.

        Les premiers profils ont été enregistrés sans identifiant de lieu : ils
        deviendraient immodifiables, ce qui est exactement le blocage qu'on
        cherche à lever. La tolérance (~2 km) absorbe les arrondis d'écriture.
        """
        r = self.con.execute(
            "SELECT * FROM lieux WHERE ABS(lat - ?) < ? AND ABS(lon - ?) < ? "
            "ORDER BY ABS(lat - ?) + ABS(lon - ?) LIMIT 1",
            (lat, tolerance, lon, tolerance, lat, lon),
        ).fetchone()
        return dict(r) if r else None

    def homonymes(self, nom, pays=None):
        """Y a-t-il ambiguïté ? Le savoir décide si l'UI doit faire choisir."""
        return len(self.chercher(nom, pays, limite=50)) > 1
