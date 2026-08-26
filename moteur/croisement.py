"""LE CROISEMENT — ce qui fait Align, et que personne d'autre ne fait.

Les apps qui « croisent » astrologie, numérologie et tarot les JUXTAPOSENT :
trois lectures côte à côte, sans lien. Align les CROISE, et par une charnière
qui n'est pas inventée pour l'occasion :

    date de naissance
        ├──► carte calculée (Arrien/Greer, 1977)
        │         └──► correspondance Golden Dawn (Mathers, 1888)
        │                   └──► une PLANÈTE, un SIGNE ou un ÉLÉMENT
        │                             └──► qu'on va lire dans le THÈME RÉEL
        │                                       │
        │                             ┌─────────┴─────────┐
        │                             ▼                   ▼
        │                        RÉSONANCE            TENSION
        │                    (le facteur est      (le facteur est
        │                     fort dans le          en difficulté
        │                     thème)                ou absent)
        │
        └──► nombres (pythagoriciens)
                  └──► accords et frottements avec le thème

Les 22 arcanes correspondent exactement à 12 signes + 7 planètes classiques +
3 éléments. Ce n'est pas une analogie décorative : c'est la structure
historique, et elle se referme sans reste.

⚠️ RÈGLE ABSOLUE — rédiger DEPUIS LA CARTE, jamais depuis le nombre.
Le 4 numérologique évoque la structure et l'autorité ; l'arcane 4 est
L'Empereur ; mais son sens en lecture zen bascule vers la révolte contre
l'autorité. Dériver l'un de l'autre produirait des contresens.

⚠️ Ni résonance ni tension ne sont un verdict. Une tension n'est pas un
mauvais présage : c'est l'endroit où il y a du travail — et donc, dans le
cadrage d'Align, l'endroit intéressant.
"""
from moteur import aspects as A
from moteur import numerologie as N
from moteur import tarot as T

SEUIL_FORT = 62
SEUIL_FAIBLE = 42


def _lire_planete(planete, corps, asps):
    f = A.force_planete(planete, corps, asps)
    if f is None:
        return None
    if f["score"] >= SEUIL_FORT:
        etat = "resonance"
    elif f["score"] <= SEUIL_FAIBLE:
        etat = "tension"
    else:
        etat = "neutre"
    return {
        "cible": planete, "type": "planete", "etat": etat,
        "score": f["score"], "raisons": f["raisons"],
        "position": {"signe": corps[planete]["signe"], "maison": corps[planete]["maison"]},
    }


def _lire_signe(signe, corps, asps):
    """Un signe est fort s'il est habité, angulaire, ou si son maître est fort."""
    habitants = [n for n, c in corps.items()
                 if c.get("signe") == signe and n not in ("asc", "mc", "noeud_moyen")]
    angles = [n for n in ("asc", "mc") if corps.get(n, {}).get("signe") == signe]
    maitres = A.MAITRISE.get(signe, [])
    forces = [A.force_planete(m, corps, asps) for m in maitres]
    force_maitre = max((f["score"] for f in forces if f), default=50)

    score = 50 + 12 * len(habitants) + 15 * len(angles) + (force_maitre - 50) * 0.3
    score = max(0, min(100, score))
    raisons = []
    if habitants:
        raisons.append(f"habité par {', '.join(sorted(habitants))}")
    if angles:
        raisons.append("sur un angle du thème" if angles else "")
    if not habitants and not angles:
        raisons.append("aucun corps n'y séjourne")
    if maitres:
        raisons.append(f"son maître {maitres[0]} y est "
                       + ("solide" if force_maitre >= SEUIL_FORT else
                          "en difficulté" if force_maitre <= SEUIL_FAIBLE else "moyen"))

    etat = ("resonance" if score >= SEUIL_FORT else
            "tension" if score <= SEUIL_FAIBLE else "neutre")
    return {"cible": signe, "type": "signe", "etat": etat, "score": round(score),
            "raisons": raisons, "habitants": sorted(habitants), "angles": angles}


def _lire_element(element, corps):
    """Un élément est fort s'il est bien représenté parmi les dix planètes.

    Repère : 10 planètes sur 4 éléments -> 2,5 en moyenne. Trois et plus =
    marqué ; zéro ou un = en creux.
    """
    bilan = A.bilan_elements(corps)["elements"]
    n = bilan[element]
    score = max(0, min(100, 50 + (n - 2.5) * 16))
    etat = ("resonance" if n >= 4 else "tension" if n <= 1 else "neutre")
    return {"cible": element, "type": "element", "etat": etat, "score": round(score),
            "raisons": [f"{n} planète(s) sur 10 dans cet élément"], "compte": n}


