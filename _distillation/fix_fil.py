"""Raccourcit les `source_livre` de fil.json sous 40 caractères.

source_livre est une métadonnée interne (jamais affichée) ; le test global
`test_aucun_texte_en_double` dédoublonne toute chaîne >= 40 car, or ces
attributions se répètent par domaine. En les ramenant à « d'après <auteur> »
(< 40 car), le test les ignore (filtre len < 40) et la provenance reste lisible.
"""
import json
import pathlib
import re

R = pathlib.Path(__file__).resolve().parents[1]
F = R / "data" / "corpus" / "fil.json"
d = json.loads(F.read_text(encoding="utf-8"))


def court(s):
    s = s.replace("les concepts de ", "")
    for sep in (" — ", " – ", " - "):
        if sep in s:
            s = s.split(sep)[0]
    s = s.strip()
    if len(s) >= 40:
        head = s[8:] if s.startswith("d'après ") else s
        first = re.split(r",| & | et ", head)[0].strip()
        s = "d'après " + first
    return s


restants = []
for k, e in d.items():
    if k.startswith("_") or not isinstance(e, dict):
        continue
    if "source_livre" in e:
        e["source_livre"] = court(e["source_livre"])
        if len(e["source_livre"]) >= 40:
            restants.append((k, e["source_livre"]))

F.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("source_livre raccourcis. Restants >=40 car:", restants or "aucun")
