"""L'édition des textes depuis l'album du Tarot — la SEULE écriture du corpus.

Portage exact des tests de Ta Trame (test_album_edition.py) : mêmes contrats,
adaptés à la cible tarot (79 fichiers individuels, champs nichés, tableaux).

  - chaque texte affiché sait OÙ il vit (``cible_ecriture``) ;
  - une cible inconnue arrête TOUT le lot avant la moindre écriture ;
  - on sauvegarde avant d'écrire, et le format du corpus ne bouge pas ;
  - la route refuse un visiteur qui n'est pas admin d'album.

Les tests d'écriture tournent sur un faux corpus, isolé (rien de réel n'est
touché). Le dernier test, lui, tourne sur le VRAI corpus : tout texte que
l'album montre doit pouvoir s'écrire quelque part.
"""
import json
import pathlib

import pytest

import album

RACINE = pathlib.Path(__file__).resolve().parents[1]

from app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _ecrire(chemin, donnees):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")


FICHE_MINEURE = {
    "id": "eau_02", "nom": "Amitié", "type": "mineur", "famille": "eau",
    "degre": 2, "element": "eau",
    "mots_cles": ["deux arbres", "le rire"],
    "tension": {"pousse": "partager", "retient": "exiger"},
    "lumiere": "Lumière ancienne.",
    "ombre": {"mode": "differe", "texte": "Ombre ancienne.",
              "issue": "Issue ancienne."},
    "questions": ["Question une ?", "Question deux ?"],
    "lecon": "Leçon ancienne.",
    "image": {"geste": "g", "seuil": "s", "detail": "d"},
    "micro_geste": "Geste ancien.",
    "positions": {"jour": "Jour ancien.", "amene": "Amène ancien.",
                  "se_joue": "Se joue ancien.", "essayer": "Essai ancien."},
    "source_referentielle": {},
}

FICHE_MAJEURE = dict(FICHE_MINEURE, id="major_13", nom="Transformation",
                     type="majeur", registre="interieur", famille=None,
                     degre=None, rang=None)

FICHE_MASTER = {
    "id": "master", "nom": "Éveil", "type": "hors_cycle",
    "registre": "hors_cycle", "element": None,
    "mots_cles": ["le sommet"],
    "tension": {"pousse": "regarder", "retient": "courir ailleurs"},
    "lumiere": "Lumière du sommet.",
    "ombre": {"mode": "retourne", "texte": "Ombre du sommet.",
              "issue": "Issue du sommet."},
    "le_regard": ["Regard une.", "Regard deux.", "Regard trois."],
    "questions": ["Question du sommet ?"],
    "lecon": "Leçon du sommet.",
    "image": {"geste": "g", "seuil": "s", "detail": "d"},
    "micro_geste": "Geste du sommet.",
    "source_referentielle": {},
}


@pytest.fixture
def faux_corpus(tmp_path, monkeypatch):
    """Un corpus minimal, isolé : rien de réel n'est touché par ces tests."""
    corpus = tmp_path / "data" / "corpus" / "cartes"
    _ecrire(corpus / "eau_02.json", FICHE_MINEURE)
    _ecrire(corpus / "major_13.json", FICHE_MAJEURE)
    _ecrire(corpus / "master.json", FICHE_MASTER)
    monkeypatch.setattr(album, "CORPUS", corpus)
    monkeypatch.setattr(album, "IMAGES", tmp_path / "img")
    return corpus


# ------------------------------------------------------------- les cibles

def test_cible_champ_simple(faux_corpus):
    chemin, cle = album.cible_ecriture("eau_02", "lumiere")
    assert chemin == faux_corpus / "eau_02.json"
    assert cle == ["lumiere"]


def test_cible_champ_niche(faux_corpus):
    chemin, cle = album.cible_ecriture("eau_02", "ombre.texte")
    assert cle == ["ombre", "texte"]
    chemin, cle = album.cible_ecriture("eau_02", "positions.jour")
    assert cle == ["positions", "jour"]


def test_cible_indice_de_tableau(faux_corpus):
    chemin, cle = album.cible_ecriture("eau_02", "questions.0")
    assert cle == ["questions", 0]
    assert isinstance(cle[1], int)


def test_cible_le_regard_sur_master(faux_corpus):
    chemin, cle = album.cible_ecriture("master", "le_regard.1")
    assert cle == ["le_regard", 1]
    assert chemin == faux_corpus / "master.json"


def test_cible_inconnue_refusee(faux_corpus):
    assert album.cible_ecriture("major_13", "nom") is None          # métadonnée
    assert album.cible_ecriture("major_99", "lumiere") is None      # fiche absente
    assert album.cible_ecriture("eau_02", "le_regard.0") is None    # pas sur une mineure
    assert album.cible_ecriture("master", "positions.jour") is None # pas de positions
    assert album.cible_ecriture("eau_02", "questions.9") is None    # indice absent
    assert album.cible_ecriture("inconnu", "lumiere") is None


# ------------------------------------------------------------- l'écriture

