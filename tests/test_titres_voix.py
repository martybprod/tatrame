"""Le titre du jour nomme la voix élue — numéro, lune — sans toucher au ciel.

Piste (b) du message du jour : quand le routeur élit la bascule numérologique
ou un pic lunaire, le titre doit NOMMER cette voix (sous-titre explicite :
« Année personnelle 9 », « Nouvelle Lune »), même logique que le chinois qui
nomme les animaux. Zéro régression : un jour-ciel reste un jour-ciel, mot
pour mot — et tout est rejouable (fonction pure de naissance + date).
"""
import datetime as dt

import app as application

NB = {"jour": 16, "mois": 7, "annee": 1975}
TRANSIT = {"miroir": "Le ciel du jour parle d'un pas à faire.",
           "geste": "Fais ce premier pas, petit."}


def _titre(force, date, ecart, n=NB):
    titre, routage = application._titre_du_jour(
        {"transit": TRANSIT}, force, date, ecart, n)
    return titre, routage


# ------------------------------------------------------------- cas unitaires

def test_la_bascule_d_annee_prend_le_titre_et_est_nommee():
    titre, routage = _titre(0.2, dt.date(2026, 1, 2), 90.0)
    assert routage["choix"]["voix"] == "numero"
    assert titre["source"] == "numero"
    num = application.annee_personnelle(NB["jour"], NB["mois"], 2026)
    assert titre["sous_titre"] == f"Année personnelle {num}"
    assert titre["miroir"] and titre["geste"]


def test_le_pic_lunaire_prend_le_titre_et_est_nomme():
    titre, routage = _titre(0.2, dt.date(2026, 7, 17), 0.0)
    assert routage["choix"]["voix"] == "lune"
    assert titre["source"] == "lune"
    assert titre["sous_titre"] == "Nouvelle Lune"
    titre_pleine, routage_pleine = _titre(0.2, dt.date(2026, 7, 17), 180.0)
    assert routage_pleine["choix"]["voix"] == "lune"
    assert titre_pleine["sous_titre"] == "Pleine Lune"


def test_un_jour_ciel_reste_un_jour_ciel_mot_pour_mot():
    titre, routage = _titre(0.9, dt.date(2026, 7, 17), 90.0)
    assert routage["choix"]["voix"] == "ciel"
    assert titre["source"] == "ciel"
    assert titre["miroir"] == TRANSIT["miroir"]
    assert titre["geste"] == TRANSIT["geste"]
    assert "sous_titre" not in titre


def test_rejouable_a_l_identique():
    a = _titre(0.2, dt.date(2026, 1, 2), 0.0)
    b = _titre(0.2, dt.date(2026, 1, 2), 0.0)
    assert a == b


# --------------------------------------------- simulation : une année réelle

def test_simulation_une_annee_la_voix_elue_est_toujours_nommee():
    """N jours × naissances × saillances : dès que la voix élue est numéro ou
    lune, le titre la mentionne ; sinon le ciel garde son titre, inchangé."""
    naissances = [NB, {"jour": 3, "mois": 11, "annee": 1990}]
    ecarts = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
    forces = [0.0, 0.3, 0.6, 0.9]
    elues = set()
    jour = dt.date(2026, 1, 1)
    while jour.year == 2026:
        for n in naissances:
            for ecart in ecarts:
                for force in forces:
                    titre, routage = _titre(force, jour, ecart, n)
                    voix = routage["choix"]["voix"]
                    elues.add(voix)
                    if voix in ("numero", "lune"):
                        assert titre["source"] == voix
                        assert titre["sous_titre"]
                        assert titre["miroir"] and titre["geste"]
                        if voix == "numero":
                            quel = routage["choix"]["details"]["numero"]["quel"]
                            attendu = ("Année personnelle" if quel == "annee"
                                       else "Mois personnel")
                            assert titre["sous_titre"].startswith(attendu)
                        else:
                            assert titre["sous_titre"] in ("Nouvelle Lune",
                                                           "Pleine Lune")
                    elif voix == "chinois":
                        # Voix branchée avant la piste (b). Le repli ciel reste
                        # possible quand le corpus de la relation manque —
                        # comportement pré-existant et documenté.
                        assert titre["source"] in ("chinois", "ciel")
                        if titre["source"] == "chinois":
                            assert titre["miroir"] and titre["sous_titre"]
                        else:
                            assert titre["miroir"] == TRANSIT["miroir"]
                    else:
                        assert voix == "ciel"
                        assert titre["source"] == "ciel"
                        assert titre["miroir"] == TRANSIT["miroir"]
        jour += dt.timedelta(days=3)
    # La simulation traverse bien les voix : la piste (b) est réellement
    # exercée (numero ET lune gagnent au moins une fois), pas court-circuitée.
    assert {"ciel", "numero", "lune", "chinois"} <= elues
