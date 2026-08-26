"""LE JOUR — le cœur d'Align, et sa promesse tenue sans un gramme de hasard.

📐 POURQUOI C'EST DIFFÉRENT CHAQUE MATIN SANS AUCUN TIRAGE
Le ciel bouge tout seul. La Lune change de signe tous les 2 jours et demi,
les aspects se font et se défont, l'année personnelle tourne. Un conseil
entièrement déterminé par (naissance, date) est donc neuf chaque jour — la
variété vient du réel, pas d'un dé. C'est la thèse d'Align : le déterminisme
n'est pas une contrainte subie, c'est le produit.

🏗️ ARCHITECTURE À DEUX ÉTAGES
  - Planètes LENTES (Jupiter → Pluton) = le POTENTIEL. Tendance de fond,
    dormante. Elles disent le climat, pas la journée.
  - Planètes RAPIDES (Soleil, Lune, Mercure, Vénus, Mars) = les DÉCLENCHEURS.
    Elles donnent le timing à un ou deux jours près.
  - La LUNE fixe le jour. Son signe donne le ton — mais un aspect dur l'annule.

⚖️ Le moteur CLASSE et SÉLECTIONNE. Il ne rédige rien : les textes viennent du
corpus, choisis par les clés qu'il produit. C'est cette frontière qui garantit
le déterminisme — ici on calcule, ailleurs on lit.

🎯 UNE configuration dominante, pas dix. Un conseil qui énumère n'est pas un
conseil.
"""
from moteur import aspects as A

RAPIDES = ("lune", "mercure", "venus", "soleil", "mars")
LENTES = ("jupiter", "saturne", "uranus", "neptune", "pluton")

# Orbes PRÉDICTIVES — sans rapport avec les orbes natales, et beaucoup plus
# serrées. Un transit agit quand il est juste, pas quand il approche.
ORBES_TRANSIT = {
    "lune": 5.0, "soleil": 3.0, "mercure": 3.0, "venus": 3.0,
    "mars": 2.0,          # Mars agit EN AVANCE -> on lui laisse du large
    "jupiter": 1.0, "saturne": 1.0, "uranus": 1.0, "neptune": 1.0,
    "pluton": 3.0,        # Pluton porte loin en applicatif
}

# Ce qui compte quand un transit touche une cible natale. Les luminaires et
# les angles priment : c'est là que ça se sent.
#
# Plage COMPRESSÉE (0,66–0,95 au lieu de 0,5–1,0). Une plage étalée faisait
# que le même aspect à un point natal « lourd » (Soleil, Asc) gagnait même
# quand un autre transit, plus juste astronomiquement, était en lice. En
# resserrant les poids, l'EXACTITUDE redevient le critère qui départage — et
# le ciel réel, qui bouge, décide davantage du dominant que la table fixe.
# Mesuré : +20 % de dominantes distinctes sur l'année, sans dégrader la
# primauté des luminaires (Lune et Soleil restent en tête de plage).
POIDS_CIBLE = {
    "soleil": 0.9, "lune": 0.95, "asc": 0.9, "mc": 0.88,
    "mercure": 0.82, "venus": 0.82, "mars": 0.82,
    "saturne": 0.74, "jupiter": 0.74,
    "uranus": 0.66, "neptune": 0.66, "pluton": 0.66,
}

# carre-opposition raboté (0,9 → 0,82) : les aspects durs sont astronomiquement
# les plus fréquents (carré + opposition = 3 contacts sur 4), le bonus les
# laissait dominer par routine plutôt que par justesse. Le sextile/trigone
# remonte légèrement (0,7 → 0,72) pour la même raison, à l'inverse.
POIDS_CLASSE = {"conjonction": 1.0, "carre-opposition": 0.82, "sextile-trigone": 0.72}

# Sous cet écart de force avec le leader, deux déclencheurs sont jugés
# COMPARABLES : la sélection sensible à la récurrence peut alors préférer le
# moins récent. Au-delà, le leader est net et gagne — on n'affiche jamais un
# transit faible au nom de la variété.
MARGE_COMPARABLES = 0.12


