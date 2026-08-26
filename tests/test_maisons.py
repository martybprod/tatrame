"""Le filet golden des maisons.

On alimente notre moteur avec l'ARMC et l'obliquité de l'ORACLE, pas avec les
nôtres : ainsi ce test juge la trigonométrie des maisons SEULE, sans la
mélanger à l'exactitude des éphémérides (testée dans test_ephemerides.py).
Les maisons ne dépendent pas du moteur de positions -> la comparaison est
exacte, et la tolérance peut être serrée.
"""
import json
import pathlib

import pytest

from moteur import maisons

GOLDEN = json.loads(
    (pathlib.Path(__file__).parent / "golden" / "attendu.json").read_text(encoding="utf-8")
)
THEMES = GOLDEN["themes"]
IDS = [t["id"] for t in THEMES]

# Pure trigonométrie sur les mêmes entrées : on doit coller à la précision
# machine. 1e-9° = 3,6 microsecondes d'arc, soit ~10^7 fois plus fin que le
# seuil astrologique (1'). Tout écart au-dessus signale une vraie divergence
# de formule, pas du bruit flottant.
TOL_ANGLE = 1e-9

# Placidus est itératif des deux côtés (nous et swisseph) : les critères
# d'arrêt diffèrent, d'où une tolérance plus lâche — mais toujours 10^4 fois
# sous le seuil astrologique.
TOL_PLACIDUS = 1e-5


def ecart(a, b):
    """Écart angulaire signé le plus court, en degrés."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_angles(theme):
    """ASC et MC — identiques dans tous les systèmes, donc testés à part."""
    ref = theme["maisons"]["porphyry"]        # toujours défini, même aux pôles
    asc, mc = maisons.angles(ref["armc"], theme["obliquite"], theme["lat"])
    assert ecart(asc, ref["asc"]) < TOL_ANGLE, f"ASC: {asc} vs {ref['asc']}"
    assert ecart(mc, ref["mc"]) < TOL_ANGLE, f"MC: {mc} vs {ref['mc']}"


@pytest.mark.parametrize("systeme", ["porphyry", "signe_entier", "egal"])
@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_cuspides_non_iteratives(theme, systeme):
    """Porphyry, signe entier, égal : formules fermées -> précision machine."""
    ref = theme["maisons"][systeme]
    if ref.get("indefini"):
        pytest.skip("l'oracle ne définit pas ce système ici")
    armc = theme["maisons"]["porphyry"]["armc"]
    c, _, _, repli = maisons.cuspides(systeme, armc, theme["obliquite"], theme["lat"])
    assert repli is None
    for i, (nous, oracle) in enumerate(zip(c, ref["cuspides"]), start=1):
        assert ecart(nous, oracle) < TOL_ANGLE, f"cuspide {i}: {nous} vs {oracle}"


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_placidus(theme):
    """Placidus là où il est défini."""
    ref = theme["maisons"]["placidus"]
    if ref.get("indefini"):
        pytest.skip("Placidus indéfini ici — couvert par test_repli_polaire")
    armc = theme["maisons"]["porphyry"]["armc"]
    c, _, _, repli = maisons.cuspides("placidus", armc, theme["obliquite"], theme["lat"])
    assert repli is None, f"repli inattendu : {repli}"
    for i, (nous, oracle) in enumerate(zip(c, ref["cuspides"]), start=1):
        assert ecart(nous, oracle) < TOL_PLACIDUS, f"cuspide {i}: {nous} vs {oracle}"


@pytest.mark.parametrize(
    "theme", [t for t in THEMES if t["maisons"]["placidus"].get("indefini")],
    ids=[t["id"] for t in THEMES if t["maisons"]["placidus"].get("indefini")],
)
def test_repli_polaire(theme):
    """Au-delà du cercle polaire : repli sur Porphyry, ANNONCÉ, sans exception.

    C'est le contrat qui compte le plus ici : là où l'oracle lève une erreur,
    nous devons rendre un thème utilisable ET dire pourquoi il est dégradé.
    """
    armc = theme["maisons"]["porphyry"]["armc"]
    c, asc, mc, repli = maisons.cuspides("placidus", armc, theme["obliquite"], theme["lat"])

    assert repli is not None, "le repli doit être annoncé, jamais silencieux"
    assert len(c) == 12 and all(0.0 <= x < 360.0 for x in c)

    # Deux protections se superposent : le garde-fou de latitude (qui aligne
    # notre comportement sur celui de swisseph, lequel replie au-delà du
    # cercle polaire quel que soit l'ARMC) et la détection du cas
    # circumpolaire dans l'itération. On épingle laquelle doit agir : sans
    # cela, retirer le garde-fou passerait inaperçu (constaté en mutation).
    assert repli == "au-delà du cercle polaire", (
        f"le garde-fou de latitude doit primer ici, or le repli dit : {repli!r}"
    )

    # Le repli doit valoir exactement le Porphyry de l'oracle.
    ref = theme["maisons"]["porphyry"]
    for i, (nous, oracle) in enumerate(zip(c, ref["cuspides"]), start=1):
        assert ecart(nous, oracle) < TOL_ANGLE, f"cuspide {i}: {nous} vs {oracle}"


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_invariants(theme):
    """Invariants structurels vrais quel que soit le système."""
    armc = theme["maisons"]["porphyry"]["armc"]
    for systeme in maisons.SYSTEMES:
        c, asc, mc, _ = maisons.cuspides(systeme, armc, theme["obliquite"], theme["lat"])
        assert len(c) == 12
        assert all(0.0 <= x < 360.0 for x in c), f"{systeme}: cuspide hors [0,360)"
        # Les quadrants sont en opposition stricte dans tous nos systèmes.
        for i in range(6):
            assert ecart(c[i], c[i + 6] + 180.0) < 1e-9, f"{systeme}: maison {i+1} vs {i+7}"


def test_tous_les_pieges_sont_exerces():
    """Garde-fou : personne ne supprime un cas limite par mégarde."""
    from tests.golden.cas import PIEGES_ATTENDUS
    couverts = {t["piege"] for t in THEMES if t["piege"]}
    assert PIEGES_ATTENDUS <= couverts, f"pièges perdus : {PIEGES_ATTENDUS - couverts}"
