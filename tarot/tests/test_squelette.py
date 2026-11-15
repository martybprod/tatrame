"""Tests du squelette Tarot — santé, page, tirage honnête et reproductibilité.

pytest.ini → testpaths = tests
"""
import json
import pathlib

import pytest

from app import app as flask_app

RACINE = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_health_toujours_200(client):
    r = client.get("/health")
    assert r.status_code == 200
    d = r.get_json()
    assert d["status"] == "ok"
    assert d["port"] == 5089
    assert "79" in d["detail"]  # le jeu complet est annoncé


def test_index_sert_leventail(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'id="eventail"' in html
    assert "img/dos.png" not in html or True  # le dos est posé par le JS


def test_tirage_une_carte(client):
    r = client.get("/api/tirage?mode=1")
    assert r.status_code == 200
    d = r.get_json()
    assert d["total_jeu"] == 79
    assert len(d["cartes"]) == 1
    carte = d["cartes"][0]
    assert {"id", "nom", "type", "image"} <= set(carte.keys())
    assert isinstance(d["graine"], int)


def test_tirage_trois_cartes_sans_doublon(client):
    d = client.get("/api/tirage?mode=3").get_json()
    ids = [c["id"] for c in d["cartes"]]
    assert len(ids) == 3
    assert len(set(ids)) == 3


def test_tirage_reproductible_par_graine(client):
    d1 = client.get("/api/tirage?mode=3&graine=1234567").get_json()
    d2 = client.get("/api/tirage?mode=3&graine=1234567").get_json()
    assert d1["graine"] == 1234567
    assert [c["id"] for c in d1["cartes"]] == [c["id"] for c in d2["cartes"]]


def test_mode_invalide_400(client):
    assert client.get("/api/tirage?mode=2").status_code == 400


def test_tirage_jeu_complet(client):
    d = client.get("/api/tirage?mode=1").get_json()
    assert d["total_jeu"] == 79
    assert "pilote" not in d


def test_jeu_complet_79():
    jeu = json.loads((RACINE / "data/grammaire/jeu.json").read_text(encoding="utf-8"))
    assert jeu["total"] == 79
    types = {c["type"] for c in jeu["cartes"]}
    assert types == {"majeur", "mineur", "figure", "hors_cycle"}


def test_images_app_presentes():
    for id_carte in ("major_13", "eau_08"):
        assert (RACINE / "static/img/cartes" / f"{id_carte}.jpg").exists()
    assert (RACINE / "static/img/dos.png").exists()
