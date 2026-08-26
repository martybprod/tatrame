"""Garde-fous du corpus des 17 lois (Millman, distillées) — data/corpus/lois.json.

Sur le patron de tests/test_periodes_corpus.py : ici on teste le CORPUS écrit
à la main (les lois comme leviers du jour), pas un calcul. `_routage` associe
à chaque base de Cap (1-9) 2-3 lois prioritaires ; le câblage moteur (Cap →
loi(s) prioritaires) est une suite, hors scope ici (voir le brief Millman).
"""
import json
import pathlib
import re
import unicodedata

import pytest

RACINE = pathlib.Path(__file__).resolve().parents[1]
LOIS_JSON = json.loads((RACINE / "data" / "corpus" / "lois.json").read_text(encoding="utf-8"))
SOURCE = RACINE / "_distillation" / "sources" / "votre_chemin_de_vie_dan_millman.txt"

LOIS_SLUGS = {
    "flexibilite", "choix", "responsabilite", "equilibre", "methode",
    "comportements", "discipline", "perfection", "moment_present",
    "non_jugement", "foi", "attentes", "honnetete", "volonte_superieure",
    "intuition", "action", "cycles",
}

LOIS_ENTREES = {k: v for k, v in LOIS_JSON.items() if not k.startswith("_")}
ROUTAGE = LOIS_JSON.get("_routage", {})


def _norm(txt):
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).split()


# ------------------------------------------------------------- COUVERTURE

def test_les_17_lois_sont_presentes():
    manque = LOIS_SLUGS - LOIS_ENTREES.keys()
    en_trop = LOIS_ENTREES.keys() - LOIS_SLUGS
    assert not manque, f"lois manquantes : {manque}"
    assert not en_trop, f"clés inattendues (hors les 17 lois) : {en_trop}"


def test_chaque_loi_a_ses_quatre_champs():
    incomplets = [k for k, e in LOIS_ENTREES.items()
                  if not e.get("nom", "").strip()
                  or not e.get("en_un_mot", "").strip()
                  or not e.get("le_principe", "").strip()
                  or not e.get("le_pas", "").strip()]
    assert not incomplets, f"champs manquants : {incomplets}"


def test_noms_de_lois_uniques():
    noms = [e["nom"] for e in LOIS_ENTREES.values()]
    doublons = {n for n in noms if noms.count(n) > 1}
    assert not doublons, f"noms de loi dupliqués : {doublons}"


# --------------------------------------------------------------- LONGUEURS

def test_longueur_le_principe():
    fautes = {k: len(e["le_principe"].split()) for k, e in LOIS_ENTREES.items()}
    fautes = {k: n for k, n in fautes.items() if n < 50 or n > 90}
    assert not fautes, f"le_principe hors bornes (50-90 mots) : {fautes}"


def test_longueur_le_pas():
    fautes = {k: len(e["le_pas"].split()) for k, e in LOIS_ENTREES.items()}
    fautes = {k: n for k, n in fautes.items() if n < 25 or n > 55}
    assert not fautes, f"le_pas hors bornes (25-55 mots) : {fautes}"


# ------------------------------------------------------------------ VOIX

def test_pas_de_prediction_ni_prescription():
    motif = r"\btu (vas |)(rencontrer|recevr|trouver|connaîtr|vivr)a?s?\b|\bil faut que tu\b|\btu devras\b|\btu es quelqu'un\b|\bton destin\b|\bc'est écrit\b"
    fautifs = []
    for k, e in LOIS_ENTREES.items():
        for champ in ("nom", "en_un_mot", "le_principe", "le_pas"):
            txt = e.get(champ, "")
            if txt and re.search(motif, txt, re.I):
                fautifs.append((k, champ))
    assert not fautifs, f"prédiction/prescription/fatalisme détecté : {fautifs}"


# ------------------------------------------------------------ ANTI-PLAGIAT

def test_aucun_8gramme_dans_la_source_millman():
    if not SOURCE.exists():
        pytest.skip("source Millman absente — anti-plagiat non exécuté")

    suspects = {}
    for k, e in LOIS_ENTREES.items():
        texte = " ".join(e.get(c, "") for c in ("nom", "en_un_mot", "le_principe", "le_pas"))
        mots = _norm(texte)
        for i in range(len(mots) - 7):
            suspects[" ".join(mots[i:i + 8])] = k
    assert suspects, "aucun 8-gramme extrait du corpus des lois"

    mots_source = _norm(SOURCE.read_text(encoding="utf-8", errors="replace"))
    hits = []
    vus = set()
    for i in range(len(mots_source) - 7):
        gr = " ".join(mots_source[i:i + 8])
        if gr in suspects and gr not in vus:
            vus.add(gr)
            hits.append((suspects[gr], gr))
    assert not hits, f"8-grammes copiés de la source Millman : {hits[:8]}"


# ---------------------------------------------------------------- ROUTAGE

def test_le_routage_couvre_les_neuf_bases():
    attendu = {str(i) for i in range(1, 10)}
    assert set(ROUTAGE.keys()) == attendu, (
        f"le routage doit couvrir exactement les bases 1-9 : {set(ROUTAGE.keys())}"
    )


def test_le_routage_ne_cite_que_des_lois_existantes():
    fautifs = {}
    for base, cites in ROUTAGE.items():
        inconnues = set(cites) - LOIS_ENTREES.keys()
        if inconnues:
            fautifs[base] = inconnues
    assert not fautifs, f"le routage cite des lois absentes de lois.json : {fautifs}"


def test_chaque_base_a_deux_ou_trois_lois():
    fautes = {base: len(cites) for base, cites in ROUTAGE.items() if not (2 <= len(cites) <= 3)}
    assert not fautes, f"nombre de lois hors 2-3 par base : {fautes}"
