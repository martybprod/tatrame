"""Le corpus tenu par des tests — parce que c'est LUI qui peut tuer Align.

Le risque n°1 de ce projet n'est ni le calcul ni le juridique : c'est la
RÉPÉTITION. Une app concurrente en est morte — « les readings cessent de
sembler personnels dès qu'on voit les cinq mêmes descripteurs recyclés chez
tous ses amis ».

Ces tests mesurent ce qu'une relecture humaine ne voit pas : un tic né ENTRE
deux rédacteurs qui ne se lisent pas. C'est exactement comme ça que le premier
tic est apparu (9 miroirs sur 9 en « Tu es en train de » dans un bloc, 0 dans
les deux autres) — chaque agent respectait sa consigne, le corpus assemblé
non.

Ils vérifient aussi les interdits juridiques : marques et vocabulaire protégé
n'ont pas le droit d'entrer, jamais.
"""
import json
import pathlib
import re
import unicodedata
from collections import Counter

import pytest

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "data" / "corpus"
FICHIERS = sorted(CORPUS.glob("*.json"))


def _plier(s):
    """Minuscules, sans accents — pour comparer un libellé à une clé technique."""
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def charger():
    tables = {}
    for f in FICHIERS:
        tables[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return tables


#: Les champs qui portent de la PROSE — ceux que la charte engage.
#:
#: ⚠️ Cette liste s'est révélée être un piège : elle ne contenait au départ que
#: les champs de la première vague (miroir/geste/anime/conditionnement), si
#: bien que les 264 entrées du Ciel et les 21 approfondies échappaient à TOUS
#: les contrôles — 97 000 mots sans vérification d'interdits ni de répétition,
#: pendant que la suite affichait un vert rassurant. Un test qui ne voit pas
#: ce qu'il est censé garder est pire que pas de test : il endort.
#:
#: `test_aucune_entree_n_echappe_aux_controles` empêche que ça se reproduise.
CHAMPS_DE_PROSE = frozenset({
    # le jour
    "miroir", "geste",
    # la pensée du soir (« À méditer ») — vit AU NIVEAU HAUT d'un transit, y
    # compris sur une entrée en forme variantes (approche/coeur/retrait) où
    # elle serait sinon la seule chaîne et échapperait à tous les contrôles.
    "pensee_soir",
    # les nombres et les arcanes
    "anime", "alimenter", "contrarie", "conditionnement",
    "en_resonance", "en_tension",
    # les approfondissements
    "resume", "le_mouvement", "au_quotidien", "avec_les_autres", "les_canaux",
    "le_piege", "si_tu_ne_te_reconnais_pas", "de_quoi_il_s_agit",
    "ce_qui_arrive_souvent", "ce_qui_aide", "ce_qui_nuit",
    "la_place_dans_le_cycle", "comment_savoir_que_c_est_reussi",
    # le ciel
    "comment_ca_marche", "le_revers", "ou_ca_se_joue", "generationnel",
    "pourquoi_c_est_personnel", "texte",
    # le lexique — de la prose, elle aussi, et la plus lue : c'est elle qui
    # explique les termes. Elle échappait aux contrôles ; le garde-fou l'a vue.
    "quoi", "d_ou", "pourquoi_ce_mot", "quand",
    # les aspects entre planètes (en_bref + texte) et l'année universelle
    # (le climat du monde, le décalage constant de chacun)
    "en_bref", "climat", "en_un_mot", "titre",
    # les héritages (mémoires familiales 13/14/16/19)
    "ce_qui_se_transmet", "ce_que_tu_peux_en_faire",
    # les âges de la vie
    "le_ciel_derriere",
    # le signe chinois natal (portrait de l'animal, nuance de l'élément)
    "portrait", "nuance",
    # les messages de la carte du jour et de la carte de l'année
    "invitation", "pour_l_annee",
    # la personologie (48 sous-périodes + axe des nœuds)
    "essence", "origine", "destination",
    # les 17 lois (Millman, distillées) — le levier du jour
    "le_principe", "le_pas",
    # le nombre composé d'une relation (Millman) — le « vous » en nombres
    "le_but", "l_atout", "le_piege", "la_question",
})


def entrees():
    """Toutes les entrées rédigées, à plat, avec leur provenance."""
    out = []

    def descendre(noeud, chemin):
        if isinstance(noeud, dict):
            # On ne garde que les champs de PROSE. Un champ de métadonnée comme
            # `source_livre` (l'attribution « d'après Chapman… ») est
            # légitimement identique d'une entrée à l'autre : le scanner comme
            # de la prose le ferait passer pour un doublon de texte, et le
            # soumettrait à tort aux interdits de la charte. La charte engage la
            # prose, pas l'attribution.
            champs = {k: v for k, v in noeud.items()
                      if isinstance(v, str) and k in CHAMPS_DE_PROSE}
            if champs:
                out.append((chemin, champs))
            for k, v in noeud.items():
                if not k.startswith("_"):
                    descendre(v, chemin + [k])

    for nom, table in charger().items():
        descendre(table, [nom])
    return out


TOUTES = entrees()
TEXTES = [(c, t) for c, champs in TOUTES for t in champs.values()]


def test_le_corpus_existe():
    assert len(TOUTES) >= 400, f"seulement {len(TOUTES)} entrées"


def test_aucune_entree_n_echappe_aux_controles():
    """Le garde-fou du garde-fou — et il a une histoire.

    `CHAMPS_DE_PROSE` ne listait que les champs de la première vague. Quand le
    corpus a quadruplé, 264 entrées du Ciel se sont mises à passer sous le
    radar : aucun contrôle d'interdit, aucune mesure de répétition, sur
    97 000 mots — et la suite restait verte. **Un test qui ne voit pas ce
    qu'il garde est pire que pas de test : il endort.**

    Ici on compare le nombre d'entrées CONTRÔLÉES au nombre d'entrées
    RÉELLES. Ajouter un fichier au corpus avec des noms de champs inédits fait
    échouer ce test — donc on y pense.
    """
    reelles = 0
    for nom, table in charger().items():
        for cle, contenu in table.items():
            if cle.startswith("_") or not isinstance(contenu, dict):
                continue
            for _, entree in contenu.items():
                # une entrée = un dict dont au moins une valeur est du texte long
                if isinstance(entree, dict) and any(
                    isinstance(v, str) and len(v.split()) > 15 for v in entree.values()
                ):
                    reelles += 1

    controlees = len(TOUTES)
    assert controlees >= reelles, (
        f"{reelles - controlees} entrées de prose échappent aux contrôles.\n"
        f"Un champ nouveau n'est pas dans CHAMPS_DE_PROSE — ajoute-l'y, "
        f"sinon la charte n'est plus vérifiée sur ces textes."
    )


# --------------------------------------------------- interdits juridiques

INTERDITS_MARQUES = [
    r"\bosho\b",                       # marque UE valide, confirmée en 2017
    r"numérologie\s+stratégique",      # marque INPI
    r"triangle\s+fondamental",
    r"arbre\s+(personnel|de\s+vie)",
]

# Le vocabulaire de la source numérologique. Align a le sien (Cap, Voix,
# Foyer, Élan, Héritages, Frictions, Appuis, Chantiers) précisément pour ne
# jamais avoir à employer celui-là.
INTERDITS_VOCABULAIRE = [
    r"\bmémoire\s+familiale\b",
    r"\bdynamique\s+de\s+vie\b",
    r"\bécorce\b",
]


@pytest.mark.parametrize("motif", INTERDITS_MARQUES + INTERDITS_VOCABULAIRE)
def test_aucune_marque_ni_vocabulaire_protege(motif):
    """Ce qui rend Align distribuable. Non négociable."""
    fautifs = [(c, t[:60]) for c, t in TEXTES if re.search(motif, t, re.I)]
    assert not fautifs, f"{motif!r} trouvé dans : {fautifs[:3]}"


def test_align_n_interdit_pas_son_propre_vocabulaire():
    """Une contradiction de doctrine, trouvée en la commettant.

    L'interdit porte sur la MÉTAPHORE de la source (l'arbre appliqué aux
    nombres), pas sur les mots français. Or Align nomme lui-même la maison 4
    « tes racines » — et une consigne « jamais racine » donnée à des
    rédacteurs les a poussés à réécrire quatre passages innocents qui
    parlaient simplement de famille.

    Ce test vérifie qu'aucun interdit ne mord sur le vocabulaire que l'app
    emploie elle-même. Un interdit trop large coûte du texte juste et ne
    protège de rien de plus.
    """
    lexique = charger()["lexique"]
    propres = [v["nom"] for v in lexique["maisons"].values()]
    propres += [v["nom"] for v in lexique["termes"].values()]

    for motif in INTERDITS_MARQUES + INTERDITS_VOCABULAIRE:
        for mot in propres:
            assert not re.search(motif, mot, re.I), (
                f"l'interdit {motif!r} mord sur « {mot} », qui est le vocabulaire "
                f"d'Align lui-même — l'interdiction est trop large"
            )


# ----------------------------------------------------- interdits de ton

def _voix_d_align(texte):
    """Ce qu'Align dit EN PROPRE — les paroles rapportées retirées.

    La charte engage la voix d'Align, pas celle des personnages qu'elle cite.
    « On te dit "tu es quelqu'un de gentil" » ne commet pas l'essentialisation :
    il la RAPPORTE, et souvent pour la dénoncer. Sur le corpus réel, 100 % des
    « tu es quelqu'un » étaient des citations.
    """
    return re.sub(r"«[^»]*»", "⟨cité⟩", texte)


# Les verbes d'oracle : ceux qui annoncent un ÉVÉNEMENT à venir. C'est ça, la
# prédiction — pas le futur grammatical.
#
# ⚠️ LA LIMITE DE CE TEST, dite franchement : « ne pas prédire » est un ACTE DE
# PAROLE, pas une chaîne de caractères. Une première version cherchait « tu
# vas » et « tu dois » : sur 467 entrées elle a produit 20 alertes, TOUTES
# fausses — « tu vas vers un 2 », « comment tu vas », « tu vas droit au point »,
# « ce que tu dois à qui ». Le futur simple ne marche pas mieux (« quand tu dis
# à quelqu'un que tu seras là » n'annonce rien).
#
# Ce test n'attrape donc que les formes SANS AMBIGUÏTÉ. Le reste se joue dans
# les consignes de rédaction et la relecture — pas ici. Un test qui hurle à
# tort finit ignoré, et un test ignoré ne protège plus rien.
ORACLE = r"\btu (vas |)(rencontrer|recevr|trouver|connaîtr|vivr)a?s?\b(?![^.]*\b(pas|jamais)\b)"

INTERDITS_REGISTRE = [
    (ORACLE, "prédiction d'événement — Align ne prédit pas"),
    (r"\bil faut que tu\b", "prescription"),
    (r"\btu devras\b", "prescription au futur"),
    (r"\btu es quelqu'un\b", "essentialisation"),
    (r"\bton destin\b", "fatalisme — la date de naissance est un point de départ"),
    (r"\bc'est écrit\b", "fatalisme"),
]


@pytest.mark.parametrize("motif,pourquoi", INTERDITS_REGISTRE)
def test_registre(motif, pourquoi):
    """C'est l'ACTE d'énoncé qui est interdit, jamais la chaîne.

    Deux corrections apportées par le corpus réel :
      1. une tournure NIÉE dit le contraire de ce qu'on proscrit — « demande-toi
         de quoi tu as envie, PAS ce que tu dois faire » récuse la prescription ;
      2. une tournure CITÉE est la voix d'un autre, pas celle d'Align.
    """
    fautifs = []
    for chemin, t in TEXTES:
        propre = _voix_d_align(t)
        for m in re.finditer(motif, propre, re.I):
            avant = propre[max(0, m.start() - 22):m.start()].lower()
            if re.search(r"\b(pas|jamais|sans|non|plutôt que|au lieu de)\b[^.]*$", avant):
                continue                       # tournure niée -> conforme
            fautifs.append((chemin, propre[max(0, m.start() - 40):m.end() + 30]))
    assert not fautifs, f"{pourquoi} : {fautifs[:3]}"


# ------------------------------------------- LE MUR DU CORPUS (le vrai)

def test_aucune_ouverture_ne_domine():
    """Le test qui aurait attrapé le tic dès sa naissance.

    On mesure sur le corpus ASSEMBLÉ, pas fichier par fichier : le tic est né
    entre deux rédacteurs qui ne se lisaient pas, chacun conforme de son côté.
    Seule la vue d'ensemble le révèle.
    """
    ouvertures = Counter(
        " ".join(champs[k].split()[:4]).lower().rstrip(",:")
        for _, champs in TOUTES for k in ("miroir",) if champs.get(k)
    )
    total = sum(ouvertures.values())
    if total < 20:
        pytest.skip("corpus trop petit pour être significatif")
    pire, n = ouvertures.most_common(1)[0]
    seuil = max(3, total * 0.10)
    assert n <= seuil, (
        f"« {pire} » ouvre {n} miroirs sur {total} ({100*n/total:.0f} %). "
        f"C'est le mur du corpus : un lecteur qui compare deux jours verra la couture."
    )


def test_les_gestes_ne_commencent_pas_tous_pareil():
    """Un verbe d'action qui domine rend les conseils interchangeables."""
    verbes = Counter(
        champs["geste"].split()[0].strip(",").lower()
        for _, champs in TOUTES if champs.get("geste")
    )
    total = sum(verbes.values())
    if total < 20:
        pytest.skip("corpus trop petit")
    pire, n = verbes.most_common(1)[0]
    assert n <= max(4, total * 0.15), (
        f"« {pire} » ouvre {n} gestes sur {total} ({100*n/total:.0f} %)"
    )


def test_aucun_texte_en_double():
    """Deux entrées identiques = un copier-coller oublié."""
    vus = {}
    for chemin, t in TEXTES:
        if len(t) < 40:
            continue
        cle = t.strip().lower()
        assert cle not in vus, f"texte dupliqué : {'.'.join(chemin)} et {'.'.join(vus[cle])}"
        vus[cle] = chemin


def test_longueurs_dans_la_charte():
    """Un texte trop court dit trop peu ; trop long, il n'est pas lu."""
    for chemin, champs in TOUTES:
        if champs.get("miroir") and champs.get("geste"):
            n = len((champs["miroir"] + " " + champs["geste"]).split())
            assert 30 <= n <= 85, f"{'.'.join(chemin)} : {n} mots"


def test_les_gestes_sont_concrets():
    """« ouvre-toi à l'inattendu » n'est pas un geste. Le test : faisable en 10 min ?

    On ne peut pas mesurer la concrétude, mais on peut attraper le vague le
    plus courant — l'injonction abstraite sans verbe d'action.
    """
    vagues = [r"ouvre-toi", r"laisse-toi porter", r"fais confiance à l'univers",
              r"sois toi-même", r"écoute ton cœur", r"lâche prise"]
    for chemin, champs in TOUTES:
        g = champs.get("geste", "")
        for v in vagues:
            assert not re.search(v, g, re.I), f"{'.'.join(chemin)} : geste vague « {v} »"


# ------------------------------------------------------- complétude

def test_les_cles_attendues_sont_toutes_la():
    """Un trou de corpus laisse un écran vide chez l'utilisateur."""
    t = charger()
    assert set(t["nombres"]["cap"]) == {"1","2","3","4","5","6","7","8","9","11","22","33"}
    assert set(t["nombres"]["foyer"]) == {"1","2","3","4","5","6","7","8","9","11","22"}
    assert set(t["nombres"]["annee_perso"]) == {str(i) for i in range(1, 10)}

    # Le détail approfondi : chaque nombre a SA table (un 9 en Cap n'est pas un
    # 9 en Voix). Les quatre couvrent les douze valeurs, maîtres compris.
    douze = {"1","2","3","4","5","6","7","8","9","11","22","33"}
    for nombre in ("cap", "voix", "foyer", "elan"):
        assert set(k for k in t["nombres_detail"][nombre] if not k.startswith("_")) == douze, (
            f"nombres_detail['{nombre}'] incomplet"
        )
    # les mémoires familiales : les quatre héritages, jamais un nombre nu
    assert set(t["heritages_detail"]["heritages"]) == {"13", "14", "16", "19"}

    # le signe chinois natal : 12 animaux + 5 éléments, additifs (jamais 60).
    # Les clés sont sans accent (chevre, metal), comme le lookup de l'app.
    assert set(t["chinois_natal"]["animaux"]) == {
        "rat", "buffle", "tigre", "lapin", "dragon", "serpent",
        "cheval", "chevre", "singe", "coq", "chien", "cochon"}
    assert set(t["chinois_natal"]["elements"]) == {
        "bois", "feu", "terre", "metal", "eau"}

    # les âges de la vie : chaque passage a son texte (sinon un trou à l'âge
    # correspondant). La liste doit coller AU MOTEUR, pas à une copie figée.
    from moteur.ages import PASSAGES
    assert set(t["ages_detail"]["passages"]) == {cle for cle, _, _ in PASSAGES}

    assert set(t["arcanes"]["arcanes"]) == {str(i) for i in range(22)}
    # chaque arcane porte SES DEUX messages : la carte du jour (une invitation
    # du présent) et la carte de l'année (la couleur du chapitre). Sans quoi un
    # jour, ou une année, tombe sur une carte muette. Ni l'un ni l'autre ne
    # prédit — ce sont des colorations, additives au ciel et au nombre.
    for i in range(22):
        arc = t["arcanes"]["arcanes"][str(i)]
        assert arc.get("invitation"), f"arcane {i} sans message de carte du jour"
        assert arc.get("pour_l_annee"), f"arcane {i} sans message de carte de l'année"
    assert set(t["ciel"]["phases"]) == {
        "nouvelle", "croissante", "premier_quartier", "gibbeuse",
        "pleine", "diffusante", "dernier_quartier", "balsamique"}
    assert set(t["ciel"]["lune_maison"]) == {str(i) for i in range(1, 13)}

    attendus = {f"{p}_{c}"
                for p in ("soleil", "lune", "mercure", "venus", "mars", "jupiter",
                          "saturne", "uranus", "neptune", "pluton")
                for c in ("conjonction", "carre-opposition", "sextile-trigone")}
    assert set(t["transits"]["transits_generiques"]) == attendus

    # Chantier A COMPLET : le titre du jour peut nommer n'importe lequel des
    # 12 points natals. 5 rapides × 3 classes × 12 cibles = 180, additif
    # (vague 1 : Soleil/Lune/Vénus/Mars/Mercure ; vague 2 : Saturne/Jupiter/
    # Ascendant/Milieu du Ciel ; vague 3 : Uranus/Neptune/Pluton).
    rapides = ("lune", "mercure", "venus", "soleil", "mars")
    cibles = ("soleil", "lune", "venus", "mars", "mercure",
             "saturne", "jupiter", "asc", "mc",
             "uranus", "neptune", "pluton")
    attendus_precis = {f"{r}_{c}_{n}" for r in rapides
                       for c in ("conjonction", "carre-opposition", "sextile-trigone")
                       for n in cibles}
    assert len(attendus_precis) == 180
    assert set(t["transits"]["transits_precis"]) == attendus_precis


def test_les_nombres_ne_se_recopient_pas_sur_un_meme_chiffre():
    """Le mur du corpus, version nombres — et il a une histoire.

    Cap, Voix, Foyer, Élan partagent le SENS d'un chiffre (un 9 parle de lien
    partout) mais pas son TEXTE : le Cap dit la direction, la Voix l'expression,
    le Foyer l'intime, l'Élan l'énergie dégagée. Quand les tables ont été
    écrites en lisant le Cap comme modèle, elles l'ont recopié quasi mot pour
    mot — jusqu'à 70 phrases de 8 mots identiques sur un même chiffre. Le
    Jaccard ne le voyait pas (dilué par le texte propre) ; le COMPTE de suites
    de 8 mots partagées, si. Un lecteur qui a le même chiffre en deux nombres
    lirait deux fois le même paragraphe — exactement ce qu'Align refuse.

    On mesure CHAMP PAR CHAMP, pas sur l'entrée entière : un lecteur lit une
    section à la fois, et c'est là qu'une phrase recopiée saute aux yeux.
    Seuil : moins de 6 suites de 8 mots communes dans un même champ entre deux
    tables sur un même chiffre. L'état livré est à 0 (marge confortable ; le
    pire cas d'origine dépassait 30 dans un seul champ).
    """
    import re
    import itertools
    t = charger()["nombres_detail"]
    champs = ("resume", "le_mouvement", "au_quotidien",
              "avec_les_autres", "les_canaux", "le_piege")

    def suites(texte, n=8):
        mots = re.findall(r"\w+", texte.lower())
        return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}

    douze = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "22", "33")
    tables = ("cap", "voix", "foyer", "elan")
    fautifs = []
    for v in douze:
        for c in champs:
            emp = {n: suites(t[n][v].get(c, "")) for n in tables if v in t[n]}
            for a, b in itertools.combinations(emp, 2):
                partage = len(emp[a] & emp[b])
                if partage >= 6:
                    fautifs.append((v, c, f"{a}~{b}", partage))
    fautifs.sort(key=lambda x: -x[3])
    assert not fautifs, (
        "des nombres recopient un autre sur le même chiffre "
        f"(≥ 6 suites de 8 mots dans un champ) : {fautifs[:6]}"
    )


