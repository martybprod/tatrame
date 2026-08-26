"""Garde-fous du corpus des 56 arcanes mineurs (data/corpus/mineurs.json).

Distinct de tests/test_mineurs.py (qui teste le CALCUL, moteur/mineurs.py) :
ici on teste le CORPUS écrit à la main. `nom` et `correspondance` sont
calculés par le moteur (pas dans ce fichier) ; seul `invitation` est rédigé.
"""
import json
import pathlib
import re
import unicodedata

import pytest

from moteur import mineurs as M

RACINE = pathlib.Path(__file__).resolve().parents[1]
CORPUS_PATH = RACINE / "data" / "corpus" / "mineurs.json"
SOURCE = RACINE / "_distillation" / "sources"

CLES_ATTENDUES = {f"{s}_{r}" for s in M.SUIT_NOM for r in M.RANGS}


def _charger():
    if not CORPUS_PATH.exists():
        pytest.skip("data/corpus/mineurs.json absent — corpus pas encore écrit")
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def _entrees():
    d = _charger()
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _norm(txt):
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).split()


# ------------------------------------------------------------- COUVERTURE

def test_les_56_cles_sont_couvertes():
    entrees = _entrees()
    manque = CLES_ATTENDUES - entrees.keys()
    assert not manque, f"mineurs sans entrée corpus : {manque}"


def test_aucune_cle_hors_namespace():
    entrees = _entrees()
    hors = entrees.keys() - CLES_ATTENDUES
    assert not hors, f"clés hors namespace (faute de frappe ?) : {hors}"


def test_chaque_entree_a_une_invitation():
    entrees = _entrees()
    vides = [k for k, e in entrees.items() if not e.get("invitation", "").strip()]
    assert not vides, f"invitation manquante : {vides}"


# --------------------------------------------------------------- LONGUEUR

def test_longueur_invitation():
    entrees = _entrees()
    hors = {k: len(e["invitation"].split()) for k, e in entrees.items()}
    fautes = {k: n for k, n in hors.items() if n < 20 or n > 55}
    assert not fautes, f"invitation hors bornes (20-55 mots) : {fautes}"


# ------------------------------------------------------------------ VOIX

def test_pas_de_prediction_ni_prescription():
    motif = r"\btu (vas|dois|devras)\b|\bil faut que tu\b"
    entrees = _entrees()
    fautifs = [k for k, e in entrees.items() if re.search(motif, e["invitation"], re.I)]
    assert not fautifs, f"prédiction/prescription détectée : {fautifs}"


def test_pas_d_ouverture_ce_n_est_pas():
    entrees = _entrees()
    fautifs = [k for k, e in entrees.items()
               if re.match(r"^\s*ce n['’]est pas", e["invitation"].lower())]
    assert not fautifs, f"ouverture « Ce n'est pas… » : {fautifs}"


def test_pas_de_titre_esoterique_du_jeu_source():
    # Les 56 titres traditionnels du courant "Lord of..." (Golden Dawn /
    # Book T, popularisés par Crowley) sont une expression protégée distincte
    # des noms génériques "As de Coupes" etc. qu'Align utilise (calculés,
    # voir moteur/mineurs.py) — vérifie qu'aucun n'a été recopié dans la prose.
    interdits = ["lord of", "seigneur de", "domination oppression", "abondance materielle",
                 "plaisir illusoire"]
    entrees = _entrees()
    for k, e in entrees.items():
        plat = " ".join(_norm(e["invitation"]))
        for m in interdits:
            assert m not in plat, f"{k} : motif du jeu source détecté « {m} »"


# ------------------------------------------------------------ ANTI-PLAGIAT

def test_aucun_8gramme_dans_les_sources():
    if not SOURCE.exists() or not any(SOURCE.glob("*.txt")):
        pytest.skip("sources absentes — anti-plagiat non exécuté")

    entrees = _entrees()
    suspects = {}
    for k, e in entrees.items():
        mots = _norm(e["invitation"])
        for i in range(len(mots) - 7):
            suspects[" ".join(mots[i:i + 8])] = k

    hits = []
    for f in sorted(SOURCE.glob("*.txt")):
        mots_source = _norm(f.read_text(encoding="utf-8", errors="replace"))
        vus = set()
        for i in range(len(mots_source) - 7):
            gr = " ".join(mots_source[i:i + 8])
            if gr in suspects and gr not in vus:
                vus.add(gr)
                hits.append((f.name, suspects[gr], gr))
    assert not hits, f"8-grammes copiés d'une source : {hits[:8]}"


# ---------------------------------------------------------------- VARIÉTÉ

def test_pas_de_longue_suite_partagee_entre_deux_cartes():
    entrees = _entrees()
    vus = {}
    collisions = []
    for k, e in entrees.items():
        mots = _norm(e["invitation"])
        for i in range(len(mots) - 7):
            g = " ".join(mots[i:i + 8])
            if g in vus and vus[g] != k:
                collisions.append((g, vus[g], k))
            else:
                vus[g] = k
    assert not collisions, f"suites de 8 mots partagées : {collisions[:5]}"


def test_aucune_ouverture_ne_domine():
    from collections import Counter
    entrees = _entrees()
    debuts = Counter(" ".join(_norm(e["invitation"])[:4]) for e in entrees.values())
    trop = {d: n for d, n in debuts.items() if n > 5}
    assert not trop, f"ouvertures qui dominent : {trop}"
