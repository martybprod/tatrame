"""« Une question » (2026-11-16) : le tirage à une carte remplace la carte du
jour. Chaque question est une position qui lit un champ EXISTANT de la fiche
(Wen : une carte = le cœur du sujet, posé par une question ; INDEX règle 1 :
jamais une carte seule)."""
import app
import album

BLOC = app.TIRAGES["question_1"]


def test_cinq_questions_declarees():
    ids = [p["id"] for p in BLOC["positions"]]
    assert ids == ["se_joue", "ne_regarde_pas", "prendre_conscience", "traverser", "apporte"]
    assert BLOC["question_par_defaut"] in ids
    for p in BLOC["positions"]:
        assert p["question"].endswith("?")
        assert p.get("champ")


def test_aucune_reponse_vide_sur_les_79_cartes():
    for cid in app.IDS:
        fiche = app.CORPUS.get(cid, {})
        for pos in BLOC["positions"]:
            r = app._resoudre_position(fiche, pos, 7)
            assert r["texte"].strip(), (cid, pos["id"])


def test_api_resout_les_cinq_reponses_d_avance():
    client = app.app.test_client()
    d = client.get("/api/tirage?mode=1&graine=42").get_json()
    assert d["grille"] == "question_1"
    assert set(d["questions_textes"]) == {p["id"] for p in BLOC["positions"]}
    assert d["question_par_defaut"] == "se_joue"
    # la même graine relit la même carte : changer de question ne retire rien
    d2 = client.get("/api/tirage?mode=1&graine=42").get_json()
    assert d2["cartes"][0]["id"] == d["cartes"][0]["id"]


def test_traverser_porte_le_geste():
    pos = next(p for p in BLOC["positions"] if p["id"] == "traverser")
    assert pos["appoint"]["genre"] == "geste"


def test_album_edite_la_pedagogie_et_les_questions():
    assert album._cible_tirage("tirage-question_1", "pedagogie.resume")
    for i in range(len(BLOC["positions"])):
        assert album._cible_tirage("tirage-question_1", "positions.%d.question" % i)
