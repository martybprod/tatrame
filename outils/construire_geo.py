"""Construit la base SQLite des lieux de naissance depuis les dumps GeoNames.

⚠️ LE PIÈGE QUI JUSTIFIE CE SCRIPT
Les fichiers `cities500`/`cities1000`/`cities15000` de GeoNames ÉCHOUENT sur le
Québec, et silencieusement :
  - 2 145 des 2 702 lieux québécois de classe P ont `population = 0` → tout
    filtre par population les jette ;
  - ~1 100 municipalités n'existent QUE comme `A.ADM3` (la couche municipale
    officielle), que les fichiers `cities*` excluent par conception.
Résultat : Trois-Pistoles, Notre-Dame-du-Portage, Rivière-Éternité sont
absents de cities500 ; même Baie-Saint-Paul (7 146 hab.) manque de cities15000.

La recette retenue : partir des dumps PAYS (CA, FR) et filtrer sur
`feature_class = 'P' OR feature_code IN ('ADM3','ADM4')`.

Le fuseau vient du CHAMP 18 de GeoNames : pas besoin de timezonefinder
(~90 Mo + numpy + h3 + une compilation CFFI sur macOS faute de wheel).

Licence GeoNames : CC BY 4.0 → l'attribution doit rester VISIBLE dans l'app.

    python outils/construire_geo.py
"""
import pathlib
import sqlite3
import sys
import unicodedata

RACINE = pathlib.Path(__file__).resolve().parents[1]
GEO = RACINE / "data" / "geo"
BASE = GEO / "lieux.sqlite"
PAYS = ["CA", "FR"]

GARDER_CODES = {"ADM3", "ADM4"}   # couche municipale officielle
COLONNES = (
    "geonameid nom nom_ascii noms_alt lat lon classe code pays cc2 "
    "admin1 admin2 admin3 admin4 population elevation dem fuseau maj"
).split()


def plier(s):
    """Normalise pour la recherche : sans accents, minuscules.

    Cohérent avec la convention de la numérologie retenue (les diacritiques
    sont transparents) — un seul geste de normalisation dans toute l'app.
    """
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def lignes(chemin):
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            champs = ligne.rstrip("\n").split("\t")
            if len(champs) >= 18:
                yield dict(zip(COLONNES, champs))


def main():
    manquants = [p for p in PAYS if not (GEO / f"{p}.txt").exists()]
    if manquants:
        sys.exit(
            f"✗ dumps absents : {manquants}\n"
            f"  cd {GEO} && curl -O https://download.geonames.org/export/dump/CA.zip"
            " && unzip CA.zip"
        )

    BASE.unlink(missing_ok=True)
    con = sqlite3.connect(BASE)
    con.executescript("""
        CREATE TABLE lieux (
            geonameid INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            recherche TEXT NOT NULL,   -- nom plié, sans accents
            pays TEXT NOT NULL,
            admin1 TEXT,
            code TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            population INTEGER NOT NULL,
            fuseau TEXT NOT NULL
        );
        CREATE INDEX idx_recherche ON lieux(recherche);
        CREATE INDEX idx_pays_admin ON lieux(pays, admin1);
    """)

    total, gardes, sans_fuseau = 0, 0, 0
    lot = []
    for pays in PAYS:
        for r in lignes(GEO / f"{pays}.txt"):
            total += 1
            if not (r["classe"] == "P" or r["code"] in GARDER_CODES):
                continue
            if not r["fuseau"]:
                sans_fuseau += 1
                continue
            gardes += 1
            lot.append((
                int(r["geonameid"]), r["nom"], plier(r["nom"]), r["pays"],
                r["admin1"], r["code"], float(r["lat"]), float(r["lon"]),
                int(r["population"] or 0), r["fuseau"],
            ))
            if len(lot) >= 20000:
                con.executemany("INSERT OR REPLACE INTO lieux VALUES (?,?,?,?,?,?,?,?,?,?)", lot)
                lot.clear()
    if lot:
        con.executemany("INSERT OR REPLACE INTO lieux VALUES (?,?,?,?,?,?,?,?,?,?)", lot)
    con.commit()
    con.execute("VACUUM")
    con.close()

    taille = BASE.stat().st_size / 1e6
    print(f"✓ {gardes:,} lieux gardés sur {total:,} lus  ->  {BASE.relative_to(RACINE)}"
          .replace(",", " "))
    print(f"  {taille:.1f} Mo · {sans_fuseau} lignes écartées faute de fuseau")
    print("  ⚠️ Données GeoNames (CC BY 4.0) — l'attribution doit rester visible dans l'app.")


if __name__ == "__main__":
    main()
