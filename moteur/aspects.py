"""Aspects, dignités, configurations — la structure lisible d'un thème.

Choix de conception hérités de la lecture des sources (voir PROPOSITION.md §3) :

  1. **12 corps aspectables**, pas 10 : l'Ascendant et le Milieu du Ciel sont
     traités comme des planètes.
  2. **3 CLASSES d'aspects, pas 5** : conjonction / carré-opposition /
     sextile-trigone. C'est ce qui rend le corpus tabulable — et ça divise le
     volume à rédiger par ~1,7 sans rien perdre d'utile.
  3. **Additionner des tables indépendantes, JAMAIS le produit cartésien.**
     Le produit explose (« plusieurs centaines de milliers de cas pour un seul
     thème », et c'est une objection fondée) ; des tables factorisées restent
     rédigeables à la main.
  4. **Orbes d'une seule source**, cohérentes avec ses propres tables. Les
     ouvrages divergent (conjonction 8°/8-10°/10°) : mélanger leurs orbes
     produirait des aspects que personne n'a jamais interprétés.
"""

SIGNES = [
    "Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge",
    "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons",
]

ELEMENTS = {
    "Feu": ["Bélier", "Lion", "Sagittaire"],
    "Terre": ["Taureau", "Vierge", "Capricorne"],
    "Air": ["Gémeaux", "Balance", "Verseau"],
    "Eau": ["Cancer", "Scorpion", "Poissons"],
}
ELEMENT_DE = {s: e for e, ss in ELEMENTS.items() for s in ss}

MODALITES = {
    "Cardinal": ["Bélier", "Cancer", "Balance", "Capricorne"],
    "Fixe": ["Taureau", "Lion", "Scorpion", "Verseau"],
    "Mutable": ["Gémeaux", "Vierge", "Sagittaire", "Poissons"],
}
MODALITE_DE = {s: m for m, ss in MODALITES.items() for s in ss}

# (angle, orbe, classe). Les orbes sont celles de la source retenue.
ASPECTS = {
    "conjonction": (0.0, 8.0, "conjonction"),
    "sextile": (60.0, 6.0, "sextile-trigone"),
    "carre": (90.0, 8.0, "carre-opposition"),
    "trigone": (120.0, 8.0, "sextile-trigone"),
    "opposition": (180.0, 8.0, "carre-opposition"),
}

CORPS_ASPECTABLES = [
    "soleil", "lune", "mercure", "venus", "mars", "jupiter",
    "saturne", "uranus", "neptune", "pluton", "asc", "mc",
]

# Dignités. Maîtrises modernes ET traditionnelles : les deux sont utiles, et
# on ne les mélange pas silencieusement.
DOMICILE = {
    "soleil": ["Lion"], "lune": ["Cancer"], "mercure": ["Gémeaux", "Vierge"],
    "venus": ["Taureau", "Balance"], "mars": ["Bélier", "Scorpion"],
    "jupiter": ["Sagittaire", "Poissons"], "saturne": ["Capricorne", "Verseau"],
    "uranus": ["Verseau"], "neptune": ["Poissons"], "pluton": ["Scorpion"],
}
EXALTATION = {
    "soleil": "Bélier", "lune": "Taureau", "mercure": "Vierge",
    "venus": "Poissons", "mars": "Capricorne", "jupiter": "Cancer",
    "saturne": "Balance",
}
MAITRISE = {}
for _p, _ss in DOMICILE.items():
    for _s in _ss:
        MAITRISE.setdefault(_s, []).append(_p)

ANGULAIRES = (1, 4, 7, 10)
SUCCEDENTES = (2, 5, 8, 11)
CADENTES = (3, 6, 9, 12)


def _oppose(signe):
    return SIGNES[(SIGNES.index(signe) + 6) % 12]


def dignite(planete, signe):
    """domicile / exil / exaltation / chute / None. Purement tabulaire."""
    if signe in DOMICILE.get(planete, []):
        return "domicile"
    if any(signe == _oppose(s) for s in DOMICILE.get(planete, [])):
        return "exil"
    if EXALTATION.get(planete) == signe:
        return "exaltation"
    if planete in EXALTATION and signe == _oppose(EXALTATION[planete]):
        return "chute"
    return None


