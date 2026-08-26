"""Fusionne les 12 fragments de domaine en data/corpus/fil.json.

Échoue bruyamment sur toute collision de clé entre domaines (il ne doit pas
y en avoir : chaque domaine préfixe ses clés par son slug).
"""
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[1]
FRAGMENTS = RACINE / "_distillation" / "fil_fragments"
SORTIE = RACINE / "data" / "corpus" / "fil.json"

DOMAINES = ["soi", "ressources", "echanges", "racines", "creation", "quotidien",
            "autre", "traversee", "sens", "metier", "communaute", "retrait"]

fusion = {
    "_charte": "data/corpus/CHARTE.md",
    "_note": ("Le Fil du jour — couche coaching, distillee des 24 ouvrages "
              "(voir _distillation/cartes_de_concepts.md). CONCEPTS repris, JAMAIS "
              "la prose des livres. Route par le ciel : maison de la Lune = domaine, "
              "transit dominant + phase = nuance. Jamais un de. Additif : une perle "
              "par (domaine x condition-ciel qui a un sens). Remplace creativite.json "
              "(migre dans le domaine creation)."),
}

total = 0
par_domaine = {}
for slug in DOMAINES:
    f = FRAGMENTS / f"{slug}.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    entrees = {k: v for k, v in data.items() if not k.startswith("_")}
    # Chaque cle doit commencer par le slug du domaine (garde-fou).
    for k in entrees:
        if not (k == slug or k.startswith(slug + "_")):
            raise SystemExit(f"ERREUR {slug}: cle hors domaine « {k} »")
    collisions = fusion.keys() & entrees.keys()
    if collisions:
        raise SystemExit(f"ERREUR {slug}: collision de cles {sorted(collisions)}")
    fusion.update(entrees)
    par_domaine[slug] = len(entrees)
    total += len(entrees)

SORTIE.write_text(json.dumps(fusion, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"fil.json ecrit : {total} perles, {len(DOMAINES)} domaines")
for slug in DOMAINES:
    # verifie que chaque domaine a bien sa cle generique (socle)
    ok = "OK" if slug in fusion else "!!! MANQUE GENERIQUE"
    print(f"  {slug}: {par_domaine[slug]}  {ok}")
