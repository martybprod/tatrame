#!/usr/bin/env python3
"""Exporte en Markdown (prêt à copier-coller) les fiches qui attendent la
reformulation de Martin — c'est-à-dire celles qui n'ont pas encore de champ
« reprise » dans leur source_referentielle.

Sortie : maquettes/a_reformuler/<id>.md — un fichier par fiche, structuré
exactement comme le format que Martin reformule et renvoie.

Usage : ./venv/bin/python outils/exporter_reformulation.py
"""
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCES = [RACINE / "data" / "corpus" / "cartes", RACINE / "data" / "grammaire" / "exemples"]
SORTIE = RACINE / "maquettes" / "a_reformuler"


def charger_fiches():
    fiches, vus = {}, set()
    for dossier in SOURCES:
        if not dossier.is_dir():
            continue
        for p in sorted(dossier.glob("*.json")):
            f = json.loads(p.read_text(encoding="utf-8"))
            if f["id"] not in vus:
                vus.add(f["id"])
                fiches[f["id"]] = f
    return [fiches[k] for k in sorted(fiches)]


def exporter(f):
    meta = []
    if f.get("registre") and f["registre"] != "hors_cycle":
        meta.append(f["registre"])
    if f.get("element"):
        meta.append(f["element"])
    if f.get("famille"):
        meta.append(f["famille"])
    if f.get("degre") is not None:
        meta.append(f"degré {f['degre']}")
    if f.get("rang"):
        meta.append(f["rang"])
    pos = f.get("positions")
    img = f["image"]

    lignes = [
        f"# {f['nom']}",
        "",
        f"{f['id']} · {' · '.join(meta)}",
        "",
        "*" + " · ".join(f["mots_cles"]) + "*",
        "",
        f"pousse : {f['tension']['pousse']}",
        f"retient : {f['tension']['retient']}",
        "",
        "### Lumière — la qualité qui circule",
        "",
        f["lumiere"],
        "",
        f"### Ombre — mode « {f['ombre']['mode']} »",
        "",
        f["ombre"]["texte"],
        "",
        "**Issue (la chaîne large)**",
        "",
        f["ombre"]["issue"],
        "",
        "### Questions (Greer)",
        "",
    ]
    lignes += [f"- {q}" for q in f["questions"]]
    lignes += [
        "",
        "### Leçon",
        "",
        f"*{f['lecon']}*",
        "",
        "### L'image (Pollack — décrire avant d'interpréter)",
        "",
        f"**geste** — {img['geste']}",
        "",
        f"**seuil** — {img['seuil']}",
        "",
        f"**détail** — {img['detail']}",
        "",
        "### Micro-geste (24 h)",
        "",
        f["micro_geste"],
        "",
    ]
    if pos:
        lignes += [
            "### Positions (table A)",
            "",
            "**Aujourd'hui — tirage du jour**",
            "",
            pos["jour"],
            "",
            "**Ce que j'amène**",
            "",
            pos["amene"],
            "",
            "**Ce qui se joue**",
            "",
            pos["se_joue"],
            "",
            "**Ce que je peux essayer**",
            "",
            pos["essayer"],
            "",
        ]
    else:
        lignes += [
            "### Le regard (variantes — la graine en choisit une)",
            "",
        ]
        lignes += [f"- {r}" for r in f.get("le_regard", [])]
        lignes += [""]
    return "\n".join(lignes)


def main():
    import json

    SORTIE.mkdir(parents=True, exist_ok=True)
    ecrites = []
    for f in charger_fiches():
        reprise = (f.get("source_referentielle") or {}).get("reprise")
        if reprise:
            continue  # déjà reformulée par Martin
        cible = SORTIE / f"{f['id']}.md"
        cible.write_text(exporter(f), encoding="utf-8")
        ecrites.append(cible)
    if not ecrites:
        print("Aucune fiche en attente de reformulation.")
    for c in ecrites:
        print(c.relative_to(RACINE))


if __name__ == "__main__":
    main()
