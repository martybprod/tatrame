"""Les âges de la vie — une couche de temps qui ne dépend que de l'âge.

Pas d'oracle ici : ce sont des faits calendaires. Les bornes sont un choix
éditorial, mais leur COHÉRENCE (contiguë, sans trou, rejouable) est un contrat.
"""
import datetime as dt

from moteur.ages import PASSAGES, age_en_annees, passage_de_vie

REPERE = dt.date(2026, 7, 17)


def _ne_a_l_age(age, aujourd_hui=REPERE):
    """Une date de naissance qui donne pile cet âge au repère."""
    return aujourd_hui - dt.timedelta(days=int(age * 365.2425))


def test_les_passages_couvrent_la_vie_sans_trou():
    """Contigus de 0 à l'infini : tout âge tombe dans exactement un passage."""
    assert PASSAGES[0][1] == 0.0, "le premier passage doit partir de la naissance"
    for actuel, suivant in zip(PASSAGES, PASSAGES[1:]):
        assert actuel[2] == suivant[1], "un trou (ou un chevauchement) entre deux passages"
    assert PASSAGES[-1][2] >= 120.0, "le dernier passage doit couvrir le grand âge"


def test_les_jalons_planetaires_tombent_au_bon_age():
    """Les grands rendez-vous universels, à l'âge où ils arrivent vraiment."""
    attendus = {
        29.5: "retour_saturne_1",     # premier retour de Saturne
        42.0: "milieu_de_vie",        # opposition d'Uranus
        50.5: "tournant_cinquantaine",  # retour de Chiron
        59.0: "retour_saturne_2",     # second retour de Saturne
        5.0: "premiere_enfance",
        90.0: "grand_age",
    }
    for age, cle in attendus.items():
        nais = _ne_a_l_age(age)
        r = passage_de_vie(nais.day, nais.month, nais.year, REPERE)
        assert r["passage"] == cle, f"à {age} ans, attendu {cle}, obtenu {r['passage']}"


def test_chaque_passage_est_atteignable():
    """Aucun passage-fantôme : chaque clé du moteur a un âge qui l'active."""
    vus = set()
    for cle, debut, fin in PASSAGES:
        milieu = (debut + fin) / 2 if fin < 150 else debut + 5
        nais = _ne_a_l_age(milieu)
        vus.add(passage_de_vie(nais.day, nais.month, nais.year, REPERE)["passage"])
    assert vus == {cle for cle, _, _ in PASSAGES}


def test_l_age_est_rejouable():
    """Même naissance + même date = même passage, au jour près."""
    a = passage_de_vie(6, 4, 1980, REPERE)
    b = passage_de_vie(6, 4, 1980, REPERE)
    assert a == b
    # et il avance quand la date avance
    plus_tard = passage_de_vie(6, 4, 1980, dt.date(2035, 7, 17))
    assert plus_tard["age"] > a["age"]


def test_l_age_ne_devient_jamais_negatif():
    """Une date « dans le futur » (saisie farfelue) ne casse pas la lecture."""
    assert age_en_annees(1, 1, 2100, REPERE) == 0.0
    assert passage_de_vie(1, 1, 2100, REPERE)["passage"] == "premiere_enfance"
