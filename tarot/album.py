# -*- coding: utf-8 -*-
"""L'album visuel des cartes du Tarot.

Portage exact de l'album de Ta Trame (ASTRO_PLUS_APP/album.py) : mêmes
helpers, même contrat d'écriture (``cible_ecriture`` seul décide, ``appliquer``
résout tout avant d'écrire, sauvegarde horodatée par fichier touché), même
logique d'affichage (lecture à la source à chaque visite).

Une différence de CIBLE, et elle est voulue : le corpus du Tarot vit dans
79 fichiers individuels (``data/corpus/cartes/<id>.json``, une fiche par
carte), pas dans un arcanes.json/mineurs.json. ``cible_ecriture`` renvoie
donc le fichier de la fiche et le chemin JSON du champ, avec des entiers
pour les indices de tableau (``questions.0`` → ``["questions", 0]``).

Les champs éditables sont les TEXTES de la fiche : lumière, ombre (texte +
issue), leçon, micro-geste, les quatre positions, les questions, et pour
Éveil (hors cycle, forme propre) les trois variantes du regard. Les métadonnées
(id, nom, mode d'ombre, mots-clés, tension, note_grille) s'affichent mais
ne s'éditent pas : ce n'est pas du message.

Aucun LLM, aucun réseau : lecture disque pure, comme le reste de l'app.
"""
from __future__ import annotations

import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent
CORPUS = RACINE / "data" / "corpus" / "cartes"
IMAGES = RACINE / "static" / "img" / "cartes"
TIRAGES = RACINE / "data" / "grammaire" / "tirages.json"

# Les familles, dans l'ordre d'affichage (même ordre que l'app de tirage).
FAMILLES = [
    {"cle": "feu", "nom": "Feu"},
    {"cle": "eau", "nom": "Eau"},
    {"cle": "air", "nom": "Air"},
    {"cle": "terre", "nom": "Terre"},
]

RANGS = [
    ("as", "As"), ("02", "Deux"), ("03", "Trois"), ("04", "Quatre"),
    ("05", "Cinq"), ("06", "Six"), ("07", "Sept"), ("08", "Huit"),
    ("09", "Neuf"), ("10", "Dix"), ("page", "Page"),
    ("chevalier", "Chevalier"), ("reine", "Reine"), ("roi", "Roi"),
]

# Les champs texte d'une fiche, dans l'ordre d'affichage. La partie avant le
# point est le chemin JSON (« ombre.texte » → ["ombre", "texte"]) ; un entier
# final désigne un indice de tableau (« questions.0 » → ["questions", 0]).
CHAMPS_FICHE = [
    ("lumiere", "La lumière"),
    ("ombre.texte", "L’ombre"),
    ("ombre.issue", "L’issue (la chaîne large)"),
    ("lecon", "La leçon"),
    ("micro_geste", "Le micro-geste"),
    ("positions.jour", "Aujourd’hui — tirage du jour"),
    ("positions.amene", "Ce que j’amène"),
    ("positions.se_joue", "Ce qui se joue"),
    ("positions.essayer", "Ce que je peux essayer"),
    ("questions.0", "Question 1"),
    ("questions.1", "Question 2"),
    ("questions.2", "Question 3"),
    ("questions.3", "Question 4"),
]

# Éveil : forme propre — pas de positions, les trois variantes du regard.
CHAMPS_MASTER = [
    ("lumiere", "La lumière"),
    ("ombre.texte", "L’ombre"),
    ("ombre.issue", "L’issue (la chaîne large)"),
    ("lecon", "La leçon"),
    ("micro_geste", "Le micro-geste"),
    ("le_regard.0", "Le regard — variante 1"),
    ("le_regard.1", "Le regard — variante 2"),
    ("le_regard.2", "Le regard — variante 3"),
]


# --------------------------------------------------------------- utilitaires

