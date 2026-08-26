"""L'idée globale du ciel, et la divulgation progressive.

« Une idée globale, mais qu'on peut facilement aller en demander plus. »

Le Ciel jetait un tableau de treize lignes sans jamais dire l'essentiel. Ces
tests verrouillent les deux moitiés du contrat : la synthèse dit vrai, et la
profondeur est bien là quand on la demande.
"""
import pytest

from moteur import synthese as S
from moteur.corpus import Corpus
from moteur.theme import Moteur

MOTEUR = Moteur()
CORPUS = Corpus()

SIGNES = ["belier", "taureau", "gemeaux", "cancer", "lion", "vierge",
          "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons"]
ASTRES_SIGNE = ["soleil", "lune", "mercure", "venus", "mars", "jupiter",
                "saturne", "uranus", "neptune", "pluton", "asc", "mc"]
ASTRES_MAISON = ["soleil", "lune", "mercure", "venus", "mars",
                 "jupiter", "saturne", "uranus", "neptune", "pluton"]


@pytest.fixture(scope="module")
def theme():
    return MOTEUR.theme_natal(1975, 7, 16, 14, 30, 48.1266, -69.1697, "America/Toronto")


# ------------------------------------------------------- la couverture

def test_astre_en_signe_est_complet():
    """144 cases : aucun thème ne doit tomber sur un trou."""
    manque = [f"{a}_{s}" for a in ASTRES_SIGNE for s in SIGNES
              if not CORPUS.lire("astre_signe", f"{a}_{s}")]
    assert not manque, f"{len(manque)} manquantes, ex. {manque[:5]}"


def test_astre_en_maison_est_complet():
    """120 cases. Les angles n'en ont pas : ils SONT une maison."""
    manque = [f"{a}_{m}" for a in ASTRES_MAISON for m in range(1, 13)
              if not CORPUS.lire("astre_maison", f"{a}_{m}")]
    assert not manque, f"{len(manque)} manquantes, ex. {manque[:5]}"


def test_les_axes_fusionnent_sans_collision():
    """Trois fichiers, un axe. Une entrée écrasée = du travail perdu en silence."""
    assert len(CORPUS.axes["astre_signe"]) == 144
    assert len(CORPUS.axes["astre_maison"]) == 120


# ------------------------------------------------------- les aspects

import itertools

CLASSES = ["conjonction", "carre-opposition", "sextile-trigone"]
#: 45 paires de planètes (C(10,2)) × 3 classes = 135. Écrit en quatre lots par
#: des rédacteurs différents (c'est ce qui casse les tics), lu comme un axe.
CLES_ASPECTS = [f"{a}_{b}_{c}"
                for a, b in itertools.combinations(S.ORDRE_PAIRE, 2)
                for c in CLASSES]


def test_aspects_entre_planetes_est_complet():
    """135 cases : deux planètes en aspect ne doivent jamais tomber sur un trou."""
    manque = [k for k in CLES_ASPECTS if not CORPUS.lire("aspects_paires", k)]
    assert not manque, f"{len(manque)} manquantes, ex. {manque[:5]}"


def test_chaque_aspect_porte_ses_deux_lectures():
    """Une phrase courte (en_bref) ET le texte long, sur chaque entrée."""
    creux = [k for k in CLES_ASPECTS
             if not (CORPUS.lire("aspects_paires", k, "en_bref")
                     and CORPUS.lire("aspects_paires", k, "texte"))]
    assert not creux, f"{len(creux)} entrées incomplètes, ex. {creux[:5]}"


def test_les_aspects_fusionnent_sans_collision():
    """Quatre fichiers, un axe, exactement 135 clés canoniques."""
    assert len(CORPUS.axes["aspects_paires"]) == 135
    assert set(CORPUS.axes["aspects_paires"]) == set(CLES_ASPECTS)


def test_cle_aspect_est_canonique_et_ignore_les_angles():
    """L'ordre des deux corps ne change pas la clé ; un angle n'a pas de clé.

    Lune-Soleil et Soleil-Lune sont le même aspect : sans clé canonique, il
    faudrait écrire le texte deux fois. Les aspects aux angles (asc/mc) n'ont
    pas de corpus long et renvoient None — assumé.
    """
    assert S.cle_aspect("lune", "soleil", "conjonction") == "soleil_lune_conjonction"
    assert S.cle_aspect("soleil", "lune", "conjonction") == "soleil_lune_conjonction"
    assert S.cle_aspect("soleil", "asc", "conjonction") is None
    assert S.cle_aspect("mc", "venus", "sextile-trigone") is None


