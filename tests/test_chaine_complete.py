"""La CHAÎNE entière contre l'oracle, pas seulement ses pièces.

Les autres tests isolent chaque étage (maisons à ARMC donné, éphémérides à
UT1 donné). Celui-ci part de ce que l'utilisateur saisit — date, heure, lieu,
fuseau — et compare le thème final à ce que swisseph produirait sur la même
saisie. C'est le test qui attraperait un mauvais branchement entre étages :
un fuseau appliqué à l'envers, une longitude de signe inversé, un UTC décalé.

Il utilise l'oracle, donc il est dev-only comme les autres.
"""
from datetime import timezone

import pytest
import swisseph as swe

from moteur.temps import vers_utc
from moteur.theme import Moteur, maison_de, signe_de

MOTEUR = Moteur()

# (libellé, an, mois, jour, h, min, lat, lon, fuseau)
SAISIES = [
    ("Trois-Pistoles, été 1975", 1975, 7, 16, 14, 30, 48.1266, -69.1697, "America/Toronto"),
    ("Montréal, hiver 1975 (le piège US/Canada)", 1975, 3, 15, 10, 0, 45.5088, -73.5878, "America/Toronto"),
    ("Paris, 1980", 1980, 5, 20, 9, 15, 48.8566, 2.3522, "Europe/Paris"),
    ("Sydney, hémisphère sud", 1993, 2, 12, 9, 45, -33.8688, 151.2093, "Australia/Sydney"),
    ("Quito, équateur", 1985, 9, 23, 10, 30, -0.1807, -78.4678, "America/Guayaquil"),
    ("Tromsø, au-delà du cercle polaire", 1990, 12, 21, 12, 0, 69.6492, 18.9553, "Europe/Oslo"),
    ("Suva, près de l'antiméridien", 2010, 4, 6, 10, 10, -18.1416, 178.4419, "Pacific/Fiji"),
    ("Montréal, aujourd'hui", 2024, 6, 15, 14, 0, 45.5088, -73.5878, "America/Toronto"),
]
IDS = [s[0] for s in SAISIES]

SECONDE = 1.0 / 3600.0
TOL_CORPS = 30 * SECONDE     # borné par la Lune / Moshier (cf. test_ephemerides)

# Les angles tolèrent plus ici que dans test_maisons.py (où l'accord est
# EXACT à 1e-9°), et c'est voulu : ce test-ci part de l'heure civile, donc il
# inclut la conversion des échelles de temps. L'API de swisseph prend un jour
# julien « UT » qu'elle traite comme de l'UT1, alors que nous lui donnons de
# l'UTC ; Skyfield, lui, distingue les deux et applique ΔUT1 (jusqu'à ±0,9 s,
# soit ±13,5" de temps sidéral, qui se propagent à l'ASC et aux cuspides).
# Autrement dit ce résidu n'est pas notre erreur : c'est SKYFIELD qui est
# juste et l'oracle qui simplifie. Mesuré ≤ 11" sur ce jeu ; 20" reste 3x
# sous le seuil astrologique (1'). Les corps, eux, ne bougent quasi pas
# (≤ 0,75") car ils dépendent de TT, pas de la rotation terrestre.
TOL_ANGLE = 20 * SECONDE

CORPS_SWE = {
    "soleil": swe.SUN, "lune": swe.MOON, "mercure": swe.MERCURY,
    "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
    "saturne": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
    "pluton": swe.PLUTO,
}


def ecart(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


@pytest.mark.parametrize("saisie", SAISIES, ids=IDS)
def test_chaine_complete(saisie):
    _, an, mo, jo, hh, mi, lat, lon, tz = saisie
    theme = MOTEUR.theme_natal(an, mo, jo, hh, mi, lat, lon, tz)

    # L'oracle repart de la MÊME saisie, avec sa propre conversion de fuseau.
    utc, _ = vers_utc(an, mo, jo, hh, mi, tz)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)

    for nom, ip in CORPS_SWE.items():
        xx, _ = swe.calc_ut(jd, ip, swe.FLG_SWIEPH | swe.FLG_SPEED)
        d = ecart(theme["corps"][nom]["lon"], xx[0])
        assert d < TOL_CORPS, f"{nom} : écart {d * 3600:.2f}\""
        assert theme["corps"][nom]["retrograde"] == (xx[3] < 0) or abs(xx[3]) < 0.01

    # Aux hautes latitudes, l'écliptique frôle l'horizon : l'Ascendant y
    # devient hypersensible au temps, et le même ΔUT1 s'y traduit par un écart
    # plusieurs fois plus grand (mesuré 28,6" à Tromsø contre 4,9" sur le MC,
    # au même instant). Ce n'est pas une perte de précision de notre part,
    # c'est la géométrie du lieu — cf. test_ascendant_hypersensible_en_altitude.
    tol = TOL_ANGLE * 3 if abs(lat) > 60.0 else TOL_ANGLE

    systeme = b"O" if theme["maisons"]["repli"] else b"P"
    cusps, ascmc = swe.houses_ex(jd, lat, lon, systeme)
    assert ecart(theme["angles"]["asc"]["lon"], ascmc[0]) < tol
    assert ecart(theme["angles"]["mc"]["lon"], ascmc[1]) < TOL_ANGLE
    for i, (nous, oracle) in enumerate(zip(theme["maisons"]["cuspides"], cusps[:12]), 1):
        assert ecart(nous, oracle) < tol, f"cuspide {i} : {nous} vs {oracle}"


