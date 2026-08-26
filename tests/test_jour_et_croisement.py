"""Le Jour et le croisement — la promesse d'Align, vérifiée.

Deux choses se jouent ici, et ce sont les deux arguments du produit :
  1. **le déterminisme** — même profil + même date = même réponse, toujours ;
  2. **la variété sans hasard** — et pourtant chaque jour diffère.

Si l'un des deux tombe, l'app n'a plus de raison d'être.
"""
import pytest

from moteur import aspects as A
from moteur import croisement as X
from moteur import jour as J
from moteur import tarot as T
from moteur.theme import Moteur

MOTEUR = Moteur()

# Un profil de référence, fixe. Trois-Pistoles, 16/07/1975, 14h30.
PROFIL = dict(annee=1975, mois=7, jour=16, heure=14, minute=30,
              lat=48.1266, lon=-69.1697, fuseau="America/Toronto")
NOMS = ["Marie", "Claire", "Tremblay"]


@pytest.fixture(scope="module")
def theme():
    p = PROFIL
    return MOTEUR.theme_natal(p["annee"], p["mois"], p["jour"], p["heure"],
                              p["minute"], p["lat"], p["lon"], p["fuseau"])


def ciel(annee, mois, jour):
    t = MOTEUR.eph.instant(annee, mois, jour, 12, 0, 0)
    p = {c: MOTEUR.eph.position(c, t) for c in MOTEUR.eph.CORPS}
    return {c: v["lon"] for c, v in p.items()}, {c: v["vitesse_lon"] for c, v in p.items()}


# ----------------------------------------------------- LE déterminisme

def test_meme_entree_meme_sortie(theme):
    """La promesse d'Align, littéralement.

    Deux appels identiques doivent produire des structures identiques —
    pas « proches », identiques. C'est ce qu'un LLM à température 0 ne
    garantit pas, et c'est pourquoi le corpus est écrit à l'avance.
    """
    pos, vit = ciel(2026, 7, 16)
    a = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
    b = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
    assert a == b


def test_le_theme_lui_meme_est_reproductible():
    p = PROFIL
    a = MOTEUR.theme_natal(p["annee"], p["mois"], p["jour"], p["heure"],
                           p["minute"], p["lat"], p["lon"], p["fuseau"])
    b = MOTEUR.theme_natal(p["annee"], p["mois"], p["jour"], p["heure"],
                           p["minute"], p["lat"], p["lon"], p["fuseau"])
    assert a == b


def test_croisement_reproductible(theme):
    a = X.croiser(theme, NOMS, 16, 7, 1975, 2026)
    b = X.croiser(theme, NOMS, 16, 7, 1975, 2026)
    assert a == b


# --------------------------------------- LA variété, sans aucun hasard

def test_chaque_jour_differe_sans_tirage(theme):
    """L'argument fondateur, mesuré plutôt qu'affirmé.

    Aucun aléa n'intervient nulle part : la variété vient du CIEL, qui bouge
    tout seul. Sur 30 jours consécutifs, la dominante et la Lune doivent
    changer souvent — sinon l'app radoterait, et le pari « déterministe »
    tomberait.
    """
    lectures = []
    for jour in range(1, 31):
        pos, vit = ciel(2026, 4, jour)
        j = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
        lectures.append((j["dominante"]["cle"] if j["dominante"] else None,
                         j["lune"]["signe"], j["lune"]["maison"], j["phase"]["phase"]))

    assert len(set(l[0] for l in lectures)) >= 8, "trop peu de dominantes distinctes"
    assert len(set(l[1] for l in lectures)) >= 10, "la Lune doit parcourir le zodiaque"
    assert len(set(l[3] for l in lectures)) == 8, "les 8 phases en un mois lunaire"
    assert len(set(lectures)) >= 25, f"trop de jours identiques : {len(set(lectures))}/30"


