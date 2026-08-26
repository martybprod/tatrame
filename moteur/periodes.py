"""Les 48 sous-périodes du zodiaque — la personologie, version Align.

📐 L'IDÉE (libre), PAS L'EXPRESSION (protégée)
Le système de personologie découpe l'année en 48 périodes : 12 « cuspides »
(à cheval sur une frontière de signe) + 36 « semaines » (l'intérieur de chaque
signe, en trois). C'est une STRUCTURE — une idée, réutilisable. En revanche les
NOMS de périodes et leurs descriptions du livre sont de l'expression protégée :
Align n'en reprend rien. Il définit ses propres bornes, par DEGRÉ solaire (le
Soleil est déjà calculé exactement), et écrira son propre vocabulaire.

⚖️ CONVENTION ALIGN (tranché par Align, à publier dans « Les Règles »)
  - Une cuspide = ±3,5° autour de chaque frontière de signe (7° de large).
  - L'intérieur d'un signe (23°) se divise en trois semaines égales (~7,667°).
Somme : 12×7° + 36×7,667° = 360°. Le découpage tuile le cercle sans reste.

Ce module ne fait que CALCULER (longitude → période). Aucun texte, aucun corpus.
"""
import unicodedata

from moteur.theme import SIGNES

DEMI_CUSPE = 3.5                        # demi-largeur d'une cuspide, en degrés
SEMAINE = (30.0 - 2 * DEMI_CUSPE) / 3   # largeur d'une semaine ≈ 7,6667°


def _slug(nom):
    s = unicodedata.normalize("NFD", nom.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def slug_signe(nom_signe):
    """« Bélier » -> « belier ». Clé publique : les corpus (noeuds.json,
    lexique) et la couche transport en ont besoin pour indexer par signe."""
    return _slug(nom_signe)


def _construire():
    """Les 48 périodes, ordonnées par signe : [cuspide d'entrée, sem. 1, 2, 3]."""
    periodes = []
    for s in range(12):
        base = 30.0 * s
        avant = (s - 1) % 12
        periodes.append({
            "cle": f"cuspe_{_slug(SIGNES[avant])}_{_slug(SIGNES[s])}",
            "type": "cuspe",
            "signe": SIGNES[s], "signe_avant": SIGNES[avant], "rang": None,
            "debut": (base - DEMI_CUSPE) % 360.0,
            "fin": (base + DEMI_CUSPE) % 360.0,
            "largeur": 2 * DEMI_CUSPE,
        })
        for r in range(3):
            d = base + DEMI_CUSPE + r * SEMAINE
            periodes.append({
                "cle": f"{_slug(SIGNES[s])}_{r + 1}",
                "type": "semaine",
                "signe": SIGNES[s], "signe_avant": None, "rang": r + 1,
                "debut": d % 360.0, "fin": (d + SEMAINE) % 360.0,
                "largeur": SEMAINE,
            })
    for i, p in enumerate(periodes):
        p["index"] = i
    return periodes


PERIODES = _construire()
_PAR_CLE = {p["cle"]: p for p in PERIODES}


def periode_de(longitude):
    """La sous-période (1 des 48) où tombe une longitude écliptique."""
    lon = longitude % 360.0
    s = int(lon // 30) % 12
    reste = lon % 30.0
    if reste < DEMI_CUSPE:                       # cuspide d'ENTRÉE du signe s
        avant = (s - 1) % 12
        return _PAR_CLE[f"cuspe_{_slug(SIGNES[avant])}_{_slug(SIGNES[s])}"]
    if reste >= 30.0 - DEMI_CUSPE:               # cuspide de SORTIE = entrée de s+1
        suiv = (s + 1) % 12
        return _PAR_CLE[f"cuspe_{_slug(SIGNES[s])}_{_slug(SIGNES[suiv])}"]
    rang = min(int((reste - DEMI_CUSPE) // SEMAINE), 2) + 1
    return _PAR_CLE[f"{_slug(SIGNES[s])}_{rang}"]