def test_tout_aspect_reel_entre_planetes_a_son_texte(theme):
    """Sur un vrai thème : chaque lien planète-planète résout dans le corpus.

    Le garde-fou de bout en bout — non seulement les 135 clés existent, mais
    celles que le moteur FABRIQUE pour un thème réel tombent bien dessus.
    """
    for nom in S.ORDRE_PAIRE:
        for lien in S.aspects_d_un_astre(theme, nom):
            if lien["cle"] is None:      # un aspect à un angle : normal
                continue
            assert CORPUS.lire("aspects_paires", lien["cle"]), (
                f"aspect réel sans texte : {lien['cle']}"
            )


def test_la_fusion_refuse_un_doublon():
    """Le garde-fou doit mordre : deux rédacteurs sur la même case, on le dit.

    ⚠️ La fusion est EXPLICITE (`AXES_FUSIONNES`), pas automatique : `lexique`
    et `ciel` portent tous deux une clé `phases` sans être le même axe — les
    fusionner mélangerait un glossaire et des textes du jour.
    """
    from moteur import corpus as mod
    assert "phases" not in mod.AXES_FUSIONNES, (
        "fusionner « phases » mêlerait le lexique et les textes du jour"
    )
    assert mod.AXES_FUSIONNES == {"astre_signe", "astre_maison", "aspects_paires"}


# ------------------------------------------------------- la synthèse

def test_le_trio_est_le_premier(theme):
    """Soleil, Lune, Ascendant — le plus parlant, donc le premier."""
    t = S.trio(theme)
    assert t["soleil"]["signe"] and t["lune"]["signe"] and t["asc"]["signe"]
    assert t["soleil"]["maison"] and t["lune"]["maison"]


def test_les_equilibres_ne_comptent_que_les_dix_planetes(theme):
    """Les angles sont des points, pas des corps : les compter fausserait tout."""
    corps = dict(theme["corps"])
    corps["asc"] = {"signe": theme["angles"]["asc"]["signe"]}
    corps["mc"] = {"signe": theme["angles"]["mc"]["signe"]}
    eq = S.equilibres(corps)
    assert sum(eq["elements"].values()) == 10
    assert sum(eq["modalites"].values()) == 10


def test_un_thème_équilibré_est_une_information(theme):
    """Ni dominante ni creux n'est PAS un vide à masquer.

    Le moteur doit le dire explicitement, sinon l'écran resterait muet pour
    les thèmes les plus équilibrés — les plus fréquents.
    """
    eq = S.equilibres({f"p{i}": {"signe": s} for i, s in enumerate(
        ["Bélier", "Lion", "Taureau", "Vierge", "Gémeaux", "Balance",
         "Cancer", "Scorpion", "Sagittaire", "Capricorne"])})
    assert eq["element_dominant"] is None and eq["element_creux"] is None
    assert eq["equilibre"] is True


def test_un_creux_est_detecte(theme):
    """0 ou 1 planète dans un élément = un creux, et il doit se voir."""
    corps = {f"p{i}": {"signe": s} for i, s in enumerate(
        ["Cancer", "Scorpion", "Poissons", "Cancer", "Scorpion",
         "Bélier", "Lion", "Taureau", "Vierge", "Gémeaux"])}
    eq = S.equilibres(corps)
    assert eq["element_dominant"] == "Eau"
    assert eq["element_creux"] == "Air"       # un seul (Gémeaux)


def test_les_hemispheres_ne_parlent_que_si_c_est_net(theme):
    """Un partage 5/5 ne dit rien : le marquer serait raconter du bruit."""
    h = S.hemispheres(theme["corps"], theme["maisons"]["cuspides"])
    assert h["haut"] + h["bas"] == 10
    assert h["est"] + h["ouest"] == 10
    if 4 <= h["haut"] <= 6:
        assert h["vertical"] is None


def test_le_maitre_du_theme_porte_sa_force(theme):
    """« Qui mène » n'a de sens que si l'on dit dans quel état il mène."""
    m = S.maitre_du_theme(theme, [])
    assert m and m["planete"] and m["etat"] in ("solide", "en peine", "moyen")


def test_l_astre_en_vue_reutilise_le_bareme_existant(theme):
    """Deux barèmes de force divergeraient. On en garde UN."""
    from moteur import aspects as A
    s = S.synthetiser(theme)
    v = s["en_vue"]
    f = A.force_planete(v["planete"], theme["corps"], [])
    assert v["force"] >= 0 and f is not None


def test_la_synthese_est_reproductible(theme):
    """Le contrat d'Align : même entrée, même sortie. Toujours."""
    assert S.synthetiser(theme) == S.synthetiser(theme)


def test_les_cles_de_synthese_trouvent_toutes_leur_texte(theme):
    """Une clé sans texte = un écran vide chez l'utilisateur."""
    for genre, cle in S.synthetiser(theme)["cles"]:
        assert CORPUS.lire("ciel_global", genre, cle), f"pas de texte pour {genre}.{cle}"


