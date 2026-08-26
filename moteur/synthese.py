"""L'IDÉE GLOBALE d'un thème — ce qu'on voit avant de plonger.

« Une idée globale, mais qu'on peut facilement aller en demander plus. »

Le Ciel jetait un tableau de treize lignes sans jamais dire l'essentiel. Or un
thème A un essentiel, et il se calcule : ce qui domine, ce qui manque, où ça se
concentre, qui mène. C'est ce que fait un lecteur expérimenté en trente
secondes avant d'entrer dans le détail.

⚠️ Ce module CLASSE et SÉLECTIONNE. Il ne rédige rien : il produit des clés de
corpus. La frontière est la même que partout dans Align — ici on calcule,
ailleurs on lit.

⚠️ L'ordre de lecture est un CHOIX éditorial, assumé et stable : le trio
d'abord (c'est le plus parlant et le plus personnel), puis les équilibres, puis
les concentrations. Un autre astrologue ordonnerait autrement ; ce qui compte
pour du déterministe, c'est que l'ordre ne bouge jamais.
"""
from moteur import aspects as A

# Un élément est « dominant » à partir de 4 planètes sur 10 (la moyenne est
# 2,5), « en creux » à 0 ou 1. Seuils fixes : un seuil qui bouge n'est plus
# déterministe.
SEUIL_DOMINANT = 4
SEUIL_CREUX = 1

MODALITE_DOMINANTE = 5   # sur 10, avec une moyenne à 3,3


def _corps_reels(corps):
    """Les 10 planètes seules. Les angles sont des points, pas des corps —
    les compter fausserait toutes les pesées."""
    return {n: c for n, c in corps.items()
            if n not in ("asc", "mc", "noeud_moyen")}


def trio(theme):
    """Soleil, Lune, Ascendant — le plus parlant, et le plus personnel.

    C'est ce qu'un lecteur veut savoir en premier, et c'est aussi ce qui
    distingue vraiment deux personnes : le Soleil bouge d'un signe par mois,
    la Lune tous les 2,5 jours, l'Ascendant toutes les 2 heures.
    """
    return {
        "soleil": {"signe": theme["corps"]["soleil"]["signe"],
                   "maison": theme["corps"]["soleil"]["maison"]},
        "lune": {"signe": theme["corps"]["lune"]["signe"],
                 "maison": theme["corps"]["lune"]["maison"]},
        "asc": {"signe": theme["angles"]["asc"]["signe"]},
    }


def equilibres(corps):
    """Ce qui domine et ce qui manque, en éléments et en modalités."""
    bilan = A.bilan_elements(corps)
    els, mods = bilan["elements"], bilan["modalites"]

    dominants = sorted([e for e, n in els.items() if n >= SEUIL_DOMINANT],
                       key=lambda e: (-els[e], e))
    creux = sorted([e for e, n in els.items() if n <= SEUIL_CREUX],
                   key=lambda e: (els[e], e))
    mod_dom = sorted([m for m, n in mods.items() if n >= MODALITE_DOMINANTE],
                     key=lambda m: (-mods[m], m))

    return {
        "elements": els,
        "modalites": mods,
        "element_dominant": dominants[0] if dominants else None,
        "element_creux": creux[0] if creux else None,
        "modalite_dominante": mod_dom[0] if mod_dom else None,
        # Un thème sans dominante ni creux est ÉQUILIBRÉ — ce n'est pas un
        # vide à masquer, c'est une information.
        "equilibre": not dominants and not creux,
    }


def hemispheres(corps, cuspides):
    """Au-dessus ou en dessous de l'horizon, à l'est ou à l'ouest.

    Lecture classique et purement géométrique : les maisons 7 à 12 sont
    au-dessus de l'horizon (la vie visible), 1 à 6 en dessous (la vie
    intérieure) ; 10-12 et 1-3 sont à l'est (l'initiative), 4-9 à l'ouest
    (la réponse à autrui).
    """
    reels = _corps_reels(corps)
    haut = sum(1 for c in reels.values() if 7 <= c["maison"] <= 12)
    est = sum(1 for c in reels.values() if c["maison"] >= 10 or c["maison"] <= 3)
    n = len(reels)
    return {
        "haut": haut, "bas": n - haut, "est": est, "ouest": n - est,
        # Marqué seulement si c'est net (7/10) : sinon on raconterait du bruit.
        "vertical": "haut" if haut >= 7 else ("bas" if haut <= 3 else None),
        "horizontal": "est" if est >= 7 else ("ouest" if est <= 3 else None),
    }


def maitre_du_theme(theme, asps):
    """La planète qui maîtrise le signe de l'Ascendant.

    Lecture classique : elle « mène » le thème. On rend aussi sa force, pour
    que le texte puisse dire si ce guide est solide ou en peine.
    """
    signe_asc = theme["angles"]["asc"]["signe"]
    maitres = A.MAITRISE.get(signe_asc, [])
    if not maitres:
        return None
    # Un signe peut avoir deux maîtres (moderne et traditionnel) : on prend le
    # premier de la table, toujours le même — le déterminisme avant l'élégance.
    nom = maitres[0]
    c = theme["corps"].get(nom)
    if not c:
        return None
    f = A.force_planete(nom, theme["corps"], asps)
    return {
        "planete": nom, "signe": c["signe"], "maison": c["maison"],
        "force": f["score"] if f else None,
        "etat": ("solide" if f and f["score"] >= 62
                 else "en peine" if f and f["score"] <= 42 else "moyen"),
    }


