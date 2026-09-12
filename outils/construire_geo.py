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

La recette retenue : partir des dumps PAYS (CA, FR, BE) et filtrer sur
`feature_class = 'P' OR feature_code IN ('ADM3','ADM4')`.

⚠️ LE SECOND PIÈGE : LES NOMS USUELS (table `alias`)
GeoNames nomme les villes belges en anglais ou en néerlandais — `Brussels`,
`Antwerp`, `Gent`, `Oostende`. Sans table d'alias, un utilisateur francophone
tapant « Bruxelles », « Anvers », « Gand » ou « Ostende » ne trouve RIEN : la
Belgique serait dans la base sans être joignable. Pire, « Gand » tombait sur
Gander (Terre-Neuve). On indexe donc les noms du champ 3 (`noms_alt`), filtrés
pour rester tapables : alphabet latin, 3 lettres minimum.

Le seuil de 3 lettres n'exclut aucune commune : les noms courts (« Ur », « Ee »)
restent trouvables par leur nom principal, lui toujours indexé.

Le fuseau vient du CHAMP 18 de GeoNames : pas besoin de timezonefinder
(~90 Mo + numpy + h3 + une compilation CFFI sur macOS faute de wheel).

Licence GeoNames : CC BY 4.0 → l'attribution doit rester VISIBLE dans l'app.

    python outils/construire_geo.py
"""
import pathlib
import re
import sqlite3
import sys
import unicodedata

RACINE = pathlib.Path(__file__).resolve().parents[1]
GEO = RACINE / "data" / "geo"
BASE = GEO / "lieux.sqlite"
# BE ajouté le 2026-09-12 (demande de Martin) : les naissances belges manquaient
# purement et simplement — aucune commune n'était trouvable.
PAYS = ["CA", "FR", "BE"]

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


# Un nom alternatif doit rester TAPABLE : alphabet latin, sans trop de ponctuation.
# Sans ce filtre, on indexerait « Москва », « 東京 » et des codes IATA de 3 lettres.
ALIAS_TAPABLE = re.compile(r"^[a-z0-9 \-'.]+$")


def alias_de(nom, noms_alt):
    """Les noms sous lesquels on veut AUSSI trouver ce lieu.

    Renvoie le nom plié et ses variantes pliées, dédoublonnées. Le nom principal
    est toujours inclus — un lieu reste joignable même si ses variantes sont
    toutes écartées par le filtre.
    """
    plie = plier(nom)
    vus = {plie}
    for alt in noms_alt.split(","):
        a = plier(alt.strip())
        if len(a) >= 3 and a not in vus and ALIAS_TAPABLE.match(a):
            vus.add(a)
    return vus


def _ecrire(con, lot, lot_alias):
    """Vide un lot dans les deux tables. Les lieux D'ABORD : la clé étrangère
    des alias l'exige, et SQLite n'a pas de contrainte différée ici."""
    con.executemany("INSERT OR REPLACE INTO lieux VALUES (?,?,?,?,?,?,?,?,?)", lot)
    con.executemany("INSERT INTO alias VALUES (?,?)", lot_alias)


def lignes(chemin):
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            champs = ligne.rstrip("\n").split("\t")
            if len(champs) >= 18:
                yield dict(zip(COLONNES, champs))


def main():
    manquants = [p for p in PAYS if not (GEO / f"{p}.txt").exists()]
    if manquants:
        # GeoNames ne sert PAS de <CC>.txt : seul le .zip existe (BE.txt -> 404,
        # BE.zip -> 200). D'où l'aller-retour par l'archive.
        zips = " ".join(f"{p}.zip" for p in manquants)
        sys.exit(
            f"✗ dumps absents : {manquants}\n"
            f"  cd {GEO} && curl -O {' '.join(f'https://download.geonames.org/export/dump/{p}.zip' for p in manquants)}"
            f" && unzip {zips}"
        )

    BASE.unlink(missing_ok=True)
    con = sqlite3.connect(BASE)
    con.executescript("""
        CREATE TABLE lieux (
            geonameid INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,          -- nom officiel GeoNames, tel quel pour l'affichage
            pays TEXT NOT NULL,
            admin1 TEXT,
            code TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            population INTEGER NOT NULL,
            fuseau TEXT NOT NULL
        );
        CREATE INDEX idx_pays_admin ON lieux(pays, admin1);

        -- Tous les noms sous lesquels un lieu se CHERCHE : son nom principal plié
        -- et ses variantes utiles (voir alias_de). Le nom plié n'est donc PAS
        -- dupliqué dans `lieux` — une seule source pour la recherche.
        CREATE TABLE alias (
            nom TEXT NOT NULL,
            geonameid INTEGER NOT NULL REFERENCES lieux(geonameid)
        );
        CREATE INDEX idx_alias_nom ON alias(nom);
    """)

    total, gardes, sans_fuseau, alias_total = 0, 0, 0, 0
    lot, lot_alias = [], []
    for pays in PAYS:
        for r in lignes(GEO / f"{pays}.txt"):
            total += 1
            if not (r["classe"] == "P" or r["code"] in GARDER_CODES):
                continue
            if not r["fuseau"]:
                sans_fuseau += 1
                continue
            gardes += 1
            geonameid = int(r["geonameid"])
            lot.append((
                geonameid, r["nom"], r["pays"],
                r["admin1"], r["code"], float(r["lat"]), float(r["lon"]),
                int(r["population"] or 0), r["fuseau"],
            ))
            noms = alias_de(r["nom"], r["noms_alt"])
            alias_total += len(noms)
            lot_alias.extend((nom, geonameid) for nom in noms)
            if len(lot) >= 20000:
                _ecrire(con, lot, lot_alias)
                lot, lot_alias = [], []
    if lot:
        _ecrire(con, lot, lot_alias)
    con.commit()
    con.execute("VACUUM")
    con.close()

    taille = BASE.stat().st_size / 1e6
    print(f"✓ {gardes:,} lieux gardés sur {total:,} lus  ->  {BASE.relative_to(RACINE)}"
          .replace(",", " "))
    print(f"  {taille:.1f} Mo · {sans_fuseau} lignes écartées faute de fuseau")
    print(f"  {alias_total:,} noms indexés (nom principal + variantes)".replace(",", " "))
    print("  ⚠️ Données GeoNames (CC BY 4.0) — l'attribution doit rester visible dans l'app.")


if __name__ == "__main__":
    main()
