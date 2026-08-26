"""Vérification jetable des ajouts au Fil du jour, mêmes seuils que tests/test_fil.py
et tests/test_corpus.py — avant fusion dans data/corpus/fil.json. Usage :
venv/bin/python3 _distillation/_verif_ajouts.py <fichier_ajouts.json>"""
import json, re, sys, pathlib

RACINE = pathlib.Path(__file__).resolve().parents[1]
fil = json.loads((RACINE / "data/corpus/fil.json").read_text())
chemin_ajouts = RACINE / "_distillation" / sys.argv[1]
ajouts = json.loads(chemin_ajouts.read_text())
domaine = sys.argv[2] if len(sys.argv) > 2 else next(iter(ajouts)).split("_")[0]

erreurs = []

def suites(texte, n=8):
    mots = re.findall(r"\w+", texte.lower())
    return {" ".join(mots[i:i+n]) for i in range(len(mots)-n+1)}

for k in ajouts:
    if k in fil:
        erreurs.append(f"CLE DEJA PRESENTE : {k}")

for k, e in ajouts.items():
    n = len((e["miroir"] + " " + e["geste"]).split())
    if not (30 <= n <= 85):
        erreurs.append(f"{k} : longueur {n} mots (hors 30-85)")
    if not e.get("miroir") or not e.get("geste") or not e.get("source_livre"):
        erreurs.append(f"{k} : champ manquant")

PLANETES = {"soleil","lune","mercure","venus","mars","jupiter","saturne","uranus","neptune","pluton"}
CLASSES = {"conjonction","carre-opposition","sextile-trigone"}
for k in ajouts:
    m = re.match(r"^[a-z]+_transit_([a-z]+)_(.+)$", k)
    if not m or m.group(1) not in PLANETES or m.group(2) not in CLASSES:
        erreurs.append(f"{k} : motif de clé invalide")

existant_textes = {k: e["miroir"] + " " + e.get("geste","")
                   for k, e in fil.items() if isinstance(e, dict) and e.get("miroir")}
nouveaux_textes = {k: e["miroir"] + " " + e["geste"] for k, e in ajouts.items()}

for k, t in nouveaux_textes.items():
    s1 = suites(t)
    for k2, t2 in existant_textes.items():
        partage = s1 & suites(t2)
        if len(partage) >= 4:
            erreurs.append(f"{k} partage {len(partage)} suites de 8 mots avec {k2} : {list(partage)[:2]}")
    for k2, t2 in nouveaux_textes.items():
        if k >= k2: continue
        partage = s1 & suites(t2)
        if len(partage) >= 2:
            erreurs.append(f"{k} partage {len(partage)} suites de 8 mots avec NOUVEAU {k2}")

def ouverture(texte):
    return " ".join(texte.split()[:5]).lower().rstrip(",.:")

ouv_existantes = {ouverture(t) for k, t in existant_textes.items() if k.startswith(domaine)}
for k, e in ajouts.items():
    o = ouverture(e["miroir"])
    if o in ouv_existantes:
        erreurs.append(f"{k} : ouverture deja utilisee -> {o!r}")
    ouv_existantes.add(o)

for k, e in ajouts.items():
    txt = e["miroir"] + " " + e["geste"]
    if "—" in txt:
        erreurs.append(f"{k} : tiret cadratin present")
    if re.match(r"^\s*ce n'est pas", e["miroir"], re.I):
        erreurs.append(f"{k} : ouverture 'Ce n'est pas'")

INTERDITS = [
    (r"\btu (vas |)(rencontrer|recevr|trouver|connaîtr|vivr)a?s?\b", "prediction"),
    (r"\btu es quelqu'un\b", "essentialisation"),
    (r"\bton destin\b", "fatalisme"),
    (r"\bil faut que tu\b", "prescription"),
    (r"\btu devras\b", "prescription au futur"),
    (r"\bc'est écrit\b", "fatalisme"),
]
for k, e in ajouts.items():
    txt = e["miroir"] + " " + e["geste"]
    for motif, label in INTERDITS:
        if re.search(motif, txt, re.I):
            erreurs.append(f"{k} : interdit de registre ({label})")

print(f"{len(ajouts)} entrées vérifiées (domaine {domaine}).")
if erreurs:
    print(f"\n{len(erreurs)} PROBLÈME(S) :")
    for e in erreurs:
        print(" -", e)
    sys.exit(1)
else:
    print("AUCUN PROBLÈME — prêt à fusionner.")