def test_la_lune_change_de_signe_tous_les_deux_jours_et_demi(theme):
    """Le fait qui porte tout l'argument de variété."""
    signes = []
    for jour in range(1, 29):
        pos, _ = ciel(2026, 4, jour)
        signes.append(J.lune_du_jour(theme, pos["lune"])["signe"])
    changements = sum(1 for a, b in zip(signes, signes[1:]) if a != b)
    assert 10 <= changements <= 14, f"{changements} changements en 28 jours"


# ---------------------------------------------- l'architecture du Jour

def test_une_seule_dominante_pas_dix(theme):
    """Un conseil qui énumère n'est pas un conseil."""
    pos, vit = ciel(2026, 7, 16)
    j = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
    assert j["dominante"] is not None
    assert len(j["declencheurs"]) <= 3 and len(j["potentiel"]) <= 2


def test_les_rapides_priment_sur_les_lentes(theme):
    """L'architecture à deux étages : les rapides donnent le timing.

    À exactitude comparable, un déclencheur doit sortir devant un potentiel —
    sinon l'app parlerait du climat des trois prochaines années au lieu de la
    journée.
    """
    pos, vit = ciel(2026, 7, 16)
    j = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
    if j["dominante"]:
        assert j["dominante"]["etage"] == "declencheur"


def test_un_transit_applicatif_est_plus_fort(theme):
    """Ce qui se resserre agit plus que ce qui se desserre."""
    pos, vit = ciel(2026, 7, 16)
    trs = J.transits(theme, pos, vit)
    appliquants = [t for t in trs if t.get("applicatif")]
    assert appliquants, "au moins un transit applicatif attendu"


# ---------------------------------- la sélection sensible à la récurrence
#
# Un transit serré (une station rétrograde, par ex.) peut dominer toute une
# semaine, et l'ancienne règle « le plus fort gagne, point » affichait alors le
# MÊME message jour après jour. `choisir_dominante` brise ces blocs : parmi les
# déclencheurs comparables au leader, le moins récent gagne. Pure fonction — la
# fenêtre de regard en arrière est calculée en amont, de façon déterministe.

def _decl(cle, force):
    return {"cle": cle, "force": force}


def test_dominante_leader_net_gagne_meme_si_recent():
    """Un leader au-delà de la marge gagne toujours : on n'affiche jamais un
    transit faible au nom de la variété."""
    decl = [_decl("a", 0.90), _decl("b", 0.50)]   # écart 0.40 >> marge
    assert J.choisir_dominante(decl, ["a", "a", "a"])["cle"] == "a"


def test_dominante_le_moins_recent_gagne_parmi_les_comparables():
    """Deux déclencheurs comparables (écart < marge) : celui montré hier cède
    la place à celui qu'on n'a pas vu récemment."""
    decl = [_decl("a", 0.90), _decl("b", 0.80)]   # écart 0.10 < marge 0.12
    assert J.choisir_dominante(decl, ["a"])["cle"] == "b"


def test_dominante_jamais_vue_bat_tout():
    """Un candidat jamais montré dans la fenêtre gagne, même s'il est le moins
    fort des comparables — c'est tout l'objet du mécanisme."""
    decl = [_decl("a", 0.90), _decl("b", 0.88), _decl("c", 0.82)]
    assert J.choisir_dominante(decl, ["b", "a"])["cle"] == "c"


def test_dominante_sans_passe_departage_par_la_force():
    """Bord gauche de la fenêtre : rien de connu → on retombe sur le plus fort.
    C'est l'amorce naturelle qui borne le regard en arrière."""
    decl = [_decl("a", 0.90), _decl("b", 0.85)]
    assert J.choisir_dominante(decl, ["x", "y"])["cle"] == "a"


