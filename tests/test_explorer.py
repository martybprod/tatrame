"""Garde-fous d'Explorer : le domaine choisi par la personne (pas la maison de
la Lune) résout bien, avec la même logique de nuance que le Fil du jour.
"""
import json
import pathlib

from moteur import jour as J

RACINE = pathlib.Path(__file__).resolve().parents[1]
FIL = json.loads((RACINE / "data" / "corpus" / "fil.json").read_text(encoding="utf-8"))


def test_cles_fil_domaine_domaine_invalide():
    assert J._cles_fil_domaine("pas-un-domaine", None, {"phase": "pleine"}) == []


def test_cles_fil_domaine_ordre_precis_vers_generique():
    dom = {"transit": "venus", "classe": "conjonction"}
    ph = {"phase": "pleine"}
    cles = J._cles_fil_domaine("autre", dom, ph)
    assert cles[0] == "autre_transit_venus_conjonction"
    assert cles[-1] == "autre"


def test_cles_fil_domaine_a_phase_utilise_la_phase_pas_la_tonalite():
    ph = {"phase": "nouvelle"}
    cles = J._cles_fil_domaine("creation", None, ph)
    assert "creation_phase_nouvelle" in cles
    assert not any(c.endswith("_fluide") or c.endswith("_tension") for c in cles)


def test_cles_fil_domaine_hors_phase_utilise_la_tonalite():
    dom = {"transit": "mars", "classe": "carre-opposition"}
    ph = {"phase": "pleine"}
    cles = J._cles_fil_domaine("racines", dom, ph)
    assert "racines_tension" in cles
    assert not any("_phase_" in c for c in cles)


def test_cles_fil_equivaut_a_cles_fil_domaine_pour_le_domaine_de_la_lune():
    dom = {"transit": "lune", "classe": "sextile-trigone"}
    ph = {"phase": "gibbeuse"}
    lune = {"maison": 7}  # maison VII -> "autre"
    assert J._cles_fil(dom, ph, lune) == J._cles_fil_domaine("autre", dom, ph)


def test_les_douze_domaines_resolvent_au_moins_leur_generique():
    for domaine in J.MAISON_DOMAINE.values():
        assert domaine in FIL, f"pas de socle générique pour {domaine}"
