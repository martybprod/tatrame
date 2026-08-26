"""Le moteur des Relations — le contrat, écrit AVANT le moteur (discipline Align).

Deux personnes → une lecture déterministe de leur lien. Comme le reste d'Align :
on CALCULE ici (structure, badges, clés de corpus), on LIT ailleurs (les textes).
Ces tests verrouillent la structure, la rejouabilité, la dégradation gracieuse et
la couverture du corpus — jamais la « justesse » astrologique, qui n'est pas testable.

Le moteur est PUR sur des primitives (cap, éléments, positions, branches) : aucun
appel aux éphémérides ici, tout est monté à la main. C'est ce qui le rend testable.
"""
import itertools
import json
import pathlib

import pytest

from moteur import relations as R

CORPUS = pathlib.Path(__file__).resolve().parent.parent / "data" / "corpus"


def _charger(nom):
    return json.loads((CORPUS / nom).read_text(encoding="utf-8"))


def _cles_utiles(d):
    """Les clés d'un fichier de corpus, hors méta (`_charte`, `_note`…)."""
    return {k for k in d if not k.startswith("_")}


# ═══════════════════════════════════════════ 1. Fonctions pures : nombres

def test_paire_nombres_cle_canonique_et_symetrique():
    a = R.paire_nombres(7, 3)
    b = R.paire_nombres(3, 7)
    assert a["cle"] == b["cle"] == "3-7"
    assert a["min"] == 3 and a["max"] == 7
    assert a["sens"] == "mixte"
    assert a["identiques"] is False


def test_paire_nombres_identiques():
    a = R.paire_nombres(5, 5)
    assert a["cle"] == "5-5"
    assert a["identiques"] is True
    assert a["sens"] == "meme"
    assert a["harmonique"] == "identiques"


@pytest.mark.parametrize("a,b,attendu", [
    (5, 5, "identiques"),
    (1, 9, "opposes"), (2, 8, "opposes"), (3, 7, "opposes"), (4, 6, "opposes"),
    (1, 3, "ecart_deux"), (7, 5, "ecart_deux"),
    (1, 4, "autre"), (2, 7, "autre"),
])
def test_harmonique_numerologique(a, b, attendu):
    assert R.paire_nombres(a, b)["harmonique"] == attendu


def test_nombre_composite_symetrique_et_reduit():
    # Le composé ADDITIONNE les deux Cap et réduit à 1-9 (Millman, convention
    # Align). 8 + 8 = 16 -> 7. Symétrique : l'ordre ne change rien.
    a = R.nombre_composite(8, 8)
    assert a["valeur"] == 7
    assert R.nombre_composite(7, 3) == R.nombre_composite(3, 7)


def test_nombre_composite_reduit_les_maitres():
    # Un Cap maître entre dans le calcul par sa BASE (11->2, 22->4, 33->6),
    # comme paire_nombres. 22(->4) + 5 = 9. 11(->2) + 11(->2) = 4.
    assert R.nombre_composite(22, 5)["valeur"] == 9
    assert R.nombre_composite(22, 5)["bases"] == [4, 5]
    assert R.nombre_composite(11, 11)["valeur"] == 4


@pytest.mark.parametrize("a,b", list(itertools.combinations_with_replacement(range(1, 10), 2)))
def test_nombre_composite_toujours_1_a_9(a, b):
    v = R.nombre_composite(a, b)["valeur"]
    assert 1 <= v <= 9


# ═══════════════════════════════════════ Synthèse : appuis / reliefs ordonnés

def test_synthese_ordonne_appuis_et_reliefs_par_priorite():
    # Priorité de lecture : synastrie > chinois > éléments > nombres. La synthèse
    # d'intro nomme le plus fort appui, puis le plus fort relief.
    axes = {
        "synastrie": None,
        "chinois": {"etat": "resonance"},
        "elements": {"etat": "tension"},
        "nombres": {"etat": "resonance"},
    }
    s = R._synthese(axes)
    assert s["climat"] == "mixte"
    assert s["appuis"] == ["chinois", "nombres"]   # ordre de priorité
    assert s["reliefs"] == ["elements"]
    assert s["top_appui"] == "chinois"
    assert s["top_bouscule"] == "elements"


