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

def _cles_attendues():
    """Les clés réellement servies par le moteur : 4 familles × 14 rangs.
    Une famille Align ne remplace sa couleur classique que pour les rangs
    DÉJÀ LIVRÉS (M.ALIGN_RANGS) ; ailleurs, la carte classique reste servie."""
    cles = set()
    # Les quatre couleurs classiques restent au corpus (transition douce : un
    # rang non encore dessiné dans une famille Align sert sa carte classique).
    for suit in M.SUIT_PAR_ELEMENT.values():
        for r in M.RANGS:
            cles.add(f"{suit}_{r}")
    # Plus les rangs déjà livrés de chaque famille Align.
    for suit, rangs in M.ALIGN_RANGS.items():
        for ra in rangs:
            cles.add(f"{suit}_{ra}")
    return cles


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
    manque = _cles_attendues() - entrees.keys()
    assert not manque, f"mineurs sans entrée corpus : {manque}"


def test_aucune_cle_hors_namespace():
    entrees = _entrees()
    hors = entrees.keys() - _cles_attendues()
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


# ------------------------------------------------ SYMBOLES (famille Feu)
# Le filet des symboles, comme SYMBOLES_REQUIS pour les majeurs : inventaire
# fait en regardant chaque image validée ; le texte « comprendre » doit nommer
# tous les symboles de sa carte, l'invitation en nomme au moins trois.
SYMBOLES_REQUIS_MINEURS = {
    "feu_as": ["source", "eau", "lumière", "arbres", "pierres", "fougères", "fleurs"],
    "feu_2": ["pissenlits", "graines", "vent", "pré", "collines", "ciel"],
    "feu_3": ["fille", "main", "tronc", "arbre", "yeux", "forêt"],
    "feu_4": ["lucioles", "fleuve de lumière", "rivière", "nuit", "roseaux", "étoiles"],
    "feu_5": ["ballon", "cordes", "personnes", "prairie fleurie", "soleil couchant"],
    "feu_6": ["feu", "guirlandes", "mât", "danse", "village", "étoiles filantes"],
    "feu_7": ["fil", "précipice", "pile", "livres", "pont", "bras"],
    "feu_8": ["marcheur", "pieds nus", "chemin", "blés", "village", "montagnes"],
    "feu_9": ["machine", "rouages", "sablier", "manivelle", "porte", "mer"],
    "feu_10": ["spirale de feu", "cœur", "femme", "blé"],
    "feu_page": ["fille", "château de sable", "vague", "papillons", "plage"],
    "feu_chevalier": ["bloc de pierre", "lunettes", "lumière blanche", "machine de cuivre", "nuit", "étoiles"],
    "feu_reine": ["reine", "feu", "robe", "jardins", "terrasses", "montagnes"],
    "feu_roi": ["feu", "branches", "pierres", "personnes", "nuit"],
}


def _couvre(texte, symbole):
    mots = set(_norm(symbole))
    plats = set(_norm(texte))
    return mots <= plats


def test_comprendre_nomme_tous_les_symboles():
    entrees = _entrees()
    absents = [k for k, sym in SYMBOLES_REQUIS_MINEURS.items()
               if k in entrees
               and [s for s in sym if not _couvre(entrees[k].get("comprendre", ""), s)]]
    assert not absents, f"« comprendre » ne nomme pas tous les symboles : "                         f"{[(k, SYMBOLES_REQUIS_MINEURS[k]) for k in absents]}"


def test_invitation_n_est_pas_une_scene():
    """Convention du 2026-10-17 (option A) : l'invitation d'une mineure est
    une INVITATION DU JOUR — un geste adressé au lecteur, jamais une
    description de la scène. La scène vit dans le premier paragraphe du
    « comprendre » seul. Avant la correction, l'invitation reprenait 56 %
    (Feu) à 71 % (Air) des mots du 1er ¶, avec 21 suites de ≥ 5 mots
    partagées ; les majeures, elles, sont à ~26 % et 0 suite.
    Ce test garde la ligne au niveau des majeures."""
    entrees = _entrees()
    fautifs = []
    for k, v in entrees.items():
        inv, comp = v.get("invitation", ""), v.get("comprendre", "")
        if not inv or not comp:
            continue  # les entrées à invitation seule (textes traditionnels) n'ont rien à dupliquer
        a = [w for w in _norm(inv) if len(w) > 2]
        b = _norm(comp.split("\n\n")[0])
        if not a or not b:
            continue
        part = sum(1 for w in a if w in set(b)) / len(a)
        sb = {" ".join(b[i:i + 5]) for i in range(len(b) - 4)}
        suite = any(" ".join(a[i:i + 5]) in sb for i in range(len(a) - 4))
        if part > 0.45 or suite:
            fautifs.append((k, round(100 * part), suite))
    assert not fautifs, (
        "invitation qui re-décrit la scène (à réécrire en invitation du jour) : "
        f"{fautifs} — la scène appartient au 1er ¶ du « comprendre » seul")


