"""Numérologie déterministe — calculs pythagoriciens classiques.

⚖️ CADRE JURIDIQUE, tenu strictement
Les CALCULS sont de la numérologie pythagoricienne classique : libres depuis
des siècles, ni brevetables ni protégeables. Castells le dit elle-même en note
de bas de page : « à quelques exceptions près, ce sont les mêmes calculs
mathématiques » — son apport est l'interprétation, pas l'arithmétique.

En revanche « Numérologie Stratégique® » est une marque INPI, et son
vocabulaire (l'arbre, racines/tronc/écorce/branches/feuilles/fruits,
« triangle fondamental », « dynamique de vie », « mémoire familiale») lui
appartient. Align a donc **sa propre métaphore** — celle de l'orientation,
accordée à son nom : un cap, une voix, un foyer, un élan.

Ce module ne contient AUCUN texte d'interprétation : que des nombres.
Les textes vivent dans data/corpus/, rédigés en original.

Convention des accents : TRANSPARENTE (é = e, ç = c). C'est ce que fait la
source de référence, et l'app le PUBLIE — aucune app française ne documente
la sienne, alors que les deux conventions concurrentes donnent des résultats
différents pour le même nom.
"""
import unicodedata

# --------------------------------------------------------------- primitives

MAITRES = frozenset({11, 22, 33})

# Seconde famille de sous-nombres, distincte des maîtres. Align les appelle
# « héritages » : ce qui a été reçu, non ce qui est dû. Le cadrage compte —
# ce ne sont ni des dettes ni des fautes, mais de la matière de travail.
HERITAGES = frozenset({13, 14, 16, 19})

REMARQUABLES = MAITRES | HERITAGES

VOYELLES = frozenset("AEIOUY")   # Y est traité comme voyelle


def plier(texte):
    """Normalise un nom : majuscules, sans diacritiques, lettres seules.

    La convention transparente en une fonction : la décomposition NFD sépare
    la lettre de son accent, on jette les accents (catégorie Mn) et É redevient
    E, donc 5.

    L'apostrophe tombe ici avec le reste de la ponctuation : « D'Artagnan »
    devient DARTAGNAN, un seul mot. Voir CONVENTIONS.
    """
    texte = unicodedata.normalize("NFD", texte.upper())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return "".join(c for c in texte if c.isalpha())


# Les particules FONT PARTIE DU NOM et comptent dans le calcul — elles ne
# sont pas jetées. C'est ce qu'impose la philosophie de la source, qui exige
# **l'état civil exact** (tous les prénoms + le nom de naissance) : or « de
# Gaulle » EST l'état civil, « de » compris.
#
# Elles ne forment pas une unité à part pour autant : une particule n'est pas
# un nom, elle en introduit un. Elle se SOUDE donc au mot qui suit — l'unité
# de calcul est le nom civil entier (« de Gaulle » → DEGAULLE), exactement
# comme la source raisonne en « prénoms » et « noms », pas en mots.
#
# Joli effet de bord : la règle rejoint celle de l'apostrophe. « D'Artagnan »
# → DARTAGNAN et « de Gaulle » → DEGAULLE relèvent du même geste — une
# particule élidée ou espacée se comporte pareil. Une seule idée, deux graphies.
PARTICULES = frozenset({
    "DE", "DU", "DES", "D", "LE", "LA", "LES", "L",
    "VAN", "VON", "DER", "DEN", "TEN", "TER",
    "DI", "DA", "DAL", "DEL", "DELLA", "DEGLI", "DEI",
    "DO", "DOS", "DAS", "Y", "AF", "AV", "ZU",
})


def normaliser_noms(noms):
    """Prépare les unités de calcul : plie chaque mot, soude les particules.

    Le découpage en unités est la variable la plus sensible de tout
    l'algorithme — les routes réduisent PAR unité, et ce sont les sous-nombres
    qui portent les maîtres et les héritages, c'est-à-dire toute la valeur de
    la méthode. D'où trois règles nettes plutôt qu'une intuition :

      - le trait d'union NE fusionne PAS (**spécifié** par la source) : les
        deux prénoms restent deux unités dont on additionne les totaux ;
      - l'apostrophe n'est pas un séparateur : D'Artagnan → DARTAGNAN ;
      - une particule se SOUDE au nom qu'elle introduit : de Gaulle → DEGAULLE.

    Les deux dernières sont des choix d'Align (la source se tait), tranchés et
    publiés plutôt que subis. Elles gardent toutes les lettres de l'état civil :
    rien n'est jeté, tout compte.

    Une particule en fin de liste n'a rien à souder (saisie malformée) : elle
    reste alors une unité, plutôt que de faire tomber l'app.
    """
    mots = [m for m in (plier(n) for n in noms) if m]
    unites, en_attente = [], ""
    for mot in mots:
        if mot in PARTICULES:
            en_attente += mot          # « de » puis « La » se cumulent
            continue
        unites.append(en_attente + mot)
        en_attente = ""
    if en_attente:                      # particule orpheline en fin de saisie
        unites.append(en_attente)
    return unites