def test_synthese_neutre_n_a_ni_appui_ni_bouscule():
    axes = {"nombres": {"etat": "neutre"}, "chinois": {"etat": "neutre"}}
    s = R._synthese(axes)
    assert s["climat"] == "neutre"
    assert s["top_appui"] is None and s["top_bouscule"] is None


def test_synthese_pur_appui_n_a_pas_de_bouscule():
    axes = {"nombres": {"etat": "resonance"}, "elements": {"etat": "resonance"}}
    s = R._synthese(axes)
    assert s["climat"] == "resonance"
    assert s["top_appui"] == "elements"          # priorité éléments > nombres
    assert s["top_bouscule"] is None
    assert s["double_whammy"]["actif"] is True   # deux appuis concordent


# ═══════════════════════════════════════════ 2. Fonctions pures : éléments

@pytest.mark.parametrize("e1,e2,attendu", [
    ("Feu", "Air", "resonance"),
    ("Terre", "Eau", "resonance"),
    ("Feu", "Feu", "neutre"),
    ("Eau", "Eau", "neutre"),
    ("Feu", "Terre", "tension"),
    ("Feu", "Eau", "tension"),
    ("Air", "Terre", "tension"),
    ("Air", "Eau", "tension"),
])
def test_resonance_deux_elements(e1, e2, attendu):
    assert R.resonance_deux_elements(e1, e2) == attendu
    assert R.resonance_deux_elements(e2, e1) == attendu   # symétrique


def test_cle_elements_canonique():
    assert R.cle_elements("Feu", "Air") == R.cle_elements("Air", "Feu") == "air-feu"


# ═══════════════════════════════════════════ 3. Fonctions pures : chinois

@pytest.mark.parametrize("e1,e2,attendu", [
    ("bois", "bois", "meme"),
    ("bois", "feu", "genere"),        # le bois nourrit le feu
    ("eau", "bois", "genere"),        # l'eau nourrit le bois
    ("bois", "terre", "controle"),    # le bois fixe la terre
    ("eau", "feu", "controle"),       # l'eau éteint le feu
    ("métal", "feu", "controle"),     # le feu fond le métal (symétrique)
])
def test_relation_elements_chinois(e1, e2, attendu):
    assert R.relation_elements_chinois(e1, e2) == attendu
    assert R.relation_elements_chinois(e2, e1) == attendu   # symétrique


def test_lien_chinois_reutilise_le_moteur():
    # Rat (0) et Cheval (6) = choc (六沖, +6 mod 12) ; déjà vérifié dans chinois.py
    lien = R.lien_chinois(0, "eau", 6, "feu")
    assert lien["branche"] == "choc"
    # eau vs feu = contrôle
    assert lien["element"] == "controle"


# ═══════════════════════════════════════════ 4. Synastrie (aspects croisés)

def _pos(**kw):
    return dict(kw)


def test_synastrie_trouve_un_aspect_croise():
    # Soleil de A à 10°, Lune de B à 10° → conjonction exacte (orbe 0)
    a = _pos(soleil=10.0)
    b = _pos(lune=10.0)
    syn = R.synastrie(a, b)
    assert any(x["de_a"] == "soleil" and x["de_b"] == "lune"
               and x["aspect"] == "conjonction" for x in syn)


def test_synastrie_triee_par_orbe_et_cle_canonique():
    a = _pos(soleil=10.0, venus=100.0)
    b = _pos(lune=10.5, mars=99.0)
    syn = R.synastrie(a, b)
    orbes = [x["orbe"] for x in syn]
    assert orbes == sorted(orbes)                       # les plus serrés d'abord
    for x in syn:
        if x["cle"] is not None:
            # clé canonique réutilisable telle quelle par le corpus des 135 aspects
            assert x["cle"].endswith(("_conjonction", "_carre-opposition",
                                      "_sextile-trigone"))


