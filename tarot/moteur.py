"""Moteur de composition — assemble la lecture d'un tirage à trois.

Déterministe : même tirage ⇒ même lecture. Pure fonction des cartes tirées
et des tables (`data/grammaire/tables.json`). Spec : GRAMMAIRE.md §5.

Ordre de la lecture rendue :
  seuil → cartes (textes de position, gérés par l'UI) → liaisons → motifs → clôture
Le plafond « 2 motifs max » (Pollack : le déversement de détails est un échec)
et la règle de la carte-ressource (clôture sur une ressource, jamais un verdict)
sont appliqués ici, une seule fois, pour toute l'app.
"""
import json
import pathlib
import re

RACINE = pathlib.Path(__file__).parent
TABLES = json.loads((RACINE / "data" / "grammaire" / "tables.json").read_text(encoding="utf-8"))

SEUILS = TABLES["seuils_moteur"]
POIDS_POSITION = {"essayer": 3, "se_joue": 2, "amene": 1, "jour": 2}


def element_de(carte):
    e = carte.get("element")
    if e:
        return e
    return carte.get("famille")


# « de feu » mais « d'eau », « d'air » : l'élision dépend de la première lettre.
DE_FAMILLE = {"feu": "de feu", "eau": "d'eau", "air": "d'air", "terre": "de terre"}


def type_liaison(e1, e2):
    """Type de liaison élémentaire entre deux éléments (symétrique).
    Même élément = pas une liaison : c'est un écho de famille."""
    if not e1 or not e2 or e1 == e2:
        return None
    for nom in ("renforce", "neutralise", "tension"):
        for paire in TABLES["liaisons"][nom]["paires"]:
            if {e1, e2} == set(paire):
                return nom
    return None


def colonne_de(id_carte):
    for num, col in TABLES["colonnes"].items():
        if num.startswith("_") or not isinstance(col, dict):
            continue
        if id_carte in col["cartes"]:
            return num, col["motif"]
    return None, None


def famille_dominante(cartes):
    """(famille, nombre) dominante du tirage, ou (None, 0) sous le seuil.
    Une seule définition pour le seuil, l'écho et le motif de dominance."""
    compteur = {}
    for c in cartes:
        f = c.get("famille")
        if f:
            compteur[f] = compteur.get(f, 0) + 1
    if not compteur:
        return None, 0
    fam = max(compteur, key=compteur.get)
    if compteur[fam] >= SEUILS["famille_dominante_min"]:
        return fam, compteur[fam]
    return None, 0


def phrases_seuil(cartes):
    """(phrase de seuil, famille déjà expliquée ou None).
    La famille expliquée en ouverture n'est pas réexpliquée plus bas : une
    même famille ne reçoit sa glose qu'une fois par lecture."""
    majeurs = [c for c in cartes if c.get("type") == "majeur"]
    if len(majeurs) >= SEUILS["majeurs_passage_de_vie"]:
        return TABLES["motifs"]["seuil_passage"], None
    fam, _ = famille_dominante(cartes)
    if fam:
        return TABLES["motifs"]["seuil_famille"][fam], fam
    return TABLES["motifs"]["seuil_neutre"], None


def _phrase_echo_famille(cartes, familles_expliquees=()):
    """Écho de famille pour deux ou trois cartes (jamais « Deux » pour trois).
    La glose n'apparaît que si la famille n'a pas déjà été expliquée ailleurs."""
    noms = _join_et(c["nom"] for c in cartes)
    fam = cartes[0]["famille"]
    gabarit = TABLES["motifs"]["echo_famille"]
    if len(cartes) > 2:
        gabarit = gabarit.replace("Deux cartes", "Trois cartes", 1)
        gabarit = gabarit.replace("deux fois de suite", "trois fois de suite")
    if fam in familles_expliquees:
        gabarit = gabarit.replace("{glose}. ", "")
    else:
        gabarit = gabarit.replace("{glose}", TABLES["gloses"][fam].rstrip("."))
    return gabarit.replace("{famille}", DE_FAMILLE[fam]).replace("{noms}", noms)


