"""Câblage des lois (Millman) dans le portrait — l'intégration, pas le corpus.

Le corpus lui-même est gardé par test_lois_corpus.py. Ici on vérifie le SEUL
point de câblage : `app._lois_du_cap` route par la BASE du Cap (1-9), sert des
lois complètes, et le portrait les expose dans `textes.lois` (y compris pour un
profil incomplet, car les leviers ne dépendent que de la date).
"""
import json

import pytest

import app
from moteur import numerologie as NUM

LOIS = json.loads(
    (app.RACINE / "data" / "corpus" / "lois.json").read_text(encoding="utf-8")
) if hasattr(app, "RACINE") else json.loads(
    (__import__("pathlib").Path(app.__file__).resolve().parent / "data" / "corpus" / "lois.json").read_text(encoding="utf-8")
)
ROUTAGE = LOIS["_routage"]


def _nb(noms, j, m, a):
    return NUM.portrait(noms, j, m, a)


def test_route_par_la_base_du_cap_pas_la_valeur():
    # Marie Curie : Cap valeur 22 (maître), base 4. Les leviers doivent être
    # ceux du 4, pas une entrée « 22 » (qui n'existe pas dans le routage).
    nb = _nb(["Marie", "Curie"], 7, 11, 1867)
    assert nb["cap"]["valeur"] == 22 and nb["cap"]["base"] == 4
    cles = [L["cle"] for L in app._lois_du_cap(nb)]
    assert cles == ROUTAGE["4"], f"un Cap maître doit hériter du routage de sa base : {cles}"


def test_chaque_loi_servie_est_complete():
    nb = _nb(["Jean", "Tremblay"], 22, 2, 1946)
    lois = app._lois_du_cap(nb)
    assert lois, "aucune loi servie pour un Cap 8"
    for L in lois:
        for champ in ("cle", "nom", "en_un_mot", "le_principe", "le_pas"):
            assert L.get(champ), f"champ manquant dans une loi servie : {champ}"


def test_le_portrait_expose_les_lois_meme_incomplet():
    profil = {"id": "t", "nom_affiche": "Zoe Aventure",
              "prenoms_nom": ["Zoe", "Aventure"], "genre": None,
              "naissance": {"annee": 1990, "mois": 5, "jour": 14},
              "complet": False, "fold": 0}
    original = app._charger
    app._charger = lambda pid: profil
    try:
        with app.app.test_request_context("/api/portrait/t"):
            data = json.loads(app.api_portrait("t").get_data(as_text=True))
    finally:
        app._charger = original

    lois = data["textes"].get("lois")
    assert lois, "textes.lois absent du portrait incomplet"
    base = data["nombres"]["cap"]["base"]
    assert [L["cle"] for L in lois] == ROUTAGE[str(base)], "le portrait route mal les lois"
