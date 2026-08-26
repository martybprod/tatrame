"""Le filet golden des éphémérides : Skyfield/DE440s contre l'oracle swisseph.

Deux moteurs indépendants (DE440 numérique vs Moshier analytique) : leur
accord est une vraie preuve, pas une tautologie. Le désaccord résiduel est
le désaccord des MODÈLES, pas une erreur de notre code — d'où des tolérances
exprimées en secondes d'arc et justifiées.

Seuil de référence : l'astrologie travaille à la MINUTE d'arc (1' = 60").
Tout ce qui est nettement sous ce seuil est sans conséquence sur un thème.
"""
import json
import pathlib

import pytest

from moteur.ephemerides import Ephemerides

GOLDEN = json.loads(
    (pathlib.Path(__file__).parent / "golden" / "attendu.json").read_text(encoding="utf-8")
)
THEMES = GOLDEN["themes"]
IDS = [t["id"] for t in THEMES]

SECONDE = 1.0 / 3600.0     # une seconde d'arc, en degrés
MINUTE = 1.0 / 60.0        # une minute d'arc — le seuil astrologique

# Moshier annonce ~1" sur 1900-2100 pour les planètes. On se donne 5" : on
# valide notre chaîne, pas la précision de l'oracle.
TOL_PLANETE = 5 * SECONDE
# La Lune est le cas dur : Moshier y est le moins bon (modèle analytique
# tronqué), et elle bouge 13°/jour. 30" reste 2x sous le seuil astrologique.
TOL_LUNE = 30 * SECONDE
# Nœud moyen : deux polynômes de sources voisines.
TOL_NOEUD = 5 * SECONDE
# Vitesse : nos différences finies contre la dérivée analytique de swisseph.
TOL_VITESSE = 1e-3         # °/jour
TOL_VITESSE_LUNE = 5e-2    # °/jour, sur ~13°/jour = 0,4 %

EPH = Ephemerides()