def test_synastrie_angle_na_pas_de_cle_planetaire():
    # un aspect impliquant l'Ascendant n'a pas de clé dans le corpus des paires
    a = _pos(asc=10.0)
    b = _pos(soleil=10.0)
    syn = R.synastrie(a, b)
    croise = [x for x in syn if x["de_a"] == "asc" and x["de_b"] == "soleil"]
    assert croise and croise[0]["cle"] is None


def test_synastrie_symetrie_des_positions():
    a = _pos(soleil=10.0, lune=200.0)
    b = _pos(venus=13.0, mars=205.0)
    s1 = R.synastrie(a, b)
    s2 = R.synastrie(b, a)
    # mêmes aspects, mêmes orbes (les rôles de_a/de_b s'échangent seulement)
    assert sorted(round(x["orbe"], 6) for x in s1) == \
           sorted(round(x["orbe"], 6) for x in s2)


# ═══════════════════════════════════════════ 4bis. Le composite (« le vous »)

@pytest.mark.parametrize("a,b,attendu", [
    (10.0, 50.0, 30.0),        # milieu simple
    (350.0, 10.0, 0.0),        # à cheval sur 0° : l'arc court passe par 0
    (0.0, 90.0, 45.0),
    (100.0, 100.0, 100.0),     # deux points confondus
])
def test_milieu_angulaire(a, b, attendu):
    assert abs(R.milieu_angulaire(a, b) - attendu) < 1e-9


def test_milieu_angulaire_prend_l_arc_court():
    # 350 et 10 sont à 20° l'un de l'autre : le milieu est 0, pas 180.
    assert abs(R.milieu_angulaire(350.0, 10.0) - 0.0) < 1e-9
    assert abs(R.milieu_angulaire(10.0, 350.0) - 0.0) < 1e-9


def test_milieu_angulaire_symetrique_et_borne():
    for a, b in [(12.0, 205.0), (33.0, 300.0), (170.0, 200.0)]:
        m1, m2 = R.milieu_angulaire(a, b), R.milieu_angulaire(b, a)
        assert abs(((m1 - m2 + 180) % 360) - 180) < 1e-9   # même point
        assert 0.0 <= m1 < 360.0


def test_theme_composite_midpoints_et_signes():
    a = {"soleil": 10.0, "lune": 200.0, "venus": 45.0}
    b = {"soleil": 40.0, "lune": 210.0, "venus": 44.0}
    comp = R.theme_composite(a, b)
    assert abs(comp["corps"]["soleil"]["lon"] - 25.0) < 1e-9   # milieu de 10 et 40
    assert comp["corps"]["soleil"]["signe"] == "Bélier"        # 25° = Bélier
    assert "aspects" in comp and isinstance(comp["aspects"], list)


def test_theme_composite_absent_si_donnees_manquantes():
    assert R.theme_composite(None, {"soleil": 10.0}) is None
    assert R.theme_composite({"soleil": 10.0}, None) is None


def test_theme_composite_ne_garde_que_les_corps_communs():
    a = {"soleil": 10.0, "lune": 100.0, "mercure": 200.0}
    b = {"soleil": 20.0, "lune": 110.0}          # pas de mercure
    comp = R.theme_composite(a, b)
    assert set(comp["corps"]) == {"soleil", "lune"}


# ═══════════════════════════════ 4quater. La ressemblance du composite (Skymates 2)

def _diag(a, b):
    """Le diagnostic à partir de deux jeux de positions natales bruts."""
    comp = R.theme_composite(a, b)
    return R.diagnostic_ressemblance(comp, a, b)


def test_diagnostic_democratie_quand_les_deux_thermes_concordent():
    # Triade dans les MÊMES signes des deux côtés -> le milieu y reste -> les deux
    # s'y reconnaissent.
    a = {"soleil": 10.0, "lune": 100.0, "asc": 130.0}   # Bélier, Cancer, Lion
    b = {"soleil": 20.0, "lune": 110.0, "asc": 140.0}   # Bélier, Cancer, Lion
    d = _diag(a, b)
    assert d["cle"] == "democratie"
    assert d["souverain"] is None
    assert d["ressemblance_a"] == 3.0 and d["ressemblance_b"] == 3.0