def phrases_liaisons(cartes, familles_expliquees=()):
    """Les liaisons des paires adjacentes (1→2, 2→3), phrases écrites.
    La clé de paire est la liste triée des éléments (« air|feu ») : chaque
    paire a SON gabarit, qui nomme les deux familles.

    Les liaisons consécutives du MÊME type forment une CHAÎNE (A→B→A : les
    éléments alternent) — elles fusionnent en une seule phrase qui traverse
    toutes les cartes, au lieu de répéter deux fois la même phrase.
    Les échos consécutifs de même famille fusionnent aussi (trois cartes
    d'une seule famille = une phrase, pas deux)."""
    brutes = []
    for a, b in zip(cartes, cartes[1:]):
        e1, e2 = element_de(a), element_de(b)
        t = type_liaison(e1, e2)
        if t:
            cle = "|".join(sorted([e1, e2]))
            texte = TABLES.get("liaisons_paires", {}).get(cle) \
                or TABLES["liaisons"][t]["texte"]
            # la paire nommée, en ordre de lecture, avec son élément :
            # « Lâcher-prise (eau) et Changement (feu) » — jamais ambiguë.
            noms = f"{a['nom']} ({e1}) et {b['nom']} ({e2})"
            texte = texte.replace("{noms}", noms)
            brutes.append({"cle": cle, "type": t, "elems": (e1, e2),
                           "cartes": [a, b], "de": a["id"], "vers": b["id"],
                           "phrase": texte})
        elif e1 == e2:
            if a.get("type") == "majeur" and b.get("type") == "majeur":
                phrase = TABLES["motifs"]["echo_majeures"].replace(
                    "{nom_a}", a["nom"]).replace("{nom_b}", b["nom"])
                kind = "majeures"
            elif a.get("famille") and b.get("famille"):
                phrase = _phrase_echo_famille([a, b], familles_expliquees)
                kind = "famille"
            else:
                # quel que soit l'ordre du tirage, on nomme la majeure et la mineure
                majeure = a if a.get("type") == "majeur" else b
                mineure = b if majeure is a else a
                phrase = TABLES["motifs"]["echo_mixte"].replace(
                    "{nom_majeure}", majeure["nom"]).replace(
                    "{nom_mineure}", mineure["nom"])
                kind = "mixte"
            brutes.append({"cle": f"echo|{e1}", "type": "echo",
                           "echo_kind": kind,
                           "elems": (e1, e2), "cartes": [a, b],
                           "de": a["id"], "vers": b["id"], "phrase": phrase})

    # fusion des chaînes : liaisons ou échos consécutifs de même clé → une phrase
    sorties = []
    i = 0
    while i < len(brutes):
        l = brutes[i]
        j = i
        while j + 1 < len(brutes) and brutes[j + 1]["cle"] == l["cle"] \
                and brutes[j + 1]["type"] == l["type"] \
                and brutes[j + 1].get("echo_kind") == l.get("echo_kind"):
            j += 1
        if j == i:
            sorties.append(l)
        else:
            chaine = l["cartes"][:1]
            for x in range(i, j + 1):
                chaine.append(brutes[x]["cartes"][1])
            if l["type"] == "echo":
                fam = chaine[0].get("famille")
                if fam and all(c.get("famille") == fam for c in chaine):
                    phrase = _phrase_echo_famille(chaine, familles_expliquees)
                elif all(c.get("type") == "majeur" for c in chaine):
                    gabarit = TABLES["motifs"]["echo_majeures"].replace(
                        "Deux cartes majeures", "Trois cartes majeures", 1)
                    phrase = gabarit.replace(
                        "{nom_a} et {nom_b}",
                        _join_et(c["nom"] for c in chaine))
                else:
                    # échos mixtes : les phrases d'origine, bout à bout
                    phrase = " ".join(brutes[x]["phrase"] for x in range(i, j + 1))
                sorties.append({"cle": l["cle"], "type": "echo", "chaine": True,
                                "de": l["de"], "vers": brutes[j]["vers"],
                                "cartes": chaine, "phrase": phrase})
            else:
                # chaque carte porte son élément entre parenthèses : l'attribution
                # du rythme devient visible pour chaque carte nommée.
                noms = _join_et(f"{c['nom']} ({element_de(c)})" for c in chaine)
                gabarit = TABLES.get("chaines", {}).get(l["cle"])
                phrase = gabarit.replace("{noms}", noms) if gabarit else \
                    " — ".join(b["phrase"] for b in brutes[i:j + 1])
                sorties.append({"cle": l["cle"], "type": l["type"], "chaine": True,
                                "de": l["de"], "vers": brutes[j]["vers"],
                                "phrase": phrase})
        i = j + 1
    return sorties


