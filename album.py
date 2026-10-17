# -*- coding: utf-8 -*-
"""L'album visuel des cartes de Ta Trame.

Un seul endroit qui rassemble, pour CHAQUE carte du jeu maison :

  - son image (vignette + pleine résolution), quand elle est produite ;
  - tous ses textes déjà écrits, tels quels (aucune réécriture).

L'album ne RECOPIE rien : il lit à la source, à chaque visite.
  - ``data/corpus/arcanes.json``   -> les 22 arcanes majeurs (+ l'Éveil) : textes
  - ``data/corpus/mineurs.json``   -> invitation + « comprendre » des mineures
  - ``_distillation/corpus_mineurs_*.json`` -> corpus de TRAVAIL des familles
        écrites mais pas encore intégrées à l'app (ex. Eau) : même format, avec
        leur « comprendre ». Unis au corpus de l'app, l'app gagne en cas de
        doublon — aucune écriture perdue, et une nouvelle famille se ramasse
        seule le jour où son corpus de travail apparaît.
  - ``_distillation/noms_cartes.json`` -> le nom maison inscrit sur la carte
  - ``static/cartes/``             -> les images (on regarde ce qui existe)

Conséquence voulue : une carte ajoutée (image ou texte) apparaît SEULE à la
prochaine ouverture de l'album. Rien à relancer, rien à générer.

ÉCRITURE (``appliquer``) — la seule partie de l'app qui MODIFIE le corpus.
L'album est aussi un bureau d'édition : chaque texte affiché connaît SA maison
(``cible_ecriture``), et « Appliquer » y réécrit le texte, après sauvegarde
horodatée. Rien n'est deviné : on n'écrit que dans un fichier ET une clé que
``cible_ecriture`` a reconnus, sinon on refuse (une écriture refusée vaut mieux
qu'un texte rangé au mauvais endroit). Garde d'accès : la session admin, dans
la route (app.py). Ici, que du disque.

Aucun LLM, aucun réseau : lecture disque pure, comme le reste de l'app.
"""
from __future__ import annotations

import json
import pathlib

from moteur import mineurs as M

RACINE = pathlib.Path(__file__).resolve().parent
CORPUS = RACINE / "data" / "corpus"
CARTES = RACINE / "static" / "cartes"
MINI = CARTES / "mini"

# Le dossier de production (hors app) : noms maison ET corpus de travail des
# familles pas encore intégrées.
DISTILLATION = RACINE.parent / "_distillation"

# Noms maison (source de vérité). Hors dossier app (là où il vit vraiment) :
# l'album reste utilisable sans lui, mais affiche alors le rang plutôt que
# le nom du cartouche.
NOMS_CARTES = DISTILLATION / "noms_cartes.json"

# --------------------------------------------------------------- les familles
#
# Les quatre familles du nouveau tarot, dans l'ordre d'affichage.
#   cle        : préfixe des images ET des clés de noms_cartes.json
#   nom        : libellé montré
#   classique  : préfixe des invitations déjà écrites dans mineurs.json
#                (même carte, couleur traditionnelle — la transition douce)
#   couleur    : nom traditionnel de la couleur, pour dire d'où vient le texte
FAMILLES = [
    {"cle": "feu", "nom": "Feu", "classique": "batons", "couleur": "Bâtons"},
    {"cle": "eau", "nom": "Eau", "classique": "coupes", "couleur": "Coupes"},
    {"cle": "air", "nom": "Air", "classique": "epees", "couleur": "Épées"},
    {"cle": "terre", "nom": "Terre", "classique": "deniers", "couleur": "Deniers"},
]

# Les 14 rangs d'une famille, dans l'ordre de lecture (Align : Page, Chevalier).
# (clé image/noms, libellé affiché)
RANGS = [
    ("as", "As"), ("2", "Deux"), ("3", "Trois"), ("4", "Quatre"),
    ("5", "Cinq"), ("6", "Six"), ("7", "Sept"), ("8", "Huit"),
    ("9", "Neuf"), ("10", "Dix"), ("page", "Page"),
    ("chevalier", "Chevalier"), ("reine", "Reine"), ("roi", "Roi"),
]

