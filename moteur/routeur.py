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

from moteur.jour import FENETRE_NON_REPETITION

# Fenêtres, en jours ou en degrés. Choix ASSUMÉS et stables : un seuil qui
# bouge n'est plus déterministe. Réglés ensuite par la validation empirique.
FENETRE_ANNEE_JOURS = 5.0     # « nouvelle année » : gros événement, ~5 jours
FENETRE_MOIS_JOURS = 2.0      # « nouveau mois » : plus discret, ~2 jours
POIDS_MOIS = 0.6              # un changement de mois ne doit pas battre un transit fort
FENETRE_LUNE_DEG = 15.0       # ~1,25 jour autour de la Nouvelle / Pleine Lune exacte
POIDS_LUNE = 0.85            # un pic lunaire est notable, sans écraser un aspect dur exact

# Le plancher du MUR DES VOIX : pour remplacer une voix évincée (son texte
# vient d'être montré), une remplaçante doit avoir assez à dire aujourd'hui.
# Sous 0,30, on est au rabais — jour 3 d'une bascule, Lune à 10° du pic — et
# le mur cède plutôt que de couronner un message hors-sol. (La seule
# saillance plus bas qui existe, 0,15 = chinois « neutre », n'a de toute
# façon pas de texte dédié : elle n'est jamais remplaçante, voir
# `_cles_texte_voix` côté app.)
PLANCHER_VOIX = 0.30

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


def choisir_voix(candidats, cles_texte, titres_recents,
                 exclusion=FENETRE_NON_REPETITION, plancher=PLANCHER_VOIX):
    """Élire la voix du titre SANS répéter un texte montré récemment.

    Même architecture que `jour.choisir_dominante`, appliquée aux voix :
      1. l'élection normale — le meilleur score, PRIORITE au partage ;
      2. LE MUR — si le texte de la voix élue a déjà été affiché dans les
         `exclusion` derniers jours, on réélit parmi les voix restantes qui
         ont un texte (clé présente), un texte neuf, et assez à dire
         (saillance ≥ plancher). Sinon le mur CÈDE : une répétition vaut
         mieux qu'un titre hors-sol.

    ⚠️ Le plancher ne pèse que sur les REMPLAÇANTES : l'élection normale
    garde son comportement historique (un pic modeste peut gagner s'il est
    le plus fort du jour). C'est le mur qui change les choses, rien d'autre.

    `candidats` = {nom: saillance 0-1}. `cles_texte` = {nom: clé du TEXTE que
    la voix afficherait} — la clé de texte, pas la voix : « annee » est un
    seul texte pour toute l'année, « mois_numeros:4 » un texte par numéro, le
    chinois se décline par relation × élément. None = la voix n'a rien à
    montrer (elle n'est jamais remplaçante). `titres_recents` = les jours
    précédents, du plus ancien au plus récent ; un jour est la liste des
    clés de texte affichées ce jour-là (le héros ET le transit, qui se voit
    même quand il ne mène pas).
    """
    choix = choisir(candidats)
    if exclusion <= 0 or not titres_recents:
        return {**choix, "mur": None}
    vus = {cle for jour in titres_recents[-exclusion:]
           for cle in (jour or []) if cle}
    elue = choix["voix"]
    if not cles_texte.get(elue) or cles_texte[elue] not in vus:
        return {**choix, "mur": None}
    remplacantes = {nom: s for nom, s in candidats.items()
                    if nom != elue
                    and cles_texte.get(nom)
                    and cles_texte[nom] not in vus
                    and s >= plancher}
    if not remplacantes:
        return {**choix, "mur": None}      # le mur cède
    nouvelle = choisir(remplacantes)
    return {"voix": nouvelle["voix"], "score": nouvelle["score"],
            "scores": dict(candidats),
            "mur": {"voix_evincee": elue, "cle": cles_texte[elue]}}


def router_du_jour(force_transit, date, ecart_soleil_lune, score_chinois=0.0,
                   cles_texte=None, titres_recents=None):
    """Le point d'entrée : rassemble les saillances et élit la voix.

    `force_transit` = la force 0-1 de la dominante (déjà calculée dans jour.py).
    Les autres saillances sont calculées ici. `score_chinois` reste 0 tant que
    la discipline n'est pas branchée — la place est réservée, pas remplie.

    Le MUR DES VOIX (paramètres `cles_texte` + `titres_recents`) empêche le
    même texte de reprendre la tête à quelques jours d'écart — même logique
    que le mur des transits dans `jour.choisir_dominante`. Sans ces deux
    paramètres (tests, calculs isolés), l'élection reste la règle historique.
    """
    bascule = saillance_bascule(date)
    lune = saillance_pic_lunaire(ecart_soleil_lune)
    candidats = {
        "ciel": _clamp01(force_transit or 0.0),
        "numero": bascule["score"],
        "lune": lune["score"],
        "chinois": _clamp01(score_chinois),
    }
    if cles_texte is not None:
        choix = choisir_voix(candidats, cles_texte, titres_recents or [])
    else:
        choix = choisir(candidats)
    choix["details"] = {"numero": bascule, "lune": lune}
    return choix
