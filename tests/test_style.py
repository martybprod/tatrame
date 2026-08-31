"""Le style, mesuré — parce qu'il s'est dégradé sans que personne le voie.

Retour de Martin, 3e passe d'usage : « le vocabulaire ou la manière de tourner
les phrases est parfois difficile d'approche ».

Le diagnostic sur les 131 000 mots n'était PAS la longueur des phrases (médiane
15 mots, c'est bien) : c'est que le corpus écrit en APHORISMES. 1 363 tirets
cadratins et 1 728 deux-points sur 8 565 phrases — plus d'une phrase sur trois
porte une chute.

Ce n'est pas un défaut de qualité, c'est un défaut de DENSITÉ. Quand chaque
phrase veut placer sa formule, aucune ne porte, et le lecteur doit se battre
pour entrer. Un ami lucide ne parle pas en aphorismes.

⚠️ Origine honnête : mes propres consignes ont produit ça, en poussant les
rédacteurs à la variété et à la formule sans jamais leur donner le droit d'être
simples. D'où ces tests : ce qui n'est pas mesuré dérive.
"""
import json
import pathlib
import re
from collections import Counter

import pytest

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "data" / "corpus"

# Les fichiers déjà passés au style. Les autres attendent leur tour : on les
# mesure quand même (`test_tendance_generale`) pour que ça ne s'aggrave pas,
# mais sans les faire échouer — un test rouge en permanence finit ignoré.
# Le corpus ENTIER est passé au style. Cette liste n'est plus un sous-ensemble
# transitoire : c'est le contrat, et il couvre tout. Un nouveau fichier rejoint
# la liste dès qu'il naît conforme (le mois y est venu directement).
PASSES_AU_STYLE = {"transits", "ciel", "nombres", "arcanes", "ciel_global", "mois_detail",
                   "ciel_signe_1", "ciel_signe_2", "ciel_signe_3", "nombres_detail",
                   "annees_detail", "ciel_maison_1", "ciel_maison_2", "ciel_maison_3",
                   "aspects_1", "aspects_2", "aspects_3", "aspects_4", "univers_detail",
                   "heritages_detail", "ages_detail", "chinois_detail",
                   "chinois_natal", "fil", "periodes", "noeuds", "mineurs", "lois",
                   "rel_composite_nombre"}

CHAMPS_DE_PROSE = {
    "miroir", "geste", "anime", "alimenter", "contrarie", "conditionnement",
    "en_resonance", "en_tension", "resume", "le_mouvement", "au_quotidien",
    "avec_les_autres", "les_canaux", "le_piege", "si_tu_ne_te_reconnais_pas",
    "de_quoi_il_s_agit", "ce_qui_arrive_souvent", "ce_qui_aide", "ce_qui_nuit",
    "la_place_dans_le_cycle", "la_place_dans_l_annee",
    "comment_savoir_que_c_est_reussi", "comment_ca_marche", "le_revers",
    "ou_ca_se_joue", "generationnel", "pourquoi_c_est_personnel", "texte",
    # les aspects (en_bref = la phrase courte) et l'année universelle
    "en_bref", "climat", "en_un_mot", "titre",
    # les héritages (mémoires familiales)
    "ce_qui_se_transmet", "ce_que_tu_peux_en_faire",
    # les âges de la vie (le cycle planétaire derrière le passage)
    "le_ciel_derriere",
    # le signe chinois natal (le portrait de l'animal, la nuance de l'élément)
    "portrait", "nuance",
    # les messages de la carte du jour et de la carte de l'année
    "invitation", "pour_l_annee",
    # la personologie (48 sous-périodes + axe des nœuds)
    "essence", "origine", "destination",
    # les 17 lois (Millman, distillées) — le levier du jour
    "le_principe", "le_pas",
    # le nombre composé d'une relation (Millman) — le « vous » en nombres
    "le_but", "l_atout", "le_piege", "la_question",
}

# Le tic visé : un nom de FONCTION mis en sujet là où « tu » devrait être.
# « L'action, ici, se joue en silence » au lieu de « Tu agis en silence ».
#
# ⚠️ LISTE EXPLICITE, et c'est une leçon apprise deux fois. Une première
# version cherchait « article + nom + verbe » — elle attrapait « Le livre reste
# fermé », « Le trône est occupé par une absence », « Le calcul est simple »,
# « Le tien est un 5 ». Des images concrètes et des phrases parlées, soit
# l'inverse du défaut cherché. Un tiers du français normal commence comme ça.
#
# On ne peut pas détecter « l'abstraction » en général. On peut lister les
# noms de fonction qui, dans CE corpus, remplacent « tu ». C'est moins élégant
# et beaucoup plus juste.
FONCTIONS = (
    "action|plaisir|sécurité|attirance|goût|envie|besoin|élan|colère|calme|"
    "pensée|émotion|désir|ambition|confiance|doute|intensité|lucidité|"
    "prudence|contrôle|parole|attachement|solitude|lenteur|rumination|"
    "méfiance|jalousie|susceptibilité|agressivité|impatience"
)
ABSTRAIT_EN_SUJET = re.compile(
    rf"^(L'|Le |La )({FONCTIONS})\b[^.]{{0,30}}?\s(est|n'est|se |passe|arrive|devient|vient|reste)",
    re.I,
)