def test_les_transits_precis_ne_se_recopient_pas_entre_cibles():
    """Le même garde-fou, appliqué aux transits précis (Chantier A).

    « Mars carré ton Soleil natal » et « Mars carré ta Lune natale » partagent
    le même déclencheur (mars, carré) mais visent un terrain différent
    (identité vs besoin profond) : le texte doit varier avec la cible, pas
    seulement le nom qu'on lui accole. Écrit par 5 agents en parallèle, un par
    cible — le risque de convergence existe surtout sur le vocabulaire de la
    CLASSE (conjonction = fusion, partout), pas sur la cible elle-même.

    Seuil : moins de 4 suites de 8 mots communes entre deux cibles pour le
    même déclencheur+classe. L'état livré est à 0.
    """
    import re
    import itertools
    precis = charger()["transits"]["transits_precis"]

    def suites(texte, n=8):
        mots = re.findall(r"\w+", texte.lower())
        return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}

    def texte_entier(e):
        """Une entrée précise a un texte unique, ou plusieurs variantes
        (approche/cœur/retrait) : on les compare toutes ensemble, la
        convergence entre cibles se joue sur le vocabulaire, pas la phase.
        `pensee_soir` (« À méditer ») vit au niveau HAUT, une chaîne et non
        une phase : on l'ignore ici, seuls miroir/geste sont comparés."""
        if "miroir" in e:
            return e["miroir"] + " " + e["geste"]
        return " ".join(v["miroir"] + " " + v["geste"]
                        for v in e.values() if isinstance(v, dict))

    rapides = ("lune", "mercure", "venus", "soleil", "mars")
    classes = ("conjonction", "carre-opposition", "sextile-trigone")
    cibles = ("soleil", "lune", "venus", "mars", "mercure",
             "saturne", "jupiter", "asc", "mc",
             "uranus", "neptune", "pluton")
    fautifs = []
    for r in rapides:
        for c in classes:
            emp = {}
            for cible in cibles:
                e = precis.get(f"{r}_{c}_{cible}")
                if e:
                    emp[cible] = suites(texte_entier(e))
            for a, b in itertools.combinations(emp, 2):
                partage = len(emp[a] & emp[b])
                if partage >= 4:
                    fautifs.append((r, c, f"{a}~{b}", partage))
    fautifs.sort(key=lambda x: -x[3])
    assert not fautifs, (
        "des transits précis recopient une autre cible pour le même "
        f"déclencheur (≥ 4 suites de 8 mots) : {fautifs[:6]}"
    )