def _lire_json(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _lire_json_strict(chemin):
    return json.loads(pathlib.Path(chemin).read_text(encoding="utf-8"))


def _paragraphes(texte):
    return [p.strip() for p in str(texte).split("\n\n") if p.strip()]


def _relatif(chemin):
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


def _url_image(id_carte):
    """L'URL de la face d'app si le fichier existe, sinon None (jamais
    d'image cassée : la carte s'affiche « à venir »). ?v=3 : cartouches CLAIRS
    (médaillon + nom sur la carte) — force le rechargement du cache."""
    if (IMAGES / ("%s.jpg" % id_carte)).exists():
        return "img/cartes/%s.jpg?v=3" % id_carte
    return None


def _chemin_de_champ(chemin_texte):
    """``"ombre.texte"`` → ``["ombre", "texte"]`` ; ``"questions.0"`` →
    ``["questions", 0]`` (entier pour un indice de tableau)."""
    parties = chemin_texte.split(".")
    return [int(p) if p.isdigit() else p for p in parties]


def _valeur_nichée(fiche, chemin):
    noeud = fiche
    for cle in chemin:
        try:
            noeud = noeud[cle]
        except (KeyError, IndexError, TypeError):
            return None
    return noeud if isinstance(noeud, str) else None


def _ecrire_valeur(fiche, chemin, texte):
    noeud = fiche
    for cle in chemin[:-1]:
        noeud = noeud[cle]
    noeud[chemin[-1]] = texte


# ---------------------------------------------------------- cible + écriture

def cible_ecriture(carte_id, champ):
    """OÙ vit le texte (carte_id, champ) : ``(chemin, chemin_json)``.

    ``None`` si l'un ou l'autre n'est pas reconnu — on refuse alors d'écrire.
    C'est le SEUL endroit qui décide ; la route et l'écran ne font que
    l'appeler, donc la règle « un texte = une maison » tient en dix lignes.
    """
    carte_id = str(carte_id or "")
    champ = str(champ or "")

    # — la pédagogie des tirages (tirages.json) —
    if carte_id.startswith("tirage-"):
        return _cible_tirage(carte_id, champ)

    fichier = CORPUS / ("%s.json" % carte_id)
    if not fichier.exists():
        return None
    fiche = _lire_json(fichier)

    champs = CHAMPS_MASTER if fiche.get("type") == "hors_cycle" else CHAMPS_FICHE
    autorises = {c: _chemin_de_champ(c) for c, _ in champs}
    if champ not in autorises:
        return None
    chemin_json = autorises[champ]

    # Le champ doit exister dans la fiche (on n'invente jamais une entrée).
    if _valeur_nichée(fiche, chemin_json) is None:
        return None
    return fichier, chemin_json


def appliquer(modifications, dossier_sauvegardes=None):
    """Écrit chaque texte modifié dans SON fichier, après sauvegarde.

    ``modifications`` : ``[{"carte": "major_13", "champ": "lumiere", "texte": "…"}]``.

    Deux étapes, jamais mélangées : on RÉSOUT toutes les cibles d'abord (une
    clé inconnue arrête tout avant la moindre écriture), puis on écrit. Un lot
    à moitié appliqué serait le pire des états. Renvoie un rapport lisible ;
    lève ``ValueError`` sur une cible inconnue ou un texte vide.
    """
    par_fichier = {}   # chemin -> [(chemin_json, texte, carte, champ)]
    for brut in modifications or []:
        carte = str((brut or {}).get("carte") or "").strip()
        champ = str((brut or {}).get("champ") or "").strip()
        texte = (brut or {}).get("texte")
        if not isinstance(texte, str) or not texte.strip():
            raise ValueError("texte vide (%s / %s)" % (carte, champ))
        cible = cible_ecriture(carte, champ)
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
            _ecrire_valeur(donnees, chemin_json, texte)
            ecrites.append({"carte": carte, "champ": champ,
                            "cle": ".".join(str(c) for c in chemin_json)})
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


# ------------------------------------------------------------------- album

def _fiche(carte_id, groupe, etiquette):
    """Une carte d'album depuis SON fichier (lecture à la source)."""
    fichier = CORPUS / ("%s.json" % carte_id)
    fiche = _lire_json(fichier)
    if not fiche:
        return None

    champs = CHAMPS_MASTER if fiche.get("type") == "hors_cycle" else CHAMPS_FICHE
    blocs = []
    for chemin_texte, titre in champs:
        chemin = _chemin_de_champ(chemin_texte)
        valeur = _valeur_nichée(fiche, chemin)
        if valeur and valeur.strip():
            paras = _paragraphes(valeur)
            if paras:
                blocs.append({"titre": titre, "paragraphes": paras,
                              "champ": chemin_texte})

    return {
        "id": carte_id,
        "groupe": groupe,
        "etiquette": etiquette,
        "nom": fiche.get("nom", carte_id),
        "type": fiche.get("type", ""),
        "registre": fiche.get("registre") or "",
        "element": fiche.get("element") or "",
        "mots_cles": " · ".join(fiche.get("mots_cles", [])),
        "tension": fiche.get("tension", {}),
        "image": _url_image(carte_id),
        "mini": _url_image(carte_id),
        "cle_texte": carte_id,
        "fichier_texte": _relatif(fichier),
        "textes": blocs,
        "note_texte": "",
    }


# Les champs texte des deux tirages v1, dans l'ordre d'affichage. Le champ
# est le chemin JSON dans tirages.json (entier = indice de tableau).
CHAMPS_TIRAGE_JOUR = [
    ("pedagogie.resume", "Résumé (deux lignes)"),
    ("pedagogie.pourquoi", "Pourquoi ce tirage"),
    ("pedagogie.le_tirage", "Le sens général"),
    ("pedagogie.comment_lire", "Comment lire"),
    ("pedagogie.apres", "Après la lecture"),
    ("pedagogie.vocabulaire.0.texte", "Vocabulaire — les familles"),
    ("pedagogie.vocabulaire.1.texte", "Vocabulaire — majeures et mineures"),
    ("pedagogie.vocabulaire.2.texte", "Vocabulaire — les figures"),
    ("pedagogie.vocabulaire.3.texte", "Vocabulaire — la lecture des éléments"),
]
CHAMPS_TIRAGE_CAUSALE = [
    ("pedagogie.resume", "Résumé (deux lignes)"),
    ("pedagogie.pourquoi", "Pourquoi ce tirage"),
    ("pedagogie.le_tirage", "Le sens général"),
    ("pedagogie.comment_lire", "Comment lire"),
    ("pedagogie.apres", "Après la lecture"),
    ("pedagogie.positions_expliquees.amene", "Position — ce que j'amène"),
    ("pedagogie.positions_expliquees.se_joue", "Position — ce qui se joue"),
    ("pedagogie.positions_expliquees.essayer", "Position — ce que je peux essayer"),
    ("pedagogie.vocabulaire.0.texte", "Vocabulaire — les familles"),
    ("pedagogie.vocabulaire.1.texte", "Vocabulaire — majeures et mineures"),
    ("pedagogie.vocabulaire.2.texte", "Vocabulaire — les figures"),
    ("pedagogie.vocabulaire.3.texte", "Vocabulaire — la lecture des éléments"),
]


def _champs_tirage_grille(grille):
    """Les champs éditables d'une grille : sa pédagogie, ses positions, son
    vocabulaire — construits depuis la grille, jamais écrits en dur."""
    champs = [
        ("pedagogie.resume", "Résumé (deux lignes)"),
        ("pedagogie.pourquoi", "Pourquoi ce tirage"),
        ("pedagogie.le_tirage", "Le sens général"),
        ("pedagogie.comment_lire", "Comment lire"),
        ("pedagogie.apres", "Après la lecture"),
    ]
    for pos in grille.get("positions", []):
        champs.append(("pedagogie.positions_expliquees.%s" % pos["id"],
                       "Position — %s" % pos["libelle"]))
    for i, voc in enumerate((grille.get("pedagogie") or {}).get("vocabulaire", [])):
        champs.append(("pedagogie.vocabulaire.%d.texte" % i,
                       "Vocabulaire — %s" % voc.get("titre", "")))
    return champs


def _champs_tirage_question(bloc):
    """« Une question » (2026-11-16) : sa pédagogie, le libellé de chacune
    des cinq questions (ce que la personne lit et choisit), son vocabulaire."""
    champs = [
        ("pedagogie.resume", "Résumé (deux lignes)"),
        ("pedagogie.pourquoi", "Pourquoi ce tirage"),
        ("pedagogie.le_tirage", "Le sens général"),
        ("pedagogie.comment_lire", "Comment lire"),
        ("pedagogie.apres", "Après la lecture"),
    ]
    for i, pos in enumerate(bloc.get("positions", [])):
        champs.append(("positions.%d.question" % i,
                       "Question %d — %s" % (i + 1, pos.get("libelle", ""))))
    for i, voc in enumerate((bloc.get("pedagogie") or {}).get("vocabulaire", [])):
        champs.append(("pedagogie.vocabulaire.%d.texte" % i,
                       "Vocabulaire — %s" % voc.get("titre", "")))
    return champs


def _champs_tirage_etendu(bloc):
    """Les champs éditables du 9 + 1 : sa pédagogie, ses trois niveaux, son
    vocabulaire — construits depuis le bloc, jamais écrits en dur."""
    champs = [
        ("pedagogie.resume", "Résumé (deux lignes)"),
        ("pedagogie.pourquoi", "Pourquoi ce tirage"),
        ("pedagogie.le_tirage", "Le sens général"),
        ("pedagogie.comment_lire", "Comment lire"),
        ("pedagogie.apres", "Après la lecture"),
    ]
    for niveau in bloc.get("niveaux", []):
        champs.append(("pedagogie.positions_expliquees.%s" % niveau["id"],
                       "Niveau — %s" % niveau["nom"]))
    for i, voc in enumerate((bloc.get("pedagogie") or {}).get("vocabulaire", [])):
        champs.append(("pedagogie.vocabulaire.%d.texte" % i,
                       "Vocabulaire — %s" % voc.get("titre", "")))
    return champs


def _champs_tirage_choix(bloc):
    """Les champs éditables du tirage au choix : sa méthode et son vocabulaire."""
    champs = [
        ("pedagogie.resume", "Résumé (deux lignes)"),
        ("pedagogie.pourquoi", "Pourquoi ce tirage"),
        ("pedagogie.comment", "Comment choisir"),
        ("pedagogie.reticence", "La réticence à écarter"),
        ("pedagogie.apres", "Après la lecture"),
    ]
    for i, voc in enumerate((bloc.get("pedagogie") or {}).get("vocabulaire", [])):
        champs.append(("pedagogie.vocabulaire.%d.texte" % i,
                       "Vocabulaire — %s" % voc.get("titre", "")))
    return champs


def _cible_tirage(carte_id, champ):
    """La cible d'un texte pédagogique de tirage : (fichier, chemin_json)."""
    cle = carte_id[len("tirage-"):]
    donnees = _lire_json(TIRAGES)
    if cle in ("jour", "causale_3"):
        champs = CHAMPS_TIRAGE_JOUR if cle == "jour" else CHAMPS_TIRAGE_CAUSALE
        noeud = donnees
        if not isinstance(donnees.get(cle), dict):
            return None
        chemin = [cle] + _chemin_de_champ(champ)
    elif cle == "etendu_9_1":
        bloc = donnees.get("etendu_9_1") if isinstance(donnees, dict) else None
        if not isinstance(bloc, dict):
            return None
        champs = _champs_tirage_etendu(bloc)
        noeud = donnees
        chemin = ["etendu_9_1"] + _chemin_de_champ(champ)
    elif cle == "question_1":
        bloc = donnees.get("question_1") if isinstance(donnees, dict) else None
        if not isinstance(bloc, dict):
            return None
        champs = _champs_tirage_question(bloc)
        noeud = donnees
        chemin = ["question_1"] + _chemin_de_champ(champ)
    elif cle == "choix_3":
        bloc = donnees.get("choix_3") if isinstance(donnees, dict) else None
        if not isinstance(bloc, dict):
            return None
        champs = _champs_tirage_choix(bloc)
        noeud = donnees
        chemin = ["choix_3"] + _chemin_de_champ(champ)
    else:
        grille = ((donnees.get("grilles") or {}) if isinstance(donnees, dict)
                  else {}).get(cle)
        if isinstance(grille, dict):
            chemin = ["grilles", cle] + _chemin_de_champ(champ)
        else:
            # les croix vivent à la racine du fichier, comme les autres tirages
            grille = donnees.get(cle) if isinstance(donnees, dict) else None
            if not isinstance(grille, dict) or not grille.get("positions"):
                return None
            chemin = [cle] + _chemin_de_champ(champ)
        champs = _champs_tirage_grille(grille)
        noeud = donnees
    if champ not in dict(champs):
        return None
    # chaque maillon doit exister — on n'invente jamais une entrée
    for partie in chemin[:-1]:
        if isinstance(noeud, list):
            if isinstance(partie, int) and 0 <= partie < len(noeud):
                noeud = noeud[partie]
                continue
            return None
        noeud = noeud.get(partie) if isinstance(noeud, dict) else None
        if noeud is None:
            return None
    return TIRAGES, chemin


def _section_tirages():
    """Les tirages v1 : la couche pédagogique de chaque mode d'affichage."""
    donnees = _lire_json(TIRAGES)

    def carte_tirage(cle, nom, champs, entree):
        entree = entree if isinstance(entree, dict) else {}
        blocs = []
        for chemin_texte, titre in champs:
            chemin = _chemin_de_champ(chemin_texte)
            valeur = _valeur_nichée(entree, chemin)
            if valeur and valeur.strip():
                paras = _paragraphes(valeur)
                if paras:
                    blocs.append({"titre": titre, "paragraphes": paras,
                                  "champ": chemin_texte})
        return {
            "id": "tirage-" + cle, "genre": "message", "groupe": "Les tirages",
            "nom": nom, "etiquette": "",
            "apercu": next((b["paragraphes"][0] for b in blocs
                            if b["paragraphes"]), "")[:190],
            "champs": " · ".join(b["titre"] for b in blocs),
            "image": None, "mini": None,
            "cle_texte": cle, "fichier_texte": _relatif(TIRAGES),
            "textes": blocs, "note_texte": "",
        }

    cartes = [
        carte_tirage("question_1", "Une question",
                     _champs_tirage_question(donnees.get("question_1") or {}),
                     donnees.get("question_1")),
        carte_tirage("jour", "La carte du jour (ancienne, hors de l'accueil)",
                     CHAMPS_TIRAGE_JOUR, donnees.get("jour")),
        carte_tirage("causale_3", "Trois cartes — situation, nœud, levier",
                     CHAMPS_TIRAGE_CAUSALE, donnees.get("causale_3")),
        carte_tirage("etendu_9_1", "Neuf + une — approfondir en trois temps",
                     _champs_tirage_etendu(donnees.get("etendu_9_1") or {}),
                     donnees.get("etendu_9_1")),
        carte_tirage("choix_3", "Trois cartes au choix",
                     _champs_tirage_choix(donnees.get("choix_3") or {}),
                     donnees.get("choix_3")),
    ]
    for cle, grille in (donnees.get("grilles") or {}).items():
        cartes.append(carte_tirage(cle, "Grille — %s" % grille.get("nom", cle),
                                   _champs_tirage_grille(grille), grille))
    # les croix : même pédagogie qu'une grille, mais elles vivent à la racine
    for cle, bloc in donnees.items():
        if isinstance(bloc, dict) and bloc.get("grammaire") == "croix":
            cartes.append(carte_tirage(cle, bloc.get("nom", cle),
                                       _champs_tirage_grille(bloc), bloc))

    return [{
        "id": "tirages", "genre": "messages", "titre": "Les tirages",
        "note": "La couche pédagogique de chaque mode : pourquoi ce tirage, "
                "comment lire, le vocabulaire du jeu. Les grilles de relecture "
                "ont la leur. Ce que l'écran repliable « Comprendre ce tirage » "
                "affiche.",
        "cartes": cartes,
    }]


def construire_album():
    """L'album complet, prêt à afficher (dict sérialisable en JSON)."""
    noms = _lire_json(NOMS_CARTES) if False else None  # noms non utilisés au Tarot
    sections = []

    majeurs = [_fiche("major_%02d" % n, "Arcanes majeurs", str(n))
               for n in range(22)]
    sections.append({
        "id": "majeurs", "titre": "Arcanes majeurs",
        "note": "Les 22 arcanes du cycle. Éveil (la 79ᵉ carte, hors cycle) "
                "a sa propre section, à la fin.",
        "cartes": [c for c in majeurs if c],
    })

    for famille in FAMILLES:
        cartes = []
        for rang, rang_nom in RANGS:
            carte = _fiche("%s_%s" % (famille["cle"], rang),
                           "Famille %s" % famille["nom"], rang_nom)
            if carte:
                cartes.append(carte)
        sections.append({
            "id": famille["cle"], "titre": "Famille %s" % famille["nom"],
            "note": "Les 14 cartes de la famille %s." % famille["nom"],
            "cartes": cartes,
        })

    eveil = _fiche("master", "Éveil (hors cycle)", "79")
    if eveil:
        eveil["note_texte"] = ("Carte hors cycle — forme propre : pas de "
                               "positions, les trois variantes du regard.")
        sections.append({
            "id": "eveil", "titre": "Éveil (hors cycle)",
            "note": "La 79ᵉ carte. Elle sort comme les autres (1/79) mais "
                    "elle ne répond pas à la question : elle la regarde.",
            "cartes": [eveil],
        })

    sections += _section_tirages()

    cartes = [c for s in sections if s.get("genre") != "messages"
              for c in s["cartes"]]
    messages = [c for s in sections if s.get("genre") == "messages"
                for c in s["cartes"]]
    stats = {
        "cartes": len(cartes),
        "images": sum(1 for c in cartes if c["image"]),
        "textes": sum(1 for c in cartes if c["textes"]),
        "messages": len(messages),
    }
    return {"sections": sections, "stats": stats}
