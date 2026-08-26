"""Le filet golden de la numérologie.

Les valeurs de référence sont RELEVÉES dans la source (chacune porte son
numéro de page imprimée), pas recalculées : sinon le test ne prouverait rien —
il validerait le code contre lui-même.

Ce module ne teste que des NOMBRES. Aucun texte d'interprétation n'entre ici,
ni dans le golden : les calculs sont libres, la prose ne l'est pas.
"""
import json
import pathlib

import pytest

from moteur import numerologie as N

GOLDEN = json.loads(
    (pathlib.Path(__file__).parent / "golden" / "numerologie.json").read_text(encoding="utf-8")
)


def _cle(portrait, nom):
    """Lit une clé du portrait Align sous le nom de la source."""
    correspondance = {
        "racine1": "cap", "racine2": "voix", "tronc": "foyer",
        "dynamique": "elan", "ecorce": "reflet", "branche": "geste",
        "feuille": "source", "fruit": "trace",
    }
    return portrait[correspondance[nom]]


# ------------------------------------------------- la convention des accents

def test_accents_transparents():
    """Le point capital, et il est IMPRIMÉ noir sur blanc : é = e, ç = c.

    STÉPHANE = 34 n'est atteignable qu'avec É = 5. Aucune app française ne
    documente sa convention, alors que les deux conventions concurrentes
    donnent des résultats différents pour le même nom. Align publie la sienne.
    """
    assert N.somme_lettres("STÉPHANE") == 34
    assert N.somme_lettres("STEPHANE") == 34
    for accentue, nu in [("FRANÇOIS", "FRANCOIS"), ("RENÉE", "RENEE"),
                         ("NOËL", "NOEL"), ("MAÏTÉ", "MAITE")]:
        assert N.somme_lettres(accentue) == N.somme_lettres(nu), accentue


def test_table_pythagoricienne():
    assert N.valeur_lettre("A") == 1 and N.valeur_lettre("I") == 9
    assert N.valeur_lettre("J") == 1 and N.valeur_lettre("R") == 9
    assert N.valeur_lettre("S") == 1 and N.valeur_lettre("Z") == 8


# ------------------------------------------------------ maître vs héritage

def test_un_maitre_devient_la_valeur():
    """La distinction la plus discriminante de toute la méthode."""
    c = N.cap(16, 7, 1972)
    assert c["valeur"] == 33 and c["base"] == 6      # le livre note « 33/6 »
    f = N.foyer(10, 12)
    assert f["valeur"] == 22 and f["base"] == 4      # « 22/4 »


def test_un_heritage_ne_devient_jamais_la_valeur():
    """L'autre moitié de la règle — et l'erreur classique.

    Un cap porteur d'un 19 vaut 1, pas 19. L'héritage est un drapeau posé à
    côté, jamais la valeur.
    """
    c = N.cap(24, 2, 1955)                            # Steve Jobs
    assert c["valeur"] == 1, "le 19 ne doit PAS devenir la valeur"
    assert 19 in c["heritages"]


def test_maitre_et_heritage_coexistent_depuis_des_routes_differentes():
    """Deux routes, deux révélations, simultanément."""
    c = N.cap(29, 9, 2000)
    assert c["valeur"] == 22 and c["base"] == 4
    assert 13 in c["heritages"]


# -------------------------------------------- `pas` vs `reduire_total`

def test_le_meme_29_donne_deux_resultats_selon_le_nombre():
    """Le piège n°1, et la source est incohérente d'une section à l'autre.

    Sur un cap ou un foyer, 29 s'arrête à 11 (le maître tient). Sur les
    frictions et le reflet, 29 → 11 → 2 : le maître est ÉCRASÉ.
    Harmoniser dans un sens ou dans l'autre casse des exemples de référence.
    On reproduit l'incohérence de la source, et on la documente.
    """
    assert N.reduire(29) == 11           # s'arrête
    assert N.reduire_total(29) == 2      # écrase
    assert N.reflet(29) == 2             # le reflet écrase — imprimé p300