def test_les_trois_phases_ne_sont_pas_des_reformulations():
    """Le piège du système approche/cœur/retrait : trois paraphrases du même
    constat. Le lecteur a l'impression de relire le même texte sur plusieurs
    jours — exactement le radotage qu'Align refuse.

    La charte (voir CHARTE.md) impose que chaque phase change d'OBJET : approche
    = un signal, cœur = un vécu, retrait = un résidu. Ce test n'attrape que la
    reformulation LITTÉRALE (suites de 8 mots partagées entre deux phases d'une
    même entrée) — la reformulation sémantique, elle, se joue à la rédaction.
    Mais sans ce filet, le pire cas (les trois phases quasi identiques) passe
    inaperçu, comme l'ancien tic.

    Seuil : moins de 2 suites de 8 mots communes entre deux phases d'une même
    entrée. L'état sain est à 0.
    """
    import re
    import itertools
    precis = charger()["transits"]["transits_precis"]

    def suites(texte, n=8):
        mots = re.findall(r"\w+", texte.lower())
        return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}

    fautifs = []
    for cle, e in precis.items():
        if "miroir" in e:          # entrée à texte unique : une seule phase
            continue
        phases = {p: suites(e[p]["miroir"] + " " + e[p]["geste"])
                  for p in ("approche", "coeur", "retrait")}
        for a, b in itertools.combinations(phases, 2):
            partage = len(phases[a] & phases[b])
            if partage >= 2:
                fautifs.append((cle, f"{a}~{b}", partage))
    fautifs.sort(key=lambda x: -x[2])
    assert not fautifs, (
        "des entrées en trois phases reformulent la même chose "
        f"(≥ 2 suites de 8 mots entre deux phases) : {fautifs[:6]}. "
        f"Chaque phase doit changer d'objet — signal / vécu / résidu "
        f"(voir CHARTE.md), pas paraphraser la précédente."
    )


