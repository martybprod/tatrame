#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quels TEXTES de cartes diffèrent du dernier commit — carte par carte.

Pour le rituel « j'édite dans l'album, puis je viens pousser ». Au lieu de
lire « data/corpus/arcanes.json modifié » (et de devoir fouiller un diff JSON
à la main), on lit :

    • XIII · Transformation — La carte et sa lecture
    • 9 d'Eau · Paresse — Comprendre cette carte

La correspondance (fichier, clé, champ) est celle de l'ÉDITEUR : le script
demande à `album.cible_ecriture` où vit chaque texte, donc ce qu'on voit ici
est exactement ce que « Appliquer à l'app » aurait écrit.

Deux sections, jamais mélangées :
  - SOUS GIT : ce qui partirait si tu commits ces fichiers ;
  - HORS DÉPÔT : le corpus de travail d'Eau, qui n'est pas dans le dépôt et
    ne partira donc JAMAIS tel quel (quoi qu'on commite).

LECTURE SEULE : le script ne modifie rien, il lit git et le disque.

Usage :
    ./venv/bin/python scripts/textes_modifies.py          # les textes changés
    ./venv/bin/python scripts/textes_modifies.py --etat    # + l'état du dépôt
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import album  # noqa: E402  (après l'insertion de RACINE dans sys.path)

#: Les libellés humains des champs de texte.
LIBELLES = dict(album.CHAMPS_MAJEURS)
LIBELLES.update(dict(album.CHAMPS_MINEURS))


# ------------------------------------------------------------------ git

def _git(*arguments):
    """(code, sortie) d'une commande git, depuis la racine de l'app."""
    r = subprocess.run(["git", *arguments], cwd=RACINE,
                       capture_output=True, text=True)
    return r.returncode, (r.stdout if r.returncode == 0 else "").strip()


def _racine_depot():
    return pathlib.Path(_git("rev-parse", "--show-toplevel")[1] or RACINE)


RACINE_DEPOT = _racine_depot()


def _dans_le_depot(chemin):
    try:
        pathlib.Path(chemin).resolve().relative_to(RACINE_DEPOT)
        return True
    except ValueError:
        return False


def _suivi(relatif):
    """Le fichier est-il connu de git (donc commitable) ?"""
    return _git("ls-files", "--error-unmatch", relatif)[0] == 0


def version_commitee(relatif):
    """Le JSON tel qu'il est dans le dernier commit, ou {} s'il n'y est pas."""
    code, sortie = _git("show", "HEAD:%s" % relatif)
    if code != 0:                      # absent du dernier commit
        return {}
    try:
        return json.loads(sortie)
    except ValueError:
        return {}


# -------------------------------------------------- l'index des textes

def index_des_textes(album_data=None):
    """Où vit chaque texte, et comment le nommer.

    Rend ``{chemin: {"prefixe": [...], "noms": {clé de carte: nom affiché}}}``.
    Le préfixe est le chemin JSON qui MÈNE aux cartes (``["arcanes"]`` pour le
    fichier des majeurs, ``[]`` pour les mineures).
    """
    album_data = album_data or album.construire_album()
    index = {}
    for section in album_data["sections"]:
        for carte in section["cartes"]:
            nom = _nom_affiche(carte)
            for bloc in carte["textes"]:
                cible = album.cible_ecriture(carte["id"], bloc["champ"])
                if cible is None:
                    continue
                chemin, chemin_json = cible
                entree = index.setdefault(chemin, {"prefixe": chemin_json[:-2],
                                                   "noms": {}})
                entree["noms"][chemin_json[-2]] = nom
    return index


def _nom_affiche(carte):
    """« XIII · Transformation » (majeur), « 9 d'Eau · Paresse » (mineure)."""
    if carte["id"].startswith("maj-"):
        return "%s · %s" % (carte.get("etiquette") or carte["numero"], carte["nom"])
    prefixe, _, rang = carte["id"].partition("-")
    famille = next((f["nom"] for f in album.FAMILLES if f["cle"] == prefixe), prefixe)
    rang = {"as": "As", "page": "Page", "chevalier": "Chevalier",
            "reine": "Reine", "roi": "Roi"}.get(rang, rang)
    liaison = "d'" if famille[:1].upper() in "AEIOUY" else "de "
    return "%s %s%s · %s" % (rang, liaison, famille, carte["nom"])


# ------------------------------------------------------------- comparer

def _noeud(donnees, chemin):
    noeud = donnees
    for cle in chemin:
        if not isinstance(noeud, dict):
            return {}
        noeud = noeud.get(cle)
    return noeud if isinstance(noeud, dict) else {}


def _textes_non_vides(donnees, prefixe):
    """Combien de textes écrits dans ce fichier (pour la section hors dépôt)."""
    total = 0
    for carte in _noeud(donnees, prefixe).values():
        if not isinstance(carte, dict):
            continue
        total += sum(1 for champ, valeur in carte.items()
                     if champ in LIBELLES and isinstance(valeur, str) and valeur.strip())
    return total


def _apercu(avant, apres):
    """Le petit bout de texte autour du PREMIER écart (« …a→b… »)."""
    i = 0
    while i < min(len(avant), len(apres)) and avant[i] == apres[i]:
        i += 1
    debut = max(0, i - 24)
    return ("…" + avant[debut:i + 48] + "…",
            "…" + apres[debut:i + 48] + "…")


def differences(ancien, nouveau, prefixe, noms):
    """Les textes qui diffèrent entre deux versions d'un même fichier.

    Rend une liste de dicts : ``genre`` (modifie / nouveau / supprime),
    ``carte``, ``champ`` (libellé humain), ``avant``, ``apres``.
    """
    vieilles = _noeud(ancien, prefixe)
    nouvelles = _noeud(nouveau, prefixe)
    trouves = []
    for cle in sorted(set(vieilles) | set(nouvelles)):
        carte_avant = vieilles.get(cle) or {}
        carte_apres = nouvelles.get(cle) or {}
        if not isinstance(carte_avant, dict) or not isinstance(carte_apres, dict):
            continue
        for champ in sorted(set(carte_avant) | set(carte_apres)):
            if champ not in LIBELLES:
                continue
            avant = carte_avant.get(champ) or ""
            apres = carte_apres.get(champ) or ""
            if not isinstance(avant, str) or not isinstance(apres, str):
                continue
            if avant == apres:
                continue
            genre = ("nouveau" if not avant
                     else "supprime" if not apres else "modifie")
            trouves.append({"genre": genre, "carte": noms.get(cle, cle),
                            "champ": LIBELLES[champ], "cle": champ,
                            "avant": avant, "apres": apres})
    return trouves


# --------------------------------------------------------------- rapports

GENRES = {"modifie": "modifié", "nouveau": "texte NOUVEAU", "supprime": "texte SUPPRIMÉ"}


def textes_sous_git(index):
    """Ce qui partirait dans un commit : (fichier, changements) par fichier."""
    resultat = []
    for chemin, entree in sorted(index.items()):
        if not _dans_le_depot(chemin):
            continue
        chemin = pathlib.Path(chemin)
        relatif = album._relatif(chemin)
        actuel = album._lire_json(chemin) if chemin.exists() else {}
        ancien = version_commitee(relatif) if _suivi(relatif) else {}
        changees = differences(ancien, actuel, entree["prefixe"], entree["noms"])
        if changees:
            resultat.append((relatif, changees))
    return resultat


def textes_hors_depot(index):
    """Ce qui n'est PAS dans le dépôt : (fichier, nombre de textes écrits)."""
    resultat = []
    for chemin, entree in sorted(index.items()):
        if _dans_le_depot(chemin):
            continue
        chemin = pathlib.Path(chemin)
        actuel = album._lire_json(chemin) if chemin.exists() else {}
        n = _textes_non_vides(actuel, entree["prefixe"])
        if n:
            resultat.append((album._relatif(chemin), n))
    return resultat


def etat_du_depot():
    """L'état du dépôt, pour le coup d'œil avant un commit."""
    _, statut = _git("status", "--short")
    _, branche = _git("rev-parse", "--abbrev-ref", "HEAD")
    _, dernier = _git("log", "-1", "--pretty=%h %s")
    lignes = ["État du dépôt (branche %s)" % branche,
              "  dernier commit : %s" % dernier, ""]
    suivies = [l for l in statut.splitlines() if not l.startswith("??")]
    nouvelles = [l for l in statut.splitlines() if l.startswith("??")]
    if suivies:
        lignes.append("  fichiers suivis, modifiés :")
        lignes += ["    %s" % l.rstrip() for l in suivies]
    if nouvelles:
        lignes.append("  nouveaux fichiers (non suivis — un `git add` explicite "
                      "est nécessaire) :")
        lignes += ["    %s" % l[3:] for l in nouvelles]
    if not suivies and not nouvelles:
        lignes.append("  rien en attente.")
    return "\n".join(lignes)


def main():
    avec_etat = "--etat" in sys.argv
    index = index_des_textes()

    if avec_etat:
        print(etat_du_depot())
        print()

    print("TEXTES DE CARTES MODIFIÉS DEPUIS LE DERNIER COMMIT")
    print()
    sous_git = textes_sous_git(index)
    if not sous_git:
        print("  Aucun. Le corpus de cartes est identique au dernier commit.")
    else:
        total = 0
        for relatif, changees in sous_git:
            total += len(changees)
            print("  %s" % relatif)
            for c in changees:
                print("    • %s — %s   [%s]" % (c["carte"], c["champ"],
                                                GENRES[c["genre"]]))
                if c["genre"] == "modifie":
                    avant, apres = _apercu(c["avant"], c["apres"])
                    print("        avant : %s" % avant)
                    print("        après : %s" % apres)
            print()
        print("%d texte%s modifié%s dans %d fichier%s."
              % (total, "s" if total > 1 else "", "s" if total > 1 else "",
                 len(sous_git), "s" if len(sous_git) > 1 else ""))
        print()
        print("Pour les emporter (un commit = une intention, jamais `git add -A`) :")
        print("    git add %s" % " ".join(r for r, _ in sous_git))
        print('    git commit -m "Textes : …"')
        print("    git push        # ← un push = un déploiement Coolify")
    print()
    print("Rappel : un `push` ne pousse que des COMMITS. Tant qu'un texte n'est")
    print("pas dans un commit, il reste local.")

    hors = textes_hors_depot(index)
    if hors:
        print()
        print("HORS DU DÉPÔT GIT — ces textes ne partiront JAMAIS tel quel :")
        for relatif, n in hors:
            print("    %s   (%d textes écrits)" % (relatif, n))
        print("    → une famille pas encore câblée dans l'app ; à traiter le jour")
        print("      où on l'intègre (copier le corpus dans data/corpus/ de l'app).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
