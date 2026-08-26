"""Le routeur du titre — quelle voix mérite la grosse place aujourd'hui.

Trois échelles de temps, plus le ciel du jour, cohabitent déjà à l'écran. Mais
UN seul message doit être en tête, sinon ce n'est plus un conseil, c'est une
liste. Jusqu'ici ce titre venait toujours du ciel (le transit dominant). Le
routeur généralise ça : chaque discipline propose une VOIX avec une SAILLANCE
0-1, et la plus forte prend la tête. Le reste reste affiché en contexte — le
routeur ne cache rien, il ÉLIT.

⚠️ Déterminisme : chaque saillance est une fonction pure de (date de naissance,
date du jour). Aucun tirage, aucun état. Rejouable comme tout le reste.

⚠️ Ce module NE rédige rien : il produit un choix (quelle voix) et un score.
Le texte vit dans le corpus, choisi par la voix élue.

Le calcul du ciel (la force du transit dominant) vit déjà dans `jour.py` ; ici
on ajoute les saillances qui manquaient (bascules numériques, pics lunaires) et
la règle de sélection. La voix « chinois » a sa place réservée mais reste à 0
tant que sa discipline n'est pas branchée.
"""
import datetime as dt

# Fenêtres, en jours ou en degrés. Choix ASSUMÉS et stables : un seuil qui
# bouge n'est plus déterministe. Réglés ensuite par la validation empirique.
FENETRE_ANNEE_JOURS = 5.0     # « nouvelle année » : gros événement, ~5 jours
FENETRE_MOIS_JOURS = 2.0      # « nouveau mois » : plus discret, ~2 jours
POIDS_MOIS = 0.6              # un changement de mois ne doit pas battre un transit fort
FENETRE_LUNE_DEG = 15.0       # ~1,25 jour autour de la Nouvelle / Pleine Lune exacte
POIDS_LUNE = 0.85            # un pic lunaire est notable, sans écraser un aspect dur exact

# L'ordre de départage en cas d'égalité stricte. Documenté et figé : le
# déterminisme avant l'élégance.
PRIORITE = ("ciel", "numero", "lune", "chinois")


def _clamp01(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def saillance_bascule(date):
    """La voix « numérologie » : forte juste après un basculement.

    L'année personnelle tourne le 1er janvier, le mois personnel le 1er du
    mois. Le basculement lui-même est un fait de CALENDRIER (universel) ; ce
    que devient le nombre dépend de la naissance, mais QUAND il tourne, non.
    La saillance décroît sur les quelques jours qui suivent le seuil.
    """
    jour_de_l_an = dt.date(date.year, 1, 1)
    depuis_an = (date - jour_de_l_an).days
    s_annee = _clamp01(1.0 - depuis_an / FENETRE_ANNEE_JOURS) if depuis_an >= 0 else 0.0

    depuis_mois = date.day - 1
    s_mois = _clamp01(1.0 - depuis_mois / FENETRE_MOIS_JOURS) * POIDS_MOIS

    quel = "annee" if s_annee >= s_mois else "mois"
    return {"score": max(s_annee, s_mois), "quel": quel}


def saillance_pic_lunaire(ecart_soleil_lune):
    """La voix « lune » : forte autour de la Nouvelle et de la Pleine Lune.

    `ecart_soleil_lune` = (Lune − Soleil) mod 360, déjà calculé par
    `jour.phase_lunaire`. La Nouvelle est à 0°, la Pleine à 180° ; on mesure la
    distance angulaire au plus proche des deux et on la convertit en saillance.
    """
    e = ecart_soleil_lune % 360.0
    dist_nouvelle = min(e, 360.0 - e)
    dist_pleine = abs(e - 180.0)
    dist = min(dist_nouvelle, dist_pleine)
    score = _clamp01(1.0 - dist / FENETRE_LUNE_DEG) * POIDS_LUNE
    quel = "nouvelle" if dist_nouvelle <= dist_pleine else "pleine"
    return {"score": score, "quel": quel}


def choisir(candidats):
    """Élire la voix du jour. `candidats` = {nom: score 0-1}.

    Renvoie le nom gagnant et son score. Départage STRICT et stable : à score
    égal, l'ordre de PRIORITE tranche, jamais un `max` au hasard sur un dict.
    """
    def rang(nom):
        return PRIORITE.index(nom) if nom in PRIORITE else len(PRIORITE)

    # tri : score décroissant, puis priorité croissante (rang petit = prioritaire)
    gagnant = min(candidats.items(), key=lambda kv: (-kv[1], rang(kv[0])))
    return {"voix": gagnant[0], "score": gagnant[1], "scores": dict(candidats)}


def router_du_jour(force_transit, date, ecart_soleil_lune, score_chinois=0.0):
    """Le point d'entrée : rassemble les saillances et élit la voix.

    `force_transit` = la force 0-1 de la dominante (déjà calculée dans jour.py).
    Les autres saillances sont calculées ici. `score_chinois` reste 0 tant que
    la discipline n'est pas branchée — la place est réservée, pas remplie.
    """
    bascule = saillance_bascule(date)
    lune = saillance_pic_lunaire(ecart_soleil_lune)
    candidats = {
        "ciel": _clamp01(force_transit or 0.0),
        "numero": bascule["score"],
        "lune": lune["score"],
        "chinois": _clamp01(score_chinois),
    }
    choix = choisir(candidats)
    choix["details"] = {"numero": bascule, "lune": lune}
    return choix
