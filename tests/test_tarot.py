"""Les cartes illustrées — un accent visuel qui suit le calcul, pas un oracle.

La doctrine d'Align (voir moteur/tarot.py) : une carte ne s'affiche que parce
qu'elle a été CALCULÉE. Ces tests verrouillent les deux choses qui pourraient
silencieusement casser l'expérience :

  1. la COHÉRENCE du mapping numéro → image (22 ≡ 0, format 00.jpg…) ;
  2. l'EXISTENCE de chaque vignette — si une image manque, c'est ICI que ça
     casse, pas à l'écran d'un utilisateur (la leçon des garde-fous image).
"""
from pathlib import Path

from moteur.tarot import url_carte, URL_DOS, carte_de_naissance, carte_de_l_annee, carte_du_jour

# La racine du projet : tests/ → parent. Les images sont servies depuis
# static/cartes/ à l'exécution ; on vérifie qu'elles existent sur le disque.
RACINE = Path(__file__).resolve().parent.parent


def test_url_carte_couvre_les_22_arcanes():
    """0 à 21 → 00.jpg à 21.jpg ; 22 ≡ 0 (Foi ferme la boucle)."""
    for n in range(22):
        assert url_carte(n) == f"/static/cartes/{n:02d}.jpg"
    assert url_carte(22) == "/static/cartes/00.jpg"


def test_url_carte_ne_sort_jamais_des_majeurs():
    """Un numéro invalide ne doit jamais produire un chemin de carte mineure."""
    for n in (-1, 23, 99):
        chemin = url_carte(n)
        assert "/static/cartes/" in chemin
        # 22≡0 mis à part, on ne promet rien pour l'hors-domaine ; on garantit
        # juste qu'on ne crashe pas et qu'on reste dans le dossier cartes.


def test_chaque_arcane_a_sa_vignette():
    """Le garde-fou image : chaque arcane 0-21 a une vraie vignette servie."""
    for n in range(22):
        p = RACINE / url_carte(n).lstrip("/")
        assert p.exists(), f"vignette manquante pour l'arcane {n} : {p}"


def test_le_dos_de_carte_existe():
    """Le dos sert à la révélation de l'arcane du jour — il doit être là."""
    assert (RACINE / URL_DOS.lstrip("/")).exists()


def test_une_carte_calculee_pointe_vers_une_vignette_valide():
    """Bout en bout : la carte de naissance (et celle de l'année) d'une vraie
    date tombe sur un fichier existant."""
    for jour, mois, annee in [(1, 1, 2000), (15, 6, 1985), (29, 2, 2000), (6, 4, 1986)]:
        for carte in (carte_de_naissance(jour, mois, annee),
                      carte_de_l_annee(jour, mois, 2026)):
            chemin = RACINE / url_carte(carte["numero"]).lstrip("/")
            assert chemin.exists(), f"carte {carte['numero']} → vignette manquante"


def test_carte_du_jour_est_deterministe():
    """Même date → même carte, toujours. Zéro hasard — c'est la thèse."""
    a = carte_du_jour(18, 7, 2026)
    b = carte_du_jour(18, 7, 2026)
    assert a == b
    assert a["numero"] in range(22)


def test_carte_du_jour_est_celle_de_la_naissance_de_la_journee():
    """La carte du jour = la carte de naissance de CETTE journée
    (même formule, appliquée à la date du jour). C'est ce qui la rend légitime."""
    assert carte_du_jour(18, 7, 2026) == carte_de_naissance(18, 7, 2026)


def test_carte_du_jour_change_selon_le_jour():
    """Sur un mois, plusieurs cartes distinctes tombent : la variété vient du
    quanti qui change, pas du hasard (et pas d'un tirage interdit)."""
    cartes = {carte_du_jour(j, 7, 2026)["numero"] for j in range(1, 31)}
    assert len(cartes) > 1, "la carte du jour doit varier dans un mois"


def test_carte_du_jour_pointe_vers_une_vignette_valide():
    """La carte calculée pour de vraies dates tombe sur une vignette existante."""
    for j, m in [(1, 1), (15, 6), (28, 2), (18, 7), (31, 12)]:
        c = carte_du_jour(j, m, 2026)
        chemin = RACINE / url_carte(c["numero"]).lstrip("/")
        assert chemin.exists(), f"carte du jour {c['numero']} → vignette manquante"


# ─────────────────────────────────────────────────────────────────────
# Le vivier + la rotation — la carte majeure PERSONNELLE du jour.
#
# Le bug que ces tests verrouillent : un rang de récence NÉGATIF (l'offset
# du jour) faisait passer « vu il y a 7 jours » avant « jamais vu »
# (sentinelle -1), et la même carte se figeait à l'écran des semaines
# durant. La sentinelle « jamais vu » doit rester la plus petite valeur.
# ─────────────────────────────────────────────────────────────────────

import datetime as dt

from moteur.tarot import ARCANES, candidats_du_jour, choisir_personnelle

