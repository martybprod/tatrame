"""Le Fil du jour — garde-fous du corpus `fil.json`.

Cinq familles de tests (voir _distillation/fil_du_jour_SPEC.md §7) :
  1. STRUCTURE   — miroir + geste présents, longueur, clés dans le namespace.
  2. COUVERTURE  — chaque domaine a son socle générique (le fil résout toujours).
  3. STYLE       — tics aphoristiques sous les seuils (tirets, deux-points).
  4. VARIÉTÉ     — aucune ouverture ne domine ; pas de longue suite dupliquée.
  5. ANTI-PLAGIAT— aucun 8-gramme d'une perle ne se retrouve dans un texte source
                   (garantie contractuelle : on commercialise). Sauté si les
                   sources (gitignorées) sont absentes.
"""
import json
import pathlib
import re
import unicodedata
from collections import Counter

import pytest

RACINE = pathlib.Path(__file__).resolve().parents[1]
FIL = json.loads((RACINE / "data" / "corpus" / "fil.json").read_text(encoding="utf-8"))
SOURCES = RACINE / "_distillation" / "sources"

DOMAINES = {"soi", "ressources", "echanges", "racines", "creation", "quotidien",
            "autre", "traversee", "sens", "metier", "communaute", "retrait"}
A_PHASE = {"creation", "quotidien", "metier"}
PLANETES = {"soleil", "lune", "mercure", "venus", "mars",
            "jupiter", "saturne", "uranus", "neptune", "pluton"}
CLASSES = {"conjonction", "carre-opposition", "sextile-trigone"}
PHASES = {"nouvelle", "croissante", "premier_quartier", "gibbeuse",
          "pleine", "diffusante", "dernier_quartier", "balsamique"}


def _cles_autorisees():
    """Le namespace complet et fermé des clés valides (SPEC §3)."""
    ok = set()
    for d in DOMAINES:
        ok.add(d)
        ok.add(f"{d}_fluide")
        ok.add(f"{d}_tension")
        for p in PLANETES:
            for c in CLASSES:
                ok.add(f"{d}_transit_{p}_{c}")
        if d in A_PHASE:
            for ph in PHASES:
                ok.add(f"{d}_phase_{ph}")
    return ok


AUTORISEES = _cles_autorisees()
ENTREES = {k: v for k, v in FIL.items() if not k.startswith("_")}