def _ecart(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def aspects_entre(positions, vitesses=None):
    """Tous les aspects du thème, les plus serrés d'abord.

    `positions` : {corps -> longitude}. `vitesses` (optionnel) sert à dire si
    l'aspect est APPLICATIF (il se resserre) ou SÉPARATIF (il se desserre) —
    l'applicatif est le plus fort, et c'est déterministe.
    """
    trouves = []
    corps = [c for c in CORPS_ASPECTABLES if c in positions]
    for i, a in enumerate(corps):
        for b in corps[i + 1:]:
            d = _ecart(positions[a], positions[b])
            for nom, (angle, orbe, classe) in ASPECTS.items():
                if abs(d - angle) <= orbe:
                    ecart_exact = abs(d - angle)
                    asp = {
                        "corps": (a, b),
                        "aspect": nom,
                        "classe": classe,
                        "orbe": ecart_exact,
                        "exactitude": 1.0 - ecart_exact / orbe,   # 1 = exact
                    }
                    if vitesses and a in vitesses and b in vitesses:
                        asp["applicatif"] = _est_applicatif(
                            positions[a], positions[b], vitesses[a], vitesses[b], angle
                        )
                    trouves.append(asp)
                    break
    trouves.sort(key=lambda x: x["orbe"])
    return trouves


def _est_applicatif(la, lb, va, vb, angle):
    """L'aspect se resserre-t-il ? Par différence finie sur un petit pas."""
    if va is None or vb is None:
        return None
    pas = 0.01
    d0 = abs(_ecart(la, lb) - angle)
    d1 = abs(_ecart(la + va * pas, lb + vb * pas) - angle)
    return d1 < d0


def bilan_elements(corps):
    """Répartition par élément et par modalité — les 10 planètes seulement.

    Les angles sont exclus : ce sont des points, pas des corps, et les
    compter fausserait la pesée.
    """
    els = {e: 0 for e in ELEMENTS}
    mods = {m: 0 for m in MODALITES}
    for nom, c in corps.items():
        if nom in ("asc", "mc", "noeud_moyen"):
            continue
        els[ELEMENT_DE[c["signe"]]] += 1
        mods[MODALITE_DE[c["signe"]]] += 1
    return {"elements": els, "modalites": mods}


def stelliums(corps, minimum=3):
    """Trois corps ou plus dans un même signe. La configuration la plus lisible."""
    par_signe = {}
    for nom, c in corps.items():
        if nom in ("asc", "mc", "noeud_moyen"):
            continue
        par_signe.setdefault(c["signe"], []).append(nom)
    return [{"signe": s, "corps": sorted(v)}
            for s, v in sorted(par_signe.items()) if len(v) >= minimum]


def force_planete(nom, corps, aspects_du_theme):
    """Un score de force 0-100, entièrement déterministe.

    Sert au croisement : la carte de naissance pointe vers une planète, et on
    veut savoir si cette planète est FORTE ou EN DIFFICULTÉ dans le thème réel.

    Aucun de ces critères n'est une invention : angularité, dignité et densité
    d'aspects sont les trois pesées classiques. Le barème, lui, est un choix
    d'Align — assumé, documenté, et surtout STABLE (c'est ce qui compte pour
    du déterministe).
    """
    c = corps.get(nom)
    if not c:
        return None
    score = 50
    raisons = []

    maison = c.get("maison")
    if maison in ANGULAIRES:
        score += 15
        raisons.append("en maison angulaire")
    elif maison in CADENTES:
        score -= 10
        raisons.append("en maison cadente")

    d = dignite(nom, c["signe"])
    if d == "domicile":
        score += 20
        raisons.append("dans son domicile")
    elif d == "exaltation":
        score += 15
        raisons.append("en exaltation")
    elif d == "exil":
        score -= 15
        raisons.append("en exil")
    elif d == "chute":
        score -= 15
        raisons.append("en chute")

    liens = [a for a in aspects_du_theme if nom in a["corps"]]
    serres = [a for a in liens if a["orbe"] < 3.0]
    score += min(len(serres) * 5, 15)
    if serres:
        raisons.append(f"{len(serres)} aspect(s) serré(s)")
    if not liens:
        score -= 10
        raisons.append("sans aspect majeur")

    if c.get("retrograde"):
        score -= 5
        raisons.append("rétrograde")

    return {"score": max(0, min(100, score)), "raisons": raisons, "dignite": d}
