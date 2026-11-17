"""Le tableau de bord d'activité — les sections réellement visitées.

Régression vécue (Martin, 2026-11-17) : le Tarot n'apparaissait jamais dans
« Sections les plus visitées » — les clics d'onglets n'étaient pas journalisés
côté client (le handler #nav appelait montrer() sans passer par montrerVue(),
seul à envoyer l'événement `nav`), et le libellé n'existait pas côté serveur.
Ces tests verrouillent les DEUX bouts : l'événement `nav` arrive, la synthèse
le compte, le libellé « Tarot » l'affiche.
"""
import pytest

import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", tmp_path / "profils")
    application.PROFILS.mkdir()
    monkeypatch.setattr(application, "ACTIVITE_PATH", tmp_path / "activite.jsonl")
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        # Créer le PREMIER profil déverrouille la session (compte racine) :
        # c'est ce que /api/activite exige pour enregistrer.
        c.post("/api/profil", json={
            "id": "jean-test", "prenoms_nom": ["Jean", "Test"],
            "annee": 1975, "mois": 7, "jour": 16,
        })
        yield c


# ------------------------------------------------- /api/activite → synthèse

def test_le_nav_tarot_est_journalise_et_compte(client):
    r = client.post("/api/activite",
                    json={"type": "nav", "vue": "tarot", "profil": "jean-test"})
    assert r.status_code == 204
    _, sections = application._synthese_activite()
    assert ("tarot", 1) in sections


def test_le_tarot_a_son_libelle_de_section():
    assert application._LIBELLES_VUE["tarot"] == "Tarot"


def test_sans_session_deverrouillee_on_ne_journalise_pas(client):
    """La porte côté serveur : sans compte déverrouillé, aucun événement n'est
    écrit — sinon n'importe quel visiteur anonyme gonflerait le journal."""
    with client.session_transaction() as sess:
        sess.clear()
    client.post("/api/activite",
                json={"type": "nav", "vue": "tarot", "profil": "jean-test"})
    assert application._lire_activite() == []