def valeur_lettre(lettre):
    """Table pythagoricienne : A=1…I=9, J=1…R=9, S=1…Z=8."""
    return (ord(lettre) - ord("A")) % 9 + 1


def somme_lettres(mot, filtre=None):
    return sum(valeur_lettre(c) for c in plier(mot)
               if filtre is None or (c in VOYELLES) == filtre)


def pas(n):
    """UN pas de somme des chiffres. Ne protège RIEN.

    Distinction subtile et essentielle : certains nombres se calculent par un
    pas unique sans protection des maîtres, d'autres par réduction totale.
    Les mélanger casse les exemples de référence — vérifié dans les deux sens.
    """
    return sum(int(c) for c in str(n)) if n > 9 else n


def reduire_total(n):
    """Réduction jusqu'à un chiffre. Aucun sous-nombre conservé."""
    while n > 9:
        n = pas(n)
    return n


def reduire(n, garder=REMARQUABLES):
    """Réduction qui S'ARRÊTE sur un sous-nombre remarquable."""
    while n > 9:
        if n in garder:
            return n
        n = pas(n)
    return n


def _lire(routes, unites=None):
    """La règle de sélection — le cœur de la méthode.

    Un nombre se calcule par plusieurs ROUTES qui donnent toutes le même
    réduit mais peuvent révéler des sous-nombres différents. Alors :

      - un MAÎTRE trouvé sur n'importe quelle route DEVIENT la valeur ;
      - un HÉRITAGE ne devient JAMAIS la valeur : c'est un drapeau annexe.

    Cette asymétrie n'est pas un détail : la confondre change les portraits
    de référence (un cap porteur d'un 19 vaut 1, pas 19).

    ⚠️ `unites` = les valeurs BRUTES par mot (prénom, nom). Un héritage peut
    n'exister QUE là, sans apparaître dans aucun total : chez « Marie Lise
    Dupont », les voyelles de LISE valent 14, mais le total (38 → 11 → 2) ne
    le contient nulle part. Ne scanner que les totaux le raterait — et c'est
    l'apport le plus fin de la méthode qu'on perdrait. Un maître dans un mot,
    en revanche, ne promeut PAS la valeur : seules les routes le font.
    """
    base = reduire_total(routes[0])
    maitres = [r for r in routes if r in MAITRES]
    heritages = sorted({r for r in routes if r in HERITAGES})

    locaux = []
    for etiquette, valeur in (unites or []):
        if valeur in HERITAGES:
            locaux.append({"valeur": valeur, "ou": etiquette})

    return {
        "valeur": maitres[0] if maitres else base,
        "base": base,
        "maitre": maitres[0] if maitres else None,
        "heritages": sorted(set(heritages) | {h["valeur"] for h in locaux}),
        "heritages_de_routes": heritages,
        "heritages_locaux": locaux,
    }


# ------------------------------------------------------- les nombres d'Align

def cap(jour, mois, annee):
    """LE CAP — la direction de fond (chemin de vie). Depuis la date seule."""
    return _lire([
        reduire(jour + mois + annee),                                   # verticale
        reduire(sum(int(c) for c in f"{jour}{mois}{annee}")),           # horizontale
        reduire(reduire_total(jour) + reduire_total(mois) + reduire_total(annee)),
    ])


def _etiquettes(noms):
    """Nomme chaque mot pour situer un héritage local.

    La position pondère : premier prénom et nom de famille pèsent plus que les
    prénoms suivants. « Un héritage dans ton deuxième prénom » est une
    information ; « tu as un héritage 14 » n'en est pas une.
    """
    etiq = []
    for i, n in enumerate(noms):
        if i == len(noms) - 1:
            etiq.append("nom de famille")
        elif i == 0:
            etiq.append("premier prénom")
        else:
            etiq.append(f"{i + 1}e prénom")
    return etiq