# Rang Align -> rang classique (le texte traditionnel s'écrit valet/cavalier).
RANG_CLASSIQUE = {"page": "valet", "chevalier": "cavalier"}

# Les champs des majeurs, dans l'ordre d'affichage, avec leur titre humain.
CHAMPS_MAJEURS = [
    ("conditionnement", "Le conditionnement"),
    ("alimenter", "Comment l’alimenter"),
    ("contrarie", "Quand elle est contrariée"),
    ("en_resonance", "Dans un ciel en résonance"),
    ("en_tension", "Dans un ciel en tension"),
    ("invitation", "L’invitation du jour"),
    ("invitation_personnelle", "L’invitation personnelle"),
    ("lecture", "La carte et sa lecture"),
    ("pour_l_annee", "Pour l’année"),
]

# Les textes d'une mineure, dans l'ordre d'affichage. Ce sont les SEULES clés
# éditables d'une famille — ``comprendre`` est le nom d'usage dans le corpus.
CHAMPS_MINEURS = [
    ("invitation", "L’invitation du jour"),
    ("comprendre", "Comprendre cette carte"),
]

#: Un texte de mineure peut arriver sous un autre nom selon la vague de
#: rédaction ; on les accepte en LECTURE, on écrit toujours sous le nom canonique.
ALIAS_COMPRENDRE = ("comprendre", "texte_long", "lecture", "explication")


# --------------------------------------------------------------- utilitaires

