"""L'utilitaire `scripts/textes_modifies.py` — la liste lisible avant un commit.

Le script sert au rituel « j'édite, puis je viens pousser » : il doit dire
QUELS textes de cartes diffèrent du dernier commit, et surtout ne pas mentir
sur ce qui est poussable. Deux pièges qu'on verrouille ici :

  - un champ qui n'est PAS un texte (nom, correspondance) ne doit jamais
    apparaître comme un texte modifié ;
  - le corpus de travail d'Eau vit HORS du dépôt : il ne doit jamais être
    annoncé comme « poussable, texte nouveau ».

L'index vient de `album.cible_ecriture` — donc ces tests protègent aussi la
cohérence entre l'ÉDITEUR et le script qui relit ses écritures.
"""
import pathlib

import album
import scripts.textes_modifies as TM

RACINE = pathlib.Path(__file__).resolve().parents[1]


# ------------------------------------------------------------- comparer

def test_detecte_un_texte_modifie():
    noms = {"4": "IV · Liberté"}
    avant = {"arcanes": {"4": {"lecture": "Un texte ancien."}}}
    apres = {"arcanes": {"4": {"lecture": "Un texte neuf."}}}
    d = TM.differences(avant, apres, ["arcanes"], noms)
    assert len(d) == 1
    assert d[0]["genre"] == "modifie"
    assert d[0]["carte"] == "IV · Liberté"
    assert d[0]["champ"] == "La carte et sa lecture"
    assert d[0]["cle"] == "lecture"


def test_detecte_un_texte_nouveau_et_un_texte_supprime():
    noms = {"4": "IV · Liberté", "5": "V · Vide"}
    avant = {"arcanes": {"4": {"lecture": "Ancien."}, "5": {"lecture": "Qui s'en va."}}}
    apres = {"arcanes": {"4": {"lecture": "Ancien.", "pour_l_annee": "Tout neuf."},
                         "5": {"lecture": ""}}}
    d = TM.differences(avant, apres, ["arcanes"], noms)
    genres = {(c["carte"], c["champ"]): c["genre"] for c in d}
    assert genres[("IV · Liberté", "Pour l’année")] == "nouveau"
    assert genres[("V · Vide", "La carte et sa lecture")] == "supprime"


def test_ignore_les_champs_qui_ne_sont_pas_des_textes():
    """« nom » et « correspondance » changent souvent sans qu'aucun texte ne
    bouge : les annoncer serait du bruit."""
    noms = {"4": "IV · Liberté"}
    avant = {"arcanes": {"4": {"nom": "Liberté", "correspondance": "Bélier",
                               "lecture": "Idem."}}}
    apres = {"arcanes": {"4": {"nom": "Liberté II", "correspondance": "Mars",
                               "lecture": "Idem."}}}
    assert TM.differences(avant, apres, ["arcanes"], noms) == []


def test_aucun_changement_ne_rend_rien():
    noms = {"9": "9 d'Eau · Paresse"}
    donnees = {"eau_9": {"invitation": "Pareil.", "comprendre": "Pareil aussi."}}
    assert TM.differences(donnees, donnees, [], noms) == []


def test_les_mineures_se_comparent_sans_prefixe():
    """mineurs.json porte ses cartes à la RACINE du fichier (pas de nœud
    intermédiaire) : le préfixe est la liste vide."""
    noms = {"eau_9": "9 d'Eau · Paresse"}
    avant = {"eau_9": {"invitation": "Avant."}}
    apres = {"eau_9": {"invitation": "Après."}}
    d = TM.differences(avant, apres, [], noms)
    assert len(d) == 1 and d[0]["champ"] == "L’invitation du jour"


# ----------------------------------------------------------- les noms

def test_nom_affiche_d_un_majeur():
    carte = {"id": "maj-13", "numero": 13, "etiquette": "XIII", "nom": "Transformation"}
    assert TM._nom_affiche(carte) == "XIII · Transformation"


def test_nom_affiche_d_une_mineure():
    pour = {"id": "eau-9", "nom": "Paresse"}
    assert TM._nom_affiche(pour) == "9 d'Eau · Paresse"
    as_ = {"id": "feu-as", "nom": "Source"}
    assert TM._nom_affiche(as_) == "As de Feu · Source"


# ------------------------------------------------------- le dépôt

def test_le_corpus_de_travail_d_eau_est_hors_depot():
    """Eau vit dans `_distillation/`, en dehors du dépôt de l'app : ses textes
    ne doivent JAMAIS être annoncés comme poussables."""
    chemin = album.DISTILLATION / "corpus_mineurs_eau.json"
    assert not TM._dans_le_depot(chemin)


def test_les_deux_fichiers_de_cartes_sont_dans_l_index():
    """L'index vient de `album.cible_ecriture` : c'est lui qui garantit que le
    script parle des mêmes fichiers que l'éditeur."""
    index = TM.index_des_textes()
    relatifs = {album._relatif(chemin) for chemin in index}
    assert "data/corpus/arcanes.json" in relatifs
    assert "data/corpus/mineurs.json" in relatifs
    # Eau est INTÉGRÉE (2026-10-13 : 14 images + 14 textes) : ses clés vivent
    # dans mineurs.json, l'app gagne le doublon et le corpus de travail
    # `_distillation/corpus_mineurs_eau.json` n'est plus indexé — voulu. La
    # prochaine famille (Nuages…) se ramassera seule, de la même façon.
    sources = album._sources_mineurs()
    assert sources["eau_roi"][1].name == "mineurs.json"
    assert sources["eau_reine"][1].name == "mineurs.json"
    # …et les préfixes sont justes : majeurs sous "arcanes", mineures à la racine.
    arcanes = next(e for c, e in index.items() if c.name == "arcanes.json")
    mineurs = next(e for c, e in index.items() if c.name == "mineurs.json")
    assert arcanes["prefixe"] == ["arcanes"]
    assert mineurs["prefixe"] == []


def test_le_script_tourne_et_sort_la_liste(capsys):
    assert TM.main() == 0
    sortie = capsys.readouterr().out
    assert "TEXTES DE CARTES MODIFIÉS DEPUIS LE DERNIER COMMIT" in sortie
    assert "un `push` ne pousse que des COMMITS" in sortie
