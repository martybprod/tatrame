"""Les âges de la vie — la couche de temps la plus lente, et la plus partagée.

Trois échelles bougeaient déjà : l'année (le chapitre), le mois (la saison), le
ciel (la journée). En voici une quatrième, encore plus lente : la traversée de
la vie elle-même. Elle ne dépend QUE de l'âge, elle est donc universelle —
tout le monde vit le retour de Saturne vers 29 ans et demi, l'opposition
d'Uranus vers 42, le retour de Chiron vers 50. Rien à voir avec le thème natal :
ce sont les grands cycles des planètes lentes qui reviennent à heure fixe pour
chacun.

⚠️ Comme partout dans Align : ici on CALCULE (quel âge, quel passage), le texte
vit dans le corpus. Et le cadrage reste celui de Dryburgh — un passage n'est pas
une épreuve qu'on subit, c'est un seuil qu'on franchit.

Les bornes sont des CHOIX assumés et stables. Un astrologue les placerait au
demi-degré près ; ce qui compte pour du déterministe, c'est qu'elles ne bougent
jamais. Les fenêtres serrées (retours de Saturne, opposition d'Uranus) durent
le temps réel du transit, deux à trois ans ; les bandes larges couvrent
l'entre-deux, sans trou.
"""
import datetime as dt

# Une année julienne moyenne : le même diviseur que partout, pour que l'âge ne
# saute pas d'un jour selon les années bissextiles.
JOURS_PAR_AN = 365.2425

#: (clé, début, fin) en années. Contigu de 0 à l'infini, jamais de trou : tout
#: âge tombe dans exactement un passage. L'ordre est l'ordre de lecture.
PASSAGES = [
    ("premiere_enfance", 0.0, 7.0),
    ("enfance", 7.0, 14.0),
    ("adolescence", 14.0, 21.0),
    ("seuil_adulte", 21.0, 28.0),
    ("retour_saturne_1", 28.0, 31.0),      # Saturne revient à sa place, ~29½
    ("jeune_trentaine", 31.0, 36.0),
    ("installation", 36.0, 41.0),
    ("milieu_de_vie", 41.0, 45.0),         # opposition d'Uranus, ~42
    ("seconde_moitie", 45.0, 50.0),
    ("tournant_cinquantaine", 50.0, 52.0),  # retour de Chiron, ~50
    ("maturite", 52.0, 58.0),
    ("retour_saturne_2", 58.0, 61.0),       # second retour de Saturne, ~59
    ("autre_rythme", 61.0, 68.0),
    ("transmission", 68.0, 77.0),
    ("grand_age", 77.0, 200.0),
]


def age_en_annees(jour, mois, annee, aujourd_hui):
    """L'âge en années décimales à une date donnée.

    `aujourd_hui` est passé en paramètre, jamais lu ici : comme le reste du
    moteur, l'âge est REJOUABLE (`?date=…` redonne le même passage).
    """
    naissance = dt.date(annee, mois, jour)
    return max(0.0, (aujourd_hui - naissance).days / JOURS_PAR_AN)


def passage_de_vie(jour, mois, annee, aujourd_hui):
    """Où tu en es dans la grande traversée. Renvoie la clé de corpus.

    `position` situe dans le passage (début / milieu / fin) sans que ça change
    la clé : un texte par passage, pas trois. C'est une nuance d'affichage,
    pas une multiplication du corpus.
    """
    age = age_en_annees(jour, mois, annee, aujourd_hui)
    for cle, debut, fin in PASSAGES:
        if debut <= age < fin:
            duree = fin - debut
            avance = (age - debut) / duree if duree else 0.0
            position = ("début" if avance < 0.34
                        else "milieu" if avance < 0.67 else "fin")
            return {
                "age": age,
                "age_ans": int(age),
                "passage": cle,
                "debut": debut,
                "fin": fin,
                "position": position,
            }
    # Inatteignable (le dernier passage va jusqu'à 200), mais on ne tombe pas :
    # un trou de calcul ne doit jamais faire planter la lecture du jour.
    return None
