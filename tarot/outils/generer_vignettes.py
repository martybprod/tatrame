"""Vignettes légères des faces de cartes (2026-11-16).

Les faces d'app font 1024×1776 (≈ 340 Ko) : parfaites en plein écran, mais
démesurées dans une case de 60 à 170 px — un tirage à dix cartes pesait
3,4 Mo et « Je choisis » 27 Mo, et chaque face décodée occupe ~7 Mo de
mémoire sur iPhone. Les vignettes (400 px de large, WebP) servent partout
sauf au plein écran et à la page du récit.

Relancer après tout changement d'une face :  ./venv/bin/python outils/generer_vignettes.py
(et monter VERSION_VIGNETTES dans app.py pour invalider les caches).
"""
import pathlib
from PIL import Image

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCE = RACINE / "static" / "img" / "cartes"
CIBLE = SOURCE / "mini"
LARGEUR = 400

CIBLE.mkdir(exist_ok=True)
total_avant = total_apres = 0
for f in sorted(SOURCE.glob("*.jpg")):
    im = Image.open(f).convert("RGB")
    h = round(im.height * LARGEUR / im.width)
    mini = im.resize((LARGEUR, h), Image.LANCZOS)
    dest = CIBLE / f"{f.stem}.webp"
    mini.save(dest, "WEBP", quality=82, method=6)
    total_avant += f.stat().st_size
    total_apres += dest.stat().st_size
print(f"{len(list(CIBLE.glob('*.webp')))} vignettes · {total_avant/1e6:.1f} Mo → {total_apres/1e6:.1f} Mo")
