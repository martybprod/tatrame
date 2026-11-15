"""Tests des grilles de relecture — la même donne, plusieurs cadres.

Ce que ces tests protègent :
  · l'API sert les quatre grilles et résout chaque position pour chaque carte ;
  · la question de la grille « leçon · geste · question » est choisie par la
    graine (déterministe, reproductible) ;
  · Éveil (hors cycle) tient la place avec sa phrase du regard ;
  · la clôture porte de quoi finir selon la grille (geste, leçon ou question) ;
  · l'album sait éditer les grilles, et refuse une cible inconnue.
"""
import json
import pathlib

import pytest

import album
from app import GRILLES, app as flask_app

RACINE = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_quatre_grilles_servies(client):
    d = client.get("/api/tirage?mode=3&graine=12").get_json()
    assert [g["id"] for g in d["grilles"]] == [
        "causale_3", "visible_latent_resolution", "temps", "lecon_geste_question"]
    assert d["grille"] == "causale_3"          # la grille d'origine par défaut


def test_chaque_position_resolue_pour_chaque_carte(client):
    """Aucune case vide : chaque grille × chaque carte × chaque position a
    un texte (ou le regard d'Éveil). C'est la promesse du plan de
    correspondance — le corpus est la banque."""
    d = client.get("/api/tirage?mode=3&graine=12").get_json()
    for grille in d["grilles"]:
        for carte in d["cartes"]:
            for pos in grille["positions"]:
                r = d["textes_par_grille"][grille["id"]][carte["id"]][pos["id"]]
                assert r["texte"].strip(), (grille["id"], carte["id"], pos["id"])


def test_grille_inconnue_refusee(client):
    r = client.get("/api/tirage?mode=3&grille=inventee")
    assert r.status_code == 400


def test_question_choisie_par_la_graine(client):
    """La question de la position « question » vient des trois de la fiche,
    choisie par la graine : même graine, même question."""
    a = client.get("/api/tirage?mode=3&graine=12").get_json()
    b = client.get("/api/tirage?mode=3&graine=12").get_json()
    for carte in a["cartes"]:
        qa = a["textes_par_grille"]["lecon_geste_question"][carte["id"]]["question"]
        qb = b["textes_par_grille"]["lecon_geste_question"][carte["id"]]["question"]
        assert qa == qb
        assert qa["texte"] in (carte["questions"] or [])


def test_les_grilles_lisent_des_champs_differents():
    """Le visible lit la lumière, le latent l'ombre, la résolution l'issue :
    trois champs distincts de la même fiche."""
    grille = GRILLES["visible_latent_resolution"]
    champs = [p["champ"] for p in grille["positions"]]
    assert champs == ["lumiere", "ombre.texte", "ombre.issue"]
    assert GRILLES["lecon_geste_question"]["positions"][0]["champ"] == "lecon"
    assert GRILLES["temps"]["positions"][0]["champ"] == "positions.amene"


def test_cloture_porte_la_lecon(client):
    """La grille leçon/geste/question clôt sur la leçon : le geste est déjà
    lu en position 2, on ne le répète pas."""
    d = client.get("/api/tirage?mode=3&graine=12").get_json()
    assert d["lecture"]["cloture"]["lecon"].strip()
    assert d["lecture"]["cloture"]["micro_geste"].strip()


def test_eveil_tient_sa_place_dans_toutes_les_grilles(client):
    """Éveil n'a pas de positions : la phrase du regard tient la place, et
    l'appoint est passé — jamais de case vide."""
    trouve = None
    for graine in range(1, 60):
        d = client.get("/api/tirage?mode=3&graine=%d" % graine).get_json()
        if any(c["type"] == "hors_cycle" for c in d["cartes"]):
            trouve = d
            break
    assert trouve, "aucun tirage avec Éveil dans les 60 graines"
    for carte in trouve["cartes"]:
        if carte["type"] != "hors_cycle":
            continue
        for grille in trouve["grilles"]:
            for pos in grille["positions"]:
                r = trouve["textes_par_grille"][grille["id"]][carte["id"]][pos["id"]]
                if r["regard"]:
                    assert r["texte"].strip()
                    assert r["appoint"] is None


def test_album_edite_les_grilles():
    """Chaque grille a ses champs éditables, résolus jusqu'au fichier."""
    donnees = json.loads((RACINE / "data/grammaire/tirages.json").read_text(encoding="utf-8"))
    for cle, grille in donnees["grilles"].items():
        champs = album._champs_tirage_grille(grille)
        for chemin, _titre in champs:
            cible = album._cible_tirage("tirage-" + cle, chemin)
            assert cible is not None, (cle, chemin)
    assert album._cible_tirage("tirage-inventee", "pedagogie.pourquoi") is None


def test_album_liste_les_grilles():
    sections = album._section_tirages()
    noms = [c["nom"] for c in sections[0]["cartes"]]
    assert "La carte du jour" in noms
    assert any("Visible · latent · résolution" in n for n in noms)
    assert any("Leçon · geste · question" in n for n in noms)

def test_chaque_tirage_a_un_resume_court():
    """Deux paliers : chaque tirage porte un résumé de deux phrases, et le
    panneau « Comprendre ce tirage » peut l'afficher avant la méthode."""
    import json, pathlib
    racine = pathlib.Path(__file__).resolve().parent.parent
    t = json.loads((racine / "data/grammaire/tirages.json").read_text(encoding="utf-8"))
    blocs = [(cle, t[cle]) for cle in ("jour", "causale_3", "etendu_9_1",
                                       "choix_3", "croix_celtique")]
    blocs += [(cle, g) for cle, g in t["grilles"].items()]
    for cle, bloc in blocs:
        resume = (bloc.get("pedagogie") or {}).get("resume", "")
        assert resume.strip(), cle
        assert len(resume.split()) <= 45, (cle, len(resume.split()))