def textes_de(fichier):
    out = []

    def descendre(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in CHAMPS_DE_PROSE and isinstance(v, str):
                    out.append(v)
                elif not str(k).startswith("_"):
                    descendre(v)
        elif isinstance(x, list):
            for v in x:
                descendre(v)

    descendre(json.loads(fichier.read_text(encoding="utf-8")))
    return out


def phrases_de(fichier):
    return [p.strip() for t in textes_de(fichier)
            for p in re.split(r"(?<=[.!?])\s+", t) if len(p.split()) > 3]


def mesures(phrases):
    n = len(phrases) or 1
    return {
        "phrases": len(phrases),
        "tirets": sum(len(re.findall(r"—", p)) for p in phrases) / n * 100,
        "deux_points": sum(len(re.findall(r"\w\s*:", p)) for p in phrases) / n * 100,
        "abstrait": sum(1 for p in phrases if ABSTRAIT_EN_SUJET.match(p)) / n * 100,
        "verdict_nie": sum(1 for p in phrases if p.startswith("Ce n'est ")) / n * 100,
        # « langage clair » : une phrase de plus de 22 mots se lit mal (Cutts,
        # Gani : viser 15-20 mots). On borne la PROPORTION de phrases longues.
        "longues": sum(1 for p in phrases if len(p.split()) > 22) / n * 100,
    }


FICHIERS = sorted(CORPUS.glob("*.json"))
RELUS = [f for f in FICHIERS if f.stem in PASSES_AU_STYLE]

# Cliquet « langage clair » : les fichiers déjà passés à la clarté. On y AJOUTE
# chaque vague terminée (voir PLAN_LANGAGE_CLAIR.md) — le test protège alors le
# travail fait contre toute régression, sans casser le build sur le reste.
PASSES_AU_CLAIR = {
    "rel_elements_v2", "rel_composite_signe", "fil", "transits", "nombres_detail",
    "ciel_signe_1", "ciel_signe_2", "ciel_signe_3",
    "ciel_maison_1", "ciel_maison_2", "ciel_maison_3",
    "ciel_global", "ciel", "aspects_1", "aspects_2", "aspects_3", "aspects_4",
    # Vague 5 (cycles) — complète
    "periodes", "ages_detail", "chinois_natal", "noeuds",
    "mois_detail", "annees_detail", "arcanes", "nombres",
    "chinois_detail", "univers_detail", "heritages_detail",
    # Vague 6 (Relations restant) — complète
    "rel_nombres", "rel_chinois", "rel_synthese", "rel_pouls",
    "rel_types", "rel_composite",
    # Millman — les 17 lois, nées directement conformes
    "lois",
    # Millman — le nombre composé d'une relation, né conforme
    "rel_composite_nombre",
}
CLAIRS = [f for f in FICHIERS if f.stem in PASSES_AU_CLAIR]


@pytest.mark.parametrize("fichier", CLAIRS, ids=[f.stem for f in CLAIRS])
def test_phrases_courtes(fichier):
    """Clarté : peu de phrases longues (> 22 mots) sur les fichiers déjà relus
    pour la clarté. Cible < 12 % — au-delà, le lecteur se perd en route."""
    ph = phrases_de(fichier)
    if len(ph) < 20:
        pytest.skip("trop peu de phrases pour être significatif")
    m = mesures(ph)
    assert m["longues"] < 12, (
        f"{fichier.stem} : {m['longues']:.0f} % de phrases > 22 mots "
        f"(cible < 12). Coupe les phrases longues en deux."
    )


# ------------------------------------------------- les fichiers déjà relus

@pytest.mark.parametrize("fichier", RELUS, ids=[f.stem for f in RELUS])
def test_pas_d_aphorisme_a_chaque_phrase(fichier):
    """Les cibles de la charte, sur les fichiers passés au style.

    Ce sont les plus lus : le Jour (chaque matin), le Portrait, et la première
    chose qu'on voit sur Le Ciel.
    """
    ph = phrases_de(fichier)
    if len(ph) < 20:
        pytest.skip("trop peu de phrases pour être significatif")
    m = mesures(ph)
    assert m["tirets"] < 8, (
        f"{fichier.stem} : {m['tirets']:.0f} tirets cadratins pour 100 phrases "
        f"(cible < 8). La chute au tiret est un tic — coupe en deux phrases."
    )
    assert m["deux_points"] < 10, (
        f"{fichier.stem} : {m['deux_points']:.0f} deux-points pour 100 phrases "
        f"(cible < 10). Le deux-points aphoristique est un tic."
    )
    assert m["abstrait"] < 3, (
        f"{fichier.stem} : {m['abstrait']:.0f} phrases pour 100 ouvrent sur un "
        f"concept abstrait (cible < 3). Mets « tu » en sujet."
    )
    assert m["verdict_nie"] < 2, (
        f"{fichier.stem} : {m['verdict_nie']:.0f} « Ce n'est pas… » pour 100 "
        f"(cible < 2). Dis la chose directement."
    )


# ------------------------------------------------------- tout le corpus

def test_les_phrases_restent_courtes():
    """Ce qui allait déjà bien, et qu'il ne faut pas casser en réécrivant.

    Le défaut n'a jamais été la longueur : médiane 15 mots. Aplanir le style ne
    doit pas produire des phrases à rallonge.
    """
    toutes = [p for f in FICHIERS for p in phrases_de(f)]
    L = sorted(len(p.split()) for p in toutes)
    mediane = L[len(L) // 2]
    assert mediane <= 18, f"médiane de {mediane} mots — les phrases s'allongent"
    trop_longues = sum(1 for x in L if x > 30) / len(L) * 100
    assert trop_longues < 5, f"{trop_longues:.0f} % de phrases > 30 mots"


def test_tendance_generale():
    """Le corpus entier ne doit pas EMPIRER, même là où le style n'a pas été repris.

    Ce test ne rend pas le passé rouge : il pose un plafond au-dessus de l'état
    mesuré (25 tirets / 30 deux-points pour 100 au pire fichier) et empêche
    qu'un nouvel apport le dépasse. Un test rouge en permanence finit ignoré ;
    un plafond qui descend au fil des passes, non.
    """
    for f in FICHIERS:
        ph = phrases_de(f)
        if len(ph) < 20:
            continue
        m = mesures(ph)
        assert m["tirets"] < 26, f"{f.stem} : {m['tirets']:.0f} tirets/100 — pire que l'état connu"
        assert m["deux_points"] < 31, f"{f.stem} : {m['deux_points']:.0f} deux-points/100"


def test_le_tutoiement_domine_l_abstraction():
    """Align parle À la personne, pas D'elle.

    « Ce Cap pense en grand angle » met une abstraction entre le lecteur et son
    propre portrait. « Tu penses en grand angle » est la même chose, en mieux.
    """
    toutes = [p for f in FICHIERS for p in phrases_de(f)]
    tu = sum(len(re.findall(r"\btu\b", p, re.I)) for p in toutes)
    abstrait = sum(len(re.findall(r"\b(ce Cap|cette fonction|ce nombre|cet astre)\b", p, re.I))
                   for p in toutes)
    assert tu > abstrait * 20, f"« tu » {tu} vs abstractions {abstrait}"


# ------------------------------------------------- le ton positif (chantier)

# Les fichiers du « message du jour » — là où le ton positif compte le plus
# (voir CHARTE.md « Le ton positif — de la privation vers la ressource »).
FICHIERS_DU_JOUR = ("fil", "transits", "ciel")


def test_pas_de_pour_une_fois():
    """« pour une fois » est un qualificatif à revers : il sous-entend que la
    norme est mauvaise et vole la bonne nouvelle qu'il annonce (mouvement C du
    chantier « ton positif »). C'est le SEUL marqueur de privation fiable à
    tester mécaniquement — « tu n'as pas à / rien à » ne l'est pas (« Tu n'as
    rien à décider, juste à observer » est au contraire la bonne voix d'Align),
    il se traite au jugement à la lecture."""
    for stem in FICHIERS_DU_JOUR:
        texte = (CORPUS / f"{stem}.json").read_text(encoding="utf-8")
        n = len(re.findall(r"pour une fois", texte, re.I))
        assert n == 0, (
            f"{stem} : {n} « pour une fois » — qualificatif à revers, à retourner "
            f"vers la ressource (CHARTE.md, ton positif)."
        )


def test_l_inventaire_de_style_est_publiable():
    """Un tableau de bord plutôt qu'une assertion — pour piloter les passes.

    Ne juge rien : imprime l'état. Lancer avec `-s` pour le voir.
    """
    print("\n\n  ÉTAT DU STYLE — tirets / deux-points / abstrait, pour 100 phrases\n")
    for f in FICHIERS:
        ph = phrases_de(f)
        if len(ph) < 20:
            continue
        m = mesures(ph)
        etat = "✓ relu" if f.stem in PASSES_AU_STYLE else "  à faire"
        print(f"    {f.stem:<22} {m['phrases']:>5} ph  "
              f"—{m['tirets']:>5.0f}  :{m['deux_points']:>5.0f}  "
              f"abs{m['abstrait']:>4.0f}   {etat}")
    assert True
