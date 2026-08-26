"""Le moteur des Relations — le lien entre DEUX personnes, calculé.

Comme tout Align : 100 % déterministe, aucun aléa, aucun LLM. On CALCULE ici
(structure, badges, clés de corpus) ; on LIT ailleurs (les textes du corpus).

Ce module est volontairement PUR sur des primitives (cap, éléments, positions
écliptiques, branches chinoises). Il ne touche ni aux éphémérides ni au disque :
c'est `app.py` qui monte une « personne » depuis un profil (thème natal, nombres,
pilier chinois) et la passe ici. Cette frontière garde le moteur testable et le
déterminisme lisible.

Trois principes de la Phase R0, tenus dans le code :
  - C1 : AUCUN score global. On lit des AXES, chacun avec un badge
    résonance / tension / neutre (le vocabulaire de `croisement.py`).
  - C2 : la synastrie réutilise les orbes natales d'Align (`aspects.ASPECTS`).
  - P6 : le TYPE de relation est une LENTILLE — il ne change pas les axes
    calculés, seulement l'ordre et le registre de lecture.
"""
from moteur import aspects as A
from moteur import jour as _jour
from moteur.numerologie import reduire_total
from moteur.chinois import relation_branches
from moteur.synthese import cle_aspect

# Les points « personnels » : là où deux personnes se distinguent vraiment, et
# le socle de toute lecture de compatibilité (Arroyo, Skymates).
POINTS_PERSO = ("soleil", "lune", "mercure", "venus", "mars", "asc")

# ------------------------------------------------------------------ nombres

# Les quatre paires d'opposés numérologiques (Decoz) : forte attirance, pont à
# bâtir. Le 5, centre, n'a pas d'opposé.
_OPPOSES = [frozenset(p) for p in ({1, 9}, {2, 8}, {3, 7}, {4, 6})]


def _harmonique(a, b):
    """La méta-règle de Decoz, déterministe : identiques / opposés / écart de
    deux (fluide) / autre."""
    if a == b:
        return "identiques"
    if frozenset((a, b)) in _OPPOSES:
        return "opposes"
    if abs(a - b) == 2:
        return "ecart_deux"
    return "autre"


def paire_nombres(cap_a, cap_b):
    """Le croisement des deux Cap (chemin de vie).

    Les maîtres (11/22/33) sont réduits à 2/4/6 pour la compatibilité — c'est la
    convention de Decoz, publiée dans « Les Règles ». La clé est canonique
    (`min-max`) pour n'écrire chaque paire qu'une fois ; les deux perspectives
    (vers_min / vers_max) portent la lecture bidirectionnelle (C3).
    """
    a, b = reduire_total(cap_a), reduire_total(cap_b)
    lo, hi = sorted((a, b))
    return {
        "cle": f"{lo}-{hi}",
        "min": lo, "max": hi,
        "sens": "meme" if a == b else "mixte",
        "identiques": a == b,
        "harmonique": _harmonique(a, b),
    }


def nombre_composite(cap_a, cap_b):
    """Le nombre COMPOSÉ de la relation (Millman) : le « vous » comme entité.

    Là où `paire_nombres` CROISE les deux chemins (comment ils interagissent),
    le composé les ADDITIONNE : reduire_total(cap_a) + reduire_total(cap_b),
    réduit à 1-9. C'est le but de vie du lien LUI-MÊME — une troisième présence
    avec sa propre montagne, pendant numérologique du thème composite (le « vous »).

    Réduit à 1-9 comme partout en relations (convention d'Align ; Millman
    garderait 10/11/12). Table ADDITIVE de 9 entrées, jamais une matrice.
    `bases` (triées) rend le calcul symétrique ET auditable : le même couple
    donne le même composé quel que soit l'ordre.
    """
    base_a, base_b = reduire_total(cap_a), reduire_total(cap_b)
    return {
        "valeur": reduire_total(base_a + base_b),
        "bases": sorted((base_a, base_b)),
    }


_ETAT_HARMONIQUE = {
    "identiques": "resonance", "ecart_deux": "resonance",
    "opposes": "neutre", "autre": "neutre",
}


# ------------------------------------------------------------------ éléments

_ACTIFS = frozenset(("Feu", "Air"))
_RECEPTIFS = frozenset(("Terre", "Eau"))