def test_comprendre_dans_la_fenetre_portrait():
    entrees = _entrees()
    hors = {k: len(entrees[k].get("comprendre", "").split())
            for k in SYMBOLES_REQUIS_MINEURS
            if k in entrees and not 120 <= len(entrees[k].get("comprendre", "").split()) <= 180}
    assert not hors, f"« comprendre » hors fenêtre 120-180 mots : {hors}"


def test_nom_align_present_pour_la_famille_produite():
    entrees = _entrees()
    vides = [k for k in SYMBOLES_REQUIS_MINEURS
             if k in entrees and not entrees[k].get("nom", "").strip()]
    assert not vides, f"nom Align manquant : {vides}"


# ------------------------------------------------ FORMES (banque, 2026-10-21)
# Charte, section « La banque de formes » : une invitation de mineure prend UNE
# forme (météo, miroir, offre, question, permission, image, geste déguisé), et
# les recettes qui ont saturé (« une seule chose », la durée imposée, « même
# petite », l'ancrage « Aujourd'hui ») reçoivent des plafonds.
#
# Le défaut cherché ici n'est PAS lexical (les 8-grammes ci-dessus l'ont) :
# c'est la FORMULE partagée, invisible test par test et criante en série.
# Les plafonds s'appliquent par famille, le jour où elle entre dans
# FAMILLES_A_LA_BANQUE — un test rouge en permanence finit ignoré, donc la
# vis se serre à chaque rétroportage au lieu de bloquer avant le travail.

BANQUE_DE_FORMES = frozenset({"météo", "miroir", "offre", "question",
                              "permission", "image", "geste déguisé"})

# Familles passées à la banque de formes (leurs invitations réécrites).
# Terre y entre au rétroportage, Feu/Eau/Air et les couleurs classiques ensuite.
FAMILLES_A_LA_BANQUE = frozenset()

PLAFOND_ANCRAGE = 0.30   # « Aujourd'hui » en ouverture
PLAFOND_RECETTE = 0.08   # chaque recette, par famille (~1 carte / 14)

# Les recettes qui ont saturé, listées une à une (leçon test_style : une liste
# explicite est moins élégante et beaucoup plus juste qu'une détection vague).
RECETTES_SURVEILLEES = {
    "une seule chose": re.compile(r"une (seule|petite) chose\b|une seule tâche\b|un seul[ee]?\b(?= .*à (faire|la fois))", re.I),
    "durée imposée": re.compile(r"\b(dix|cinq|trois|quinze|trente|deux|une)\s+minutes?\b|\b\d+\s+minutes?\b|\brespirations?\b", re.I),
    "même petite": re.compile(r"\bmême (petite?|bref|courte?|minuscule|infime)\b", re.I),
}


def _familles_de(cle):
    return cle.rsplit("_", 1)[0]


def test_familles_a_la_banque_respectent_les_plafonds():
    """Les invitations des familles réécrites tiennent les plafonds de la banque.
    « Aujourd'hui » en COURS de texte reste libre : seul l'ancrage systématique
    fatigue (85 cartes / 100 à la mesure du 2026-10-21)."""
    if not FAMILLES_A_LA_BANQUE:
        pytest.skip("aucune famille à la banque de formes encore (rétroportage à venir)")
    entrees = {k: e for k, e in _entrees().items()
               if _familles_de(k) in FAMILLES_A_LA_BANQUE}
    assert entrees, "familles à la banque mais aucune entrée dans le corpus"
    n = len(entrees)
    ancrage = [k for k, e in entrees.items()
               if re.match(r"^aujourd['’]hui\b", e["invitation"], re.I)]
    assert len(ancrage) / n <= PLAFOND_ANCRAGE, (
        f"« Aujourd'hui » en ouverture : {len(ancrage)}/{n} "
        f"(plafond {PLAFOND_ANCRAGE:.0%}) : {ancrage}")
    for nom, motif in RECETTES_SURVEILLEES.items():
        fautifs = [k for k, e in entrees.items() if motif.search(e["invitation"])]
        assert len(fautifs) / n <= PLAFOND_RECETTE, (
            f"recette « {nom} » : {len(fautifs)}/{n} (plafond {PLAFOND_RECETTE:.0%}) : {fautifs}")


