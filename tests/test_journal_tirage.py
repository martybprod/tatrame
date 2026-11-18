"""Garder un tirage de tarot dans le journal (2026-11-17).

La note du journal peut porter un `tirage` structuré : de quoi rouvrir la donne
exacte (un tirage est déterministe, la graine rejoue les mêmes cartes). Le
serveur ne garde QUE les champs attendus, validés ; tout le reste est refusé.
"""
import pytest

import app as application

TIRAGE = {"v": 1, "tirage": "croix", "mode": 11, "graine": 1551067239233072,
          "croix": "croix_osho", "grille": "causale_3", "nb": 10,
          "revelees": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "vue": "recit", "recit": 2}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "JOURNAL", tmp_path)
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c


def _poster(client, **corps):
    return client.post("/api/journal/test-profil", json=corps)


def test_un_tirage_garde_sans_note_devient_une_entree(client):
    r = _poster(client, texte="", source_nom="Tarot · La croix",
                source_texte="1. ce qui couvre — Confiance", tirage=TIRAGE)
    assert r.status_code == 200
    e = r.get_json()
    assert e["texte"] == "Tirage gardé."
    assert e["tirage"]["graine"] == 1551067239233072
    assert e["tirage"]["croix"] == "croix_osho"
    relu = client.get("/api/journal/test-profil").get_json()
    assert relu[0]["tirage"]["tirage"] == "croix"


def test_la_note_personnelle_est_conservee(client):
    e = _poster(client, texte="Je retiens la patience.", tirage=TIRAGE).get_json()
    assert e["texte"] == "Je retiens la patience."


def test_une_note_ordinaire_ne_change_pas(client):
    e = _poster(client, texte="Une note simple").get_json()
    assert "tirage" not in e
    assert _poster(client, texte="").status_code == 400


@pytest.mark.parametrize("abime", [
    {"tirage": "inconnu"},
    {"mode": 7},
    {"graine": -1},
    {"graine": 2 ** 60},
    {"graine": "42"},
    {"croix": "../../etc"},
    {"nb": 99},
    {"revelees": [0, 99]},
    {"choix": {"ids": []}},
    {"graine": None},            # ni graine ni sélection : rien à rejouer
])
def test_un_tirage_abime_est_refuse(client, abime):
    mauvais = {**TIRAGE, **abime}
    assert _poster(client, texte="x", tirage=mauvais).status_code == 400


def test_seuls_les_champs_attendus_sont_gardes(client):
    e = _poster(client, texte="x", tirage={**TIRAGE, "pirate": "<script>", "x": [1] * 500}).get_json()
    assert set(e["tirage"]) <= {"v", "tirage", "mode", "graine", "croix", "grille",
                                "question", "choix", "nb", "revelees", "vue", "recit"}


def test_un_tirage_ne_vient_pas_d_un_non_dict(client):
    assert _poster(client, texte="x", tirage="croix").status_code == 400
    assert _poster(client, texte="x", tirage=[1, 2]).status_code == 400


def test_tirage_au_choix_porte_ses_cartes(client):
    t = {"v": 1, "tirage": "trois", "mode": 3, "nb": 3, "revelees": [0, 1, 2],
         "choix": {"ids": ["air_02", "feu_03", "major_04"], "derniere": "eau_07"}}
    e = _poster(client, texte="x", tirage=t).get_json()
    assert e["tirage"]["choix"]["ids"] == ["air_02", "feu_03", "major_04"]