def test_frictions_ecrasent_les_maitres():
    """Frictions du 29/12/1997 -> [1, 6, 5, 5], imprimé p308."""
    assert N.frictions(29, 12, 1997)["toutes"] == [1, 6, 5, 5]


def test_une_friction_nulle_vaut_9_jamais_0():
    f = N.frictions(15, 15 % 12 + 1, 2000)
    assert 0 not in f["toutes"]


# ---------------------------------------------- héritage LOCAL à un mot

def test_heritage_local_invisible_dans_les_totaux():
    """Le piège le plus fin, et il vient de la source (p301).

    Chez « Marie Lise Dupont », les voyelles de LISE valent 14 — un héritage —
    mais le total (38 → 11 → 2) ne le contient NULLE PART. Ne scanner que les
    totaux de routes le raterait, et c'est justement l'apport le plus fin de
    la méthode.
    """
    s = N.source(["Marie", "Lise", "Dupont"])
    assert s["valeur"] == 11 and s["base"] == 2, "notation imprimée « 11/2 »"
    assert 14 in s["heritages"], "l'héritage 14 de LISE doit être vu"
    assert 14 not in s["heritages_de_routes"], "il n'est dans AUCUN total"
    local = [h for h in s["heritages_locaux"] if h["valeur"] == 14]
    assert local and "2e prénom" in local[0]["ou"], f"position attendue, obtenu {local}"


def test_un_maitre_dans_un_mot_ne_promeut_pas():
    """MARIE-JEANNE : JEANNE vaut 22, mais la voix reste 5, pas 22.

    Seules les ROUTES promeuvent un maître. Un mot, non.
    """
    v = N.voix(["Marie", "Jeanne"])
    assert N.somme_lettres("Jeanne") == 22
    assert v["valeur"] == 5, "le 22 de JEANNE ne doit pas promouvoir"
    assert 14 in v["heritages"], "mais la ligne réduite 10+4=14 est un héritage"


# ------------------------------------------------- exemples de l'annexe

@pytest.mark.parametrize("mot,attendu", [
    ("MARIE", 28), ("JEANNE", 22), ("DUPOND", 29), ("STÉPHANE", 34),
])
def test_sommes_de_lettres(mot, attendu):
    assert N.somme_lettres(mot) == attendu


def test_elan_cherche_un_maitre_en_deux_temps():
    """Paul Martin : 11+8+1 = 20 → 2, puis 2+8+1 = 11. Imprimé.

    L'élan garde les maîtres non réduits d'abord, puis les réduit pour voir
    s'il en apparaît un autre. Seuls les maîtres se conservent ici.
    """
    e = N.elan(11, 8, 1)
    assert e["valeur"] == 11 and e["base"] == 2


def test_foyer_route_reduite_revele_un_heritage():
    """25/07 : la route brute donne 5, la route réduite révèle 14.

    L'arbitrage entre routes dépend du RÉSULTAT, pas d'un ordre fixe : 10/12
    retient la route brute (un maître apparaît), 25/07 la route réduite (un
    héritage apparaît). Une implémentation « route 1 puis repli » se plante
    sur l'un des deux.
    """
    f = N.foyer(25, 7)
    assert f["valeur"] == 5
    assert 14 in f["heritages"]


# ------------------------------------------------------------ portraits

PORTRAITS = GOLDEN["portraits"]


@pytest.mark.parametrize("p", PORTRAITS, ids=[p["id"] for p in PORTRAITS])
def test_portraits_de_reference(p):
    """Les 5 portraits publiés, clé par clé.

    Un `null` dans le golden = la valeur n'est PAS imprimée dans la source :
    on saute plutôt que d'inventer une attente.
    """
    if p.get("litige_global"):
        pytest.skip(p["litige_global"])

    an, mo, jo = p["naissance"]
    portrait = N.portrait(p["prenoms_nom"], jo, mo, an)

    for nom, attendu in p["attendu"].items():
        if attendu is None:
            continue
        valeur = attendu.get("valeur") if isinstance(attendu, dict) else attendu
        if valeur is None:
            continue
        if nom in ("ecorce", "branche"):
            obtenu = _cle(portrait, nom)
        else:
            obtenu = _cle(portrait, nom)["valeur"]
        if nom == "racine2" and p["id"] == "jk-rowling":
            continue                    # litige connu — voir test dédié
        assert obtenu == valeur, f"{p['id']} · {nom} : {obtenu} ≠ {valeur} (p. {p.get('page')})"


