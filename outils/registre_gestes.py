#!/usr/bin/env python3
"""Le registre des gestes retirés — l'ancre des vieilles notes du journal.

Quand un geste du corpus est reformulé (le texte s'améliore, l'ancien part),
les notes du journal qui portaient CE geste perdent leur ancre : le rattrapage
rétroactif ne retrouve plus leur miroir dans le corpus actuel, et la note
rouverte ne montre que la partie « En action » (vécu du 2026-11-25 : 6 notes
de bêta dans ce cas).

Ce registre garde la paire (geste → miroir) telle qu'elle existait à sa
DERNIÈRE version dans l'historique git du corpus — assez pour regreffer le
message d'origine des notes anciennes, sans garder tout l'historique dans
l'image de production.

Régénérer après une édition de corpus qui retire des gestes :
    ./outils/registre_gestes.py

Compare le corpus actuel à l'état du 2026-08-30 (le lancement du journal) :
tout geste absent d'aujourd'hui est enregistré avec son dernier miroir connu,
et la table où il vivait (pour relire l'histoire si besoin). Le fichier écrit
— data/gestes_retires.json — est versionné et part dans l'image (data/ à la
racine, PAS dans data/corpus : le chargeur du corpus prend chaque .json du
dossier pour une table de textes, ce registre n'en est pas une).
"""
import json
import pathlib
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = RACINE / "data" / "corpus"
REGISTRE = RACINE / "data" / "gestes_retires.json"
# Le journal existe depuis le 2026-08-30 : aucune note ne peut porter un geste
# d'avant, inutile de creuser plus loin dans l'histoire.
DEPUIS = "2026-08-30"


def _corpus_a(ref):
    """Tous les (geste → (miroir, table)) d'une révision de l'historique."""
    fichiers = sorted(str(p.relative_to(RACINE)) for p in CORPUS.glob("*.json"))
    trouve = {}
    for f in fichiers:
        s = subprocess.run(["git", "show", f"{ref}:{f}"],
                           capture_output=True, text=True).stdout
        if not s:
            continue
        try:
            j = json.loads(s)
        except json.JSONDecodeError:
            continue

        def cueillir(noeud, table):
            if isinstance(noeud, dict):
                geste = noeud.get("geste")
                if isinstance(geste, str) and geste.strip():
                    trouve[geste.strip()] = {
                        "miroir": (noeud.get("miroir") or "").strip(),
                        "table": table,
                    }
                for v in noeud.values():
                    cueillir(v, table)

        cueillir(j, f)
    return trouve


def main():
    commits = [c for c in subprocess.run(
        ["git", "rev-list", f"--since={DEPUIS}", "HEAD", "--", "data/corpus"],
        capture_output=True, text=True).stdout.split() if c]
    if not commits:
        print("Aucun changement de corpus depuis le lancement du journal — "
              "rien à enregistrer.")
        return
    # Du plus ancien au plus récent : la dernière écriture d'un geste gagne.
    historique = {}
    for c in reversed(commits):
        historique.update(_corpus_a(c))
    actuel = _corpus_a("HEAD")
    retires = {geste: info for geste, info in historique.items()
               if geste not in actuel and info.get("miroir")}
    REGISTRE.write_text(
        json.dumps(retires, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8")
    print(f"{len(retires)} geste(s) retiré(s) depuis le {DEPUIS} → {REGISTRE.relative_to(RACINE)}")
    for geste in sorted(retires):
        print(f"  • {retires[geste]['table']} — {geste[:60]}…")


if __name__ == "__main__":
    sys.exit(main())