def test_appliquer_ecrit_et_sauvegarde(faux_corpus):
    rapport = album.appliquer(
        [{"carte": "eau_02", "champ": "lumiere", "texte": "Lumière neuve : éàü."}])

    donnees = json.loads((faux_corpus / "eau_02.json").read_text(encoding="utf-8"))
    assert donnees["lumiere"] == "Lumière neuve : éàü."
    assert donnees["nom"] == "Amitié"        # rien d'autre n'a bougé
    assert donnees["positions"]["jour"] == "Jour ancien."

    # Format du corpus préservé : indentation 2, accents bruts, newline final.
    brut = (faux_corpus / "eau_02.json").read_text(encoding="utf-8")
    assert brut.endswith("\n")
    assert "éàü" in brut and "\\u00e9" not in brut

    # La sauvegarde contient l'ÉTAT D'AVANT.
    assert len(rapport) == 1
    sauvegarde = pathlib.Path(rapport[0]["sauvegarde"])
    assert sauvegarde.exists()
    ancien = json.loads(sauvegarde.read_text(encoding="utf-8"))
    assert ancien["lumiere"] == "Lumière ancienne."


def test_appliquer_champ_niche_et_tableau(faux_corpus):
    album.appliquer([
        {"carte": "eau_02", "champ": "ombre.texte", "texte": "Ombre neuve."},
        {"carte": "eau_02", "champ": "questions.1", "texte": "Question neuve ?"},
        {"carte": "master", "champ": "le_regard.2", "texte": "Regard neuf."},
    ])
    ombre = json.loads((faux_corpus / "eau_02.json").read_text(encoding="utf-8"))
    assert ombre["ombre"]["texte"] == "Ombre neuve."
    assert ombre["ombre"]["mode"] == "differe"        # le mode n'a pas bougé
    assert ombre["questions"][1] == "Question neuve ?"
    assert ombre["questions"][0] == "Question une ?"  # pas d'autre indice touché
    master = json.loads((faux_corpus / "master.json").read_text(encoding="utf-8"))
    assert master["le_regard"] == ["Regard une.", "Regard deux.", "Regard neuf."]


def test_appliquer_un_lot_avec_cible_inconnue_n_ecrit_rien(faux_corpus):
    """Une clé inconnue arrête le lot ENTIER : jamais de demi-écriture."""
    avant = (faux_corpus / "eau_02.json").read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        album.appliquer([
            {"carte": "eau_02", "champ": "lumiere", "texte": "Nouveau."},
            {"carte": "eau_02", "champ": "inexistant", "texte": "…"},
        ])
    assert (faux_corpus / "eau_02.json").read_text(encoding="utf-8") == avant
    assert not (faux_corpus / "_sauvegardes").exists()


def test_appliquer_refuse_texte_vide(faux_corpus):
    with pytest.raises(ValueError):
        album.appliquer([{"carte": "eau_02", "champ": "lumiere", "texte": "   "}])
    assert not (faux_corpus / "_sauvegardes").exists()


# ---------------------------------------------------------------- l'album

def test_album_construit_les_sections(faux_corpus):
    a = album.construire_album()
    titres = [s["titre"] for s in a["sections"]]
    assert titres == ["Arcanes majeurs", "Famille Feu", "Famille Eau",
                      "Famille Air", "Famille Terre", "Éveil (hors cycle)",
                      "Les tirages"]
    assert a["stats"]["cartes"] == 3

    master = next(s for s in a["sections"] if s["titre"] == "Éveil (hors cycle)")["cartes"][0]
    champs = [b["champ"] for b in master["textes"]]
    assert "le_regard.0" in champs
    assert not any(c.startswith("positions.") for c in champs)

    mineure = a["sections"][2]["cartes"][0]   # eau_02 : Deux de la famille Eau
    assert mineure["nom"] == "Amitié"
    assert "positions.jour" in [b["champ"] for b in mineure["textes"]]


# --------------------------------------------------- le VRAI corpus (filet)

def test_tout_texte_affiche_dans_le_vrai_corpus_a_une_cible():
    """Le filet de couverture : sur le VRAI corpus (79 fiches), chaque texte
    que l'album montre doit résoudre vers une cible d'écriture réelle."""
    a = album.construire_album()
    verifiees = 0
    for section in a["sections"]:
        for carte in section["cartes"]:
            assert carte["fichier_texte"], carte["id"]
            for bloc in carte["textes"]:
                chemin, cle = album.cible_ecriture(carte["id"], bloc["champ"])
                assert chemin is not None, (carte["id"], bloc["champ"])
                fiche = json.loads(pathlib.Path(chemin).read_text(encoding="utf-8"))
                noeud = fiche
                for part in cle[:-1]:
                    noeud = noeud[part]
                assert isinstance(noeud[cle[-1]], str), (carte["id"], bloc["champ"])
                verifiees += 1
    assert verifiees > 600   # 79 fiches × ~9 textes


# ---------------------------------------------------------------- la route

def test_route_refuse_sans_session_album(client, faux_corpus):
    resp = client.post("/api/album/enregistrer", json={
        "modifications": [{"carte": "eau_02", "champ": "lumiere", "texte": "X."}]})
    assert resp.status_code == 403
    assert resp.get_json()["erreur"] == "non-admin"