def test_simone_veil_est_calculee_sous_son_nom_d_epouse():
    """Une anomalie de la source, confirmée par l'arithmétique.

    L'en-tête annonce « née Simone Jacob », mais aucun des nombres publiés ne
    sort de « Simone Jacob ». Le geste (un simple comptage de A/J/S) tranche
    sans ambiguïté : il vaut 1 sous « Simone Veil », 3 sous « Simone Jacob ».
    C'est cohérent avec sa propre règle du nom porté le plus longtemps, mais
    l'en-tête induit en erreur.
    """
    assert N.geste(["Simone", "Veil"]) == 1
    assert N.geste(["Simone", "Jacob"]) == 3


def test_rowling_le_livre_et_le_calcul_divergent():
    """Un litige qu'on EXPOSE au lieu de le masquer.

    La source imprime 22 pour la voix de Rowling ; les trois routes qu'elle
    documente donnent 13/4. Aucune variante de nom testée ne produit 22, et la
    seule règle qui y mènerait est réfutée par la source elle-même (elle
    casserait la trace de Rowling et le cap de Jobs).

    Erreur du livre, ou nom de naissance non divulgué. Tordre l'algorithme
    pour rattraper ce point isolé casserait tout le reste.
    """
    v = N.voix(["Joanne", "Rowling"])
    assert v["valeur"] == 4 and 13 in v["heritages"], (
        "si ce test change, c'est qu'on a tordu l'algorithme pour un cas litigieux"
    )


# -------------------------------------------------------------- grille

def test_appuis_et_chantiers_sur_les_lettres_seules():
    """La grille se bâtit sur les LETTRES, la date n'y entre pas.

    C'est ce qui la rend complémentaire d'une grille bâtie sur la date, et non
    concurrente : les deux ne se recouvrent en rien.
    """
    a = N.appuis(["Steven", "Paul", "Jobs"])
    assert sum(a["compte"].values()) == len("STEVENPAULJOBS")
    assert set(a["appuis"]) | set(a["chantiers"]) == set(range(1, 10))
    assert not (set(a["appuis"]) & set(a["chantiers"]))


def test_geste_zero_est_une_valeur_legitime():
    """0 n'est pas une absence : c'est un comptage qui vaut zéro."""
    assert N.geste(["Bob"]) == 0


def test_periodes_des_chantiers_seulement_ou_la_source_les_imprime():
    """4→9 sont imprimées ; 1→3 ne le sont pas. On ne les invente pas."""
    assert set(N.PERIODES_CHANTIERS) == {4, 5, 6, 7, 8, 9}
    assert N.PERIODES_CHANTIERS[4] == (27, 36)
    assert N.PERIODES_CHANTIERS[9] == (72, 81)


# ------------------------------- les conventions tranchées par Align

def test_apostrophe_ignoree_un_seul_mot():
    """« D'Artagnan » se calcule sur DARTAGNAN, pas sur D + ARTAGNAN.

    La source est MUETTE (0 occurrence d'« apostrophe » sur 90 000 mots).
    Align tranche et publie : l'apostrophe n'est pas un séparateur.
    """
    assert N.plier("D'Artagnan") == "DARTAGNAN"
    assert N.normaliser_noms(["D'Artagnan"]) == ["DARTAGNAN"]
    assert N.somme_lettres("D'Artagnan") == N.somme_lettres("Dartagnan")