def lire_correspondance(correspondance, corps, asps):
    """Lit une correspondance Golden Dawn dans le thème réel."""
    genre, cible = correspondance
    if genre == "planete":
        return _lire_planete(cible, corps, asps)
    if genre == "signe":
        return _lire_signe(cible, corps, asps)
    return _lire_element(cible, corps)


# --------------------------------------------- accords nombres <-> thème

# Chaque nombre a une couleur : élément dominant et planète affine. Ce mapping
# est un CHOIX d'Align (les sources ne croisent pas les deux mondes — le
# croisement est notre invention, pas la leur). Il est donc documenté comme
# tel : cohérent, stable, mais pas « traditionnel ».
COULEUR_NOMBRE = {
    1: ("Feu", "soleil"), 2: ("Eau", "lune"), 3: ("Feu", "jupiter"),
    4: ("Terre", "saturne"), 5: ("Air", "mercure"), 6: ("Terre", "venus"),
    7: ("Eau", "neptune"), 8: ("Terre", "saturne"), 9: ("Eau", "mars"),
    11: ("Air", "uranus"), 22: ("Terre", "saturne"), 33: ("Eau", "neptune"),
}


def accord_nombre(valeur, corps, asps):
    """Le thème appuie-t-il ce nombre, ou frotte-t-il contre lui ?

    Deux facteurs indépendants ADDITIONNÉS (jamais multipliés) : l'élément du
    nombre et sa planète affine.
    """
    if valeur not in COULEUR_NOMBRE:
        return None
    element, planete = COULEUR_NOMBRE[valeur]
    el = _lire_element(element, corps)
    pl = _lire_planete(planete, corps, asps)
    score = (el["score"] + (pl["score"] if pl else 50)) / 2
    return {
        "nombre": valeur,
        "element": element,
        "planete": planete,
        "etat": ("resonance" if score >= SEUIL_FORT else
                 "tension" if score <= SEUIL_FAIBLE else "neutre"),
        "score": round(score),
        "detail": {"element": el, "planete": pl},
    }


# ------------------------------------------------------------- assemblage

def croiser(theme, prenoms_nom, jour, mois, annee, annee_courante=None):
    """Le portrait croisé complet. Aucun texte : que de la structure.

    Les textes viennent du corpus, choisis par ces clés. C'est la frontière
    qui garantit le déterminisme : ici on CALCULE, ailleurs on LIT.
    """
    corps = theme["corps"]
    corps = dict(corps)
    corps["asc"] = {"signe": theme["angles"]["asc"]["signe"], "maison": 1,
                    "lon": theme["angles"]["asc"]["lon"]}
    corps["mc"] = {"signe": theme["angles"]["mc"]["signe"], "maison": 10,
                   "lon": theme["angles"]["mc"]["lon"]}

    positions = {n: c["lon"] for n, c in corps.items() if n != "noeud_moyen"}
    vitesses = {n: c.get("vitesse_lon") for n, c in corps.items()}
    asps = A.aspects_entre(positions, vitesses)

    nombres = N.portrait(prenoms_nom, jour, mois, annee)
    cartes = T.profil(jour, mois, annee, annee_courante)

    # LA CHARNIÈRE : les cartes pointent vers le thème réel.
    ponts = {
        "naissance": lire_correspondance(cartes["naissance"]["correspondance"], corps, asps),
        "fond": lire_correspondance(cartes["fond"]["correspondance"], corps, asps),
    }
    if "annee" in cartes:
        ponts["annee"] = lire_correspondance(cartes["annee"]["correspondance"], corps, asps)

    accords = {cle: accord_nombre(nombres[cle]["valeur"], corps, asps)
               for cle in ("cap", "voix", "foyer", "elan")}

    return {
        "theme": theme,
        "nombres": nombres,
        "cartes": cartes,
        "ponts": ponts,
        "accords": accords,
        "aspects": asps,
        "bilan": A.bilan_elements(corps),
        "stelliums": A.stelliums(corps),
        "resonances": [p for p in ponts.values() if p and p["etat"] == "resonance"],
        "tensions": [p for p in ponts.values() if p and p["etat"] == "tension"],
    }