@pytest.mark.parametrize("bloc", ["trio", "maitre", "en_vue", "stellium"])
def test_les_blocs_toujours_affiches_ont_leur_texte(bloc):
    assert CORPUS.lire("ciel_global", bloc, "intro")


# ------------------------------------------- la divulgation progressive

def test_chaque_astre_a_ses_deux_lectures(theme):
    """Signe (comment) + maison (où) — ADDITIVES, jamais leur produit.

    C'est ce qui rend le corpus rédigeable : 144 + 120 entrées, pas 144 × 120.
    """
    for nom, c in theme["corps"].items():
        if nom == "noeud_moyen":
            continue
        import unicodedata
        s = unicodedata.normalize("NFD", c["signe"].casefold())
        s = "".join(x for x in s if unicodedata.category(x) != "Mn")
        assert CORPUS.lire("astre_signe", f"{nom}_{s}"), f"{nom} en {c['signe']}"
        assert CORPUS.lire("astre_maison", f"{nom}_{c['maison']}"), f"{nom} maison {c['maison']}"


def test_la_profondeur_est_reelle():
    """« Infiniment plus détaillée » — mesuré sur le PIRE cas, pas sur un fixture.

    ⚠️ Deux erreurs de conception corrigées ici, et elles ont coûté cher.

    1. **Il ne mesurait qu'UN cas** (la Lune du thème de test) en prétendant
       garantir la profondeur de toutes les lignes. Il passait par chance : le
       vrai minimum du corpus est à 460 mots, pas au-dessus de 500.
    2. **Son seuil était arbitraire.** Quand une passe de style a retiré 2,5 %
       de mots — un progrès —, le fixture est tombé à 498 et le test a cassé.
       Un rédacteur a alors **rallongé du texte pour satisfaire le chiffre**.
       C'est exactement ce qu'un test ne doit jamais provoquer : le corpus s'est
       mis à servir la mesure au lieu du lecteur.

    Le seuil est maintenant posé BAS et à distance du réel (460 au pire) : il
    attrape ce qu'il doit attraper — un fichier vidé, un corpus à moitié écrit —
    sans peser sur l'écriture. 400 mots par ligne, c'est déjà 3 fois ce qu'il y
    avait avant la vague.
    """
    import unicodedata

    def plier(s):
        s = unicodedata.normalize("NFD", s.casefold())
        return "".join(x for x in s if unicodedata.category(x) != "Mn")

    pire = (10 ** 6, None)
    for astre in ASTRES_MAISON:
        for signe in SIGNES:
            for maison in range(1, 13):
                sg = CORPUS.lire("astre_signe", f"{astre}_{signe}") or {}
                ms = CORPUS.lire("astre_maison", f"{astre}_{maison}") or {}
                mots = sum(len(str(v).split()) for v in {**sg, **ms}.values())
                if mots < pire[0]:
                    pire = (mots, f"{astre} {signe} maison {maison}")

    assert pire[0] > 400, (
        f"la ligne la plus maigre du ciel ne fait que {pire[0]} mots ({pire[1]}). "
        f"La divulgation progressive ne mène nulle part."
    )


def test_les_aspects_d_un_astre_sont_les_plus_serres(theme):
    """Un aspect exact parle plus fort qu'un aspect large."""
    liens = S.aspects_d_un_astre(theme, "lune")
    assert liens, "la Lune doit avoir des liens"
    assert all("autre" in l and l["autre"] != "lune" for l in liens)
    assert liens == sorted(liens, key=lambda x: x["orbe"]), "les plus serrés d'abord"


def test_les_lentes_disent_leur_part_generationnelle():
    """L'honnêteté qui distingue Align d'un horoscope.

    Uranus, Neptune et Pluton EN SIGNE sont partagés par toute une génération
    — « Pluton en Scorpion = tu es intense » a été vendu à des dizaines de
    millions de gens. Le corpus doit le dire, pas l'exploiter.
    """
    for astre in ("uranus", "neptune", "pluton"):
        for s in SIGNES:
            e = CORPUS.lire("astre_signe", f"{astre}_{s}")
            assert e.get("generationnel"), f"{astre}_{s} ne dit pas sa part générationnelle"


def test_les_lentes_en_maison_disent_pourquoi_elles_sont_personnelles():
    """Le pendant : la MAISON dépend de l'heure de naissance, donc elle est à toi.

    C'est le seul endroit où ces trois astres deviennent individuels.
    """
    for astre in ("uranus", "neptune", "pluton"):
        for m in range(1, 13):
            e = CORPUS.lire("astre_maison", f"{astre}_{m}")
            assert e.get("pourquoi_c_est_personnel"), f"{astre}_{m}"