def test_les_arcanes_collent_a_la_table_golden_dawn():
    """Le corpus et le moteur doivent parler des mêmes cartes.

    Et la table doit rester celle de Mathers : les arcanes 0, 12 et 20 portent
    des ÉLÉMENTS. Le système Case (Uranus/Neptune/Pluton), affiché sur tout le
    web, détruirait la structure 12 signes + 7 planètes + 3 éléments qui fait
    tenir le croisement.
    """
    from moteur.tarot import ARCANES, GOLDEN_DAWN
    arcanes = charger()["arcanes"]["arcanes"]
    for numero, entree in arcanes.items():
        n = int(numero)
        assert entree["nom"] == ARCANES[n], f"arcane {n} : nom divergent"
        # Comparaison insensible à la casse et aux accents : le corpus écrit
        # « Vénus » (du texte, destiné à l'œil), le moteur « venus » (une clé
        # technique). Exiger l'identité stricte confondrait deux registres.
        attendu = GOLDEN_DAWN[n][1]
        assert _plier(entree["correspondance"]) == _plier(attendu), (
            f"arcane {n} : corpus dit {entree['correspondance']!r}, "
            f"moteur dit {attendu!r}"
        )
    for n in (0, 12, 20):
        assert arcanes[str(n)]["correspondance"] in ("Air", "Eau", "Feu")


def test_chaque_arcane_a_ses_deux_lectures():
    """Résonance ET tension : sans les deux, le croisement ne sert à rien."""
    for numero, e in charger()["arcanes"]["arcanes"].items():
        assert e.get("en_resonance"), f"arcane {numero} sans lecture en résonance"
        assert e.get("en_tension"), f"arcane {numero} sans lecture en tension"
