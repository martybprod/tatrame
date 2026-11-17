"""Tests des trois croix à dix cartes — même donne, trois grammaires.

Ce que ces tests protègent :
  · chaque croix a dix positions et une pédagogie complète ;
  · chaque position est résolue pour chaque carte (aucune case vide) ;
  · la tension (pousse / retient) devient une phrase, jamais un dictionnaire ;
  · l'infinitif s'élide (« d'attendre », pas « de attendre ») ;
  · les trois croix sont résolues d'avance : changer de croix relit la même
    donne, sans retirer les cartes.
"""
import pathlib
import re

import pytest

from app import CROIX, TIRAGES, app as flask_app
from moteur import _de_verbe

RACINE = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_trois_croix_declarees():
    assert list(CROIX) == ["croix_celtique", "croix_osho", "croix_composite"]
    for cid, bloc in CROIX.items():
        assert bloc["nb_cartes"] == 10, cid
        assert len(bloc["positions"]) == 10, cid
        assert [p["numero"] for p in bloc["positions"]] == list(range(1, 11)), cid


def test_pedagogie_complete_pour_chaque_croix():
    for cid, bloc in CROIX.items():
        P = bloc["pedagogie"]
        for cle in ("resume", "pourquoi", "le_tirage", "comment_lire", "apres"):
            assert (P.get(cle) or "").strip(), (cid, cle)
        assert len(P["resume"].split()) <= 45, cid
        assert len(P.get("vocabulaire") or []) >= 2, cid
        expl = P.get("positions_expliquees") or {}
        for pos in bloc["positions"]:
            assert (expl.get(pos["id"]) or "").strip(), (cid, pos["id"])


def test_croix_inconnue_refusee(client):
    r = client.get("/api/tirage?mode=11&graine=12&croix=inconnue")
    assert r.status_code == 400


def test_chaque_position_resolue_pour_chaque_carte(client):
    for cid in CROIX:
        d = client.get(f"/api/tirage?mode=11&graine=12&croix={cid}").get_json()
        assert d["grille"] == cid
        assert len(d["croix_textes"][cid]) == 10
        for carte in d["cartes"]:
            cell = d["croix_textes"][cid][carte["id"]]
            assert isinstance(cell["texte"], str), (cid, carte["id"])
            assert cell["texte"].strip(), (cid, carte["id"])


def test_les_trois_croix_viennent_avec_la_meme_donne(client):
    d = client.get("/api/tirage?mode=11&graine=12").get_json()
    assert [c["id"] for c in d["croix_choix"]] == list(CROIX)
    assert set(d["croix_textes"]) == set(CROIX)
    # même graine, mêmes cartes : changer de croix ne redistribue rien
    for cid in CROIX:
        autre = client.get(f"/api/tirage?mode=11&graine=12&croix={cid}").get_json()
        assert [c["id"] for c in autre["cartes"]] == [c["id"] for c in d["cartes"]]


def test_tension_devient_une_phrase(client):
    """La position qui lit la tension en texte principal ne sert jamais un
    dictionnaire à l'interface."""
    trouve = False
    for graine in range(1, 40):
        d = client.get(f"/api/tirage?mode=11&graine={graine}&croix=croix_osho").get_json()
        for carte in d["cartes"]:
            texte = d["croix_textes"]["croix_osho"][carte["id"]]["texte"]
            assert isinstance(texte, str)
            if "elle te retient" in texte:
                assert not re.search(r"\bde [aeiouyh]", texte), texte
                trouve = True
    assert trouve, "aucune tension rencontrée : la graine de test ne couvre rien"


def test_elision_de_linfinitif():
    assert _de_verbe("attendre") == "d'attendre"
    assert _de_verbe("accepter") == "d'accepter"
    assert _de_verbe("tenir seul") == "de tenir seul"
    assert _de_verbe("") == "de "


def test_album_liste_et_edite_les_trois_croix():
    import album
    sections = album._section_tirages()
    noms = [c["nom"] for c in sections[0]["cartes"]]
    assert "La croix d'Osho" in noms
    assert "La croix composite — la relation" in noms
    fichier, chemin = album._cible_tirage(
        "tirage-croix_composite", "pedagogie.positions_expliquees.outil")
    assert chemin == ["croix_composite", "pedagogie", "positions_expliquees", "outil"]
    _, chemin = album._cible_tirage("tirage-croix_osho", "pedagogie.resume")
    assert chemin == ["croix_osho", "pedagogie", "resume"]


def test_diamant_cinq_cartes(client):
    """Le petit tirage en croix d'Osho : cinq positions, aucune case vide,
    même graine = mêmes cartes, et il ne se mêle pas aux croix à dix cartes."""
    d = client.get("/api/tirage?mode=5&graine=12").get_json()
    assert d["mode"] == 5 and d["grille"] == "diamant"
    assert len(d["cartes"]) == 5
    assert [p["numero"] for p in d["croix"]["positions"]] == [1, 2, 3, 4, 5]
    assert [c["id"] for c in d["croix_choix"]] == ["diamant"]
    for carte in d["cartes"]:
        texte = d["croix_textes"]["diamant"][carte["id"]]["texte"]
        assert isinstance(texte, str) and texte.strip(), carte["id"]
    # le diamant n'est pas une des trois croix à dix cartes
    d11 = client.get("/api/tirage?mode=11&graine=12").get_json()
    assert "diamant" not in [c["id"] for c in d11["croix_choix"]]


def test_diamant_pedagogie_et_album():
    import album
    bloc = TIRAGES["diamant"]
    P = bloc["pedagogie"]
    assert len(P["resume"].split()) <= 45
    expl = P.get("positions_expliquees") or {}
    for pos in bloc["positions"]:
        assert (expl.get(pos["id"]) or "").strip(), pos["id"]
    noms = [c["nom"] for c in album._section_tirages()[0]["cartes"]]
    assert "Le Diamant" in noms
