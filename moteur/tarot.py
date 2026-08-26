"""Cartes calculées et pont Golden Dawn — la charnière d'Align.

⚖️ CADRE JURIDIQUE, tenu strictement
Align n'utilise PAS le Tarot Zen d'Osho : ni le nom (marque UE valide,
confirmée définitivement par le Tribunal de l'UE — T-670/15, 2017), ni les
79 illustrations (© 1994 Osho International Foundation), ni les textes
d'Osho (décès 1990 → protégés jusque ~2060), ni les noms de son jeu.

Ce qui est libre, et c'est justement ce qui nous intéresse :
  - la PHILOSOPHIE « miroir du présent plutôt que prédiction » — une idée
    n'est pas protégeable ;
  - les 22 arcanes majeurs du tarot traditionnel — domaine public depuis
    des siècles ;
  - les correspondances Golden Dawn — Mathers, *Book T*, 1888.

D'où : noms traditionnels français + interprétations rédigées en original,
sous la charte éditoriale d'Align (voir data/corpus/CHARTE.md).

📐 POURQUOI CALCULER PLUTÔT QUE TIRER
Osho lui-même donne l'argument (*The Further Shore*, ch. 5) : ces outils sont
« a reading of the unconscious of the person. It has nothing much to do with
the future ». Un calcul ne prédit donc rien — il cartographie un
conditionnement hérité pour permettre de s'en défaire. Un tirage au hasard, à
l'inverse, réintroduirait la logique oraculaire qu'il rejette.

Les cartes calculées sont par ailleurs une tradition établie : *Birth Cards*
d'Angeles Arrien (1977), publiées par Mary K. Greer (*Who Are You in the
Tarot?*).
"""

# Noms traditionnels français — domaine public.
ARCANES = {
    0: "Le Mat", 1: "Le Bateleur", 2: "La Papesse", 3: "L'Impératrice",
    4: "L'Empereur", 5: "Le Pape", 6: "L'Amoureux", 7: "Le Chariot",
    8: "La Force", 9: "L'Hermite", 10: "La Roue de Fortune", 11: "La Justice",
    12: "Le Pendu", 13: "L'Arcane sans nom", 14: "Tempérance", 15: "Le Diable",
    16: "La Maison Dieu", 17: "L'Étoile", 18: "La Lune", 19: "Le Soleil",
    20: "Le Jugement", 21: "Le Monde",
}

# ⚠️ LA TABLE AUTHENTIQUE — Mathers, *Book T*, 1888.
#
# La quasi-totalité du web affiche Le Mat = Uranus, Le Pendu = Neptune,
# Le Jugement = Pluton. C'EST FAUX : c'est le système de Paul Foster Case
# (BOTA, années 1920-30), pas la Golden Dawn. La vraie table attribue des
# ÉLÉMENTS à ces trois cartes — et c'est la clé de voûte du système : les
# arcanes 0, 12 et 20 correspondent aux trois LETTRES-MÈRES hébraïques
# (Aleph, Mem, Shin). La version Case détruit cette structure.
#
# Structure : 12 signes + 7 planètes classiques + 3 éléments = 22. Exactement.
# C'est ce qui rend le croisement d'Align structurel, et non décoratif.
GOLDEN_DAWN = {
    0:  ("element", "Air"),
    1:  ("planete", "mercure"),
    2:  ("planete", "lune"),
    3:  ("planete", "venus"),
    4:  ("signe", "Bélier"),
    5:  ("signe", "Taureau"),
    6:  ("signe", "Gémeaux"),
    7:  ("signe", "Cancer"),
    8:  ("signe", "Lion"),
    9:  ("signe", "Vierge"),
    10: ("planete", "jupiter"),
    11: ("signe", "Balance"),
    12: ("element", "Eau"),
    13: ("signe", "Scorpion"),
    14: ("signe", "Sagittaire"),
    15: ("signe", "Capricorne"),
    16: ("planete", "mars"),
    17: ("signe", "Verseau"),
    18: ("signe", "Poissons"),
    19: ("planete", "soleil"),
    20: ("element", "Feu"),
    21: ("planete", "saturne"),
}

# Une famille d'arcanes partageant la même racine. Asymétrie assumée : les
# familles 1 à 4 ont trois membres, 5 à 9 seulement deux — certains portraits
# auront donc plus de matière que d'autres. C'est la structure, pas un défaut.
FAMILLES = {
    1: [1, 10, 19], 2: [2, 11, 20], 3: [3, 12, 21], 4: [4, 13, 22],
    5: [5, 14], 6: [6, 15], 7: [7, 16], 8: [8, 17], 9: [9, 18],
}


def _reduire_vers(n, plafond):
    """Somme des chiffres, itérée, jusqu'à tomber sous le plafond.

    ⚠️ PAS un modulo : 30 -> 3, pas 30 % 22 = 8. La borne d'arrêt est 22 (les
    arcanes), pas 9 (les chiffres) — c'est ce qui distingue ce calcul de la
    numérologie.
    """
    while n > plafond:
        n = sum(int(c) for c in str(n))
    return n


def _nom(n):
    """22 est équivalent à 0 : Le Mat ferme la boucle qu'il ouvre."""
    return ARCANES[0 if n == 22 else n]