def test_le_piege_us_canada_se_voit_sur_le_theme():
    """Février-avril 1975 : le Canada n'a pas suivi l'heure d'été américaine.

    Une app qui prendrait « Québec = heure de l'Est américaine » produirait un
    thème décalé d'une heure. Ce test le montre sur l'Ascendant, là où ça fait
    mal : ~15°, soit un demi-signe.
    """
    ca = MOTEUR.theme_natal(1975, 3, 15, 10, 0, 45.5088, -73.5878, "America/Toronto")
    us = MOTEUR.theme_natal(1975, 3, 15, 10, 0, 45.5088, -73.5878, "America/New_York")

    # Une heure d'horloge = 15° de rotation terrestre, mais l'Ascendant ne
    # suit PAS ce rythme : sa vitesse dépend de l'angle entre l'écliptique et
    # l'horizon, donc de la latitude et de la saison (mesuré 16,7° ici).
    # On vérifie l'ordre de grandeur — un demi-signe — pas une valeur exacte.
    d = ecart(ca["angles"]["asc"]["lon"], us["angles"]["asc"]["lon"])
    assert 10.0 < d < 25.0, f"écart d'ASC attendu ~un demi-signe, obtenu {d:.2f}°"
    # Sur CE cas précis les deux Ascendants restent en Gémeaux : 16,7° d'écart
    # ne suffisent pas toujours à franchir une frontière de signe. L'erreur
    # n'en est pas moins majeure — un demi-signe de décalage fausse maisons,
    # aspects et donc toute lecture. Ne pas conclure « ça se verrait ».


def test_vitesse_de_l_ascendant_tres_inegale_en_haute_latitude():
    """Un fait de conception, mesuré en validant la chaîne.

    L'Ascendant ne se déplace PAS à vitesse constante : elle dépend de l'angle
    entre l'écliptique et l'horizon, qui varie au fil de la journée. À
    Montréal cette variation est modérée. À Tromsø (69°N) elle est extrême :
    l'ASC rampe à ~0,05°/min pendant presque toute la journée du 21 décembre,
    puis file à ~1,3°/min autour de midi — un rapport de plus de 20.

    (Attention au contre-sens : ce n'est pas « l'ASC va plus vite en haute
    latitude ». Au solstice à midi il est plus LENT à Tromsø qu'à Quito. C'est
    l'AMPLITUDE de variation qui explose. Une première version de ce test
    affirmait le contraire et se trompait.)

    Conséquence produit : la précision de l'heure de naissance ne vaut pas la
    même chose partout ni à toute heure. Cinq minutes d'incertitude, c'est
    ~1° d'Ascendant à Montréal, mais ~6,5° à Tromsø à midi. L'app ne devrait
    pas afficher partout la même fausse précision.
    """
    def vitesse(hh, lat, lon, tz):
        a = MOTEUR.theme_natal(1990, 12, 21, hh, 0, lat, lon, tz)["angles"]["asc"]["lon"]
        b = MOTEUR.theme_natal(1990, 12, 21, hh, 2, lat, lon, tz)["angles"]["asc"]["lon"]
        return ecart(a, b) / 2.0             # degrés par minute d'horloge

    heures = range(0, 24, 3)
    tromso = [vitesse(h, 69.6492, 18.9553, "Europe/Oslo") for h in heures]
    montreal = [vitesse(h, 45.5088, -73.5878, "America/Toronto") for h in heures]

    amplitude = lambda v: max(v) / min(v)
    assert amplitude(tromso) > 10, f"amplitude attendue >10 à Tromsø, obtenue {amplitude(tromso):.1f}"
    assert amplitude(tromso) > amplitude(montreal) * 3, (
        f"Tromsø {amplitude(tromso):.1f}x contre Montréal {amplitude(montreal):.1f}x"
    )


def test_repli_polaire_annonce_dans_le_theme():
    """Au-delà du cercle polaire, l'utilisateur doit VOIR que c'est dégradé."""
    t = MOTEUR.theme_natal(1990, 12, 21, 12, 0, 69.6492, 18.9553, "Europe/Oslo")
    assert t["maisons"]["repli"] is not None
    assert len(t["maisons"]["cuspides"]) == 12


def test_avis_et_limites_remontent_jusqu_au_theme():
    """Les réserves font partie du résultat, pas des notes de bas de page."""
    ambigu = MOTEUR.theme_natal(2024, 11, 3, 1, 30, 45.5088, -73.5878, "America/Toronto")
    assert any(a["type"] == "heure_ambigue" for a in ambigu["avis"])

    ancien = MOTEUR.theme_natal(1880, 6, 15, 12, 0, 45.5088, -73.5878, "America/Montreal")
    assert ancien["limites"], "une naissance de 1880 doit porter des réserves"


def test_signe_de_aux_frontieres():
    """Les bornes de signe : 0°, 29°59', et l'arrondi qui déborde."""
    assert signe_de(0.0) == {"signe": "Bélier", "degre": 0, "minute": 0}
    assert signe_de(29.999) == {"signe": "Bélier", "degre": 30, "minute": 0}
    assert signe_de(30.0) == {"signe": "Taureau", "degre": 0, "minute": 0}
    assert signe_de(359.9999)["signe"] == "Poissons"
    assert signe_de(180.0) == {"signe": "Balance", "degre": 0, "minute": 0}


def test_maison_de_enjambe_zero():
    """Le cas qui casse les implémentations naïves : la maison 1 enjambe 0°."""
    cusp = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0,
            170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
    assert maison_de(355.0, cusp) == 1      # après la cuspide 1, avant 360
    assert maison_de(5.0, cusp) == 1        # de l'autre côté de 0°
    assert maison_de(25.0, cusp) == 2
    assert maison_de(349.0, cusp) == 12     # juste avant la cuspide 1
