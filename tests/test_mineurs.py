"""Garde-fous du calcul de la carte mineure personnelle (56 arcanes).

Pur calcul, aucun corpus (voir tests/test_mineurs_corpus.py pour le texte).
Couleur = élément de la Lune transit. Rang = écart Soleil transit ->
Ascendant natal, sur 14. Le point sensible : vérifier que les 56 clés
restent réellement atteignables pour une personne donnée (voir le piège
documenté en tête de moteur/mineurs.py) — pas juste en théorie.
"""
import pathlib

from moteur import mineurs as M

RACINE = pathlib.Path(__file__).resolve().parents[1]

SUITS = {"batons", "coupes", "epees", "deniers"}

# Les familles ALIGN produites (Feu à ce jour) : un jour de l'élément
# correspondant sert la carte dessinée, plus la carte classique des autres
# éléments — transition douce, jamais un jour sans carte.
SUITS_ALIGN = set(M.SUIT_ALIGN.values())


def _rangs_de(suit):
    """Les rangs d'une famille, en noms Align pour les familles produites."""
    return ([M.RANG_ALIGN.get(r, r) for r in M.RANGS] if suit in SUITS_ALIGN
            else list(M.RANGS))


def _cles_atteignables():
    """Les clés que le moteur sert aujourd'hui : 4 familles × 14 rangs.
    Feu remplace Bâtons (même élément, même fenêtre de Lune)."""
    cles = set()
    for elt in M.ELEMENT_NOM:
        suit = M.SUIT_ALIGN.get(elt, M.SUIT_PAR_ELEMENT[elt])
        for r in M.RANGS:
            cles.add(f"{suit}_{M.RANG_ALIGN.get(r, r) if suit in SUITS_ALIGN else r}")
    return cles

# Vitesses moyennes réelles (°/jour) — suffisantes pour un test de couverture,
# pas pour un calcul de position (voir moteur/ephemerides.py pour le vrai calcul).
V_LUNE, V_SOLEIL = 13.176, 0.9856


def test_toutes_les_cles_sont_bien_formees():
    for lon in (0.0, 47.3, 123.9, 271.5, 359.9):
        c = M.carte_mineure(lon, (lon + 90) % 360, 10.0)
        assert c["suit"] in SUITS | SUITS_ALIGN
        assert c["rang"] in _rangs_de(c["suit"])
        assert c["cle"] == f"{c['suit']}_{c['rang']}"


def test_56_cles_possibles_au_total():
    # Quatre familles servies (Feu remplace Bâtons, même élément) × 14 rangs.
    assert len(_cles_atteignables()) == 56
    assert len(M.RANGS) == 14


def test_les_56_sont_atteignables_pour_une_meme_personne():
    """LE test qui compte : pour un Ascendant FIXE (une personne), en
    laissant Lune et Soleil transiter ~3 ans, les 56 clés doivent toutes
    apparaître. Une version antérieure de ce calcul dérivait le rang de la
    Lune elle-même : pour un Ascendant fixe, ça ne donnait jamais que ~26
    clés à vie (deux fonctions-marches d'une seule variable). Régression
    directe sur ce piège.
    """
    for asc in (0.0, 47.3, 123.9, 271.5, 359.9):
        vues = set()
        lune0, soleil0 = 10.0, 5.0
        for jour in range(3 * 365):
            lune = (lune0 + jour * V_LUNE) % 360.0
            soleil = (soleil0 + jour * V_SOLEIL) % 360.0
            vues.add(M.carte_mineure(lune, soleil, asc)["cle"])
        manque = _cles_atteignables() - vues
        assert not manque, f"asc={asc} : clés jamais atteintes en 3 ans : {manque}"


def test_couleur_independante_de_l_ascendant():
    """La couleur ne doit dépendre QUE de la Lune — pas de l'Ascendant ni
    du Soleil (sinon elle cesserait d'être « partagée » ce jour-là)."""
    for lune in (5.0, 95.0, 185.0, 275.0):
        suits = {M.carte_mineure(lune, soleil, asc)["suit"]
                  for soleil in (0.0, 120.0, 240.0) for asc in (0.0, 90.0, 200.0)}
        assert len(suits) == 1, f"lune={lune} : la couleur varie avec soleil/ascendant"


def test_rang_independant_de_la_lune():
    """Le rang ne doit dépendre QUE de (Soleil - Ascendant) — pas de la
    Lune (sinon les deux axes redeviendraient dépendants, voir le piège)."""
    for soleil, asc in ((10.0, 0.0), (200.0, 340.0), (5.0, 47.3)):
        rangs = {M.carte_mineure(lune, soleil, asc)["rang"]
                 for lune in (0.0, 95.0, 185.0, 275.0, 359.0)}
        assert len(rangs) == 1, f"soleil={soleil} asc={asc} : le rang varie avec la Lune"


def test_pas_de_trou_ni_recouvrement_du_rang():
    # Les 14 bornes de rang tuilent le cercle sans reste, pour un Ascendant
    # donné : juste après chaque frontière, on doit retrouver le rang suivant
    # dans l'ordre, une seule fois chacun, sur un tour complet.
    asc = 30.0
    c0 = M.carte_mineure(0.0, asc + 0.01, asc)
    rangs_en_ordre = [M.carte_mineure(0.0, asc + i * M.LARGEUR_RANG + 0.01, asc)["rang"]
                      for i in range(len(M.RANGS))]
    assert rangs_en_ordre == _rangs_de(c0["suit"])


def test_figures_et_as_bien_marques():
    as_cle = M.carte_mineure(5.0, 5.0, 5.0)  # écart Soleil/Ascendant = 0 -> l'As
    assert as_cle["rang"] == "as"
    assert as_cle["figure"] is False
    for r in ("valet", "cavalier", "reine", "roi"):
        assert r in M.FIGURES
    assert "as" not in M.FIGURES


def test_correspondance_toujours_presente():
    for s in SUITS:
        for r in M.RANGS:
            _, val = M._correspondance(s, r)
            assert val, f"{s}_{r} : correspondance vide"


def test_noms_traditionnels_non_vides_et_uniques():
    noms = [M._nom(s, r) for s in SUITS for r in M.RANGS]
    assert all(noms)
    assert len(set(noms)) == 56


def test_images_des_56_mineurs_presentes():
    # Pas une garantie éditoriale (voir static/cartes/mineurs/README.md),
    # mais un vrai garde-fou : si Align "sait" qu'une image existe, le
    # fichier doit être là, sinon l'UI affichera un dos de carte sans le dire.
    dossier = RACINE / "static" / "cartes" / "mineurs"
    manquants = [f"{s}_{r}.jpg" for s in SUITS for r in M.RANGS
                 if not (dossier / f"{s}_{r}.jpg").exists()]
    assert not manquants, f"images manquantes : {manquants}"
