"""Garde-fous du corpus de la personologie (48 sous-périodes + axe des nœuds).

Distinct de tests/test_periodes.py (qui teste le CALCUL, moteur/periodes.py) :
ici on teste le CORPUS écrit à la main (data/corpus/periodes.json et noeuds.json).
"""
import json
import pathlib
import re
import unicodedata

import pytest

from moteur import periodes as P

RACINE = pathlib.Path(__file__).resolve().parents[1]
PERIODES_JSON = json.loads((RACINE / "data" / "corpus" / "periodes.json").read_text(encoding="utf-8"))
NOEUDS_JSON = json.loads((RACINE / "data" / "corpus" / "noeuds.json").read_text(encoding="utf-8"))
SOURCE = RACINE / "_distillation" / "sources" / "the_secret_language_of_destiny_personology_goldschneider.txt"

PERIODES_ENTREES = {k: v for k, v in PERIODES_JSON.items() if not k.startswith("_")}
NOEUDS_ENTREES = {k: v for k, v in NOEUDS_JSON.items() if not k.startswith("_")}


def _norm(txt):
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).split()


# ------------------------------------------------------------- COUVERTURE

def test_les_48_cles_du_moteur_sont_couvertes():
    cles_moteur = {p["cle"] for p in P.PERIODES}
    manque = cles_moteur - PERIODES_ENTREES.keys()
    assert not manque, f"périodes sans entrée corpus : {manque}"


def test_chaque_periode_a_nom_essence_texte():
    incomplets = [k for k, e in PERIODES_ENTREES.items()
                  if not e.get("nom", "").strip()
                  or not e.get("essence", "").strip()
                  or not e.get("texte", "").strip()]
    assert not incomplets, f"champs manquants : {incomplets}"


def test_les_48_periodes_ont_origine_et_destination():
    cles_moteur = {p["cle"] for p in P.PERIODES}
    manque = cles_moteur - NOEUDS_ENTREES.keys()
    assert not manque, f"périodes sans entrée nœuds : {manque}"
    incomplets = [k for k in cles_moteur
                  if not NOEUDS_ENTREES[k].get("origine", "").strip()
                  or not NOEUDS_ENTREES[k].get("destination", "").strip()]
    assert not incomplets, f"origine/destination manquant : {incomplets}"


def test_noms_de_periodes_uniques():
    noms = [e["nom"] for e in PERIODES_ENTREES.values()]
    doublons = {n for n in noms if noms.count(n) > 1}
    assert not doublons, f"noms de période dupliqués : {doublons}"


# --------------------------------------------------------------- LONGUEURS

def test_longueur_texte_periodes():
    hors = {k: len(e["texte"].split()) for k, e in PERIODES_ENTREES.items()}
    fautes = {k: n for k, n in hors.items() if n < 80 or n > 155}
    assert not fautes, f"texte hors bornes (80-155 mots) : {fautes}"


def test_longueur_origine_destination():
    fautes = {}
    for s, e in NOEUDS_ENTREES.items():
        for champ in ("origine", "destination"):
            n = len(e[champ].split())
            if n < 70 or n > 145:
                fautes[f"{s}.{champ}"] = n
    assert not fautes, f"origine/destination hors bornes (70-145 mots) : {fautes}"


# ------------------------------------------------------------------ VOIX

def test_pas_de_prediction_ni_prescription():
    motif = r"\btu (vas|dois|devras)\b|\bil faut que tu\b"
    fautifs = []
    for k, e in {**PERIODES_ENTREES, **NOEUDS_ENTREES}.items():
        for champ in ("texte", "essence", "origine", "destination"):
            txt = e.get(champ, "")
            if txt and re.search(motif, txt, re.I):
                fautifs.append((k, champ))
    assert not fautifs, f"prédiction/prescription détectée : {fautifs}"


# NOTE : pas de test « vocabulaire réservé absent » ici. CHARTE.md le
# tranche déjà (§ « Ce qui est interdit, c'est la MÉTAPHORE — pas les mots
# français ») et test_corpus.py::test_align_n_interdit_pas_son_propre_
# vocabulaire documente l'incident vécu : bannir des mots français ordinaires
# (élan, geste, foyer, cap...) casse du texte innocent sans protéger de rien.
# L'interdit qui compte — le vocabulaire du LIVRE SOURCE de numérologie
# (mémoire familiale, écorce, dynamique de vie) — est déjà couvert par
# test_corpus.py::test_aucune_marque_ni_vocabulaire_protege, qui scanne
# tout le corpus (periodes/noeuds inclus, via CHAMPS_DE_PROSE).


# ------------------------------------------------------------ ANTI-PLAGIAT

def test_aucun_8gramme_dans_la_source_personologie():
    if not SOURCE.exists():
        pytest.skip("source personologie absente — anti-plagiat non exécuté")

    suspects = {}
    for k, e in {**PERIODES_ENTREES, **NOEUDS_ENTREES}.items():
        texte = " ".join(e.get(c, "") for c in ("essence", "texte", "origine", "destination"))
        mots = _norm(texte)
        for i in range(len(mots) - 7):
            suspects[" ".join(mots[i:i + 8])] = k
    assert suspects, "aucun 8-gramme extrait du corpus personologie"

    mots_source = _norm(SOURCE.read_text(encoding="utf-8", errors="replace"))
    hits = []
    vus = set()
    for i in range(len(mots_source) - 7):
        gr = " ".join(mots_source[i:i + 8])
        if gr in suspects and gr not in vus:
            vus.add(gr)
            hits.append((suspects[gr], gr))
    assert not hits, f"8-grammes copiés de la source personologie : {hits[:8]}"


# ------------------------------------------------------------------ NOMS

def test_noms_ne_reprennent_pas_ceux_du_livre():
    # Noms cités À TITRE D'EXEMPLE dans la carte de concepts (ceux DU LIVRE,
    # donc explicitement interdits) — vérifie qu'aucun n'a été recopié tel quel.
    interdits = ["semaine de l'enfant", "semaine de l'etoile", "semaine du pionnier",
                 "cuspide du pouvoir", "semaine de la manifestation",
                 "semaine du professeur", "cuspide de la renaissance",
                 "cuspide de la magie", "cuspide de la beaute",
                 "cuspide de la prophetie"]
    noms_plats = {" ".join(_norm(e["nom"])) for e in PERIODES_ENTREES.values()}
    fautifs = [n for n in interdits if n in noms_plats]
    assert not fautifs, f"nom du livre repris : {fautifs}"