def test_diagnostic_feodal_penche_vers_a():
    # Chaque milieu tombe dans le signe de A, jamais dans celui de B.
    a = {"soleil": 5.0, "lune": 95.0, "asc": 185.0}     # Bélier, Cancer, Balance
    b = {"soleil": 35.0, "lune": 125.0, "asc": 215.0}   # Taureau, Lion, Scorpion
    d = _diag(a, b)
    assert d["cle"] == "feodal"
    assert d["souverain"] == "a"
    assert d["ressemblance_a"] == 3.0 and d["ressemblance_b"] == 0.0


def test_diagnostic_feodal_symetrique_si_on_echange_a_et_b():
    a = {"soleil": 5.0, "lune": 95.0, "asc": 185.0}
    b = {"soleil": 35.0, "lune": 125.0, "asc": 215.0}
    assert _diag(a, b)["souverain"] == "a"
    assert _diag(b, a)["souverain"] == "b"


def test_diagnostic_etrangere_quand_le_milieu_est_foreign_aux_deux():
    # Points éloignés : le milieu tombe dans un signe tiers, étranger aux deux.
    a = {"soleil": 10.0, "lune": 100.0, "asc": 190.0}   # Bélier, Cancer, Balance
    b = {"soleil": 70.0, "lune": 160.0, "asc": 250.0}   # Gémeaux, Vierge, Sagittaire
    d = _diag(a, b)
    assert d["cle"] == "etrangere"
    assert d["souverain"] is None
    assert d["ressemblance_a"] == 0.0 and d["ressemblance_b"] == 0.0


def test_diagnostic_absent_si_pas_de_composite():
    assert R.diagnostic_ressemblance(None, {"soleil": 10.0}, {"soleil": 20.0}) is None


def test_diagnostic_none_si_triade_non_comparable():
    # Un composite sans aucun point de la triade primaire -> rien à diagnostiquer.
    comp = {"corps": {"venus": {"lon": 10.0, "signe": "Bélier"}}, "aspects": []}
    assert R.diagnostic_ressemblance(comp, {"venus": 10.0}, {"venus": 20.0}) is None


def test_diagnostic_degrade_sans_ascendant():
    # Sans heure de naissance (pas d'asc), la triade se réduit à Soleil+Lune.
    a = {"soleil": 10.0, "lune": 100.0}
    b = {"soleil": 20.0, "lune": 110.0}
    d = _diag(a, b)
    assert d["n"] == 2
    assert d["cle"] == "democratie"


def test_diagnostic_present_dans_croiser_relation():
    a, b = _deux_complets()
    out = R.croiser_relation(a, b, "amour")
    assert "diagnostic" in out
    assert out["diagnostic"] is not None      # les deux thèmes sont complets
    assert out["diagnostic"]["cle"] in ("democratie", "feodal", "etrangere")


def test_diagnostic_absent_du_croiser_si_composite_manque():
    a, _ = _deux_complets()
    b = _personne(7, {"soleil": "Air"}, {"i_branche": 8, "element": "métal"}, positions=None)
    out = R.croiser_relation(a, b, "amour")
    assert out["diagnostic"] is None


# ═══════════════════════════════════════════ 4ter. Le pouls du jour (R4)

def _composite_simple():
    """Un composite minimal, avec asc/mc, pour tester les transits du jour."""
    return {"corps": {"soleil": {"lon": 10.0, "signe": "Bélier"},
                      "asc": {"lon": 123.0, "signe": "Lion"},
                      "mc": {"lon": 250.0, "signe": "Sagittaire"}},
            "aspects": []}


def test_pouls_absent_si_pas_de_composite():
    assert R.pouls_composite(None, {"saturne": 10.0}) is None


def test_pouls_choisit_le_transit_le_plus_fort():
    # Le ciel du jour a Saturne pile sur le Soleil du composite -> conjonction.
    comp = _composite_simple()
    ciel = {"saturne": 10.0, "jupiter": 200.0}   # jupiter n'aspecte rien de serré
    pouls = R.pouls_composite(comp, ciel)
    assert pouls is not None
    assert pouls["natal"] == "soleil"
    assert pouls["transit"] == "saturne"
    assert pouls["classe"] == "conjonction"