def voix(noms):
    """LA VOIX — ce qui s'exprime au-dehors. Depuis toutes les lettres.

    ⚠️ La route 2 applique UN pas par unité, SANS protéger les maîtres. Une
    réduction protectrice casserait les exemples de référence : un mot valant
    22 doit y compter pour 4.
    """
    noms = normaliser_noms(noms)
    totaux = [somme_lettres(n) for n in noms]
    return _lire(
        [
            reduire(sum(totaux)),
            reduire(sum(pas(t) for t in totaux)),
            reduire(sum(reduire_total(t) for t in totaux)),
        ],
        unites=list(zip(_etiquettes(noms), totaux)),
    )


def foyer(jour, mois):
    """LE FOYER — le centre intérieur, ce vers quoi ça tend."""
    return _lire([
        reduire(jour + mois),
        reduire(reduire_total(jour) + reduire_total(mois)),
    ])


def elan(v_cap, v_voix, v_foyer):
    """L'ÉLAN — l'énergie de l'ensemble.

    Se calcule sur les VALEURS RETENUES (maîtres non réduits, héritages déjà
    ramenés à leur base), puis une seconde passe cherche un maître de plus.
    Seuls les maîtres se conservent ici — pas les héritages.
    """
    return _lire([
        reduire(v_cap + v_voix + v_foyer, garder=MAITRES),
        reduire(reduire_total(v_cap) + reduire_total(v_voix) + reduire_total(v_foyer),
                garder=MAITRES),
    ])


def reflet(jour):
    """LE REFLET — l'image qu'on renvoie. Réduction totale : aucun maître."""
    return reduire_total(jour)


def geste(noms):
    """LE GESTE — la manière d'agir. Un COMPTAGE de lettres, pas une somme."""
    n = sum(1 for nom in normaliser_noms(noms) for c in nom if valeur_lettre(c) == 1)
    return reduire_total(n) if n > 9 else n


def _agreger(noms, voyelles):
    """⚠️ Ici la route 2 réduit TOTALEMENT par unité (contrairement à `voix`).

    Incohérence de la source, pas de notre implémentation : l'harmoniser dans
    un sens ou dans l'autre casse des exemples de référence. On la reproduit
    telle quelle et on la signale.
    """
    noms = normaliser_noms(noms)
    totaux = [somme_lettres(n, filtre=voyelles) for n in noms]
    return _lire(
        [
            reduire(sum(totaux)),
            reduire(sum(reduire_total(t) for t in totaux)),
        ],
        unites=list(zip(_etiquettes(noms), totaux)),
    )


def source(noms):
    """LA SOURCE — ce qui nourrit affectivement. Les voyelles."""
    return _agreger(noms, voyelles=True)


def trace(noms):
    """LA TRACE — ce qu'on cherche à accomplir. Les consonnes."""
    return _agreger(noms, voyelles=False)


def frictions(jour, mois, annee):
    """LES FRICTIONS — les écarts à travailler (les « défis »).

    Écarts absolus entre les composantes réduites. Un écart nul donne 9, pas 0.
    ⚠️ Les DEUX PREMIÈRES sont les majeures — divergence assumée avec la
    tradition anglo-saxonne, qui majore la troisième et garde le 0.
    """
    j, m, a = reduire_total(jour), reduire_total(mois), reduire_total(annee)
    z = lambda x: 9 if x == 0 else x
    f1, f2 = z(abs(j - m)), z(abs(j - a))
    return {
        "majeures": [f1, f2],
        "toutes": [f1, f2, z(abs(f1 - f2)), z(abs(m - a))],
    }


def appuis(noms):
    """LES APPUIS et LES CHANTIERS — la grille des 9 qualités.

    Se construit sur les LETTRES SEULES : la date n'y entre pas. (C'est ce qui
    la rend complémentaire d'une grille bâtie sur la date, et non concurrente.)

    Une case vide n'est pas un manque à déplorer : c'est un chantier ouvert.
    Le cadrage est le produit.
    """
    lettres = "".join(normaliser_noms(noms))
    compte = {v: 0 for v in range(1, 10)}
    for c in lettres:
        compte[valeur_lettre(c)] += 1
    return {
        "compte": compte,
        "appuis": sorted(v for v, n in compte.items() if n > 0),
        "chantiers": sorted(v for v, n in compte.items() if n == 0),
    }


# Périodes où un chantier se fait sentir. IMPRIMÉ dans la source pour 4→9 ;
# 1→3 ne sont pas donnés, on ne les invente pas.
PERIODES_CHANTIERS = {
    4: (27, 36), 5: (36, 45), 6: (45, 54),
    7: (54, 63), 8: (63, 72), 9: (72, 81),
}