def ecart(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def instant(theme):
    """L'instant du thème, en UT1.

    Subtilité qui vaut une explication. L'API de swisseph prend un jour julien
    « UT » et le traite comme de l'UT1. Le golden a été généré en lui passant
    un JD construit depuis des composantes UTC — l'oracle a donc lu de l'UT1.
    Skyfield, lui, distingue proprement UTC et UT1 et applique ΔUT1 (jusqu'à
    ±0,9 s, soit ±13" de temps sidéral).

    Pour que ce test juge les MODÈLES et non ce décalage de convention, on
    donne ici le même UT1 aux deux. En production on utilisera `instant()`
    depuis de l'UTC réel : Skyfield y est plus juste que l'oracle.
    """
    return EPH.instant_depuis_jd(theme["jd_ut"])


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_longitudes(theme):
    """Le cœur : les longitudes écliptiques apparentes."""
    t = instant(theme)
    for nom in ("soleil", "lune", "mercure", "venus", "mars",
                "jupiter", "saturne", "uranus", "neptune", "pluton"):
        nous = EPH.position(nom, t)["lon"]
        oracle = theme["corps"][nom]["lon"]
        tol = TOL_LUNE if nom == "lune" else TOL_PLANETE
        d = ecart(nous, oracle)
        assert d < tol, (
            f"{nom}: {nous:.6f}° vs {oracle:.6f}° -> {d * 3600:.2f}\" "
            f"(tolérance {tol * 3600:.0f}\")"
        )


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_noeud_moyen(theme):
    t = instant(theme)
    d = ecart(EPH.noeud_moyen(t), theme["corps"]["noeud_moyen"]["lon"])
    assert d < TOL_NOEUD, f"nœud moyen : écart {d * 3600:.2f}\""


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_obliquite(theme):
    t = instant(theme)
    d = abs(EPH.obliquite(t) - theme["obliquite"])
    assert d < SECONDE, f"obliquité : écart {d * 3600:.3f}\""


# Fenêtre où swisseph applique le modèle de temps sidéral IAU 2006 — le même
# que Skyfield. Diagnostiqué par bissection : l'accord y est EXACT (0,000"),
# et se dégrade brutalement de part et d'autre (7,7" en 1500, 1,9" en 2050,
# 8,6" en 2400). Ces bornes correspondent aux constantes internes de swisseph
# (1er janvier 1850 / 1er janvier 2050), au-delà desquelles il bascule sur une
# formule long terme qui lui est propre. Ce n'est donc pas une erreur de notre
# côté : c'est swisseph qui change de modèle, et sur ce terrain rien ne dit
# qu'il ait raison contre l'IAU.
SIDERAL_IAU2006 = range(1850, 2050)


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_armc(theme):
    """L'ARMC alimente toutes les maisons : une erreur ici les fausse toutes."""
    t = instant(theme)
    d = ecart(EPH.armc(t, theme["lon"]), theme["maisons"]["porphyry"]["armc"])
    if theme["utc"][0] in SIDERAL_IAU2006:
        tol = SECONDE                  # même modèle des deux côtés -> exact
    else:
        # Hors fenêtre, on ne mesure plus que l'écart entre deux modèles.
        # 5" reste 12x sous le seuil astrologique (1') : sans conséquence sur
        # un thème, et seuls les transits lointains sont concernés.
        tol = 5 * SECONDE
    assert d < tol, f"ARMC : écart {d * 3600:.3f}\" (tolérance {tol * 3600:.0f}\")"


def test_accord_sideral_exact_dans_la_fenetre_iau2006():
    """Épingle le diagnostic : dans 1850-2050, l'accord doit rester EXACT.

    Si ce test se met à échouer un jour, c'est que Skyfield a changé de modèle
    de temps sidéral — information précieuse, à ne pas noyer dans une
    tolérance large.
    """
    dans_fenetre = [t for t in THEMES if t["utc"][0] in SIDERAL_IAU2006]
    assert len(dans_fenetre) >= 15, "la fenêtre doit rester bien couverte"
    for theme in dans_fenetre:
        d = ecart(EPH.armc(instant(theme), theme["lon"]),
                  theme["maisons"]["porphyry"]["armc"])
        assert d < 0.01 * SECONDE, f"{theme['id']}: {d * 3600:.4f}\""


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_vitesses(theme):
    """Nos différences finies contre la dérivée analytique de l'oracle."""
    t = instant(theme)
    for nom in CORPS_TESTES:
        nous = EPH.position(nom, t)["vitesse_lon"]
        oracle = theme["corps"][nom]["vitesse_lon"]
        tol = TOL_VITESSE_LUNE if nom == "lune" else TOL_VITESSE
        assert abs(nous - oracle) < tol, (
            f"{nom}: vitesse {nous:.6f} vs {oracle:.6f} °/j"
        )


CORPS_TESTES = ("soleil", "lune", "mercure", "venus", "mars",
                "jupiter", "saturne", "uranus", "neptune", "pluton")


@pytest.mark.parametrize("theme", THEMES, ids=IDS)
def test_retrogradation(theme):
    """Le SIGNE de la vitesse est ce qui décide « rétrograde » dans l'app.

    Près d'une station la vitesse frôle 0 : on n'exige l'accord de signe que
    si l'oracle est franchement loin de zéro, sinon on testerait du bruit.
    """
    t = instant(theme)
    for nom in CORPS_TESTES:
        oracle = theme["corps"][nom]
        if abs(oracle["vitesse_lon"]) < TOL_VITESSE * 10:
            continue                       # station : signe non significatif
        nous = EPH.position(nom, t)
        assert nous["retrograde"] == oracle["retrograde"], (
            f"{nom}: rétrograde={nous['retrograde']} vs {oracle['retrograde']} "
            f"(vitesse {nous['vitesse_lon']:.6f} vs {oracle['vitesse_lon']:.6f})"
        )


def test_retrogradations_reellement_couvertes():
    """Le filet ne prouve rien s'il ne contient aucun cas rétrograde."""
    retro = [
        (t["id"], nom)
        for t in THEMES
        for nom in CORPS_TESTES
        if t["corps"][nom]["retrograde"]
    ]
    assert len(retro) >= 10, f"trop peu de cas rétrogrades : {retro}"


def test_empreinte_ephemeride_verifiee():
    """Le refus de démarrer sur un fichier inattendu est un contrat, pas un vœu."""
    import moteur.ephemerides as m
    vrai = m.SHA256_ATTENDU
    try:
        m.SHA256_ATTENDU = "0" * 64
        with pytest.raises(RuntimeError, match="Empreinte"):
            Ephemerides()
    finally:
        m.SHA256_ATTENDU = vrai
