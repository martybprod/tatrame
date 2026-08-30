"""Le tableau de bord bêta — suppression d'un commentaire.

Un commentaire signalé par un testeur, une fois le problème réglé par Martin,
doit pouvoir être retiré (deux surfaces : l'API JSON utilisée dans l'app, et
la vieille page Jinja de repli — même mécanique de fond dans les deux cas).
"""
import json

import pytest

import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", tmp_path / "profils")
    application.PROFILS.mkdir()
    monkeypatch.setattr(application, "COMMENTAIRES_PATH", tmp_path / "commentaires" / "commentaires.json")
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        c.post("/api/profil", json={
            "id": "jean-test", "prenoms_nom": ["Jean", "Test"],
            "annee": 1975, "mois": 7, "jour": 16,
        })
        c.post("/api/commentaire", json={"texte": "un bug ici", "profil": "jean-test"})
        yield c


def _comme_admin(client):
    with client.session_transaction() as sess:
        sess["admin_ok"] = True


# ------------------------------------------------- DELETE /api/admin/commentaire/<id>

def test_supprimer_exige_d_etre_admin(client):
    cid = application._lire_commentaires()[0]["id"]
    r = client.delete(f"/api/admin/commentaire/{cid}")
    assert r.status_code == 403
    assert len(application._lire_commentaires()) == 1  # rien supprimé


def test_supprimer_retire_le_commentaire(client):
    cid = application._lire_commentaires()[0]["id"]
    _comme_admin(client)
    r = client.delete(f"/api/admin/commentaire/{cid}")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True
    assert application._lire_commentaires() == []


def test_supprimer_un_id_inconnu_ne_touche_a_rien(client):
    _comme_admin(client)
    r = client.delete("/api/admin/commentaire/id-qui-n-existe-pas")
    assert r.status_code == 404
    assert len(application._lire_commentaires()) == 1


def test_supprimer_n_efface_que_le_bon(client):
    client.post("/api/commentaire", json={"texte": "un autre", "profil": "jean-test"})
    avant = application._lire_commentaires()
    assert len(avant) == 2
    _comme_admin(client)
    client.delete(f"/api/admin/commentaire/{avant[0]['id']}")
    apres = application._lire_commentaires()
    assert len(apres) == 1
    assert apres[0]["id"] == avant[1]["id"]


# ------------------------------------------------- page Jinja de repli (?supprimer=)

def test_page_jinja_supprimer_exige_d_etre_admin(client):
    cid = application._lire_commentaires()[0]["id"]
    r = client.get(f"/admin/commentaires?supprimer={cid}")
    assert r.status_code == 403
    assert len(application._lire_commentaires()) == 1


def test_page_jinja_supprimer_retire_le_commentaire(client):
    cid = application._lire_commentaires()[0]["id"]
    _comme_admin(client)
    r = client.get(f"/admin/commentaires?supprimer={cid}")
    assert r.status_code == 302  # redirige vers la liste, comme « marquer lu »
    assert application._lire_commentaires() == []