def carte_de_naissance(jour, mois, annee):
    """La carte du CONDITIONNEMENT — ce avec quoi on est arrivé.

    Méthode dite « column addition » : jour + mois + année, puis réduction
    vers 22. C'est la variante majoritaire et canonique. Il en existe une
    autre (« horizontale ») qui diverge parfois ; on en choisit une et on s'y
    tient — pour une app déterministe, la cohérence EST la spécification.
    """
    n = _reduire_vers(jour + mois + annee, 22)
    return {"numero": n, "nom": _nom(n), "correspondance": GOLDEN_DAWN[0 if n == 22 else n]}


def carte_de_fond(jour, mois, annee):
    """La carte de la RACINE — la famille dont relève le conditionnement.

    Si la carte de naissance est déjà ≤ 9, les deux se confondent : le
    portrait est alors plus resserré, ce n'est pas un manque.
    """
    p = carte_de_naissance(jour, mois, annee)["numero"]
    n = p if p <= 9 else _reduire_vers(p, 9)
    return {"numero": n, "nom": _nom(n), "correspondance": GOLDEN_DAWN[n]}


def carte_de_l_annee(jour, mois, annee_courante):
    """La carte de l'année en cours. Cycle de 9 ans. Bascule au 1er JANVIER.

    Même horloge que l'année personnelle, et ce n'est pas négociable : les
    deux s'affichent SUR LE MÊME BLOC. Deux bascules différentes donneraient,
    pour quelqu'un né en juillet, « année personnelle 6 » à côté d'une carte
    calculée sur l'année d'avant — une incohérence visible à l'œil nu.

    La source (Greer) ne spécifie pas la bascule ; on suit donc la couche à
    laquelle cette carte appartient — la numérologique, qui bat sur le
    calendrier.
    """
    n = _reduire_vers(jour + mois + annee_courante, 22)
    return {"numero": n, "nom": _nom(n), "correspondance": GOLDEN_DAWN[0 if n == 22 else n]}


def carte_du_jour(quanti, mois, annee):
    """La carte du jour — la carte de naissance de CETTE journée.

    Même formule que la carte de naissance (jour + mois + année, réduit vers
    22), mais appliquée à la date du jour plutôt qu'à celle de naissance. Elle
    change donc chaque jour, est identique pour tout le monde ce jour-là, et
    reste déterministe — zéro tirage, zéro hasard.

    ⚖️ Doctrine — ce n'est PAS « le jour vient du tarot ». Le ciel reste la
    voix qui mène la journée (voir moteur/routeur.py) ; la carte du jour est
    un arcane-écho CALCULÉ qui la colorie, comme la carte de naissance
    colorie une vie et la carte de l'année un chapitre. Elle s'ADDITIONNE au
    ciel, elle ne le remplace pas.

    C'est une convention d'Align (aucune des deux sources ne calcule de carte
    quotidienne) : on prolonge la méthode de naissance à la journée, exactement
    comme la carte de l'année la prolonge à l'année. Publiée dans
    /api/conventions, au côté de « le jour vient du ciel » — les deux
    cohabitent : le ciel donne la journée, l'arcane en donne la coloration.
    """
    n = _reduire_vers(quanti + mois + annee, 22)
    return {"numero": n, "nom": _nom(n), "correspondance": GOLDEN_DAWN[0 if n == 22 else n]}


def famille(carte_fond):
    """Les arcanes qui partagent la racine — le fil du portrait."""
    return [{"numero": n, "nom": _nom(n)} for n in FAMILLES[carte_fond]]


def profil(jour, mois, annee, annee_courante=None):
    naissance = carte_de_naissance(jour, mois, annee)
    fond = carte_de_fond(jour, mois, annee)
    p = {
        "naissance": naissance,
        "fond": fond,
        "famille": famille(fond["numero"]),
        "confondues": naissance["numero"] == fond["numero"],
    }
    if annee_courante is not None:
        p["annee"] = carte_de_l_annee(jour, mois, annee_courante)
    return p


# ─────────────────────────────────────────────────────────────────────
# IMAGES — un accent visuel qui SUIT le calcul, jamais ne le remplace.
#
# Rappel du cadre : les cartes ILLUSTRNT un arcane calculé (naissance, fond,
# année). Aucun tirage au hasard — ce serait réintroduire la logique oraculaire
# que le module récuse en tête de fichier. La vignette est donc une fonction
# pure du numéro d'arcane.
#
# Source des images : Rider-Waite-Smith (1909). Œuvre de Pamela Colman Smith
# (†1951) et A. E. Waite (†1942) → domaine public en UE depuis 2022. Conforme
# au verrou juridique d'Align (rien sous copyright, commercialisable).
#
# Les arcanes MINEURS (56 cartes) ne s'affichent pas encore : ils n'ont pas de
# correspondance calculée. La voie légitime — les décanats Golden Dawn — est un
# chantier à part (voir CONCEPTION_MESSAGE_DU_JOUR.md / PROPOSITION.md).
# ─────────────────────────────────────────────────────────────────────
URL_DOS = "/static/cartes/dos.jpg"


def url_carte(numero):
    """L'URL de la vignette d'un arcane majeur.

    22 ≡ 0 : Le Mat ferme la boucle qu'il ouvre — même convention que _nom.
    Les images vivent dans static/cartes/ (servies par Flask) au format
    00.jpg … 21.jpg.
    """
    n = 0 if numero == 22 else numero
    return f"/static/cartes/{n:02d}.jpg"