def test_les_cles_sont_additives_jamais_cartesiennes(theme):
    """La règle qui rend le corpus rédigeable à la main.

    Les clés doivent rester des axes INDÉPENDANTS qu'on additionne. Si elles
    devenaient un produit (transit × maison × phase × année), il faudrait
    écrire des centaines de milliers d'entrées — l'objection est fondée, et
    c'est le piège qui a tué une app concurrente.
    """
    pos, vit = ciel(2026, 7, 16)
    j = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
    genres = [g for g, _ in j["cles"]]
    assert len(genres) == len(set(genres)), "un genre de clé ne doit sortir qu'une fois"
    for _, cle in j["cles"]:
        assert cle.count("_") <= 3, f"clé trop composée, ça sent le produit : {cle}"


def test_un_aspect_dur_annule_le_ton_lunaire(theme):
    """La règle déterministe qui évite « Lune en Balance donc tout est doux »
    alors qu'elle est carrée à Saturne. Elle doit se déclencher au moins une
    fois sur un mois — sinon elle serait décorative.
    """
    annulations = 0
    for jour in range(1, 29):
        pos, vit = ciel(2026, 4, jour)
        j = J.journee(theme, pos, vit, 6, T.carte_de_l_annee(16, 7, 2026))
        annulations += bool(j["ton_lunaire_annule"])
    assert annulations >= 1, "la règle ne se déclenche jamais : elle est morte"
    assert annulations <= 20, "elle se déclenche trop : le seuil est trop bas"


def test_phase_lunaire_formule_exacte():
    """(Lune − Soleil) mod 360, en 8 tranches de 45°."""
    assert J.phase_lunaire(0, 0)["phase"] == "nouvelle"
    assert J.phase_lunaire(0, 180)["phase"] == "pleine"
    assert J.phase_lunaire(0, 90)["phase"] == "premier_quartier"
    assert J.phase_lunaire(0, 270)["phase"] == "dernier_quartier"
    assert J.phase_lunaire(350, 10)["phase"] == "nouvelle", "doit enjamber 0°"


# ------------------------------------------------------- le croisement

def test_le_pont_golden_dawn_est_complet():
    """12 signes + 7 planètes + 3 éléments = 22. La structure se referme."""
    genres = [g for g, _ in T.GOLDEN_DAWN.values()]
    assert genres.count("signe") == 12
    assert genres.count("planete") == 7
    assert genres.count("element") == 3
    assert len(T.GOLDEN_DAWN) == 22


def test_la_table_est_celle_de_mathers_pas_celle_de_case():
    """Le piège : le web entier affiche la mauvaise table.

    Les arcanes 0, 12 et 20 portent des ÉLÉMENTS (les lettres-mères
    hébraïques), pas Uranus/Neptune/Pluton. La version Case détruit la
    structure qui fait justement tenir le croisement d'Align.
    """
    assert T.GOLDEN_DAWN[0] == ("element", "Air")
    assert T.GOLDEN_DAWN[12] == ("element", "Eau")
    assert T.GOLDEN_DAWN[20] == ("element", "Feu")
    for planete in ("uranus", "neptune", "pluton"):
        assert planete not in [c for _, c in T.GOLDEN_DAWN.values()]


def test_carte_de_naissance_exemple_canonique():
    """13 avril 1975 → 21 (Le Monde) → 3 (L'Impératrice). Corpus Arrien/Greer."""
    assert T.carte_de_naissance(13, 4, 1975)["numero"] == 21
    assert T.carte_de_fond(13, 4, 1975)["numero"] == 3


def test_22_referme_la_boucle_sur_le_mat():
    n = T.carte_de_naissance(6, 1, 1950)
    assert n["numero"] == 22 and n["nom"] == "Le Mat"
    assert T.carte_de_fond(6, 1, 1950)["numero"] == 4


def test_reduction_vers_22_pas_un_modulo():
    """Piège classique : 30 → 3, jamais 30 % 22 = 8."""
    assert T._reduire_vers(30, 22) == 3
    assert T._reduire_vers(1992, 22) == 21


