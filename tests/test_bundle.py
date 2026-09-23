"""Le bundle du démarrage — lexique, conventions, jour, aperçu, portrait et
ciel en UNE requête.

Le bundle appelle les routes elles-mêmes (voir app.py::api_bundle) : les tests
garantissent qu'il ne dérive JAMAIS des vues seules, qu'il respecte le rejeu
`?date=`, la mémoïsation (même réponse relue) et le verrou des comptes.
"""
import pytest

import app as application

from tests.test_profils import SAISIE, client   # noqa: F401 (fixture pytest)


def test_le_bundle_reunit_tout_le_demarrage(client):   # noqa: F811
    client.post("/api/profil", json=SAISIE)
    b = client.get("/api/bundle/jean-test").get_json()
    for cle in ("lexique", "conventions", "jour", "apercu", "portrait", "ciel"):
        assert cle in b, f"le bundle doit porter « {cle} »"
    # Chaque partie est EXACTEMENT ce que la route seule renverrait — une
    # seule source de vérité, le bundle ne réinvente rien.
    assert b["jour"] == client.get("/api/jour/jean-test").get_json()
    assert b["apercu"] == client.get("/api/apercu/jean-test").get_json()
    assert b["portrait"] == client.get("/api/portrait/jean-test").get_json()
    assert b["ciel"] == client.get("/api/ciel/jean-test").get_json()
    assert b["lexique"] == client.get("/api/lexique").get_json()
    assert b["conventions"] == client.get("/api/conventions").get_json()


def test_la_date_traverse_le_bundle(client):   # noqa: F811
    client.post("/api/profil", json=SAISIE)
    b = client.get("/api/bundle/jean-test?date=2026-07-16").get_json()
    assert b["jour"]["date"] == "2026-07-16"


def test_le_bundle_est_rejouable_a_l_identique(client):   # noqa: F811
    """Déterminisme + mémoïsation : la même journée relue deux fois (deuxième
    lecture servie par la mémoire) donne mot pour mot le même Jour."""
    client.post("/api/profil", json=SAISIE)
    un = client.get("/api/bundle/jean-test").get_json()["jour"]
    deux = client.get("/api/bundle/jean-test").get_json()["jour"]
    assert un == deux


def test_profil_inconnu_repond_404(client):   # noqa: F811
    assert client.get("/api/bundle/n-importe").status_code == 404


def test_le_verrou_s_applique_au_bundle(client, tmp_path, monkeypatch):   # noqa: F811
    """Un profil existant mais PAS déverrouillé dans CETTE session reste
    protégé : le bundle ne doit pas devenir une porte dérobée sur le Jour."""
    client.post("/api/profil", json=SAISIE)
    # Nouvelle session (nouveau client) : rien n'y est déverrouillé.
    with application.app.test_client() as autre:
        assert autre.get("/api/bundle/jean-test").status_code == 401
