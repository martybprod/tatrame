"""Prépare les images d'app à partir des cartouches validés.

Convention Align (reproduction exacte du geste de `_faire_images_app.py`,
adaptée à ce projet) :
  `_distillation/../../cartes_validees/CARTE_<id>_<Nom>_validee.png`
    → `static/img/cartes/<id>.jpg`  (largeur 600, JPEG qualité 82)
  le dos : `CARTE_dos_de_carte_APP_300x527.png` → `static/img/dos.png`

Les variantes « archivée » sont ignorées (ce ne sont pas les cartes livrées).
En cas de deux validées non archivées pour un même id, la plus récente gagne
et la collision est signalée.

Usage : ./venv/bin/python outils/preparer_images_app.py
"""
import os
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
VALIDEES = RACINE.parent / "_distillation" / "cartes_validees"
DOS_APP = RACINE.parent / "CARTE_dos_de_carte_APP_300x527.png"
SORTIE = RACINE / "static" / "img" / "cartes"
LARGEUR = 600
QUALITE = 82

MOTIF = re.compile(
    r"^CARTE_(major_\d{2}|(?:feu|eau|air|terre)_(?:as|\d{2}|page|chevalier|reine|roi))_.*_validee\.png$"
)


def est_archivee(nom):
    return "archive" in nom.lower()  # attrape « archivée » et « archivee »


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    gagnants = {}
    collisions = []
    for f in sorted(VALIDEES.glob("CARTE_*_validee.png")):
        if est_archivee(f.name):
            continue
        m = MOTIF.match(f.name)
        if not m:
            continue
        id_carte = m.group(1)
        if id_carte in gagnants:
            collisions.append(id_carte)
            if f.stat().st_mtime < gagnants[id_carte][1]:
                continue
        gagnants[id_carte] = (f, f.stat().st_mtime)

    n = 0
    for id_carte, (f, _) in sorted(gagnants.items()):
        cible = SORTIE / f"{id_carte}.jpg"
        with Image.open(f) as im:
            ratio = im.height / im.width
            taille = (LARGEUR, round(LARGEUR * ratio))
            petite = im.convert("RGB").resize(taille, Image.LANCZOS)
            petite.save(cible, "JPEG", quality=QUALITE, optimize=True)
        n += 1

    dos = SORTIE.parent / "dos.png"
    if DOS_APP.exists():
        shutil.copy(DOS_APP, dos)

    print(f"{n} faces d'app écrites dans {SORTIE.relative_to(RACINE)}")
    print(f"dos copié : {dos.name}")
    if collisions:
        print("collisions (id avec plusieurs validées non archivées) :", ", ".join(sorted(set(collisions))))
        print("→ la plus récente a gagné ; à vérifier avec Martin.")
        sys.exit(1)


if __name__ == "__main__":
    main()