def astre_le_plus_en_vue(theme, asps):
    """L'astre le plus fort du thème — celui qui se voit le plus.

    Réutilise le barème de force_planete (angularité, dignité, aspects serrés)
    plutôt que d'en inventer un second : deux barèmes divergeraient.
    """
    scores = []
    for nom in _corps_reels(theme["corps"]):
        f = A.force_planete(nom, theme["corps"], asps)
        if f:
            scores.append((f["score"], nom, f))
    if not scores:
        return None
    # tri stable : score décroissant, puis nom — jamais un `set`, jamais un
    # départage arbitraire
    scores.sort(key=lambda x: (-x[0], x[1]))
    score, nom, f = scores[0]
    c = theme["corps"][nom]
    return {"planete": nom, "signe": c["signe"], "maison": c["maison"],
            "force": score, "raisons": f["raisons"]}


def aspects_marquants(asps, combien=3):
    """Les aspects les plus serrés. Un aspect exact parle plus fort qu'un large."""
    return [a for a in asps if a["orbe"] < 3.0][:combien]


def synthetiser(theme):
    """L'idée globale, prête à lire. Renvoie de la structure et des clés.

    Aucun texte : les textes viennent du corpus, choisis par ces clés.
    """
    corps = dict(theme["corps"])
    corps["asc"] = {"signe": theme["angles"]["asc"]["signe"], "maison": 1,
                    "lon": theme["angles"]["asc"]["lon"]}
    corps["mc"] = {"signe": theme["angles"]["mc"]["signe"], "maison": 10,
                   "lon": theme["angles"]["mc"]["lon"]}
    positions = {n: c["lon"] for n, c in corps.items() if n != "noeud_moyen"}
    vitesses = {n: c.get("vitesse_lon") for n, c in corps.items()}
    asps = A.aspects_entre(positions, vitesses)

    eq = equilibres(corps)
    cles = []
    if eq["element_dominant"]:
        cles.append(("element_dominant", eq["element_dominant"].lower()))
    if eq["element_creux"]:
        cles.append(("element_creux", eq["element_creux"].lower()))
    if eq["modalite_dominante"]:
        cles.append(("modalite_dominante", eq["modalite_dominante"].lower()))
    if eq["equilibre"]:
        cles.append(("equilibre", "equilibre"))
    h = hemispheres(corps, theme["maisons"]["cuspides"])
    if h["vertical"]:
        cles.append(("hemisphere", h["vertical"]))
    if h["horizontal"]:
        cles.append(("hemisphere", h["horizontal"]))

    return {
        "trio": trio(theme),
        "equilibres": eq,
        "hemispheres": h,
        "maitre": maitre_du_theme(theme, asps),
        "en_vue": astre_le_plus_en_vue(theme, asps),
        "stelliums": A.stelliums(corps),
        "aspects_marquants": aspects_marquants(asps),
        "cles": cles,
    }


# Ordre canonique des dix planètes, du plus rapide au plus lent. Il fixe une
# fois pour toutes le sens d'écriture d'une paire : Lune-Soleil et Soleil-Lune
# sont le MÊME aspect, on l'écrit toujours « soleil_lune ». Sans cet ordre, le
# corpus aurait besoin des deux graphies — soit le double de texte à écrire.
ORDRE_PAIRE = ["soleil", "lune", "mercure", "venus", "mars",
               "jupiter", "saturne", "uranus", "neptune", "pluton"]
_RANG = {p: i for i, p in enumerate(ORDRE_PAIRE)}


def cle_aspect(a, b, classe):
    """La clé de corpus d'un aspect entre deux corps, canonique.

    Renvoie None si un angle (asc/mc) est impliqué : le corpus des paires ne
    couvre que les dix planètes. Les aspects aux angles gardent leur rendu
    court par le lexique — écrire 10×2×3 textes d'angle de plus pour un gain
    marginal ne vaut pas la peine, et c'est assumé plutôt que subi.
    """
    if a not in _RANG or b not in _RANG:
        return None
    x, y = sorted((a, b), key=_RANG.__getitem__)
    return f"{x}_{y}_{classe}"


def aspects_d_un_astre(theme, nom, combien=4):
    """Les liens d'un astre avec le reste du thème — les plus serrés d'abord.

    Sert le panneau de détail : quand on ouvre Vénus, on veut aussi savoir
    avec qui elle parle. Chaque lien porte sa `cle` de corpus (ou None pour un
    aspect à un angle).
    """
    corps = dict(theme["corps"])
    corps["asc"] = {"lon": theme["angles"]["asc"]["lon"]}
    corps["mc"] = {"lon": theme["angles"]["mc"]["lon"]}
    positions = {n: c["lon"] for n, c in corps.items() if n != "noeud_moyen"}
    vitesses = {n: c.get("vitesse_lon") for n, c in corps.items()}
    liens = [a for a in A.aspects_entre(positions, vitesses) if nom in a["corps"]]
    out = []
    for a in liens[:combien]:
        autre = a["corps"][1] if a["corps"][0] == nom else a["corps"][0]
        out.append({**a, "autre": autre, "cle": cle_aspect(nom, autre, a["classe"])})
    return out