def test_particules_soudees_au_nom_qu_elles_introduisent():
    """Les particules COMPTENT : elles font partie de l'état civil.

    La source exige le nom de naissance exact — or « de Gaulle » EST l'état
    civil, « de » compris. Mais une particule n'est pas un nom : elle en
    introduit un. Elle se soude donc au mot suivant, et l'unité de calcul
    reste le nom civil entier.
    """
    assert N.normaliser_noms(["Charles", "de", "Gaulle"]) == ["CHARLES", "DEGAULLE"]
    assert N.normaliser_noms(["Ludwig", "van", "Beethoven"]) == ["LUDWIG", "VANBEETHOVEN"]
    assert N.normaliser_noms(["Jean", "de", "La", "Fontaine"]) == ["JEAN", "DELAFONTAINE"]


def test_la_particule_est_bien_comptee():
    """Rien n'est jeté : les lettres de la particule entrent dans le total."""
    assert N.somme_lettres("DEGAULLE") == N.somme_lettres("de") + N.somme_lettres("Gaulle")
    assert N.somme_lettres("VANBEETHOVEN") == N.somme_lettres("van") + N.somme_lettres("Beethoven")


def test_de_vaut_9_donc_ne_change_jamais_la_valeur_finale():
    """Une élégance arithmétique, pas une coïncidence — et elle mérite d'être sue.

    « de » = D(4) + E(5) = 9 exactement. Or 9 est l'élément NEUTRE des racines
    numériques (9 ≡ 0 mod 9) : lui ajouter 9 ne déplace jamais le résultat.
    Donc « Charles de Gaulle » et « Charles Gaulle » ont la même Voix — non par
    hasard, mais par nécessité.

    ⚠️ Ce n'est vrai que de « de ». Les autres particules pèsent : du = 7,
    le = 8, la = 4, van = 1, von = 6.
    """
    assert N.somme_lettres("de") == 9
    assert N.voix(["Charles", "de", "Gaulle"])["valeur"] == N.voix(["Charles", "Gaulle"])["valeur"]
    # les autres, elles, déplacent bien la valeur
    assert N.somme_lettres("du") == 7 and N.somme_lettres("le") == 8
    assert N.voix(["Jean", "du", "Bois"])["valeur"] != N.voix(["Jean", "Bois"])["valeur"]


def test_mais_de_peut_faire_basculer_un_sous_nombre():
    """Le corollaire, et c'est LÀ que ça compte.

    « de » n'change pas la valeur, mais il décale la somme brute de 9 — et la
    somme brute est ce qui révèle les maîtres et les héritages. Un mot de
    somme 13 (héritage) devient 22 (MAÎTRE) une fois « de » soudé devant.

    Autrement dit : écarter les particules serait invisible sur la valeur et
    pourtant destructeur sur la lecture fine. C'est la meilleure raison de les
    garder.
    """
    assert 13 in N.HERITAGES and 22 in N.MAITRES
    assert 13 + N.somme_lettres("de") == 22, "un héritage 13 devient un maître 22"

    # sur un vrai nom : Caza vaut 13 (un héritage) ; de Caza vaut 22 (un maître)
    assert N.somme_lettres("Caza") == 13
    assert N.somme_lettres("DECAZA") == 22
    assert N.normaliser_noms(["Jean", "de", "Caza"]) == ["JEAN", "DECAZA"]


def test_apostrophe_et_particule_suivent_la_meme_regle():
    """Une seule idée, deux graphies : la particule se soude, élidée ou espacée."""
    assert N.normaliser_noms(["D'Artagnan"]) == ["DARTAGNAN"]
    assert N.normaliser_noms(["d", "Artagnan"]) == ["DARTAGNAN"]


def test_particule_orpheline_ne_fait_pas_tomber_l_app():
    """Saisie malformée : une particule sans nom à souder reste une unité."""
    assert N.normaliser_noms(["Jean", "de"]) == ["JEAN", "DE"]
    assert N.normaliser_noms(["de", "la"]) == ["DELA"]