def test_pouls_rejouable():
    comp = _composite_simple()
    ciel = {"venus": 13.0, "mars": 250.0}
    import json as _j
    p1 = _j.dumps(R.pouls_composite(comp, ciel), sort_keys=True)
    p2 = _j.dumps(R.pouls_composite(comp, ciel), sort_keys=True)
    assert p1 == p2


def test_pouls_none_si_rien_ne_touche():
    comp = _composite_simple()
    ciel = {"saturne": 65.0}     # loin de soleil(10)/asc(123)/mc(250) à tout aspect serré
    assert R.pouls_composite(comp, ciel) is None


# ═══════════════════════════════════════════ 5. croiser_relation : l'assemblage

def _personne(cap, elements, chinois, positions=None):
    return {"cap": cap, "elements": elements, "chinois": chinois, "positions": positions}


def _deux_complets():
    a = _personne(3,
                  {"soleil": "Feu", "lune": "Air", "venus": "Feu", "mars": "Terre", "asc": "Air"},
                  {"i_branche": 4, "element": "bois"},
                  {"soleil": 10.0, "lune": 200.0, "venus": 45.0, "mars": 300.0, "asc": 100.0})
    b = _personne(7,
                  {"soleil": "Air", "lune": "Eau", "venus": "Air", "mars": "Eau", "asc": "Feu"},
                  {"i_branche": 8, "element": "métal"},
                  {"soleil": 12.0, "lune": 205.0, "venus": 48.0, "mars": 120.0, "asc": 100.5})
    return a, b


def test_croiser_relation_structure_complete():
    a, b = _deux_complets()
    out = R.croiser_relation(a, b, "amour")
    assert out["type"] == "amour"
    for axe in ("nombres", "elements", "chinois", "synastrie"):
        assert axe in out["axes"]
    assert "climat" in out["synthese"]
    assert out["manques"] == []       # rien ne manque quand les deux sont complets


def test_composite_present_quand_les_deux_sont_complets():
    a, b = _deux_complets()
    out = R.croiser_relation(a, b, "amour")
    assert out["composite"] is not None
    assert "soleil" in out["composite"]["corps"]


def test_composite_absent_et_signale_si_incomplet():
    a, _ = _deux_complets()
    b = _personne(7, {"soleil": "Air"}, {"i_branche": 8, "element": "métal"}, positions=None)
    out = R.croiser_relation(a, b, "amour")
    assert out["composite"] is None
    assert "composite" in out["manques"]


def test_rejouabilite_octet_pour_octet():
    a, b = _deux_complets()
    s1 = json.dumps(R.croiser_relation(a, b, "amour"), sort_keys=True, ensure_ascii=False)
    s2 = json.dumps(R.croiser_relation(a, b, "amour"), sort_keys=True, ensure_ascii=False)
    assert s1 == s2


def test_degradation_gracieuse_sans_heure():
    """B sans positions (pas d'heure/lieu) : aucune exception, synastrie absente,
    les couches nombres/éléments-solaires/chinois restent là, `manques` renseigné."""
    a, _ = _deux_complets()
    b = _personne(7, {"soleil": "Air"}, {"i_branche": 8, "element": "métal"}, positions=None)
    out = R.croiser_relation(a, b, "amour")
    assert out["axes"]["synastrie"] is None
    assert "synastrie" in out["manques"]
    assert out["axes"]["nombres"] is not None
    assert out["axes"]["chinois"] is not None
    # pas d'exception, et la sortie reste rejouable
    s1 = json.dumps(out, sort_keys=True, ensure_ascii=False)
    s2 = json.dumps(R.croiser_relation(a, b, "amour"), sort_keys=True, ensure_ascii=False)
    assert s1 == s2


def test_type_relation_est_une_lentille_pas_un_calcul():
    """Changer le type de relation ne change pas les axes CALCULÉS (P6) —
    seulement l'ordre/registre de lecture."""
    a, b = _deux_complets()
    amour = R.croiser_relation(a, b, "amour")
    travail = R.croiser_relation(a, b, "travail")
    assert amour["axes"] == travail["axes"]        # même calcul
    assert amour["type"] != travail["type"]        # lentille différente


