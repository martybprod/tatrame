"""La carte mineure personnelle du jour — 56 arcanes, version Align.

📐 L'IDÉE (libre), PAS L'EXPRESSION (protégée)
Le tarot traditionnel a 78 cartes : 22 majeurs (déjà dans `moteur/tarot.py`,
carte du jour UNIVERSELLE — la même pour tout le monde, calculée sur la date
seule) + 56 mineurs (4 couleurs × 14 rangs : As, 2 à 10, Valet, Cavalier,
Reine, Roi). Ce module ajoute la carte mineure PERSONNELLE : différente
d'une personne à l'autre, différente chaque jour, jamais un tirage.

⚖️ CONVENTION ALIGN (tranchée par Align, à publier dans « Les Règles »)
Le Golden Dawn (Mathers, *Book T*, 1888 — domaine public) découpe le
zodiaque à TROIS résolutions superposées (36 décans de 10° pour les 9
numérales 2-10, des bandes de cuspide de 20° pour les figures, les 4
éléments pour les As) : un seul degré du ciel appartient donc à la fois à
un décan, une bande de figure ET un élément. Aucune source ne fournit de
partition PLATE « 1 degré -> 1 des 56 cartes ». Align tranche avec DEUX axes
combinés, chacun porté par un astre DIFFÉRENT :

  - COULEUR (le suit) = l'ÉLÉMENT du signe où se trouve la LUNE TRANSIT du
    jour — partagé par tout le monde ce jour-là, change tous les ~2,5
    jours (Feu -> Bâtons, Terre -> Deniers, Air -> Épées, Eau -> Coupes).
  - RANG = la position du SOLEIL TRANSIT du jour, mesurée depuis
    l'ASCENDANT NATAL (donc personnelle), le cercle divisé en 14 parts
    égales dans l'ordre traditionnel (As, 2..10, Valet, Cavalier, Reine,
    Roi) — avance doucement, sur l'année.

  ⚠️ PIÈGE ÉVITÉ (vérifié par calcul, pas supposé) : une première version
  dérivait aussi le rang de la LUNE (son arc depuis l'Ascendant natal).
  Erreur — pour un Ascendant FIXE, deux fonctions-marches d'une SEULE
  variable (la Lune) ne peuvent produire qu'au plus (12 bornes de suit +
  14 bornes de rang) ≈ 26 cellules distinctes, JAMAIS 56 : une même
  personne n'aurait jamais vu qu'un quart du jeu, à vie. En prenant le
  RANG sur le SOLEIL (un astre qui dérive de la Lune à un rythme non
  proportionnel), les deux axes redeviennent réellement indépendants —
  vérifié : les 56 clés s'affichent en moins de 3 ans, pour n'importe quel
  Ascendant. Ce choix évite aussi un doublon avec « maison de la Lune »
  (Fil du jour), qui utilise déjà Lune × Ascendant/maisons natales.

Produit : 4 × 14 = 56 clés, TOUTES atteignables (As et figures inclus
nativement, pas de règle spéciale) — contrairement au Golden Dawn « pur »
où les As et figures sont des cas rares. C'est la convention D'ALIGN, pas
une reconstruction du système d'origine ; à assumer comme telle.

Les CORRESPONDANCES decan/élément ci-dessous (quelle planète, quel signe,
quel élément pour chaque carte) sont la table Golden Dawn elle-même —
domaine public, reprise telle quelle. Les NOMS de cartes affichés sont les
noms traditionnels du tarot (As de Coupes, Roi de Deniers...) — génériques,
non protégeables. Rien ici n'emprunte à un jeu ni un auteur contemporain.

Ce module ne fait que CALCULER. Le seul texte éditorial (l'« invitation »
du jour) vit dans `data/corpus/mineurs.json`, jamais ici.
"""
from moteur.theme import SIGNES

# ───────────────────────────────────────────────────── éléments & couleurs

ELEMENT_PAR_SIGNE = {
    "Bélier": "feu", "Lion": "feu", "Sagittaire": "feu",
    "Taureau": "terre", "Vierge": "terre", "Capricorne": "terre",
    "Gémeaux": "air", "Balance": "air", "Verseau": "air",
    "Cancer": "eau", "Scorpion": "eau", "Poissons": "eau",
}

SUIT_PAR_ELEMENT = {"feu": "batons", "terre": "deniers", "air": "epees", "eau": "coupes"}

SUIT_NOM = {"batons": "Bâtons", "deniers": "Deniers", "epees": "Épées", "coupes": "Coupes"}
ELEMENT_NOM = {"feu": "Feu", "terre": "Terre", "air": "Air", "eau": "Eau"}

# ─────────────────────────────────────────────────────────────── les rangs

# Ordre traditionnel, 14 parts égales du cercle personnel (Lune depuis l'Ascendant).
RANGS = ["as", "2", "3", "4", "5", "6", "7", "8", "9", "10",
         "valet", "cavalier", "reine", "roi"]
LARGEUR_RANG = 360.0 / len(RANGS)

RANG_NOM = {
    "as": "As", "2": "Deux", "3": "Trois", "4": "Quatre", "5": "Cinq",
    "6": "Six", "7": "Sept", "8": "Huit", "9": "Neuf", "10": "Dix",
    "valet": "Valet", "cavalier": "Cavalier", "reine": "Reine", "roi": "Roi",
}
FIGURES = {"valet", "cavalier", "reine", "roi"}

# Numéro de fichier source (01-14) du jeu Rider-Waite-Smith utilisé pour les
# images (`Cups01.jpg`..`Cups14.jpg`, etc. -> voir static/cartes/mineurs/).
RANG_NUM_FICHIER = {r: f"{i + 1:02d}" for i, r in enumerate(RANGS)}