def resonance_deux_elements(e1, e2):
    """La grammaire des éléments (Arroyo, Skymates).

    Feu-Air et Terre-Eau se mêlent naturellement (résonance) ; même élément =
    fluide mais peu dynamisant (neutre) ; les autres croisements « ne parlent
    pas la même langue » (tension). Jamais un verdict — juste un climat d'énergie.
    """
    if e1 == e2:
        return "neutre"
    paire = frozenset((e1, e2))
    if paire == _ACTIFS or paire == _RECEPTIFS:
        return "resonance"
    return "tension"


def cle_elements(e1, e2):
    """Clé de corpus canonique d'une paire d'éléments : « air-feu »."""
    a, b = sorted((e1.lower(), e2.lower()))
    return f"{a}-{b}"


# ------------------------------------------------------------------ chinois

# Le cycle de GÉNÉRATION (fécond) : chacun nourrit le suivant.
_GENERE = {"bois": "feu", "feu": "terre", "terre": "métal",
           "métal": "eau", "eau": "bois"}
# Le cycle de CONTRÔLE : chacun tempère un autre.
_CONTROLE = {"bois": "terre", "terre": "eau", "eau": "feu",
             "feu": "métal", "métal": "bois"}


def relation_elements_chinois(e1, e2):
    """Le lien entre deux éléments chinois : même / génère / contrôle / neutre.

    Symétrique : « le bois nourrit le feu » et « le feu est nourri par le bois »
    sont la même relation de génération."""
    if e1 == e2:
        return "meme"
    if _GENERE.get(e1) == e2 or _GENERE.get(e2) == e1:
        return "genere"
    if _CONTROLE.get(e1) == e2 or _CONTROLE.get(e2) == e1:
        return "controle"
    return "neutre"


_ETAT_BRANCHE = {
    "harmonie": "resonance", "trine": "resonance",
    "choc": "tension", "nuisance": "tension",
    "identique": "neutre", "neutre": "neutre",
}


def lien_chinois(i_branche_a, element_a, i_branche_b, element_b):
    """Le lien entre deux naissances côté chinois : relation de branches
    (réutilise `chinois.relation_branches`, déjà vérifié) + relation d'éléments."""
    return {
        "branche": relation_branches(i_branche_a, i_branche_b),
        "element": relation_elements_chinois(element_a, element_b),
    }


# ------------------------------------------------------------------ synastrie