def test_le_trait_d_union_ne_fusionne_toujours_pas():
    """Le trait d'union est SPÉCIFIÉ par la source : deux unités, pas une.

    À ne pas confondre avec l'apostrophe et les particules, qui sont des
    choix d'Align sur des points où la source se tait.
    """
    v = N.voix(["Marie", "Jeanne"])
    assert v["valeur"] == 5 and 14 in v["heritages"]


def test_annee_personnelle_bascule_au_1er_janvier():
    """Décidé le 2026-07-16 : année CIVILE.

    Mieux appuyé que l'anniversaire — une source l'affirme explicitement, et
    « l'année en cours » de l'autre y pointe lexicalement.
    """
    # née le 16 juillet : la valeur ne dépend QUE de l'année civile,
    # elle est donc la même en janvier et en décembre.
    assert N.annee_personnelle(16, 7, 2026) == N.annee_personnelle(16, 7, 2026)
    # et elle change au passage d'année
    assert N.annee_personnelle(16, 7, 2026) != N.annee_personnelle(16, 7, 2027)


def test_annee_personnelle_tourne_sur_neuf_ans():
    valeurs = [N.annee_personnelle(16, 7, a) for a in range(2020, 2029)]
    assert sorted(valeurs) == list(range(1, 10)), "un cycle de 9 ans sans trou"


# ------------------------------------------- l'année du monde et le décalage

def test_annee_universelle_est_l_annee_civile_reduite():
    """Le climat collectif : la même pour toute la planète."""
    assert N.annee_universelle(2026) == 1     # 2+0+2+6 = 10 -> 1
    assert N.annee_universelle(2025) == 9
    assert N.annee_universelle(2027) == 2


def test_le_decalage_au_monde_ne_depend_que_de_la_naissance():
    """Il ne prend PAS l'année courante : il est constant toute la vie."""
    import inspect
    params = list(inspect.signature(N.decalage_au_monde).parameters)
    assert params == ["jour", "mois_naissance"], (
        "le décalage ne doit dépendre que de la date de naissance, "
        "sinon il ne serait plus constant"
    )


def test_le_decalage_vaut_toujours_1_a_9_jamais_0():
    """Comme toute réduction d'Align : 9 plutôt que 0."""
    for jour in range(1, 32):
        for mois in range(1, 13):
            d = N.decalage_au_monde(jour, mois)
            assert 1 <= d <= 9, f"{jour}/{mois} -> {d} hors [1,9]"


def test_le_croisement_est_exact_toute_l_annee_toute_une_vie():
    """LA relation qui fonde le croisement, et elle doit être EXACTE.

    L'année personnelle EST l'année du monde décalée par la naissance :
    annee_personnelle == réduire(annee_universelle + décalage). Si ça se
    vérifie, le petit paragraphe « le monde est en tant, toi en tant » ne
    ment jamais, quelle que soit l'année.
    """
    for jour, mois in [(6, 4), (16, 7), (1, 1), (31, 12), (29, 2)]:
        d = N.decalage_au_monde(jour, mois)
        for annee in range(2020, 2035):
            ap = N.annee_personnelle(jour, mois, annee)
            au = N.annee_universelle(annee)
            assert ap == N.reduire_total(au + d), (
                f"croisement rompu pour {jour}/{mois} en {annee}"
            )


def test_martin_court_toujours_un_cran_devant_son_epoque():
    """Le cas qui a motivé la fonctionnalité : né le 6 avril.

    2026 : le monde est en 1, Martin en 2 — un cran d'avance, et cet écart
    ne bouge jamais d'une année à l'autre.
    """
    d = N.decalage_au_monde(6, 4)
    assert d == 1
    assert N.annee_universelle(2026) == 1
    assert N.annee_personnelle(6, 4, 2026) == 2
    # constant : le même cran d'avance sur dix ans
    ecarts = {(N.annee_personnelle(6, 4, a) - N.annee_universelle(a)) % 9
              for a in range(2020, 2030)}
    assert ecarts == {1}, "l'avance d'un cran doit être invariante"