def annee_personnelle(jour, mois, annee_courante):
    """L'année en cours, dans un cycle de 9 ans. Bascule au 1er JANVIER.

    La source ne spécifie pas la bascule ; « l'année en cours » y pointe
    lexicalement vers le civil, et l'autre source de numérologie l'affirme
    explicitement. Align suit donc l'ANNÉE CIVILE (décidé le 2026-07-16, après
    une première version calée sur l'anniversaire — moins bien appuyée).

    ⚠️ Deux horloges cohabitent dans Align, et c'est VOULU :
      - la couche numérologique bat sur le CALENDRIER (ici, et la carte de
        l'année) ;
      - la couche astrologique bat sur l'ANNIVERSAIRE (le retour solaire, où
        le Soleil retrouve son degré natal — de l'astronomie, pas une
        convention).
    Elles ne se contredisent pas : ce sont des tables INDÉPENDANTES qu'on
    additionne, jamais un produit. Les forcer à s'aligner serait une élégance
    de façade, payée d'une infidélité aux deux sources.
    """
    return reduire_total(reduire_total(jour + mois) + annee_courante)


def annee_universelle(annee_courante):
    """L'année du MONDE — le climat collectif, pour tout le monde à la fois.

    2026 → 2+0+2+6 = 10 → 1. Toute la planète est en « année universelle 1 »
    cette année-là. C'est le « World Year Number » de la numérologie classique.

    ⚠️ Rien ne croisait ça avec l'année personnelle jusqu'ici, alors que le lien
    est FORT et exact : l'année personnelle EST l'année universelle, colorée par
    ta date de naissance. Voir `decalage_au_monde`.
    """
    return reduire_total(annee_courante)


def decalage_au_monde(jour, mois_naissance):
    """De combien de crans tu cours devant (ou derrière) ton époque.

    🔑 Une vérité que le calcul révèle et qui n'est pas évidente. L'année
    personnelle vaut `reduire(jour+mois) + année`, l'année universelle vaut
    `reduire(année)`. Donc :

        année personnelle = reduire( (jour+mois réduit) + année universelle )

    L'écart entre les deux ne dépend QUE de ta date de naissance — pas de
    l'année. Il est donc CONSTANT toute ta vie : tu gardes le même temps
    d'avance (ou de retard) sur le collectif, année après année.

    Renvoie 1 à 9 : le nombre de crans dont ton année personnelle devance
    l'année universelle. 9 signifie « toujours en phase avec le monde » (car
    ajouter 9 ne change rien à une racine numérique).
    """
    d = reduire_total(jour + mois_naissance) % 9
    return d or 9


def mois_personnel(jour, mois_naissance, annee_courante, mois_courant):
    """Le mois en cours, dans l'année personnelle. Cycle de 9 mois.

    ⚠️ ORIGINE, dite franchement : **ni Phillips ni Castells ne documentent le
    mois personnel.** Phillips ne l'a pas du tout (zéro occurrence sur ses
    72 000 mots), et Castells n'a aucun module prévisionnel — sa seule phrase
    porte sur l'année. La formule ci-dessous vient de la **numérologie
    pythagoricienne classique**, où elle est standard et unanime :

        mois personnel = année personnelle + numéro du mois, réduit

    C'est donc un **choix d'Align**, appuyé sur la tradition commune mais sur
    aucune de ses deux sources de référence. Publié comme tel dans « Les
    Règles » — la même honnêteté que pour les accents et les particules.

    Cohérence : l'année bascule au 1er janvier, le mois au 1er du mois. Les
    deux horloges numérologiques battent sur le calendrier ; l'astrologie, elle,
    garde la sienne (le retour solaire est de l'astronomie).

    Le cycle de 9 mois ne s'aligne pas sur les 12 du calendrier — c'est voulu,
    et c'est ce qui fait qu'un même mois ne revient pas au même endroit d'une
    année à l'autre.
    """
    return reduire_total(annee_personnelle(jour, mois_naissance, annee_courante)
                         + mois_courant)


def portrait(prenoms_nom, jour, mois, annee):
    """Tous les nombres d'une personne. Aucun texte : que des nombres."""
    noms = list(prenoms_nom)
    c, v, f = cap(jour, mois, annee), voix(noms), foyer(jour, mois)
    return {
        "cap": c,
        "voix": v,
        "foyer": f,
        "elan": elan(c["valeur"], v["valeur"], f["valeur"]),
        "reflet": reflet(jour),
        "geste": geste(noms),
        "source": source(noms),
        "trace": trace(noms),
        "frictions": frictions(jour, mois, annee),
        "appuis": appuis(noms),
        # Un héritage se lit aussi dans le jour et l'année de naissance.
        "heritages_naissance": sorted(
            {n for n in (jour, reduire(annee, garder=HERITAGES)) if n in HERITAGES}
        ),
    }