def _ecart(a, b):
    """Écart angulaire minimal en degrés (identique à `aspects._ecart`)."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def synastrie(positions_a, positions_b):
    """Les aspects ENTRE deux thèmes (chaque corps de A vs chaque corps de B).

    Réutilise les orbes et classes natales d'Align (C2). Chaque aspect porte sa
    `cle` canonique (`synthese.cle_aspect`) : elle pointe DIRECTEMENT vers l'un
    des 135 textes d'aspects déjà écrits — on n'en réécrit aucun. `cle` vaut None
    pour un aspect à un angle (ASC/MC), rendu court par le lexique, comme dans le
    thème natal. `perso` marque les aspects entre points personnels : le cœur du lien.
    """
    trouves = []
    for a in A.CORPS_ASPECTABLES:
        if a not in positions_a:
            continue
        for b in A.CORPS_ASPECTABLES:
            if b not in positions_b:
                continue
            d = _ecart(positions_a[a], positions_b[b])
            for nom, (angle, orbe, classe) in A.ASPECTS.items():
                if abs(d - angle) <= orbe:
                    ecart = abs(d - angle)
                    trouves.append({
                        "de_a": a, "de_b": b,
                        "aspect": nom, "classe": classe,
                        "orbe": ecart,
                        "exactitude": 1.0 - ecart / orbe,
                        "cle": cle_aspect(a, b, classe),
                        "perso": a in POINTS_PERSO and b in POINTS_PERSO,
                    })
                    break
    trouves.sort(key=lambda x: (x["orbe"], x["de_a"], x["de_b"]))
    return trouves


# ------------------------------------------------------------ composite
#
# « Le vous » : le thème du couple comme troisième entité (Skymates 2). Chaque
# point du composite est le MILIEU des deux points natals. Le calcul est
# purement mathématique (moyenne d'angles sur le plus petit arc), donc
# parfaitement déterministe et rejouable. On lit ensuite le composite comme un
# thème natal ordinaire : le corpus des astres-en-signe et des aspects est
# réutilisé tel quel (le Soleil du « nous » en Bélier dit la même chose
# symbolique qu'un Soleil natal en Bélier, à propos du couple).
#
# ⚠️ SANS MAISONS (convention R0/C5) : le lieu de la première rencontre est
# presque toujours inconnu, et Align ne fabrique pas un lieu faux. Le composite
# livre donc les planètes (+ ASC/MC comme points milieux) et leurs aspects
# internes, jamais des maisons trompeuses.


def milieu_angulaire(a, b):
    """Le milieu de deux longitudes, sur le PLUS PETIT arc.

    Il existe deux points milieux opposés à 180° ; la convention composite
    retient celui de l'arc court. Symétrique (à la seule exception de deux
    points exactement opposés, cas limite tranché de façon déterministe)."""
    d = ((b - a + 180.0) % 360.0) - 180.0
    return (a + d / 2.0) % 360.0


def _signe_de(lon):
    return A.SIGNES[int(lon // 30) % 12]


def theme_composite(positions_a, positions_b):
    """Le thème composite : chaque corps commun aux deux thèmes, à mi-chemin.

    Renvoie None si l'un des deux jeux de positions manque (personne B sans
    heure/lieu) — pas de composite sans deux thèmes complets. Les aspects
    internes réutilisent `aspects.aspects_entre` : ce sont des aspects
    ordinaires entre les points du « nous »."""
    if not positions_a or not positions_b:
        return None
    corps = {}
    for c in A.CORPS_ASPECTABLES:
        if c in positions_a and c in positions_b:
            lon = milieu_angulaire(positions_a[c], positions_b[c])
            corps[c] = {"lon": lon, "signe": _signe_de(lon)}
    aspects_internes = A.aspects_entre({c: v["lon"] for c, v in corps.items()})
    return {"corps": corps, "aspects": aspects_internes}


# --------------------------------------------- la ressemblance du composite
#
# Le « triangle éternel » (Skymates 2) : le thème du « nous » ressemble-t-il à A,
# à B, aux deux, ou à personne ? Un diagnostic de HAUT NIVEAU, reformulé dans le
# vocabulaire d'Align (on n'emprunte pas les noms du livre) :
#   - "democratie" : le composite résonne avec les DEUX thèmes -> terrain
#     d'entente, les deux se reconnaissent dans le lien.
#   - "feodal"     : il ressemble surtout à UN des deux (le « souverain ») ;
#     l'autre se sent moins représenté -> partage conscient à travailler.
#   - "etrangere"  : il n'appartient ni à l'un ni à l'autre -> une contrée neuve
#     que ni A ni B ne fréquente seul.
#
# La mesure suit le PILIER que la source retient : la triade primaire
# Soleil-Lune-Ascendant. Les deux autres indices du livre sont écartés :
#   - « stelliums dans les mêmes maisons » -> Align n'a PAS de maisons composites
#     (convention R0/C5, cf. theme_composite) : on ne peut pas, on ne bluffe pas ;
#   - les « éléments manquants partagés » relèvent de A vs B, pas du composite vs
#     chacun -> ce serait un autre axe.
#
# Subtilité clé : chaque point composite étant le MILIEU exact, il est toujours à
# égale distance angulaire de A et de B. Une mesure d'angle donnerait donc
# score_a == score_b, jamais de « féodal ». Ce qui casse la symétrie, c'est le
# SIGNE : de quel côté de la frontière zodiacale le milieu tombe. On lit donc le
# signe (et, à demi-crédit, l'élément), et on n'annonce « féodal » que sur un
# PENCHANT tenu à travers la triade, pas sur un accident de frontière isolé.

# Les trois points que la source nomme « triade primaire » (le pilier d'entente).
TRIADE_PRIMAIRE = ("soleil", "lune", "asc")


def _ressemblance_signe(signe_comp, signe_natal):
    """Combien un point composite « appartient » au thème natal, en un point.

    Même signe = pleine appartenance (1.0) ; même élément mais signe voisin =
    demi-appartenance (0.5, la grammaire des éléments d'Align) ; sinon 0.0."""
    if signe_comp == signe_natal:
        return 1.0
    if A.ELEMENT_DE.get(signe_comp) == A.ELEMENT_DE.get(signe_natal):
        return 0.5
    return 0.0


def diagnostic_ressemblance(composite, positions_a, positions_b):
    """Le composite ressemble-t-il à A, à B, aux deux, ou à personne ?

    Renvoie None si le composite manque (personne B incomplète) ou si aucun
    point de la triade n'est comparable des deux côtés. Sinon un diagnostic
    déterministe : une `cle` ("democratie" | "feodal" | "etrangere"), le
    `souverain` ("a" | "b" | None) quand c'est féodal, et le détail par point
    pour que le corpus lise. Aucun texte, aucun score-verdict affiché — juste la
    structure du « triangle éternel »."""
    if composite is None or not positions_a or not positions_b:
        return None
    corps = composite["corps"]
    points = []
    ressemblance_a = ressemblance_b = 0.0
    for pt in TRIADE_PRIMAIRE:
        c = corps.get(pt)
        if not c or pt not in positions_a or pt not in positions_b:
            continue
        signe_a = _signe_de(positions_a[pt])
        signe_b = _signe_de(positions_b[pt])
        vers_a = _ressemblance_signe(c["signe"], signe_a)
        vers_b = _ressemblance_signe(c["signe"], signe_b)
        ressemblance_a += vers_a
        ressemblance_b += vers_b
        points.append({"point": pt, "signe": c["signe"],
                       "signe_a": signe_a, "signe_b": signe_b,
                       "vers_a": vers_a, "vers_b": vers_b})

    n = len(points)
    if n == 0:
        return None

    ratio_a = ressemblance_a / n
    ratio_b = ressemblance_b / n
    # Le seuil : « il s'y reconnaît » = au moins la moitié de la triade tenue.
    haut_a = ratio_a >= 0.5
    haut_b = ratio_b >= 0.5

    if haut_a and haut_b:
        cle, souverain = "democratie", None
    elif haut_a or haut_b:
        cle, souverain = "feodal", ("a" if haut_a else "b")
    else:
        cle, souverain = "etrangere", None

    return {
        "cle": cle,
        "souverain": souverain,
        "n": n,
        "ressemblance_a": ressemblance_a, "ressemblance_b": ressemblance_b,
        "ratio_a": ratio_a, "ratio_b": ratio_b,
        "points": points,
    }


# ------------------------------------------------------ le pouls du jour (R4)
#
# Comme le Fil du jour colore chaque matin par le ciel réel, le pouls colore le
# LIEN : le transit du jour le plus saillant sur le thème composite. La variété
# vient du ciel qui bouge (la Lune change de signe tous les 2,5 j), jamais d'un
# tirage — même composite + même date -> même pouls, pour toujours. On réutilise
# `jour.transits` TEL QUEL (mêmes orbes prédictives, mêmes poids, même force) :
# le composite est juste passé comme thème-cible.


def pouls_composite(composite, positions_du_jour, vitesses_du_jour=None):
    """Le transit du jour le plus fort sur le « vous ». None si pas de composite
    (personne B incomplète) ou si rien ne le touche assez près aujourd'hui.

    Le composite porte l'ASC et le MC comme points milieux ; on les remet dans
    la forme d'un thème (`corps` + `angles`) qu'attend `jour.transits`."""
    if composite is None:
        return None
    corps = composite["corps"]
    theme_cible = {
        "corps": {n: {"lon": c["lon"]} for n, c in corps.items() if n not in ("asc", "mc")},
        "angles": {"asc": {"lon": corps["asc"]["lon"]},
                   "mc": {"lon": corps["mc"]["lon"]}},
    }
    tous = _jour.transits(theme_cible, positions_du_jour, vitesses_du_jour)
    return tous[0] if tous else None


# --------------------------------------------------------- l'axe par couche

def _axe_nombres(a, b):
    p = paire_nombres(a["cap"], b["cap"])
    p["etat"] = _ETAT_HARMONIQUE[p["harmonique"]]
    # Le composé : le « vous » comme entité (somme des Cap), à côté du croisement.
    p["composite"] = nombre_composite(a["cap"], b["cap"])["valeur"]
    return p


def _axe_elements(a, b):
    """Compare, point personnel par point personnel, l'élément de A et de B.

    On lit chaque fonction en miroir (ton Soleil vs son Soleil, ta Lune vs sa
    Lune…) : simple, symétrique, et honnête sur ce qui manque."""
    par_point = []
    res = ten = 0
    for pt in POINTS_PERSO:
        ea = a["elements"].get(pt)
        eb = b["elements"].get(pt)
        if not ea or not eb:
            continue
        etat = resonance_deux_elements(ea, eb)
        res += etat == "resonance"
        ten += etat == "tension"
        par_point.append({"point": pt, "element_a": ea, "element_b": eb,
                          "cle": cle_elements(ea, eb), "etat": etat})
    return {"par_point": par_point, "etat": _majorite(res, ten)}


def _axe_chinois(a, b):
    lien = lien_chinois(a["chinois"]["i_branche"], a["chinois"]["element"],
                        b["chinois"]["i_branche"], b["chinois"]["element"])
    lien["etat"] = _ETAT_BRANCHE[lien["branche"]]
    return lien


def _axe_synastrie(a, b):
    if not a.get("positions") or not b.get("positions"):
        return None
    asps = synastrie(a["positions"], b["positions"])
    perso = [x for x in asps if x["perso"]]
    res = sum(1 for x in perso if x["classe"] == "sextile-trigone")
    ten = sum(1 for x in perso if x["classe"] == "carre-opposition")
    return {"aspects": asps, "perso": perso, "etat": _majorite(res, ten)}


def _majorite(res, ten):
    if res > ten:
        return "resonance"
    if ten > res:
        return "tension"
    return "neutre"


# ------------------------------------------------------- la lentille (P6)

# Le type de relation ne change pas le CALCUL : il choisit l'ordre des couches
# mises en avant et le registre de lecture. Table additive — R2 l'étoffera.
LENTILLES = {
    "amour":        {"ordre": ["synastrie", "nombres", "chinois", "elements"]},
    "travail":      {"ordre": ["elements", "chinois", "nombres", "synastrie"]},
    "parent_enfant": {"ordre": ["chinois", "elements", "nombres", "synastrie"]},
    "ami":          {"ordre": ["chinois", "elements", "nombres", "synastrie"]},
    "famille":      {"ordre": ["chinois", "nombres", "elements", "synastrie"]},
}
_PRIORITE_DOMINANTE = ("synastrie", "chinois", "elements", "nombres")


def croiser_relation(personne_a, personne_b, type_relation="amour"):
    """L'assemblage complet : les quatre axes + la synthèse + les manques.

    Aucun texte, que de la structure et des clés — le corpus lit ensuite. Aucun
    score global (C1). Le `type_relation` n'entre PAS dans les axes (P6) : il
    n'agit que sur `lentille` (l'ordre de lecture).
    """
    axes = {
        "nombres": _axe_nombres(personne_a, personne_b),
        "elements": _axe_elements(personne_a, personne_b),
        "chinois": _axe_chinois(personne_a, personne_b),
        "synastrie": _axe_synastrie(personne_a, personne_b),
    }

    composite = theme_composite(personne_a.get("positions"), personne_b.get("positions"))
    diagnostic = diagnostic_ressemblance(composite, personne_a.get("positions"),
                                         personne_b.get("positions"))

    manques = []
    if axes["synastrie"] is None:
        manques.append("synastrie")
    if composite is None:
        manques.append("composite")

    lentille = LENTILLES.get(type_relation, LENTILLES["amour"])

    return {
        "type": type_relation,
        "lentille": lentille,
        "axes": axes,
        "composite": composite,
        "diagnostic": diagnostic,
        "synthese": _synthese(axes),
        "manques": manques,
    }


def _synthese(axes):
    """Le climat d'ensemble + l'axe dominant + le « double whammy ».

    Règle d'Arroyo/Skymates : quand plusieurs couches disent la même chose, c'est
    le cœur du lien. On compte les badges des axes PRÉSENTS ; on ne tranche jamais
    par un chiffre affiché — juste un climat qualitatif et l'axe à mettre en tête.
    """
    presents = {nom: axe["etat"] for nom, axe in axes.items() if axe is not None}
    res = sum(1 for e in presents.values() if e == "resonance")
    ten = sum(1 for e in presents.values() if e == "tension")

    if res and ten:
        climat = "mixte"
    elif res:
        climat = "resonance"
    elif ten:
        climat = "tension"
    else:
        climat = "neutre"

    dominante = next((nom for nom in _PRIORITE_DOMINANTE
                      if presents.get(nom) in ("resonance", "tension")), "nombres")

    # Les axes qui portent et ceux qui bousculent, ORDONNÉS par priorité de
    # lecture (synastrie > chinois > éléments > nombres). C'est cette matière
    # que la synthèse d'intro nomme : le plus fort appui d'abord, puis le plus
    # fort relief. `top_*` = None quand il n'y en a pas (climat neutre ou pur).
    appuis = [nom for nom in _PRIORITE_DOMINANTE if presents.get(nom) == "resonance"]
    reliefs = [nom for nom in _PRIORITE_DOMINANTE if presents.get(nom) == "tension"]

    # Double whammy : un même badge partagé par au moins deux axes.
    whammy_etat = None
    if res >= 2:
        whammy_etat = "resonance"
    if ten >= 2 and ten >= res:
        whammy_etat = "tension"

    return {
        "climat": climat,
        "dominante": dominante,
        "appuis": appuis,
        "reliefs": reliefs,
        "top_appui": appuis[0] if appuis else None,
        "top_bouscule": reliefs[0] if reliefs else None,
        "double_whammy": {"actif": whammy_etat is not None, "etat": whammy_etat},
    }
