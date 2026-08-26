"""L'astrologie chinoise — les FAITS vérifiables, verrouillés.

Ces tests n'ont pas besoin d'oracle : ce sont des faits calendaires et
structurels connus. Ils tiennent lieu de contrat. Une seule chose échappe à la
vérification interne — l'ancre du cycle des jours (quelle date est 甲子) — et
elle est marquée comme telle, à confirmer sur une source.
"""
import datetime as dt

from moteur import chinois as C


# ------------------------------------------------- le pilier de l'année

def test_piliers_annee_contre_references_connues():
    """Cinq années dont le pilier est universellement documenté."""
    cas = [
        (2020, "gēng", "zǐ", "métal", "rat"),      # 庚子
        (1984, "jiǎ", "zǐ", "bois", "rat"),        # 甲子, début du cycle de 60
        (2024, "jiǎ", "chén", "bois", "dragon"),   # 甲辰
        (1972, "rén", "zǐ", "eau", "rat"),         # 壬子
        (2000, "gēng", "chén", "métal", "dragon"),  # 庚辰
    ]
    for annee, tige, branche, element, animal in cas:
        p = C.pilier_annee(annee, 6, 15)   # mi-année : après toute frontière
        assert (p["tige"], p["branche"], p["element"], p["animal"]) == \
            (tige, branche, element, animal), f"{annee} attendu {tige}{branche}"


def test_frontiere_de_debut_d_annee():
    """Avant Li Chun (~4 fév), on appartient à l'animal de l'an d'avant.

    C'est LA subtilité qui piège les natifs de janvier et début février.
    """
    assert C.pilier_annee(2020, 1, 15)["animal"] == "cochon"   # encore 2019
    assert C.pilier_annee(2020, 2, 3)["animal"] == "cochon"    # veille de la frontière
    assert C.pilier_annee(2020, 2, 4)["animal"] == "rat"       # bascule
    assert C.pilier_annee(2020, 6, 1)["animal"] == "rat"


# ------------------------------------------------- les relations

def test_les_douze_animaux_dans_l_ordre():
    assert C.ANIMAUX[0] == "rat" and C.ANIMAUX[6] == "cheval"
    assert len(C.ANIMAUX) == 12 and len(set(C.ANIMAUX)) == 12


def test_les_chocs_sont_les_oppositions():
    """六沖 : chaque branche choque celle à six crans — son opposé exact."""
    assert len(C.CHOCS) == 12                      # 6 paires × 2 sens
    for i in range(12):
        assert sum(1 for a, b in C.CHOCS if a == i) == 1, "un choc et un seul"
    assert (0, 6) in C.CHOCS                        # rat ↔ cheval
    assert (4, 10) in C.CHOCS                       # dragon ↔ chien
    # un choc n'est jamais aussi une harmonie
    assert not (C.CHOCS & C.HARMONIE_PAIRES)


def test_les_trines_et_harmonies():
    """三合 (triangles) et 六合 (paires) — structure classique."""
    # trine de l'eau : singe(8) rat(0) dragon(4)
    for a, b in [(8, 0), (0, 4), (8, 4)]:
        assert (a, b) in C.TRINE_PAIRES
    assert (0, 1) in C.HARMONIE_PAIRES             # rat–buffle
    assert (6, 7) in C.HARMONIE_PAIRES             # cheval–chèvre


def test_priorite_des_relations():
    """Le choc prime sur tout le reste : ordre stable, déterministe."""
    # rat(0) vs cheval(6) : choc
    assert C.relation_branches(0, 6) == "choc"
    # rat(0) vs buffle(1) : harmonie
    assert C.relation_branches(0, 1) == "harmonie"
    # singe(8) vs dragon(4) : trine
    assert C.relation_branches(8, 4) == "trine"
    # même animal : identique
    assert C.relation_branches(3, 3) == "identique"
    # deux branches sans relation : neutre
    assert C.relation_branches(0, 2) == "neutre"


# ------------------------------------------------- le pilier du jour

def test_le_cycle_des_jours_est_continu():
    """La mécanique du cycle : l'ancre vaut 0, +60 jours y revient, la branche
    tourne tous les 12 jours (mais pas la tige, car 12 n'est pas multiple de 10)."""
    assert C.pilier_du_jour(C.ANCRE_JIAZI)["index"] == 0
    assert C.pilier_du_jour(C.ANCRE_JIAZI + dt.timedelta(days=60))["index"] == 0
    j0 = C.pilier_du_jour(C.ANCRE_JIAZI)
    j12 = C.pilier_du_jour(C.ANCRE_JIAZI + dt.timedelta(days=12))
    assert j0["animal"] == j12["animal"] and j0["tige"] != j12["tige"]


def test_piliers_du_jour_contre_le_calendrier_de_joey_yap():
    """L'ANCRE, vérifiée contre une source faisant autorité.

    Cinq dates lues directement dans « The Ten Thousand Year Calendar » de Joey
    Yap (page 2026, année 丙午). Si ces cinq tombent juste, tout le cycle des
    jours est calé — il est ininterrompu depuis des millénaires.
    """
    refs = [
        (dt.date(2026, 2, 17), "rén", "xū"),     # Nouvel An lunaire 2026
        (dt.date(2026, 6, 15), "gēng", "shēn"),
        (dt.date(2026, 7, 14), "jǐ", "chǒu"),
        (dt.date(2026, 7, 17), "rén", "chén"),   # Dragon d'Eau
        (dt.date(2026, 7, 21), "bǐng", "shēn"),
    ]
    for date, tige, branche in refs:
        p = C.pilier_du_jour(date)
        assert (p["tige"], p["branche"]) == (tige, branche), \
            f"{date} attendu {tige}{branche}, obtenu {p['tige']}{p['branche']}"


# ------------------------------------------------- la saillance (le routeur)

def test_saillance_chinoise_bien_formee():
    s = C.saillance_chinoise(1980, 4, 6, dt.date(2026, 7, 17))
    assert 0.0 <= s["score"] <= 1.0
    assert s["relation"] in C.POIDS_RELATION
    assert s["animal_natal"] == "singe"            # 1980 = 庚申, singe de métal
    assert s["cle"] == f"{s['relation']}_singe"


def test_le_corpus_couvre_les_relations_saillantes():
    """Chaque relation qui peut RAVIR le titre a son texte.

    Le neutre ne prend jamais la tête (saillance trop basse), donc il n'a pas
    besoin de corpus ; les cinq autres, si.
    """
    from moteur.corpus import Corpus
    rels = Corpus().lire("chinois_detail", "relations") or {}
    attendues = {"choc", "harmonie", "trine", "nuisance", "identique"}
    assert attendues <= set(rels), f"manque {attendues - set(rels)}"
    for r in attendues:
        assert rels[r].get("miroir") and rels[r].get("geste"), f"{r} incomplet"