def _lire_json(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _paragraphes(texte):
    return [p.strip() for p in str(texte).split("\n\n") if p.strip()]


def _sources_mineurs():
    """Chaque clé de mineure avec son bloc ET le FICHIER qui en est la maison.

    Deux maisons, jamais dupliquées :
      - le corpus de l'app ``data/corpus/mineurs.json`` (ce qui est LIVRÉ) ;
      - le corpus de TRAVAIL ``_distillation/corpus_mineurs_*.json`` des
        familles écrites mais pas encore intégrées (Eau aujourd'hui) — le
        suffixe ``*`` fait que la prochaine famille se ramasse seule.

    L'app gagne en cas de doublon (Feu : identique dans les deux). La maison
    est retenue par clé : c'est elle que « Appliquer » réécrira. Les archives
    ``*_ARCHIVE*`` sont ignorées.
    """
    sources = {}
    for chemin in sorted(DISTILLATION.glob("corpus_mineurs_*.json")):
        if "_ARCHIVE" in chemin.name:
            continue
        for cle, val in _lire_json(chemin).items():
            if not cle.startswith("_"):
                sources[cle] = (val, chemin)
    for cle, val in _lire_json(CORPUS / "mineurs.json").items():
        if not cle.startswith("_"):
            sources[cle] = (val, CORPUS / "mineurs.json")
    return sources


def _relatif(chemin):
    """Le chemin tel qu'on le montre à l'écran, depuis la racine du projet."""
    chemin = pathlib.Path(chemin)
    for base in (RACINE, RACINE.parent):
        try:
            return str(chemin.relative_to(base))
        except ValueError:
            continue
    return str(chemin)


def _horodatage():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def _sauvegarder(chemin, dossier=None):
    """Copie le fichier AVANT de l'écrire. Renvoie le chemin de la copie.

    Une sauvegarde par écriture, horodatée, dans ``_sauvegardes/`` à côté du
    fichier : c'est le filet, pas un historique (rien ne tourne tout seul).
    """
    chemin = pathlib.Path(chemin)
    dossier = pathlib.Path(dossier) if dossier else chemin.parent / "_sauvegardes"
    dossier.mkdir(parents=True, exist_ok=True)
    cible = dossier / ("%s.%s.json" % (chemin.stem, _horodatage()))
    cible.write_bytes(chemin.read_bytes())
    return cible


def _lire_json_strict(chemin):
    return json.loads(pathlib.Path(chemin).read_text(encoding="utf-8"))


def cible_ecriture(carte_id, champ, sources=None):
    """OÙ vit le texte (carte_id, champ) : ``(chemin, chemin_dans_le_json)``.

    ``None`` si l'un ou l'autre n'est pas reconnu — on refuse alors d'écrire.
    C'est le SEUL endroit qui décide ; la route et l'écran ne font que
    l'appeler, donc la règle « un texte = une maison » tient en dix lignes.
    """
    carte_id = str(carte_id or "")
    champ = str(champ or "")

    if carte_id.startswith("maj-"):
        num = carte_id[4:]
        if not num.isdigit() or champ not in dict(CHAMPS_MAJEURS):
            return None
        arcanes = (_lire_json(CORPUS / "arcanes.json").get("arcanes") or {})
        if num not in arcanes:
            return None
        return CORPUS / "arcanes.json", ["arcanes", num, champ]

    # — les messages du jour (fil, transits, Lune) —
    if carte_id.startswith("fil-"):
        return _cible_entree(CORPUS / "fil.json", [], carte_id[4:],
                             champ, dict(CHAMPS_FIL))
    if carte_id.startswith("transit-gen-"):
        return _cible_entree(CORPUS / "transits.json", ["transits_generiques"],
                             carte_id[len("transit-gen-"):], champ,
                             CHAMPS_TRANSIT_AUTORISES)
    if carte_id.startswith("transit-precis-"):
        return _cible_entree(CORPUS / "transits.json", ["transits_precis"],
                             carte_id[len("transit-precis-"):], champ,
                             CHAMPS_TRANSIT_AUTORISES)
    if carte_id.startswith("phase-"):
        return _cible_entree(CORPUS / "ciel.json", ["phases"],
                             carte_id[len("phase-"):], champ, dict(CHAMPS_LUNE))
    if carte_id.startswith("lune-maison-"):
        return _cible_entree(CORPUS / "ciel.json", ["lune_maison"],
                             carte_id[len("lune-maison-"):], champ, dict(CHAMPS_LUNE))

    if "-" not in carte_id:
        return None
    fam_cle, rang = carte_id.split("-", 1)
    famille = next((f for f in FAMILLES if f["cle"] == fam_cle), None)
    if famille is None or champ not in dict(CHAMPS_MINEURS):
        return None

    if sources is None:
        sources = _sources_mineurs()
    prefixe = famille.get("prefixe", famille["cle"])
    cle_image = "%s_%s" % (prefixe, rang)
    if cle_image in sources:
        return sources[cle_image][1], [cle_image, champ]
    # Famille pas encore écrite : le texte affiché est celui de la couleur
    # traditionnelle (même carte, autre nom) — c'est LUI qu'on édite, là où
    # il vit, sinon l'écriture ne s'appliquerait à rien de visible.
    cle_classique = "%s_%s" % (famille["classique"], RANG_CLASSIQUE.get(rang, rang))
    if cle_classique in sources:
        return sources[cle_classique][1], [cle_classique, champ]
    return None


def appliquer(modifications, dossier_sauvegardes=None):
    """Écrit chaque texte modifié dans SON fichier, après sauvegarde.

    ``modifications`` : ``[{"carte": "maj-4", "champ": "lecture", "texte": "…"}]``.

    Deux étapes, jamais mélangées : on RÉSOUT toutes les cibles d'abord (une
    clé inconnue arrête tout avant la moindre écriture), puis on écrit. Un lot
    à moitié appliqué serait le pire des états. Renvoie un rapport lisible ;
    lève ``ValueError`` sur une cible inconnue ou un texte vide.
    """
    sources = _sources_mineurs()
    par_fichier = {}   # chemin -> [(chemin_json, texte, carte, champ)]
    for brut in modifications or []:
        carte = str((brut or {}).get("carte") or "").strip()
        champ = str((brut or {}).get("champ") or "").strip()
        texte = (brut or {}).get("texte")
        if not isinstance(texte, str) or not texte.strip():
            raise ValueError("texte vide (%s / %s)" % (carte, champ))
        cible = cible_ecriture(carte, champ, sources=sources)
        if cible is None:
            raise ValueError("cible inconnue : %s / %s" % (carte, champ))
        chemin, chemin_json = cible
        par_fichier.setdefault(chemin, []).append((chemin_json, texte, carte, champ))

    if not par_fichier:
        raise ValueError("aucune modification à écrire")

    rapport = []
    for chemin, items in par_fichier.items():
        donnees = _lire_json_strict(chemin)
        ecrites = []
        for chemin_json, texte, carte, champ in items:
            noeud = donnees
            for cle in chemin_json[:-1]:
                noeud = noeud[cle]
            noeud[chemin_json[-1]] = texte
            ecrites.append({"carte": carte, "champ": champ,
                            "cle": ".".join(chemin_json)})
        sauvegarde = _sauvegarder(chemin, dossier_sauvegardes)
        pathlib.Path(chemin).write_text(
            json.dumps(donnees, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        rapport.append({
            "fichier": _relatif(chemin),
            "sauvegarde": _relatif(sauvegarde),
            "modifications": ecrites,
        })
    return rapport


def _url_image(chemin_relatif):
    """L'URL statique si le fichier existe vraiment, sinon None (jamais
    d'image cassée : la carte s'affiche « à venir »)."""
    if chemin_relatif is not None and (RACINE / chemin_relatif).exists():
        return "/" + chemin_relatif.replace("\\", "/")
    return None


def _mini_ou_plein(prefixe_mini, prefixe_plein):
    """La vignette si elle existe, sinon l'image pleine (jamais vide)."""
    return _url_image(prefixe_mini) or _url_image(prefixe_plein)


def _textes_depuis(dico, champs):
    """Construit les blocs de texte depuis les champs présents (non vides).

    ``champ`` est conservé sur chaque bloc : c'est lui qui nomme le texte
    quand on l'édite (couple carte + champ = une cible d'écriture).
    """
    blocs = []
    for cle, titre in champs:
        valeur = dico.get(cle)
        if valeur:
            paras = _paragraphes(valeur)
            if paras:
                blocs.append({"titre": titre, "paragraphes": paras, "champ": cle})
    return blocs


# ----------------------------------------------------------------- majeurs

def _section_majeurs(noms):
    arcanes = _lire_json(CORPUS / "arcanes.json").get("arcanes", {})
    majeurs_noms = (noms or {}).get("majeurs", {})

    cartes = []
    for num in sorted(arcanes, key=lambda k: int(k)):
        v = arcanes[num]
        n = int(num)
        trad = ""
        reference = majeurs_noms.get("master" if n == 22 else "major_%02d" % n, {})
        trad = reference.get("trad", "")
        plein = "static/cartes/%02d.jpg" % n
        mini = "static/cartes/mini/%02d.webp" % n
        cartes.append({
            "id": "maj-%d" % n,
            "groupe": "Arcanes majeurs",
            "numero": n,
            "etiquette": reference.get("roman") or str(n),
            "nom": v.get("nom", trad or num),
            "trad": trad,
            "correspondance": v.get("correspondance") or "",
            "image": _url_image(plein),
            "mini": _mini_ou_plein(mini, plein),
            "cle_texte": num,
            "fichier_texte": _relatif(CORPUS / "arcanes.json"),
            "textes": _textes_depuis(v, CHAMPS_MAJEURS),
        })

    return {
        "id": "majeurs",
        "titre": "Arcanes majeurs",
        "note": "Les 22 arcanes du cycle, et l’Éveil. Le nom maison est inscrit "
                "sur la carte ; le nom traditionnel est rappelé en gris.",
        "cartes": cartes,
    }


# ----------------------------------------------------------------- mineurs

def _section_famille(famille, noms, sources):
    prefixe = famille.get("prefixe", famille["cle"])
    famille_noms = (noms or {}).get("familles", {}).get(famille["cle"], {})

    cartes = []
    for rang, rang_nom in RANGS:
        # Clé des images : feu_2, eau_page…  Clé des noms : feu_02, arc_02…
        cle_image = "%s_%s" % (prefixe, rang)
        cle_noms = "%s_%s" % (prefixe, rang if not rang.isdigit() else "%02d" % int(rang))

        nom = (famille_noms.get(cle_noms) or {}).get("nom", "")
        plein = "static/cartes/mineurs/%s.jpg" % cle_image
        mini = "static/cartes/mini/mineurs/%s.webp" % cle_image

        # Le texte de la famille s'il est écrit ; sinon l'invitation de la
        # couleur traditionnelle (même carte, déjà rédigée) — jamais de vide.
        # On retient AUSSI la clé et le fichier d'où vient le texte : c'est la
        # maison que « Appliquer » réécrira.
        cle_classique = "%s_%s" % (famille["classique"], RANG_CLASSIQUE.get(rang, rang))
        note_texte = ""
        if cle_image in sources:
            source, fichier_source = sources[cle_image]
            cle_texte = cle_image
        elif cle_classique in sources:
            source, fichier_source = sources[cle_classique]
            cle_texte = cle_classique
            note_texte = ("Texte de la couleur traditionnelle (%s) — la "
                          "version %s n’est pas encore rédigée."
                          % (famille["couleur"], famille["nom"]))
        else:
            source, fichier_source, cle_texte = {}, None, ""

        blocs = []
        for cle, titre in CHAMPS_MINEURS:
            valeur = source.get(cle)
            if cle == "comprendre" and not valeur:
                for alias in ALIAS_COMPRENDRE:
                    if source.get(alias):
                        valeur = source[alias]
                        break
            if valeur:
                paras = _paragraphes(valeur)
                if paras:
                    blocs.append({"titre": titre, "paragraphes": paras, "champ": cle})

        # La correspondance Golden Dawn, lue sur la couleur classique.
        corr = ""
        try:
            _type, valeur = M._correspondance(
                famille["classique"], RANG_CLASSIQUE.get(rang, rang))
            corr = valeur
        except Exception:
            corr = ""

        cartes.append({
            "id": "%s-%s" % (famille["cle"], rang),
            "groupe": "Famille %s" % famille["nom"],
            "rang": rang_nom,
            "etiquette": rang_nom,
            "nom": nom,
            "couleur": famille["couleur"],
            "correspondance": corr,
            "image": _url_image(plein),
            "mini": _mini_ou_plein(mini, plein),
            "cle_texte": cle_texte,
            "fichier_texte": _relatif(fichier_source) if fichier_source else "",
            "textes": blocs,
            "note_texte": note_texte,
        })

    return {
        "id": famille["cle"],
        "titre": "Famille %s" % famille["nom"],
        "note": "%s — correspond à la couleur traditionnelle %s." % (
            famille["nom"], famille["couleur"]),
        "cartes": cartes,
    }


# --------------------------------------------- les messages du jour
#
# Le troisième étage de l'album : les textes que l'app sert CHAQUE JOUR.
# Trois maisons, toutes dans ``data/corpus/`` :
#   fil.json      — le coaching du jour (miroir + geste), en 12 domaines de vie ;
#   transits.json — le miroir, le geste et la pensée du soir de chaque contact
#                   (génériques + précis ; certaines précises portent leurs trois
#                   phases : approche / coeur / retrait) ;
#   ciel.json     — la Lune : les 8 phases et les 12 maisons.
# Même contrat que les cartes : l'album les AFFICHE, l'éditeur les réécrit dans
# leur fichier — `cible_ecriture` reste le seul endroit qui sait où. Les champs
# qui ne sont pas des textes (source_livre, themes) sont montrés mais jamais
# éditables : ils sont de la FABRICATION, pas du message.

ORDRE_DOMAINES = ["soi", "ressources", "echanges", "racines", "creation",
                  "quotidien", "autre", "traversee", "sens", "metier",
                  "communaute", "retrait"]        # l'ordre des maisons (jour.py)
LIBELLES_DOMAINES = {
    "soi": "Soi", "ressources": "Ressources", "echanges": "Échanges",
    "racines": "Racines", "creation": "Création", "quotidien": "Quotidien",
    "autre": "Autre", "traversee": "Traversée", "sens": "Sens",
    "metier": "Métier", "communaute": "Communauté", "retrait": "Retrait",
}
CHAMPS_FIL = (("miroir", "Le miroir"), ("geste", "Le geste"))
CHAMPS_PHASE = (("miroir", "Le miroir"), ("geste", "Le geste"))
CHAMPS_LUNE = CHAMPS_PHASE
#: Une entrée de transit est de l'UNE DES DEUX FORMES (la clé « miroir »
#: tranche) : un texte unique, ou ses trois phases — chacune avec son miroir
#: et son geste. Voir `_champs_transit`.
CHAMPS_TRANSIT_UNIQUES = (("miroir", "Le miroir"), ("geste", "Le geste"),
                          ("pensee_soir", "La pensée du soir"))
PHASES_TRANSIT = (("approche", "L'approche"), ("coeur", "Le cœur"),
                  ("retrait", "Le retrait"))
CHAMPS_TRANSIT_AUTORISES = ({c for c, _ in CHAMPS_TRANSIT_UNIQUES}
                            | {"%s.%s" % (p, c) for p, _ in PHASES_TRANSIT
                               for c, _ in CHAMPS_PHASE})
NOMS_PHASES = {
    "nouvelle": "Nouvelle lune", "croissante": "Lune croissante",
    "premier_quartier": "Premier quartier", "gibbeuse": "Gibbeuse",
    "pleine": "Pleine lune", "decroissante": "Lune décroissante",
    "dernier_quartier": "Dernier quartier", "balsamique": "Balsamique",
}


def _capitalise(texte):
    return texte[:1].upper() + texte[1:]


def _champs_transit(entree):
    """Les blocs d'une entrée de transit, selon sa forme."""
    if entree.get("miroir") is not None:
        return list(CHAMPS_TRANSIT_UNIQUES)
    blocs = []
    for phase, titre in PHASES_TRANSIT:
        blocs += [("%s.%s" % (phase, champ), "%s — %s" % (titre, libelle))
                  for champ, libelle in CHAMPS_PHASE]
    blocs.append(("pensee_soir", "La pensée du soir"))
    return blocs


def _valeur(entree, chemin):
    """La valeur d'un champ, qui peut être nichée (« approche.miroir »)."""
    noeud = entree
    for partie in chemin.split("."):
        if not isinstance(noeud, dict):
            return None
        noeud = noeud.get(partie)
    return noeud if isinstance(noeud, str) else None


def _carte_message(cid, nom, groupe, cle_texte, fichier_texte, entree, champs):
    """Une entrée de message, mise en forme comme une carte d'album.

    Pas d'image : la vignette est un APERÇU du texte. Seuls les champs de
    TEXTE deviennent des blocs éditables — le reste de l'entrée (source,
    thèmes) est du décor de fabrication. Le champ peut être niché
    (« approche.miroir ») : c'est le chemin JSON qu'écrira l'éditeur.
    """
    entree = entree if isinstance(entree, dict) else {}
    blocs = []
    for chemin_champ, titre in champs:
        valeur = _valeur(entree, chemin_champ)
        if valeur and valeur.strip():
            paras = _paragraphes(valeur)
            if paras:
                blocs.append({"titre": titre, "champ": chemin_champ,
                              "paragraphes": paras})
    apercu = next((b["paragraphes"][0] for b in blocs if b["paragraphes"]), "")
    return {
        "id": cid, "genre": "message", "groupe": groupe, "nom": nom,
        "etiquette": "",
        "source": entree.get("source_livre", "") if isinstance(entree, dict) else "",
        "apercu": apercu[:190],
        "champs": " · ".join(b["titre"] for b in blocs),
        "image": None, "mini": None,
        "cle_texte": cle_texte, "fichier_texte": fichier_texte,
        "textes": blocs, "note_texte": "",
    }


def _sections_fil():
    """Le Fil du jour, une section par domaine de vie (l'ordre des maisons)."""
    donnees = {k: v for k, v in _lire_json(CORPUS / "fil.json").items()
               if not k.startswith("_") and isinstance(v, dict)}
    if not donnees:
        return []
    fichier = _relatif(CORPUS / "fil.json")
    presents = [d for d in ORDRE_DOMAINES
                if any(k.split("_", 1)[0] == d for k in donnees)]
    presents += sorted({k.split("_", 1)[0] for k in donnees} - set(presents))
    sections = []
    for domaine in presents:
        libelle = LIBELLES_DOMAINES.get(domaine, _capitalise(domaine))
        cartes = []
        for cle in sorted(k for k in donnees if k.split("_", 1)[0] == domaine):
            qualifiant = cle[len(domaine):].lstrip("_")
            nom = libelle + ((" · " + qualifiant.replace("_", " ")) if qualifiant else "")
            cartes.append(_carte_message("fil-" + cle, nom, "Le Fil du jour",
                                         cle, fichier, donnees[cle], CHAMPS_FIL))
        sections.append({
            "id": "fil-" + domaine, "genre": "messages",
            "titre": "Fil · %s" % libelle,
            "note": "Le coaching du jour du domaine %s — le miroir et le geste."
                    % libelle.lower(),
            "cartes": cartes,
        })
    return sections


def _sections_transits():
    donnees = _lire_json(CORPUS / "transits.json")
    fichier = _relatif(CORPUS / "transits.json")
    sections = []
    for identifiant, groupe, titre, note in (
            ("transit-gen", ("transits_generiques",), "Transits · génériques",
             "Le miroir, le geste et la pensée du soir pour chaque classe d'aspect."),
            ("transit-precis", ("transits_precis",), "Transits · précis",
             "Le contact exact (« mars carré ton Soleil »). Certaines entrées "
             "portent leurs trois phases — approche, cœur, retrait — au lieu "
             "d'un texte unique.")):
        bloc = donnees.get(groupe[0]) or {}
        cartes = [_carte_message("%s-%s" % (identifiant, cle),
                                 _capitalise(cle.replace("_", " ")), titre,
                                 cle, fichier, valeur, _champs_transit(valeur))
                  for cle, valeur in sorted(bloc.items()) if isinstance(valeur, dict)]
        sections.append({"id": identifiant, "genre": "messages", "titre": titre,
                         "note": note, "cartes": cartes})
    return sections


def _sections_lune():
    donnees = _lire_json(CORPUS / "ciel.json")
    fichier = _relatif(CORPUS / "ciel.json")
    sections = []
    phases = donnees.get("phases") or {}
    sections.append({
        "id": "lune-phases", "genre": "messages", "titre": "Lune · phases",
        "note": "Le miroir et le geste des huit phases lunaires.",
        "cartes": [_carte_message("phase-" + cle, NOMS_PHASES.get(cle, _capitalise(cle)),
                                  "La Lune", cle, fichier, valeur, CHAMPS_LUNE)
                   for cle, valeur in sorted(phases.items()) if isinstance(valeur, dict)],
    })
    maisons = donnees.get("lune_maison") or {}
    sections.append({
        "id": "lune-maisons", "genre": "messages", "titre": "Lune · maisons",
        "note": "Le miroir et le geste de chaque maison de la Lune.",
        "cartes": [_carte_message("lune-maison-" + cle, "Lune en maison %s" % cle,
                                  "La Lune", cle, fichier, valeur, CHAMPS_LUNE)
                   for cle, valeur in sorted(maisons.items()) if isinstance(valeur, dict)],
    })
    return sections


def _sections_messages():
    return _sections_fil() + _sections_transits() + _sections_lune()


def _cible_entree(chemin_fichier, chemin_prefixe, cle, champ, champs_autorises):
    """Le chemin JSON d'un champ de message, si la clé existe vraiment.

    Le champ peut être niché (« approche.miroir ») : chaque maillon du chemin
    doit exister, sinon on refuse — on n'invente jamais une entrée.
    """
    if champ not in champs_autorises:
        return None
    chemin = list(chemin_prefixe) + [cle] + champ.split(".")
    noeud = _lire_json(chemin_fichier)
    for partie in chemin[:-1]:
        noeud = noeud.get(partie) if isinstance(noeud, dict) else None
        if not isinstance(noeud, dict):
            return None
    return chemin_fichier, chemin


# ------------------------------------------------------------------- album

def construire_album():
    """L'album complet, prêt à afficher (dict sérialisable en JSON)."""
    noms = _lire_json(NOMS_CARTES)
    sources = _sources_mineurs()

    sections = [_section_majeurs(noms)]
    sections += [_section_famille(f, noms, sources) for f in FAMILLES]
    sections += _sections_messages()

    # Les CARTES (avec image) et les MESSAGES du jour sont comptés à part :
    # ce sont deux étages de l'album, pas un même inventory de 729 « cartes ».
    cartes = [c for s in sections if s.get("genre") != "messages" for c in s["cartes"]]
    messages = [c for s in sections if s.get("genre") == "messages" for c in s["cartes"]]
    stats = {
        "cartes": len(cartes),
        "images": sum(1 for c in cartes if c["image"]),
        "textes": sum(1 for c in cartes if c["textes"]),
        "messages": len(messages),
    }

    return {
        "sections": sections,
        "stats": stats,
        "source_noms": NOMS_CARTES.exists(),
    }
