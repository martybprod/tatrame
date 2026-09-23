# Génération des miniatures WebP des cartes — FABRICATION, hors runtime.
#
# L'app affiche les cartes à ~60-72 px de large (jusqu'à ~216 px en écran
# rétine ×3) ; les JPEG servis l'étaient en pleine résolution (800×1388 pour
# les majeures, 312-491 Ko chacun) — plus d'un mégaoctet pour les trois
# cartes du jour. Ce script écrit une fois pour toutes une petite version
# WebP (256 px de large, 10-25 Ko) dans `mini/` à côté des originaux, que
# le front utilise pour les vignettes ; la pleine résolution reste servie
# pour le plein écran et la lightbox.
#
# Usage :
#   ./venv/bin/python scripts/generer_miniatures_cartes.py
#
# Idempotent et honnête : une miniature existante plus récente que sa source
# n'est pas refaite (—force pour tout régénérer).

import sys
from pathlib import Path

from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
CARTES = RACINE / "static" / "cartes"

LARGEUR_MINI = 256
QUALITE = 82


def generer(chemin_source: Path, ecraser: bool) -> None:
    relatif = chemin_source.relative_to(CARTES)
    cible = CARTES / "mini" / relatif.with_suffix(".webp")
    if not ecraser and cible.exists() and cible.stat().st_mtime >= chemin_source.stat().st_mtime:
        return
    cible.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(chemin_source)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    ratio = LARGEUR_MINI / im.width
    im = im.resize((LARGEUR_MINI, round(im.height * ratio)), Image.LANCZOS)
    im.save(cible, "WEBP", quality=QUALITE, method=6)
    print(f"  {relatif} -> {cible.relative_to(CARTES)} "
          f"({chemin_source.stat().st_size // 1024} -> {cible.stat().st_size // 1024} Ko)")


def main() -> None:
    ecraser = "--force" in sys.argv
    print("Majeures + dos :")
    sources = sorted(CARTES.glob("*.jpg"))
    for source in sources:
        generer(source, ecraser)
    print("Mineures :")
    for source in sorted((CARTES / "mineurs").glob("*.jpg")):
        generer(source, ecraser)


if __name__ == "__main__":
    main()