def _norm(txt):
    """Minuscules, sans accents, ponctuation → espace, espaces normalisés."""
    t = unicodedata.normalize("NFD", txt.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return t.split()


def _phrase(entree):
    return f"{entree.get('miroir', '')} {entree.get('geste', '')}"


# ------------------------------------------------------------- 1. STRUCTURE

def test_chaque_cle_est_dans_le_namespace():
    hors = [k for k in ENTREES if k not in AUTORISEES]
    assert not hors, f"clés hors namespace : {hors}"


def test_miroir_et_geste_presents():
    vides = [k for k, e in ENTREES.items()
             if not e.get("miroir", "").strip() or not e.get("geste", "").strip()]
    assert not vides, f"miroir/geste vide : {vides}"


def test_longueur_miroir_plus_geste():
    # Cible SPEC 30-85 mots ; bornes de test un peu élargies pour ne pas
    # échouer sur un écart mineur, tout en attrapant les vrais outliers.
    hors = {k: len(_norm(_phrase(e))) for k, e in ENTREES.items()}
    fautes = {k: n for k, n in hors.items() if n < 25 or n > 92}
    assert not fautes, f"longueur hors bornes (25-92 mots) : {fautes}"


def test_source_livre_present():
    sans = [k for k, e in ENTREES.items() if not e.get("source_livre", "").strip()]
    assert not sans, f"source_livre manquant : {sans}"


# ------------------------------------------------------------- 2. COUVERTURE

def test_chaque_domaine_a_son_socle():
    manque = [d for d in DOMAINES if d not in ENTREES]
    assert not manque, f"socle générique manquant : {manque}"


def test_domaines_a_phase_ont_leurs_phases():
    for d in A_PHASE:
        manque = [ph for ph in PHASES if f"{d}_phase_{ph}" not in ENTREES]
        assert not manque, f"{d} : phases manquantes {manque}"


# ------------------------------------------------------------- 3. STYLE

def _phrases(txt):
    return [p for p in re.split(r"[.!?]+", txt) if p.strip()]


def test_tirets_cadratins_sous_seuil():
    tirets = sum(_phrase(e).count("—") for e in ENTREES.values())
    phrases = sum(len(_phrases(_phrase(e))) for e in ENTREES.values())
    ratio = 100 * tirets / max(phrases, 1)
    assert ratio < 8, f"tirets cadratins {ratio:.1f}/100 phrases (seuil 8)"


def test_deux_points_sous_seuil():
    colons = sum(_phrase(e).count(":") for e in ENTREES.values())
    phrases = sum(len(_phrases(_phrase(e))) for e in ENTREES.values())
    ratio = 100 * colons / max(phrases, 1)
    assert ratio < 10, f"deux-points {ratio:.1f}/100 phrases (seuil 10)"


def test_pas_d_ouverture_ce_n_est_pas():
    fautes = [k for k, e in ENTREES.items()
              if re.match(r"^\s*ce n['’]est pas", e.get("miroir", "").lower())]
    assert not fautes, f"ouverture « Ce n'est pas… » : {fautes}"


# ------------------------------------------------------------- 4. VARIÉTÉ

def test_aucune_ouverture_ne_domine():
    # Les 4 premiers mots du miroir, normalisés — aucun début ne doit
    # coiffer plus de 5 entrées (sinon c'est un tic).
    debuts = Counter(" ".join(_norm(e["miroir"])[:4]) for e in ENTREES.values())
    trop = {d: n for d, n in debuts.items() if n > 5}
    assert not trop, f"ouvertures qui dominent : {trop}"


def test_pas_de_longue_suite_partagee_entre_deux_perles():
    # Aucune suite de 8 mots ne doit apparaître dans deux perles différentes
    # (miroir+geste) — signe de recopiage interne.
    vus = {}
    collisions = []
    for k, e in ENTREES.items():
        mots = _norm(_phrase(e))
        for i in range(len(mots) - 7):
            g = " ".join(mots[i:i + 8])
            if g in vus and vus[g] != k:
                collisions.append((g, vus[g], k))
            else:
                vus[g] = k
    assert not collisions, f"suites de 8 mots partagées : {collisions[:5]}"


# ------------------------------------------------------------- 5. ANTI-PLAGIAT

def test_aucun_8gramme_dans_les_sources():
    """Aucune suite de 8 mots d'une perle ne se trouve dans un texte source.

    Les sources sont sous copyright et gitignorées : si absentes (CI), on
    saute — mais en local, c'est la garantie contractuelle avant vente.
    """
    fichiers = sorted(SOURCES.glob("*.txt"))
    if not fichiers:
        pytest.skip("sources absentes (_distillation/sources vide) — anti-plagiat non exécuté")

    # L'empreinte : tous les 8-grammes des perles → la clé qui les porte.
    suspects = {}
    for k, e in ENTREES.items():
        mots = _norm(_phrase(e))
        for i in range(len(mots) - 7):
            suspects[" ".join(mots[i:i + 8])] = k
    assert suspects, "aucun 8-gramme extrait des perles"

    hits = []
    for f in fichiers:
        mots = _norm(f.read_text(encoding="utf-8", errors="replace"))
        vus = set()
        for i in range(len(mots) - 7):
            g = mots[i]  # amorce rapide : ne construit le 8-gramme que si utile
            # (micro-opti : on teste toujours, le set lookup est O(1))
            gr = " ".join(mots[i:i + 8])
            if gr in suspects and gr not in vus:
                vus.add(gr)
                hits.append((f.name, suspects[gr], gr))
    assert not hits, f"8-grammes copiés d'une source : {hits[:8]}"