def _join_et(noms):
    """« X et Y » pour deux, « X, Y et Z » pour trois — la liste des noms."""
    noms = list(noms)
    if len(noms) <= 1:
        return "".join(noms)
    return ", ".join(noms[:-1]) + " et " + noms[-1]


def phrases_motifs(cartes, familles_expliquees=(), familles_echo=()):
    """Motifs de champ : comptages purs, seuils de `tables.json`,
    plafonnés au deux plus prioritaires (ordre du dictionnaire des seuils).

    Une famille n'est expliquée qu'une fois par lecture : si la glose a déjà
    été donnée (seuil), le motif de dominance ne la répète pas. Et si un écho
    a déjà parlé de cette famille, le motif de dominance lui cède la place —
    la prudence « pas un verdict » rejoint l'écho dans `composer`."""
    degres = [str(c.get("degre")) for c in cartes if c.get("degre") is not None]
    majeurs = [c for c in cartes if c.get("type") == "majeur"]
    figures = [c for c in cartes if c.get("type") == "figure"]
    hors_cycle = [c for c in cartes if c.get("type") == "hors_cycle"]

    motifs = []

    # proportions de majeurs
    if len(majeurs) >= SEUILS["majeurs_passage_de_vie"]:
        motifs.append(TABLES["motifs"]["majeurs_passage"].replace(
            "{noms}", _join_et(c["nom"] for c in majeurs)))
    elif len(majeurs) == 0 and not hors_cycle:
        motifs.append(TABLES["motifs"]["aucun_majeur"])

    # famille absente — la plus informative, avant la dominance
    # (première absente dans l'ordre de la création : feu → eau → air → terre)
    # ⚠ on compte les ÉLÉMENTS de toutes les cartes (majeurs compris) : dire
    # « aucune carte de feu » alors qu'une majeure de feu est posée serait faux.
    elements = [element_de(c) for c in cartes if element_de(c)]
    if len(elements) >= SEUILS["absence_famille_min_mineurs"]:
        absentes = [f for f in TABLES["familles"] if f not in elements]
        if absentes:
            motifs.append(TABLES["motifs"]["famille_absente"][absentes[0]])

    # écho de nombre (degré répété)
    compte = {}
    noms_degre = {}
    for c in cartes:
        if c.get("degre") is None:
            continue
        g = str(c["degre"])
        compte[g] = compte.get(g, 0) + 1
        noms_degre.setdefault(g, []).append(c["nom"])
    for degre, n in compte.items():
        if n >= SEUILS["echo_nombre_min"]:
            texte = TABLES["degres"][degre]["texte"]
            motifs.append(TABLES["motifs"]["nombre_repete"].replace(
                "{noms}", _join_et(noms_degre.get(degre, []))).replace(
                "{texte}", texte))
            break

    # famille dominante
    fam, n_fam = famille_dominante(cartes)
    if fam and fam not in familles_echo:
        gabarit = TABLES["motifs"]["famille_dominante"]
        if n_fam > 2:
            gabarit = gabarit.replace("Deux cartes", "Trois cartes", 1)
        noms = _join_et(c["nom"] for c in cartes if c.get("famille") == fam)
        if fam in familles_expliquees:
            gabarit = gabarit.replace("{glose}. ", "")
        else:
            gabarit = gabarit.replace("{glose}", TABLES["gloses"][fam].rstrip("."))
        motifs.append(gabarit.replace(
            "{famille}", DE_FAMILLE[fam]).replace("{noms}", noms))

    # densité de figures
    if len(figures) >= SEUILS["figures_densite_min"]:
        motifs.append(TABLES["motifs"]["figures_densite"])

    # écho de colonne (majeurs)
    colonnes_vus = {}
    for c in majeurs:
        num, _ = colonne_de(c["id"])
        if num:
            colonnes_vus.setdefault(num, []).append(c["nom"])
    for num, noms in sorted(colonnes_vus.items()):
        if len(noms) >= 2:
            motifs.append(TABLES["motifs"]["meme_colonne"].replace(
                "{motif}", TABLES["colonnes"][num]["motif"]).replace(
                "{nom_a}", noms[0]).replace("{nom_b}", noms[1]))
            break

    # hors cycle (Éveil) : toujours mentionné, sans interprétation lourde
    if hors_cycle:
        motifs.append(TABLES["motifs"]["hors_cycle"])

    return motifs[: SEUILS["motifs_max"]]