# Le pilote Terre : les invitations des rangs non encore livrés (pas d'image),
# rédigées d'après le sens des cartes, testées ICI avant toute migration dans
# mineurs.json. À la livraison d'un rang : vérifier contre l'image validée
# (RELECTURE §1), écrire « comprendre », migrer, ajouter le rang à ALIGN_RANGS.
CORPUS_TRAVAIL_TERRE = RACINE.parent / "_distillation" / "corpus_mineurs_terre.json"
PLAFOND_FORME_PILOTE = 3      # une même forme : ≤ 3 cartes
PLAFOND_ANCRAGE_PILOTE = 2    # « Aujourd'hui » en ouverture : ≤ 2 cartes


def test_le_pilote_terre_respecte_la_banque_de_formes():
    from collections import Counter
    if not CORPUS_TRAVAIL_TERRE.exists():
        pytest.skip("_distillation/corpus_mineurs_terre.json absent — pilote pas encore rédigé")
    travail = json.loads(CORPUS_TRAVAIL_TERRE.read_text(encoding="utf-8"))
    entrees = {k: v for k, v in travail.items() if not k.startswith("_")}
    assert entrees, "corpus de travail Terre vide"

    hors_banque = {k: v.get("forme") for k, v in entrees.items()
                   if v.get("forme") not in BANQUE_DE_FORMES}
    assert not hors_banque, f"forme hors banque (charte) : {hors_banque}"

    longueurs = {k: len(v["invitation"].split()) for k, v in entrees.items()}
    fautes = {k: n for k, n in longueurs.items() if n < 30 or n > 55}
    assert not fautes, f"invitation hors bornes (30-55 mots, charte « jour ») : {fautes}"

    ancrage = [k for k, v in entrees.items()
               if re.match(r"^aujourd['’]hui\b", v["invitation"], re.I)]
    assert len(ancrage) <= PLAFOND_ANCRAGE_PILOTE, (
        f"« Aujourd'hui » en ouverture : {len(ancrage)}/{len(entrees)} "
        f"(plafond {PLAFOND_ANCRAGE_PILOTE}) : {ancrage}")

    for nom, motif in RECETTES_SURVEILLEES.items():
        fautifs = [k for k, v in entrees.items() if motif.search(v["invitation"])]
        assert len(fautifs) <= 1, (
            f"recette « {nom} » dans le pilote : {fautifs} (≤ 1 attendu)")

    formes = Counter(v["forme"] for v in entrees.values())
    trop = {f: n for f, n in formes.items() if n > PLAFOND_FORME_PILOTE}
    assert not trop, f"une même forme domine le pilote : {trop}"

    # rien de déjà écrit ne revient : ni entre les rangs du pilote…
    vus, collisions = {}, []
    for k, v in entrees.items():
        mots = _norm(v["invitation"])
        for i in range(len(mots) - 4):
            g = " ".join(mots[i:i + 5])
            if g in vus and vus[g] != k:
                collisions.append((g, vus[g], k))
            else:
                vus[g] = k
    assert not collisions, f"5-grammes partagés dans le pilote : {collisions[:5]}"
    # …ni avec les invitations déjà servies (as, 2, et le reste du corpus)
    existants = [(" ".join(_norm(e["invitation"])), k) for k, e in _entrees().items()]
    for k, v in entrees.items():
        mots = _norm(v["invitation"])
        for i in range(len(mots) - 7):
            g = " ".join(mots[i:i + 8])
            pour, ek = next(((t, k2) for t, k2 in existants if g in t), (None, None))
            assert pour is None, f"8-gramme déjà servi ({ek}) : {g!r} (pilote {k})"
