"""Garde-fous du calcul des 48 sous-périodes + de l'axe des nœuds (personologie).

Pur calcul, aucun corpus. On vérifie que le découpage tuile le cercle sans
trou ni recouvrement, que les cas connus tombent juste, et que l'axe des
nœuds est bien opposé à 180°.
"""
from moteur import periodes as P
from moteur import noeuds as N


def test_quarante_huit_periodes():
    assert len(P.PERIODES) == 48
    assert sum(1 for p in P.PERIODES if p["type"] == "cuspe") == 12
    assert sum(1 for p in P.PERIODES if p["type"] == "semaine") == 36


def test_cles_uniques():
    cles = [p["cle"] for p in P.PERIODES]
    assert len(set(cles)) == 48, "clés de période en double"


def test_largeurs_couvrent_360():
    total = sum(p["largeur"] for p in P.PERIODES)
    assert abs(total - 360.0) < 1e-9, total


def test_pas_de_trou_ni_recouvrement():
    # Chaque période commence là où la précédente finit (cercle, wrap compris).
    ordonnees = sorted(P.PERIODES, key=lambda p: p["debut"])
    for a, b in zip(ordonnees, ordonnees[1:]):
        assert abs(a["fin"] - b["debut"]) < 1e-9, (a["cle"], b["cle"])
    # La dernière se referme sur la première (modulo 360).
    assert abs(ordonnees[-1]["fin"] % 360.0 - ordonnees[0]["debut"]) < 1e-9


def test_cas_connus():
    # 0° = milieu de la cuspide Poissons-Bélier (frontière de signe).
    assert P.periode_de(0.0)["cle"] == "cuspe_poissons_belier"
    assert P.periode_de(0.0)["type"] == "cuspe"
    # 15° = plein milieu du Bélier → 2e semaine.
    assert P.periode_de(15.0)["cle"] == "belier_2"
    # 30° = frontière Bélier-Taureau → cuspide.
    assert P.periode_de(30.0)["cle"] == "cuspe_belier_taureau"
    # Juste après la cuspide d'entrée du Taureau → 1re semaine du Taureau.
    assert P.periode_de(34.0)["cle"] == "taureau_1"
    # Fin du Taureau, avant la cuspide de sortie → 3e semaine.
    assert P.periode_de(56.0)["cle"] == "taureau_3"


def test_chaque_periode_est_atteignable():
    # Le centre de chaque période retombe bien sur elle.
    for p in P.PERIODES:
        centre = (p["debut"] + p["largeur"] / 2.0) % 360.0
        assert P.periode_de(centre)["cle"] == p["cle"], p["cle"]


def test_rejouable():
    for lon in (0.0, 47.3, 123.9, 271.5, 359.9):
        assert P.periode_de(lon)["cle"] == P.periode_de(lon)["cle"]


def test_axe_des_noeuds_oppose():
    faux_theme = {"corps": {"noeud_moyen": {"lon": 42.0}}}
    a = N.axe(faux_theme)
    ecart = (a["nord"]["lon"] - a["sud"]["lon"]) % 360.0
    assert abs(ecart - 180.0) < 1e-9
    assert a["nord"]["lon"] == 42.0          # nord = ascendant = destination
    assert "__" in a["cle"]                  # la voie = paire sud__nord