def carte_ressource(cartes, liaisons):
    """La carte la plus porteuse : forces entrantes (liaisons renforcées
    + échos), départage par position (essayer > se_joue > amène), puis id."""
    force = {c["id"]: 0 for c in cartes}

    def poids_position(i):
        pos = ["amene", "se_joue", "essayer"][i] if i < 3 else "jour"
        return POIDS_POSITION.get(pos, 0)

    for l in liaisons:
        if l["type"] in ("renforce", "echo"):
            force[l["vers"]] += 2
    classees = sorted(enumerate(cartes),
                      key=lambda pair: (-force.get(pair[1]["id"], 0),
                                        -poids_position(pair[0]),
                                        pair[1]["id"]))
    return classees[0][1]


def _de_verbe(verbe):
    """« de attendre » → « d'attendre » : l'élision devant une voyelle."""
    v = str(verbe or "").strip()
    return ("d'" if v[:1] and v[:1].lower() in "aeiouyh" else "de ") + v


def _premiere_phrase(texte):
    """La première phrase d'un texte, pour nommer un blocage sans le jargon
    des verbes nus (« elle pousse puiser »)."""
    texte = (texte or "").strip()
    if not texte:
        return ""
    m = re.match(r"(.+?[.!?])(\s|$)", texte)
    return (m.group(1) if m else texte).strip()


def percee(cartes, liaisons, ressource, cle_tiree=None):
    """Le protocole de clôture : blocage → ressource → carte clé → geste.

    Le blocage est la carte qui reçoit le plus de friction (liaisons de
    tension ou de neutralisation : entrantes deux fois, sortantes une fois).
    Quand le tirage n'en contient aucune, c'est la carte la moins soutenue.
    La ressource est celle du moteur ; la carte clé fait le pont entre les
    deux. Aucune carte nouvelle, aucun texte nouveau par carte : la percée
    relit ce qui est déjà posé.
    """
    if len(cartes) < 2:
        return None
    P = TABLES["percee"]
    ordre = {c["id"]: i for i, c in enumerate(cartes)}
    friction = {c["id"]: 0 for c in cartes}
    soutien = {c["id"]: 0 for c in cartes}
    for l in liaisons:
        if l.get("type") in ("tension", "neutralise"):
            if l.get("vers") in friction:
                friction[l["vers"]] += 2
            if l.get("de") in friction:
                friction[l["de"]] += 1
        elif l.get("vers") in soutien:
            soutien[l["vers"]] += 1

    if max(friction.values()) > 0:
        blocage = max(cartes, key=lambda c: (friction[c["id"]], -ordre[c["id"]]))
    else:
        # tirage sans friction : le point fragile est la carte la moins soutenue
        blocage = min(cartes, key=lambda c: (soutien[c["id"]], ordre[c["id"]]))
    # le blocage : la première phrase de l'ombre de la carte (sa voix, concrète)
    tension_blocage = blocage.get("tension") or {}
    ombre = (blocage.get("ombre") or {}).get("texte") or ""
    phrase_blocage = _premiere_phrase(ombre)
    if not phrase_blocage:
        if tension_blocage.get("pousse") and tension_blocage.get("retient"):
            phrase_blocage = P["blocage_repli"].replace(
                "{pousse}", tension_blocage["pousse"]).replace(
                "de {retient}", _de_verbe(tension_blocage["retient"]))
        else:
            phrase_blocage = P["fragile"]

    tension_ressource = ressource.get("tension") or {}
    if tension_ressource.get("pousse"):
        phrase_ressource = P["ressource"].replace(
            "{nom}", ressource["nom"]).replace(
            "{pousse}", tension_ressource["pousse"])
    else:
        phrase_ressource = P["ressource_simple"]

    if cle_tiree is not None:
        cle = cle_tiree
        phrase_cle = P["cle_tiree"]
    elif blocage["id"] == ressource["id"]:
        cle = ressource
        phrase_cle = P["cle_seule"]
    else:
        pont = [c for c in cartes
                if c["id"] not in (blocage["id"], ressource["id"])]
        cle = pont[0] if pont else ressource
        phrase_cle = P["cle_pont"]

    geste = cle.get("micro_geste")
    phrase_geste = P["geste"].replace("{geste}", geste) if geste \
        else P["geste_absent"]

    return {
        "titre": P["titre"],
        "blocage": {"nom": blocage["nom"], "phrase": phrase_blocage},
        "ressource": {"nom": ressource["nom"], "phrase": phrase_ressource},
        "cle": {"nom": cle["nom"], "phrase": phrase_cle},
        "geste": {"nom": cle["nom"], "phrase": phrase_geste},
        "note": P["note"],
    }


