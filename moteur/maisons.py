"""Systèmes de maisons — trigonométrie pure, aucune dépendance.

Aucune bibliothèque d'astrologie n'existe sous licence permissive : toutes
(pyswisseph, kerykeion, immanuel, flatlib) dérivent de swisseph et sont AGPL.
Ce module est le prix à payer pour rester en MIT. Voir PROPOSITION.md §6.

Entrées : ARMC (temps sidéral local en degrés), obliquité, latitude.
Les maisons ne dépendent PAS de l'éphéméride — d'où une validation exacte
contre l'oracle, indépendamment du moteur de positions planétaires.

Références : Meeus, *Astronomical Algorithms* 2e éd., ch. 12 (temps sidéral)
et ch. 13 (transformations de coordonnées) ; documentation Swiss Ephemeris,
chapitre « houses » (algorithmes et replis — lisible, non copié).
"""
import math

CERCLE_POLAIRE = 66.5  # marge sous 66°33' : Placidus se dégrade avant la borne

_rad = math.radians
_deg = math.degrees


def _norm(d):
    """Ramène un angle dans [0, 360)."""
    return d % 360.0


def _asc(armc, eps, phi):
    """Ascendant : intersection de l'écliptique et de l'horizon, vers l'est.

    tan(ASC) = cos(ARMC) / ( -sin(ARMC)·cos(eps) - tan(phi)·sin(eps) )

    atan2 gère les quadrants ; le +180° conditionnel place le point du bon
    côté de l'horizon (l'ASC est l'intersection ORIENTALE, l'autre racine
    étant le descendant).
    """
    a, e, p = _rad(armc), _rad(eps), _rad(phi)
    x = math.cos(a)
    y = -(math.sin(a) * math.cos(e) + math.tan(p) * math.sin(e))
    asc = _deg(math.atan2(x, y))
    # atan2 renvoie la racine dans [-180,180] ; l'ASC doit être à l'est du MC.
    if _norm(asc - _mc(armc, eps)) > 180.0:
        asc += 180.0
    return _norm(asc)


def _mc(armc, eps):
    """Milieu du Ciel : intersection de l'écliptique et du méridien.

    tan(MC) = tan(ARMC) / cos(eps), en gardant le quadrant de l'ARMC.
    """
    a, e = _rad(armc), _rad(eps)
    return _norm(_deg(math.atan2(math.sin(a), math.cos(a) * math.cos(e))))


def angles(armc, eps, phi):
    """ASC et MC. Identiques dans TOUS les systèmes de maisons.

    C'est ce qui borne le risque du choix de système : seules les cuspides
    intermédiaires varient (Riske le souligne explicitement).
    """
    return _asc(armc, eps, phi), _mc(armc, eps)


# ---------------------------------------------------------------- systèmes

def signe_entier(asc, **_):
    """Whole Sign : la maison 1 est le signe entier qui contient l'ASC."""
    base = math.floor(asc / 30.0) * 30.0
    return [_norm(base + 30.0 * i) for i in range(12)]


def egal(asc, **_):
    """Equal : 12 secteurs de 30° à partir de l'ASC exact."""
    return [_norm(asc + 30.0 * i) for i in range(12)]


def porphyry(asc, mc, **_):
    """Porphyry : trisection linéaire de chaque quadrant ASC->MC.

    Toujours défini, y compris aux pôles — d'où son rôle de repli pour
    Placidus. Il s'accorde avec lui sur les angles et ne diverge que sur
    les cuspides intermédiaires.
    """
    c = [0.0] * 12
    c[0], c[3], c[6], c[9] = asc, _norm(mc + 180.0), _norm(asc + 180.0), mc
    q1 = _norm(c[3] - c[0]) / 3.0   # ASC -> FC
    q2 = _norm(c[6] - c[3]) / 3.0   # FC  -> DSC
    for i in (1, 2):
        c[i] = _norm(c[0] + q1 * i)
        c[i + 3] = _norm(c[3] + q2 * i)
    for i in range(6):
        c[i + 6] = _norm(c[i] + 180.0)
    return c


def _ra_vers_lon(ra, eps):
    """Ascension droite -> longitude écliptique (latitude écliptique nulle)."""
    return _norm(_deg(math.atan2(math.sin(_rad(ra)), math.cos(_rad(ra)) * math.cos(_rad(eps)))))


