"""Les profils — créer, MODIFIER, supprimer.

La modification manquait, et ça bloquait l'usage : une fois ses informations
saisies, l'utilisateur ne pouvait plus rien corriger. Or l'heure de naissance
est justement ce dont on doute le plus, et c'est ce qui déplace le plus
l'Ascendant.
"""
import json

import pytest

import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", tmp_path)
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c


# Trois-Pistoles — le village que `cities500` aurait perdu.
LIEU = 8672912
SAISIE = {
    "id": "jean-test", "prenoms_nom": ["Jean", "Test"],
    "annee": 1975, "mois": 7, "jour": 16, "heure": 14, "minute": 30,
    "lieu_id": LIEU,
}


def test_creer(client):
    r = client.post("/api/profil", json=SAISIE)
    assert r.status_code == 200
    p = r.get_json()["profil"]
    assert p["naissance"]["lieu"] == "Trois-Pistoles"
    assert p["naissance"]["fuseau"] == "America/Toronto"
    assert p["naissance"]["lieu_id"] == LIEU, "l'identifiant du lieu doit être conservé"


def test_modifier_recalcule_le_theme(client):
    """LE test qui compte : corriger l'heure doit déplacer l'Ascendant."""
    client.post("/api/profil", json=SAISIE)
    avant = client.get("/api/portrait/jean-test").get_json()["theme"]["angles"]["asc"]

    r = client.put("/api/profil/jean-test", json={**SAISIE, "heure": 3, "minute": 0})
    assert r.status_code == 200
    assert r.get_json()["profil"]["naissance"]["heure"] == 3

    apres = client.get("/api/portrait/jean-test").get_json()["theme"]["angles"]["asc"]
    assert (avant["signe"], avant["degre"]) != (apres["signe"], apres["degre"]), (
        "changer l'heure doit changer l'Ascendant, sinon la modification est cosmétique"
    )


def test_modifier_garde_l_identifiant(client):
    """Renommer ne doit pas casser le profil courant du navigateur.

    L'identifiant est la clé du fichier ET ce que le navigateur retient : le
    changer sur un renommage perdrait le profil affiché.
    """
    client.post("/api/profil", json=SAISIE)
    r = client.put("/api/profil/jean-test", json={**SAISIE, "prenoms_nom": ["Jean", "Autre"]})
    assert r.get_json()["profil"]["id"] == "jean-test"
    assert r.get_json()["profil"]["nom_affiche"] == "Jean Autre"


def test_vieux_profil_sans_lieu_id_reste_modifiable(client, tmp_path):
    """Le piège que seul l'usage a révélé.

    Les premiers profils ont été écrits sans identifiant de lieu. Sans lui, le
    formulaire de modification n'a rien à renvoyer → le profil devient
    IMMODIFIABLE, c'est-à-dire exactement le blocage qu'on cherchait à lever.
    Le serveur doit le retrouver par les coordonnées, toujours enregistrées.
    """
    ancien = {
        "id": "ancien", "prenoms_nom": ["Vieux", "Profil"],
        "naissance": {
            "annee": 1975, "mois": 7, "jour": 16, "heure": 14, "minute": 30,
            "lieu": "Trois-Pistoles", "lat": 48.12665, "lon": -69.1697,
            "fuseau": "America/Toronto",
            # pas de lieu_id : c'est tout le sujet
        },
        "fold": 0,
    }
    (tmp_path / "ancien.json").write_text(json.dumps(ancien), encoding="utf-8")

    r = client.get("/api/profil/ancien")
    assert r.status_code == 200
    assert r.get_json()["naissance"]["lieu_id"] == LIEU, (
        "le lieu doit être retrouvé par ses coordonnées"
    )


def test_supprimer(client):
    client.post("/api/profil", json=SAISIE)
    assert client.delete("/api/profil/jean-test").status_code == 200
    assert client.get("/api/profil/jean-test").status_code == 404


def test_liste_porte_de_quoi_choisir(client):
    """Un identifiant ne suffit pas à distinguer deux profils."""
    client.post("/api/profil", json=SAISIE)
    client.post("/api/profil", json={**SAISIE, "id": "autre", "prenoms_nom": ["Autre", "Test"]})
    liste = client.get("/api/profils").get_json()
    assert len(liste) == 2
    for p in liste:
        assert p["nom_affiche"] and p["naissance"] and p["lieu"]


# ------------------------------------------------ la validation, côté serveur

@pytest.mark.parametrize("champ,valeur,attendu", [
    ("jour", 31, "n'existe pas au calendrier"),      # 31 février
    ("annee", 1700, "entre 1800 et 2100"),
    ("heure", 25, "entre 00:00 et 23:59"),
    ("prenoms_nom", ["Jean"], "au moins un prénom et un nom"),
    ("lieu_id", 999999999, "n'existe pas dans la base"),
])
def test_saisie_fautive_refusee_avec_un_message_clair(client, champ, valeur, attendu):
    """Un profil mal formé donnerait un thème FAUX plutôt qu'une erreur.

    C'est le pire des deux mondes : l'app aurait l'air de marcher. D'où une
    validation côté serveur, avec un message qu'un humain comprend.
    """
    saisie = {**SAISIE, champ: valeur}
    if champ == "jour":
        saisie["mois"] = 2
    r = client.post("/api/profil", json=saisie)
    assert r.status_code == 400
    assert attendu in r.get_json()["erreur"]


def test_un_profil_corrompu_n_empeche_pas_les_autres(client, tmp_path):
    """Un fichier illisible ne doit pas vider toute la liste."""
    client.post("/api/profil", json=SAISIE)
    (tmp_path / "casse.json").write_text("{ ceci n'est pas du json", encoding="utf-8")
    liste = client.get("/api/profils").get_json()
    assert [p["id"] for p in liste] == ["jean-test"]


def test_apercu_ne_montre_jamais_None(client, tmp_path):
    """Un profil d'avant `nom_affiche` ne doit pas afficher « None ».

    Même famille de piège que le `lieu_id` manquant : un champ ajouté après
    coup laisse les anciens profils sans lui. L'aperçu retombe sur les prénoms.
    """
    ancien = {
        "id": "sans-nom", "prenoms_nom": ["Vieux", "Profil"],
        "naissance": {"annee": 1980, "mois": 4, "jour": 6, "heure": 5, "minute": 0,
                      "lieu": "Trois-Pistoles", "lieu_id": 8672912,
                      "lat": 48.12665, "lon": -69.1697, "fuseau": "America/Toronto"},
        "fold": 0,
        # pas de nom_affiche : c'est le sujet
    }
    (tmp_path / "sans-nom.json").write_text(json.dumps(ancien), encoding="utf-8")
    d = client.get("/api/apercu/sans-nom").get_json()
    assert d["profil"]["nom"] == "Vieux Profil"