# Élément associé à chaque figure, dans le schéma Golden Dawn (l'élément de
# l'élément du suit) — Roi=Feu, Reine=Eau, Cavalier=Air, Valet=Terre.
ELEMENT_PAR_FIGURE = {"roi": "feu", "reine": "eau", "cavalier": "air", "valet": "terre"}

# ────────────────────────────────────────────── décans (numérales 2 à 10)
# Table Golden Dawn (Mathers, *Book T*) : (planète, signe) par carte,
# domaine public. clé = (suit, rang).
DECANS = {
    ("batons", "2"): ("mars", "Bélier"), ("batons", "3"): ("soleil", "Bélier"),
    ("batons", "4"): ("venus", "Bélier"), ("batons", "5"): ("saturne", "Lion"),
    ("batons", "6"): ("jupiter", "Lion"), ("batons", "7"): ("mars", "Lion"),
    ("batons", "8"): ("mercure", "Sagittaire"), ("batons", "9"): ("lune", "Sagittaire"),
    ("batons", "10"): ("saturne", "Sagittaire"),

    ("coupes", "2"): ("venus", "Cancer"), ("coupes", "3"): ("mercure", "Cancer"),
    ("coupes", "4"): ("lune", "Cancer"), ("coupes", "5"): ("mars", "Scorpion"),
    ("coupes", "6"): ("soleil", "Scorpion"), ("coupes", "7"): ("venus", "Scorpion"),
    ("coupes", "8"): ("saturne", "Poissons"), ("coupes", "9"): ("jupiter", "Poissons"),
    ("coupes", "10"): ("mars", "Poissons"),

    ("epees", "2"): ("lune", "Balance"), ("epees", "3"): ("saturne", "Balance"),
    ("epees", "4"): ("jupiter", "Balance"), ("epees", "5"): ("venus", "Verseau"),
    ("epees", "6"): ("mercure", "Verseau"), ("epees", "7"): ("lune", "Verseau"),
    ("epees", "8"): ("jupiter", "Gémeaux"), ("epees", "9"): ("mars", "Gémeaux"),
    ("epees", "10"): ("soleil", "Gémeaux"),

    ("deniers", "2"): ("jupiter", "Capricorne"), ("deniers", "3"): ("mars", "Capricorne"),
    ("deniers", "4"): ("soleil", "Capricorne"), ("deniers", "5"): ("mercure", "Taureau"),
    ("deniers", "6"): ("lune", "Taureau"), ("deniers", "7"): ("saturne", "Taureau"),
    ("deniers", "8"): ("soleil", "Vierge"), ("deniers", "9"): ("venus", "Vierge"),
    ("deniers", "10"): ("mercure", "Vierge"),
}

assert set(SIGNES) == set(ELEMENT_PAR_SIGNE), "un signe manque à ELEMENT_PAR_SIGNE"
assert len(DECANS) == 4 * 9, "table des décans incomplète (attendu 36)"


def _nom(suit, rang):
    """« As de Coupes », « Reine de Bâtons », « As d'Épées »... (élision)."""
    de = "d'" if SUIT_NOM[suit][0] in "AEÉIOU" else "de "
    return f"{RANG_NOM[rang]} {de}{SUIT_NOM[suit]}"


def _correspondance(suit, rang):
    """La correspondance Golden Dawn affichable (type, texte)."""
    if rang == "as":
        return ("element", ELEMENT_NOM[[e for e, s in SUIT_PAR_ELEMENT.items() if s == suit][0]])
    if rang in FIGURES:
        elt_figure = ELEMENT_PAR_FIGURE[rang]
        elt_suit = [e for e, s in SUIT_PAR_ELEMENT.items() if s == suit][0]
        return ("element", f"{ELEMENT_NOM[elt_figure]} de {ELEMENT_NOM[elt_suit]}")
    planete, signe = DECANS[(suit, rang)]
    return ("decan", f"{planete.capitalize()} en {signe}")


def carte_mineure(lune_lon, soleil_lon, asc_lon):
    """La carte mineure personnelle du jour.

    `lune_lon` : longitude écliptique de la Lune TRANSIT du jour (donne la
    couleur, le même ciel pour tout le monde, change vite). `soleil_lon` :
    longitude du Soleil TRANSIT du jour. `asc_lon` : longitude de
    l'Ascendant NATAL. Le rang vient de l'écart Soleil transit -> Ascendant
    natal (ce qui rend le résultat personnel ET couvre bien les 56 clés à
    l'usage — voir le piège évité en tête de module). Pur calcul,
    déterministe, aucun accès disque — voir `data/corpus/mineurs.json`
    pour le texte.
    """
    signe_lune = SIGNES[int(lune_lon % 360.0 // 30) % 12]
    suit = SUIT_PAR_ELEMENT[ELEMENT_PAR_SIGNE[signe_lune]]

    arc = (soleil_lon - asc_lon) % 360.0
    rang = RANGS[min(int(arc // LARGEUR_RANG), len(RANGS) - 1)]

    cle = f"{suit}_{rang}"
    type_corr, valeur_corr = _correspondance(suit, rang)
    return {
        "suit": suit, "suit_nom": SUIT_NOM[suit],
        "rang": rang, "rang_nom": RANG_NOM[rang],
        "cle": cle,
        "nom": _nom(suit, rang),
        "correspondance": (type_corr, valeur_corr),
        "figure": rang in FIGURES,
    }


def url_carte_mineure(suit, rang):
    """L'URL de la vignette d'une mineure, ou None si le fichier n'existe pas
    encore (voir static/cartes/mineurs/README.md) — le front replie alors
    sur le dos de carte, jamais une image cassée."""
    return f"/static/cartes/mineurs/{suit}_{rang}.jpg"