def _placidus_ra(armc, eps, phi, fraction, sens, iterations=100, eps_conv=1e-11):
    """Ascension droite d'une cuspide Placidus, par itération de point fixe.

    Placidus trisecte l'arc semi-diurne DANS LE TEMPS, pas dans l'espace : il
    n'existe aucune solution fermée. On résout le point fixe

        RA = ARMC + sens · fraction · SD(RA)
        SD(RA) = arccos( -tan(eps)·sin(RA)·tan(phi) )

    en s'appuyant sur l'identité tan(decl) = tan(eps)·sin(RA), valable sur
    l'écliptique, et sur cos(SD) = -tan(decl)·tan(phi) (angle horaire au
    lever/coucher). `sens` vaut +1 à l'est du méridien (maisons 11, 12) et
    -1 à l'ouest (maisons 8, 9).

    Renvoie None si l'argument de l'arccos sort de [-1, 1] — le degré est
    alors circumpolaire : il ne coupe jamais l'horizon, l'arc semi-diurne
    n'existe pas, la cuspide est mathématiquement INDÉFINIE. Renvoie None
    aussi si l'itération ne converge pas. L'appelant se replie sur Porphyry.

    Itération BORNÉE, jamais de `while` libre : une boucle non bornée rendrait
    le résultat dépendant de l'ordre d'arrondi, donc non déterministe.
    """
    k = math.tan(_rad(eps)) * math.tan(_rad(phi))
    ra = _norm(armc + sens * fraction * 90.0)      # devinette : SD ~ 90°
    for _ in range(iterations):
        arg = -math.sin(_rad(ra)) * k
        if not -1.0 <= arg <= 1.0:
            return None                            # circumpolaire -> indéfini
        suivant = _norm(armc + sens * fraction * _deg(math.acos(arg)))
        ecart = abs((suivant - ra + 180.0) % 360.0 - 180.0)
        ra = suivant
        if ecart < eps_conv:
            return ra
    return None                                    # pas de convergence -> repli


def placidus(asc, mc, armc, eps, phi):
    """Placidus, avec repli Porphyry documenté.

    Renvoie (cuspides, repli) : `repli` vaut None si Placidus a abouti, sinon
    la raison. Le repli n'est JAMAIS silencieux — c'est ce que fait swisseph,
    et c'est ce que l'app doit pouvoir afficher.

    Les cuspides Placidus vont par paires opposées (1/7, 2/8 … 6/12) : on ne
    calcule donc que 11, 12, 8, 9 et on en déduit 5, 6, 2, 3 par symétrie.
    """
    if abs(phi) >= CERCLE_POLAIRE:
        return porphyry(asc, mc), "au-delà du cercle polaire"

    # (maison, fraction de l'arc semi-diurne, côté du méridien)
    plan = [(11, 1 / 3, +1), (12, 2 / 3, +1), (9, 1 / 3, -1), (8, 2 / 3, -1)]
    calculees = {}
    for maison, fraction, sens in plan:
        ra = _placidus_ra(armc, eps, phi, fraction, sens)
        if ra is None:
            return porphyry(asc, mc), "degré circumpolaire (arc semi-diurne inexistant)"
        calculees[maison] = _ra_vers_lon(ra, eps)

    c = [0.0] * 12
    c[0], c[6] = asc, _norm(asc + 180.0)               # 1 / 7
    c[9], c[3] = mc, _norm(mc + 180.0)                 # 10 / 4
    for maison, lon in calculees.items():
        c[maison - 1] = lon
        c[(maison + 6 - 1) % 12] = _norm(lon + 180.0)  # l'opposée
    return c, None


SYSTEMES = {
    "placidus": placidus,
    "porphyry": lambda asc, mc, armc, eps, phi: (porphyry(asc, mc), None),
    "signe_entier": lambda asc, mc, armc, eps, phi: (signe_entier(asc), None),
    "egal": lambda asc, mc, armc, eps, phi: (egal(asc), None),
}


def cuspides(systeme, armc, eps, phi):
    """Point d'entrée unique. Renvoie (cuspides, asc, mc, repli)."""
    if systeme not in SYSTEMES:
        raise ValueError(f"système inconnu : {systeme!r} (connus : {sorted(SYSTEMES)})")
    asc, mc = angles(armc, eps, phi)
    c, repli = SYSTEMES[systeme](asc, mc, armc, eps, phi)
    return c, asc, mc, repli