def _ecart(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def transits(theme, positions_du_jour, vitesses_du_jour=None):
    """Les contacts entre le ciel du jour et le thème natal.

    Chaque transit reçoit une FORCE 0-1 : c'est elle qui décidera lequel
    parle aujourd'hui. Le classement est le vrai travail — un thème a toujours
    des dizaines de contacts, et les énumérer n'aide personne.
    """
    natal = {n: c["lon"] for n, c in theme["corps"].items() if n != "noeud_moyen"}
    natal["asc"] = theme["angles"]["asc"]["lon"]
    natal["mc"] = theme["angles"]["mc"]["lon"]

    trouves = []
    for t_nom, t_lon in positions_du_jour.items():
        if t_nom == "noeud_moyen":
            continue
        orbe_max = ORBES_TRANSIT.get(t_nom, 1.0)
        for n_nom, n_lon in natal.items():
            d = _ecart(t_lon, n_lon)
            for a_nom, (angle, _, classe) in A.ASPECTS.items():
                delta = abs(d - angle)
                if delta > orbe_max:
                    continue
                exactitude = 1.0 - delta / orbe_max
                force = (exactitude
                         * POIDS_CLASSE[classe]
                         * POIDS_CIBLE.get(n_nom, 0.5)
                         * (1.0 if t_nom in RAPIDES else 0.85))
                tr = {
                    "transit": t_nom,
                    "natal": n_nom,
                    "aspect": a_nom,
                    "classe": classe,
                    "orbe": delta,
                    "exactitude": exactitude,
                    "force": force,
                    "etage": "declencheur" if t_nom in RAPIDES else "potentiel",
                    "cle": f"{t_nom}_{classe}_{n_nom}",
                }
                if vitesses_du_jour and t_nom in vitesses_du_jour:
                    v = vitesses_du_jour[t_nom]
                    if v is not None:
                        avant = abs(_ecart(t_lon - v * 0.1, n_lon) - angle)
                        tr["applicatif"] = delta < avant
                        if tr["applicatif"]:
                            tr["force"] *= 1.15    # l'applicatif est plus fort
                trouves.append(tr)
                break
    trouves.sort(key=lambda x: -x["force"])
    return trouves


def phase_lunaire(lon_soleil, lon_lune):
    """Les 8 phases — pur calcul : (Lune − Soleil) mod 360, par tranches de 45°.

    Applicable deux fois : en natal (un tempérament) et au quotidien (un
    moment du cycle). Même formule, deux lectures.
    """
    ecart = (lon_lune - lon_soleil) % 360.0
    i = int(ecart // 45)
    noms = ["nouvelle", "croissante", "premier_quartier", "gibbeuse",
            "pleine", "diffusante", "dernier_quartier", "balsamique"]
    return {"phase": noms[i], "index": i, "ecart": ecart,
            "progression": (ecart % 45) / 45.0}


def lune_du_jour(theme, lon_lune):
    """Où la Lune passe dans le thème. C'est elle qui fixe le jour."""
    cusp = theme["maisons"]["cuspides"]
    from moteur.theme import maison_de, signe_de
    return {**signe_de(lon_lune), "maison": maison_de(lon_lune, cusp)}


def choisir_dominante(declencheurs, recents, marge=MARGE_COMPARABLES):
    """Parmi les déclencheurs comparables au leader, le MOINS RÉCENT gagne.

    La règle historique — « le plus fort gagne, point » — laissait un transit
    serré dominer toute une semaine : une station rétrograde tient plusieurs
    jours à moins de 1° d'exact, donc le même message s'affichait jour après
    jour. On brise ces blocs. Tant que des déclencheurs sont comparables au
    leader (dans la marge), on préfère celui qu'on n'a PAS montré récemment.

    `recents` : liste des clés dominantes des N jours précédents, du plus
    ancien au plus récent (recents[-1] = hier). Calculée en amont, de façon
    déterministe — cette fonction est PURE, sans accès à l'éphéméride. Le
    bord gauche de la fenêtre s'amorce naturellement en naïf (pas de passé
    connu → on départage par la force), ce qui borne le regard en arrière.

    Un leader NET (au-delà de la marge) gagne quand même : `candidats` se
    réduit alors à lui seul, et on le renvoie tel quel.
    """
    if not declencheurs:
        return None
    seuil = declencheurs[0]["force"] - marge
    candidats = [d for d in declencheurs if d["force"] >= seuil]
    if len(candidats) == 1:
        return candidats[0]

    # Dernière apparition de chaque clé dans la fenêtre (le plus grand indice
    # l'emporte = l'occurrence la plus récente). Jamais vue → absente du dict,
    # donc -1 au .get : le moins récent possible, donc préférée.
    dernier = {}
    for i, cle in enumerate(recents):
        if cle:
            dernier[cle] = i

    def cle_tri(d):
        vu = dernier.get(d["cle"], -1)   # -1 = jamais vu → d'abord
        return (vu, -d["force"], d["cle"])   # peu vu, puis fort, puis stable

    candidats.sort(key=cle_tri)
    return candidats[0]


def journee(theme, positions_du_jour, vitesses_du_jour, annee_perso, carte_annee,
            carte_jour=None, mois_perso=None, recents=None):
    """La journée : ce qui domine, et rien d'autre.

    Renvoie des CLÉS de corpus, jamais du texte. La sélection est le produit ;
    la rédaction est ailleurs.

    Trois échelles de temps s'empilent, de la plus lente à la plus rapide :
      - l'ANNÉE personnelle (9 ans), qui donne le chapitre ;
      - le MOIS personnel (9 mois), qui donne la saison ;
      - le CIEL du jour, qui donne la journée.
    Elles s'ADDITIONNENT, comme tout le reste — jamais un produit.

    ⚠️ Il n'existe PAS de « jour personnel » chez Align : ni Phillips ni
    Castells n'en ont un, et l'inventer serait de la doctrine maison. Le jour
    vient du ciel, qui bouge tout seul — c'est ce qui fait la variété.
    """
    tous = transits(theme, positions_du_jour, vitesses_du_jour)
    lune = lune_du_jour(theme, positions_du_jour["lune"])
    phase = phase_lunaire(positions_du_jour["soleil"], positions_du_jour["lune"])

    declencheurs = [t for t in tous if t["etage"] == "declencheur"]
    potentiels = [t for t in tous if t["etage"] == "potentiel"]

    # LA règle : le signe de la Lune donne le ton, MAIS un aspect dur l'annule.
    # Elle est déterministe, et elle évite le travers du « aujourd'hui la Lune
    # est en Balance donc tout est doux » alors qu'elle est carrée à Saturne.
    dur_sur_lune = [t for t in declencheurs
                    if t["transit"] == "lune" and t["classe"] == "carre-opposition"
                    and t["exactitude"] > 0.5]

    # La dominante : naïve (le plus fort) par défaut — la sélection sensible
    # à la récurrence n'a de sens qu'avec une fenêtre de regard en arrière,
    # fournie par l'app (`recents`). Sans elle (tests, calculs isolés), on
    # reste sur la règle historique. Voir `choisir_dominante`.
    if recents is not None and declencheurs:
        dominante = choisir_dominante(declencheurs, recents)
    else:
        dominante = declencheurs[0] if declencheurs else (tous[0] if tous else None)

    return {
        "lune": lune,
        "phase": phase,
        "ton_lunaire_annule": bool(dur_sur_lune),
        "nuance": dur_sur_lune[0] if dur_sur_lune else None,
        "dominante": dominante,
        "declencheurs": declencheurs[:3],
        "potentiel": potentiels[:2],
        "annee_personnelle": annee_perso,
        "mois_personnel": mois_perso,
        "carte_annee": carte_annee,
        "carte_jour": carte_jour,
        "cles": _cles(dominante, lune, phase, annee_perso, dur_sur_lune, mois_perso),
    }


# Le Fil du jour : la maison de la Lune donne le DOMAINE de vie (correspondance
# classique des maisons — imprimé). C'est l'ANCRE ; le transit dominant et la
# phase donnent la nuance. La Lune change de maison tous les ~2,5 jours, donc le
# domaine tourne tout seul, comme le reste — la variété vient du ciel, pas d'un dé.
MAISON_DOMAINE = {
    1: "soi", 2: "ressources", 3: "echanges", 4: "racines",
    5: "creation", 6: "quotidien", 7: "autre", 8: "traversee",
    9: "sens", 10: "metier", 11: "communaute", 12: "retrait",
}
# Les domaines à PROCESSUS : leur perle suit le cycle des 8 phases lunaires
# (commencer, tenir, montrer, se reposer…). Ailleurs, une phase plaquée serait
# arbitraire — on s'en tient à la tonalité fluide/tension.
DOMAINES_A_PHASE = frozenset({"creation", "quotidien", "metier"})


def _cles_fil_domaine(domaine, dominante, phase):
    """Les clés candidates pour UN domaine donné, de la plus précise à la plus
    générale — indépendamment de la façon dont ce domaine a été choisi.

    Partagée par deux chemins :
      - `_cles_fil` : le domaine du JOUR, dérivé de la maison de la Lune ;
      - Explorer : un domaine choisi par la personne elle-même, la nuance du
        jour continuant de tourner avec le ciel réel — jamais un texte figé.

    Le moteur ÉMET, le corpus FILTRE : `corpus.lire()` prend la première clé
    qui existe (précis → générique), exactement comme les transits.
      1. le transit dominant (planète + classe) — le raffinement du jour ;
      2a. pour un domaine à processus : la phase lunaire (le cycle, le socle) ;
      2b. sinon : la tonalité (fluide si l'aspect coule, tension s'il est dur) ;
      3. le domaine seul — le socle générique, qui résout toujours.

    Volontairement AUCUNE clé lente (année, mois) : une entrée par année
    afficherait le même texte 365 jours. La variété vient du ciel réel.
    """
    if domaine not in MAISON_DOMAINE.values():
        return []
    cles = []
    if dominante:
        cles.append(f"{domaine}_transit_{dominante['transit']}_{dominante['classe']}")
    if domaine in DOMAINES_A_PHASE:
        cles.append(f"{domaine}_phase_{phase['phase']}")
    elif dominante:
        tonalite = "tension" if dominante["classe"] == "carre-opposition" else "fluide"
        cles.append(f"{domaine}_{tonalite}")
    cles.append(domaine)
    return cles


def _cles_fil(dominante, phase, lune):
    """Le Fil du jour : le domaine est imposé par le ciel (maison de la Lune),
    pas choisi. Voir `_cles_fil_domaine` pour la résolution à l'intérieur du
    domaine, partagée avec Explorer."""
    domaine = MAISON_DOMAINE.get(lune["maison"])
    if not domaine:
        return []
    return _cles_fil_domaine(domaine, dominante, phase)


def _cles(dominante, lune, phase, annee_perso, dur_sur_lune, mois_perso=None):
    """Les clés de corpus à lire, par ordre de priorité.

    Additives et indépendantes — jamais un produit cartésien. C'est ce qui
    rend le corpus rédigeable à la main : on écrit N + M entrées, pas N × M.
    """
    cles = []
    if dominante:
        cles.append(("transit", dominante["cle"]))
    cles.append(("lune_maison", f"lune_maison_{lune['maison']}"))
    cles.append(("phase", f"phase_{phase['phase']}"))
    if mois_perso:
        cles.append(("mois_perso", f"mois_{mois_perso}"))
    cles.append(("annee_perso", f"annee_{annee_perso}"))
    if dur_sur_lune:
        cles.append(("nuance", "ton_lunaire_contrarie"))
    # Le Fil du jour : UNE clé par genre, comme partout ailleurs — le
    # fallback (domaine → transit → phase/tonalité → générique) se résout à
    # la lecture, dans app.py, exactement comme "transit" résout précis →
    # générique. La clé ici sert de repère de traçabilité (debug, tests) : le
    # domaine du jour, dérivé de la maison de la Lune. app.py relit
    # dominante/phase/lune pour construire les candidates via _cles_fil.
    cles.append(("fil", MAISON_DOMAINE.get(lune["maison"], "fil")))
    return cles


def gestes_redondants(textes, seuil=2):
    """Deux gestes qui commencent pareil sur le MÊME écran.

    Le corpus peut être parfaitement varié dans l'absolu et pourtant servir
    deux « Nomme, pour toi seul… » le même matin : les tables sont écrites
    séparément, mais elles sont LUES ensemble. Aucun test global ne voit ça —
    seule la lecture du jour assemblé le révèle.

    On ne réécrit rien et on ne masque rien : on SIGNALE, et l'app choisit de
    n'afficher qu'un seul des deux gestes. Un conseil qui se répète dans la
    même page s'annule lui-même.
    """
    vus = {}
    doublons = []
    for genre, t in textes.items():
        geste = (t or {}).get("geste") if isinstance(t, dict) else None
        if not geste:
            continue
        tete = " ".join(geste.split()[:seuil]).lower().strip(",")
        if tete in vus:
            doublons.append((vus[tete], genre, tete))
        else:
            vus[tete] = genre
    return doublons