def test_pas_de_score_global(C1=None):
    """C1 : aucune note/pourcentage global de compatibilité dans la sortie."""
    a, b = _deux_complets()
    out = R.croiser_relation(a, b, "amour")
    plat = json.dumps(out, ensure_ascii=False).lower()
    assert "score" not in plat and "%" not in plat
    assert "pourcent" not in plat


# ═══════════════════════════════════════════ 6. Couverture du corpus (100 %)

def test_corpus_nombres_couvre_les_45_paires():
    d = _cles_utiles(_charger("rel_nombres.json"))
    attendues = {f"{lo}-{hi}" for lo in range(1, 10) for hi in range(lo, 10)}
    assert len(attendues) == 45
    assert attendues == d, f"manquantes={attendues - d}, en trop={d - attendues}"


def test_corpus_composite_nombre_couvre_1_a_9():
    # Le composé (Millman) est réduit à 1-9 : une entrée par valeur, chacune
    # avec ses cinq champs. Une valeur manquante = un « vous » muet à l'écran.
    d = _charger("rel_composite_nombre.json")
    cles = _cles_utiles(d)
    assert cles == {str(i) for i in range(1, 10)}, f"clés={cles}"
    for k, e in ((k, d[k]) for k in cles):
        for champ in ("en_bref", "le_but", "l_atout", "le_piege", "la_question"):
            assert e.get(champ, "").strip(), f"composé {k} : champ « {champ} » vide"


def test_le_moteur_produit_une_valeur_composee_lisible():
    # Le pont calcul -> corpus : toute somme de deux Cap réduits (1-9) tombe sur
    # une entrée existante. On balaie les 45 paires, comme le moteur les verra.
    d = _cles_utiles(_charger("rel_composite_nombre.json"))
    for a in range(1, 10):
        for b in range(a, 10):
            v = R.nombre_composite(a, b)["valeur"]
            assert str(v) in d, f"composé {a}+{b} -> {v} sans entrée corpus"


def test_composite_nombre_ne_copie_pas_millman():
    # Anti-plagiat : aucune suite de 8 mots partagée avec la source (concepts
    # repris, prose jamais). Skip propre si la source est absente.
    import re
    import unicodedata

    source = (pathlib.Path(__file__).resolve().parent.parent / "_distillation"
              / "sources" / "votre_chemin_de_vie_dan_millman.txt")
    if not source.exists():
        pytest.skip("source Millman absente — anti-plagiat non exécuté")

    def norm(t):
        t = unicodedata.normalize("NFD", t.lower())
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9]+", " ", t).split()

    d = _charger("rel_composite_nombre.json")
    champs = ("en_bref", "le_but", "l_atout", "le_piege", "la_question")
    suspects = {}
    for k in _cles_utiles(d):
        mots = norm(" ".join(d[k].get(c, "") for c in champs))
        for i in range(len(mots) - 7):
            suspects[" ".join(mots[i:i + 8])] = k
    assert suspects, "aucun 8-gramme extrait du composé"

    src = norm(source.read_text(encoding="utf-8", errors="replace"))
    hits = {g for i in range(len(src) - 7)
            for g in [" ".join(src[i:i + 8])] if g in suspects}
    assert not hits, f"8-grammes copiés de Millman : {list(hits)[:5]}"


def test_corpus_harmoniques_complet():
    d = _cles_utiles(_charger("rel_harmoniques.json"))
    assert d == {"identiques", "opposes", "ecart_deux", "autre"}


def test_corpus_elements_couvre_toutes_les_paires():
    d = _cles_utiles(_charger("rel_elements.json"))
    attendues = set()
    for e1, e2 in itertools.combinations_with_replacement(["Feu", "Terre", "Air", "Eau"], 2):
        attendues.add(R.cle_elements(e1, e2))
    assert len(attendues) == 10
    assert attendues == d


def test_corpus_chinois_complet():
    d = _charger("rel_chinois.json")
    assert _cles_utiles(d["branches"]) == {"choc", "harmonie", "trine",
                                           "nuisance", "identique", "neutre"}
    assert _cles_utiles(d["elements"]) == {"genere", "controle", "meme", "neutre"}