def test_le_croisement_lit_la_carte_dans_le_theme_reel(theme):
    """LE différenciateur d'Align : les autres juxtaposent, on croise."""
    r = X.croiser(theme, NOMS, 16, 7, 1975, 2026)
    pont = r["ponts"]["naissance"]
    assert pont["cible"] == r["cartes"]["naissance"]["correspondance"][1]
    assert pont["etat"] in ("resonance", "tension", "neutre")
    assert pont["raisons"], "un état sans raison n'est pas lisible"


def test_ni_resonance_ni_tension_ne_sont_un_verdict(theme):
    """Une tension n'est pas un mauvais présage : c'est là qu'il y a du travail.

    Le moteur doit produire les deux états sur des profils différents, sinon
    il ne discrimine rien.
    """
    etats = set()
    for an in range(1960, 1996, 5):
        t = MOTEUR.theme_natal(an, 3, 15, 10, 0, 45.5, -73.5, "America/Toronto")
        r = X.croiser(t, ["Test", "Profil"], 15, 3, an, 2026)
        etats |= {p["etat"] for p in r["ponts"].values() if p}
    assert "resonance" in etats and "tension" in etats, f"états produits : {etats}"


def test_aspects_trois_classes_pas_cinq():
    """Ce qui divise le corpus par ~1,7 sans rien perdre d'utile."""
    classes = {c for _, _, c in A.ASPECTS.values()}
    assert classes == {"conjonction", "carre-opposition", "sextile-trigone"}


def test_asc_et_mc_sont_aspectables():
    """12 corps, pas 10 — les angles comptent comme des planètes."""
    assert "asc" in A.CORPS_ASPECTABLES and "mc" in A.CORPS_ASPECTABLES
    assert len(A.CORPS_ASPECTABLES) == 12


def test_dignites():
    assert A.dignite("soleil", "Lion") == "domicile"
    assert A.dignite("soleil", "Verseau") == "exil"
    assert A.dignite("soleil", "Bélier") == "exaltation"
    assert A.dignite("soleil", "Balance") == "chute"
    assert A.dignite("soleil", "Gémeaux") is None


def test_bilan_elements_ignore_les_angles(theme):
    """10 planètes, pas 12 : compter les angles fausserait la pesée."""
    corps = dict(theme["corps"])
    corps["asc"] = {"signe": theme["angles"]["asc"]["signe"]}
    corps["mc"] = {"signe": theme["angles"]["mc"]["signe"]}
    b = A.bilan_elements(corps)
    assert sum(b["elements"].values()) == 10
    assert sum(b["modalites"].values()) == 10


# ------------------------------ la redondance qu'aucun test global ne voit

def test_gestes_redondants_detectes():
    """Le corpus peut être varié ET servir deux gestes jumeaux le même matin.

    Les tables sont écrites séparément (par des rédacteurs qui ne se lisent
    pas) mais LUES ensemble. C'est arrivé pour de vrai : « Nomme, pour toi
    seul… » deux fois sur le même écran, alors que le corpus global passait
    tous les tests de variété. Seule la lecture assemblée le révèle.
    """
    textes = {
        "transit": {"miroir": "…", "geste": "Nomme, pour toi seul, une chose."},
        "annee_perso": {"miroir": "…", "geste": "Nomme, pour toi seul, une autre."},
        "phase": {"miroir": "…", "geste": "Écris trois mots sur un papier."},
    }
    d = J.gestes_redondants(textes)
    assert len(d) == 1
    garde, retire, tete = d[0]
    assert {garde, retire} == {"transit", "annee_perso"}
    assert tete.startswith("nomme")


def test_gestes_distincts_ne_declenchent_rien():
    textes = {
        "a": {"geste": "Envoie le message que tu repousses."},
        "b": {"geste": "Note en trois mots ce que tu veux."},
    }
    assert J.gestes_redondants(textes) == []