# Un thème minimal, à la main : le vivier n'y lit que les longitudes natales.
THEME = {"corps": {"soleil": {"lon": 150.0}, "mars": {"lon": 150.0},
                   "lune": {"lon": 40.0}, "mercure": {"lon": 160.0},
                   "venus": {"lon": 210.0}, "jupiter": {"lon": 250.0}},
         "angles": {"asc": {"lon": 120.0}, "mc": {"lon": 30.0}}}
# Un ciel minimal : la planète transitante + la Lune (pour le candidat élément).
POSITIONS = {"soleil": 95.0, "lune": 200.0, "mars": 95.0}
DOMINANTE = {"transit": "mars", "natal": "soleil", "classe": "carre-opposition"}


def vivier(dominante=DOMINANTE):
    return candidats_du_jour(dominante, [], POSITIONS, THEME,
                             15, 6, 1980, 2026)


def test_vivier_propose_le_chapitre_et_l_origine_meme_sans_transit():
    """Un jour sans transit dominant n'est pas un jour sans carte : le
    chapitre (l'année) et l'origine (la naissance) sont toujours là."""
    causes = {x["cause"] for x in vivier(dominante=None)}
    assert {"chapitre", "origine"} <= causes


def test_vivier_candidats_sont_des_majeurs_nommes():
    """Chaque candidat est un majeur valide (0-21), nommé, avec sa cause."""
    causes_connues = {"astre", "meteo", "terrain", "potentiel",
                      "element", "chapitre", "origine"}
    for x in vivier():
        assert x["numero"] in range(22)
        assert x["nom"] == ARCANES[x["numero"]]
        assert x["cause"] in causes_connues


def test_rotation_jamais_vu_passe_avant_vu_recemment():
    """La sentinelle « jamais vu » gagne toute égalité — même contre une
    carte vue il y a longtemps. C'est le verrou anti-figeage."""
    premiere = vivier()[0]
    choice = choisir_personnelle(vivier(), {premiere["numero"]: 0})
    assert choice["cause"] != premiere["cause"]


def test_rotation_le_plus_ancien_gagne_puis_l_ordre_du_vivier():
    """Quand tout le monde a été vu, le moins récemment montré gagne ; à
    égalité, l'ordre du vivier (le plus central d'abord) — stable, jamais
    au hasard."""
    c = vivier()
    ancien = c[1]
    vus = {x["numero"]: 5 for x in c}      # tout le monde a été vu
    vus[ancien["numero"]] = 2              # …lui plus tôt que les autres
    assert choisir_personnelle(c, vus)["numero"] == ancien["numero"]
    vus_egal = {x["numero"]: 9 for x in c}
    assert choisir_personnelle(c, vus_egal)["cause"] == c[0]["cause"]


def test_rotation_sans_candidat_ne_leve_pas():
    assert choisir_personnelle([], {}) is None


def test_replay_la_carte_perso_ne_se_figere_pas(monkeypatch):
    """Le replay de la fenêtre (app) doit faire tourner les cartes — le bug
    du rang négatif laissait la même carte des semaines à l'écran. Le ciel est
    simulé (il glisse d'un jour à l'autre, comme le vrai) : seul le mécanisme
    de rotation est sous test."""
    import app as application

    def ciel_glissant(theme, date):
        # La Lune avance de ~13°/jour : le vivier change d'un jour à l'autre.
        lon_lune = (POSITIONS["lune"] + 13.0 * date.timetuple().tm_yday) % 360.0
        return {c: {"lon": (POSITIONS.get(c, 150.0) + 13.0 * date.day) % 360.0,
                    "vitesse_lon": 0.0}
                for c in ("soleil", "lune", "mars", "venus", "mercure",
                          "jupiter", "saturne")} | {"lune": {
                    "lon": lon_lune, "vitesse_lon": 0.0}}

    cles = ["soleil_conjonction_mars", "venus_carre-opposition_lune",
            "mars_conjonction_mercure", "lune_sextile-trigone_jupiter"]
    monkeypatch.setattr(application, "_dominantes_fenetre",
                        lambda theme, date, fenetre=7: {
                            o: cles[(date.day + o) % len(cles)]
                            for o in range(-fenetre, 0)})
    monkeypatch.setattr(application, "_ciel_leger", ciel_glissant)
    n = {"jour": 15, "mois": 6, "annee": 1980}

    def jour_pour(date):
        return {"dominante": DOMINANTE, "potentiel": []}

    cartes = [application._carte_perso_pour(
        THEME, dt.date(2026, 9, 1) + dt.timedelta(days=j), n,
        POSITIONS, jour_pour(dt.date(2026, 9, 1)))["numero"]
        for j in range(10)]
    assert len(set(cartes)) >= 3, "la rotation doit faire passer plusieurs cartes"
    # Et le replay est déterministe : même jour, même carte, toujours.
    assert application._carte_perso_pour(THEME, dt.date(2026, 9, 1), n,
                                         POSITIONS, jour_pour(dt.date(2026, 9, 1))) == \
           application._carte_perso_pour(THEME, dt.date(2026, 9, 1), n,
                                         POSITIONS, jour_pour(dt.date(2026, 9, 1)))