def test_corpus_aspects_cadre_les_trois_classes():
    d = _cles_utiles(_charger("rel_aspects_cadre.json"))
    assert d == {"conjonction", "carre-opposition", "sextile-trigone"}


def test_corpus_synthese_present():
    d = _charger("rel_synthese.json")
    assert "dominante" in d and "pied" in d


def test_corpus_composite_present():
    """R3 : le cadrage et les amorces du composite existent.

    Les amorces couvrent les points que le composite lit à l'écran. Vénus et
    Mars s'y sont ajoutés (l'amour et l'élan du lien, ce qu'un couple a de plus
    parlant) : l'assertion suit désormais la liste réelle du moteur plutôt qu'un
    sous-ensemble figé qui rendait ce test périmé."""
    d = _charger("rel_composite.json")
    assert d.get("cadrage") and d.get("pied")
    assert set(d["amorces"]) == {"soleil", "lune", "venus", "mars", "asc"}


def test_corpus_pouls_couvre_classes_et_points():
    """R4 : chaque classe d'aspect et chaque corps aspectable a sa nuance —
    aucun transit du jour possible ne tombe dans le vide."""
    d = _charger("rel_pouls.json")
    assert d.get("cadre") and d.get("pied")
    assert set(d["classe"]) == {"conjonction", "carre-opposition", "sextile-trigone"}
    from moteur import aspects as Asp
    assert set(Asp.CORPS_ASPECTABLES) <= set(d["point"])


def test_corpus_types_couvre_les_cinq_lentilles():
    """R2 : le cadrage par type de relation existe pour chaque lentille du moteur."""
    d = _cles_utiles(_charger("rel_types.json"))
    assert d == set(R.LENTILLES)
    types = _charger("rel_types.json")
    for cle in d:
        assert types[cle].get("cadrage") and types[cle].get("conseil")


def test_toute_relation_chinoise_tombe_sur_un_texte():
    """Garde-fou de bout en bout : chaque relation que le moteur peut produire
    a bien une entrée de corpus (le trou 104/467 ne se reproduit pas)."""
    branches = _cles_utiles(_charger("rel_chinois.json")["branches"])
    from moteur import chinois as C
    produites = set()
    for i in range(12):
        for j in range(12):
            produites.add(C.relation_branches(i, j))
    assert produites <= branches, f"relations sans texte : {produites - branches}"


# ═══════════════════════════════════════════ 7. Anti-verbatim (charte Align)

def _shingles(texte, n=8):
    mots = texte.lower().split()
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


def test_paires_nombres_ne_se_recopient_pas():
    """Aucune suite de 8 mots partagée entre deux paires différentes — le mur
    du corpus (jusqu'à 70 suites identiques lors de l'épisode nombres) ne revient pas."""
    d = _charger("rel_nombres.json")
    textes = {}
    for cle in _cles_utiles(d):
        parts = []
        for champ in ("vers_min", "vers_max", "meme", "atouts", "frictions", "conditions"):
            v = d[cle].get(champ)
            if v:
                parts.append(v)
        textes[cle] = " ".join(parts)
    cles = sorted(textes)
    for i, ka in enumerate(cles):
        sa = _shingles(textes[ka])
        for kb in cles[i + 1:]:
            commun = sa & _shingles(textes[kb])
            assert not commun, f"verbatim entre {ka} et {kb} : {list(commun)[:2]}"


def test_types_relation_ne_se_recopient_pas():
    """R2 : les 5 lentilles ne partagent aucune suite de 8 mots — chacune son propre angle."""
    d = _charger("rel_types.json")
    textes = {cle: f"{d[cle]['cadrage']} {d[cle]['conseil']}" for cle in _cles_utiles(d)}
    cles = sorted(textes)
    for i, ka in enumerate(cles):
        sa = _shingles(textes[ka])
        for kb in cles[i + 1:]:
            commun = sa & _shingles(textes[kb])
            assert not commun, f"verbatim entre {ka} et {kb} : {list(commun)[:2]}"