def composer_etendu(cartes, cle):
    """Le 9 + 1 : trois rangées de trois lues en trois temps, puis la clé.

    Les neuf cartes sont disposées en colonnes (les plans) et en rangées
    (les niveaux) ; chaque rangée a ses liaisons propres — c'est le « trois
    temps » de Greer. La dixième carte, tirée après les neuf autres, sert de
    clé d'intégration : la percée s'appuie sur elle.
    """
    rangees = []
    toutes = []
    for debut in (0, 3, 6):
        trio = cartes[debut:debut + 3]
        liaisons = phrases_liaisons(trio)
        toutes.extend(liaisons)
        rangees.append({"cartes": [c["id"] for c in trio], "liaisons": liaisons})
    ressource = carte_ressource(cartes, toutes)
    return {"rangees": rangees,
            "percee": percee(cartes, toutes, ressource, cle)}


def composer(cartes):
    """cartes : liste des dicts du tirage (ordre de lecture 1→2→3), tels que
    renvoyés par /api/tirage. Retourne la lecture structurée pour l'UI."""
    seuil, famille_seuil = phrases_seuil(cartes)
    expliquees = {famille_seuil} if famille_seuil else set()

    liaisons = phrases_liaisons(cartes, expliquees)

    familles_echo = {
        l["cle"].split("|", 1)[1] for l in liaisons
        if l["type"] == "echo" and "|" in l["cle"]
    } & {c.get("famille") for c in cartes}

    # la prudence « pas un verdict » rejoint l'écho qui parle de la même
    # famille, au lieu d'un second paragraphe qui redit la même chose.
    fam, _n = famille_dominante(cartes)
    if fam and fam in familles_echo:
        prudence = TABLES["motifs"]["famille_dominante"].split("{glose}. ", 1)[1].strip()
        # une seule fois : le premier écho qui parle de cette famille
        for l in liaisons:
            if l["type"] == "echo" and l["cle"] == f"echo|{fam}":
                l["phrase"] = l["phrase"].rstrip() + " " + prudence
                break

    motifs = phrases_motifs(cartes, expliquees, familles_echo)

    ressource = carte_ressource(cartes, liaisons)
    question = (ressource.get("questions") or [""])[0] if ressource.get("questions") else ""
    return {
        "seuil": seuil,
        "liaisons": liaisons,
        "motifs": motifs,
        "cloture": {
            "nom": ressource["nom"],
            "question": question,
            "micro_geste": ressource.get("micro_geste", ""),
            # la grille « leçon · geste · question » clôt sur la leçon : le
            # geste est déjà lu en position 2, on ne le répète pas
            "lecon": ressource.get("lecon", ""),
        },
        "percee": percee(cartes, liaisons, ressource),
        "_ressource": ressource["id"],
    }
