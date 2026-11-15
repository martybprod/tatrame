"""Tests du tirage « Neuf + une » (9 + 1) — trois plans × trois niveaux, une clé.

Ce que ces tests protègent :
  · la structure de Greer : 3 plans en colonnes, 3 niveaux en rangées, 1 clé ;
  · chaque case lit le champ de son niveau, chaque rangée a ses liaisons ;
  · la dixième carte est la clé, et la percée s'appuie dessus ;
  · tout est reproductible par la graine.
"""
import pytest

from app import app as flask_app

MODES = ("1", "3", "10")


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_structure_neuf_plus_une(client):
    d = client.get("/api/tirage?mode=10&graine=12").get_json()
    assert d["mode"] == 10
    assert len(d["cartes"]) == 10
    E = d["etendu"]
    assert [n["id"] for n in E["niveaux"]] == ["visible", "latent", "resolution"]
    assert [p["id"] for p in E["plans"]] == ["amene", "se_joue", "essayer"]
    assert len(E["cellules"]) == 9
    croisements = {(c["niveau"], c["plan"]) for c in E["cellules"].values()}
    attendus = {(n, p) for n in ("visible", "latent", "resolution")
                for p in ("amene", "se_joue", "essayer")}
    assert croisements == attendus


def test_chaque_case_et_la_cle_ont_un_texte(client):
    d = client.get("/api/tirage?mode=10&graine=12").get_json()
    E = d["etendu"]
    for carte in d["cartes"][:9]:
        cellule = E["cellules"][carte["id"]]
        assert cellule["texte"].strip(), carte["id"]
    assert E["cle"]["texte"].strip()
    assert E["cle"]["carte_id"] == d["cartes"][9]["id"]


def test_rangees_correspondent_aux_tranches(client):
    """Rangée 1 = cartes 0-2 (visible), rangée 2 = 3-5 (latent), rangée 3 = 6-8."""
    d = client.get("/api/tirage?mode=10&graine=12").get_json()
    rangees = d["etendu"]["rangees"]
    assert len(rangees) == 3
    attendus = [[c["id"] for c in d["cartes"][0:3]],
                [c["id"] for c in d["cartes"][3:6]],
                [c["id"] for c in d["cartes"][6:9]]]
    assert [r["cartes"] for r in rangees] == attendus
    for r in rangees:
        assert isinstance(r["liaisons"], list)


def test_percee_sappuie_sur_la_cle(client):
    d = client.get("/api/tirage?mode=10&graine=12").get_json()
    percee = d["lecture"]["percee"]
    assert percee["cle"]["nom"] == d["cartes"][9]["nom"]
    assert "tirée après les neuf" in percee["cle"]["phrase"].lower()
    assert percee["geste"]["nom"] == d["cartes"][9]["nom"]
    # le blocage et la ressource sont parmi les neuf cartes
    neuf = {c["nom"] for c in d["cartes"][:9]}
    assert percee["blocage"]["nom"] in neuf
    assert percee["ressource"]["nom"] in neuf


def test_neuf_plus_une_deterministe(client):
    a = client.get("/api/tirage?mode=10&graine=77").get_json()
    b = client.get("/api/tirage?mode=10&graine=77").get_json()
    assert [c["id"] for c in a["cartes"]] == [c["id"] for c in b["cartes"]]
    assert a["etendu"]["cellules"] == b["etendu"]["cellules"]
    assert a["lecture"]["percee"] == b["lecture"]["percee"]


def test_eveil_dans_une_case_a_toujours_un_texte(client):
    """Éveil (hors cycle) a bien lumière, ombre et leçon : ses cases lisent
    le champ de leur niveau comme les autres. Si un champ manquait, la phrase
    du regard tiendrait la place — jamais de case vide."""
    trouve = None
    for graine in range(1, 80):
        d = client.get("/api/tirage?mode=10&graine=%d" % graine).get_json()
        if any(c["type"] == "hors_cycle" for c in d["cartes"][:9]):
            trouve = d
            break
    assert trouve, "aucun 9 + 1 avec Éveil dans les 80 graines"
    for carte in trouve["cartes"][:9]:
        if carte["type"] != "hors_cycle":
            continue
        cellule = trouve["etendu"]["cellules"][carte["id"]]
        assert cellule["texte"].strip()
        if cellule["regard"]:
            assert cellule["appoint"] is None


def test_mode_deux_refuse(client):
    assert client.get("/api/tirage?mode=2").status_code == 400
