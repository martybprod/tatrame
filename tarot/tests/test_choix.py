"""Tests du tirage au choix — les cartes désignées, pas tirées.

Ce que ces tests protègent :
  · /api/jeu sert les 79 faces et la méthode (l'entonnoir de Greer) ;
  · /api/lecture compose une lecture avec les cartes DONNÉES, dans l'ordre ;
  · aucun hasard : deux appels identiques donnent la même lecture ;
  · les entrées invalides sont refusées ;
  · l'album édite la méthode.
"""
import pytest

import album
from app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_jeu_face_visible(client):
    d = client.get("/api/jeu").get_json()
    assert d["total"] == 79
    assert len(d["cartes"]) == 79
    assert all(c["image"] for c in d["cartes"])
    assert "comment" in d["methode"] and "reticence" in d["methode"]


def test_lecture_des_cartes_choisies(client):
    d = client.get("/api/lecture?cartes=air_10,terre_03,major_21").get_json()
    assert [c["id"] for c in d["cartes"]] == ["air_10", "terre_03", "major_21"]
    assert d["mode"] == 3
    assert d["choix"] is True
    assert d["lecture"]["seuil"].strip()
    assert len(d["lecture"]["liaisons"]) >= 1
    assert d["lecture"]["cloture"]["nom"]
    # les textes des quatre grilles sont résolus pour ces cartes
    for gid in ("causale_3", "visible_latent_resolution", "temps",
                "lecon_geste_question"):
        assert gid in d["textes_par_grille"]


def test_lecture_sans_hasard(client):
    """Deux appels identiques : même lecture, au mot près."""
    a = client.get("/api/lecture?cartes=feu_02,eau_05,air_03").get_json()
    b = client.get("/api/lecture?cartes=feu_02,eau_05,air_03").get_json()
    assert a["lecture"] == b["lecture"]
    assert a["textes_par_grille"] == b["textes_par_grille"]


def test_lecture_refuse_les_entrees_invalides(client):
    assert client.get("/api/lecture?cartes=feu_02,eau_05").status_code == 400
    assert client.get("/api/lecture?cartes=feu_02,feu_02,air_03").status_code == 400
    assert client.get("/api/lecture?cartes=feu_02,eau_05,inventee").status_code == 400


def test_lecture_grille_au_choix(client):
    d = client.get(
        "/api/lecture?cartes=air_10,terre_03,major_21&grille=lecon_geste_question"
    ).get_json()
    assert d["grille"] == "lecon_geste_question"
    assert d["positions_def"][0]["id"] == "lecon"


def test_eveil_peut_etre_choisi(client):
    d = client.get("/api/lecture?cartes=master,feu_02,eau_05").get_json()
    master = d["cartes"][0]
    assert master["type"] == "hors_cycle"
    assert master["regard"]
    r = d["textes_par_grille"]["causale_3"]["master"]["amene"]
    assert r["regard"] is True and r["texte"].strip()


def test_album_edite_la_methode_du_choix():
    for champ, _titre in album._champs_tirage_choix(
            {"pedagogie": {"vocabulaire": [{"titre": "x"}]}}):
        assert album._cible_tirage("tirage-choix_3", champ) is not None
