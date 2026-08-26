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
    """0 à 21 → 00.jpg à 21.jpg ; 22 ≡ 0 (Le Mat ferme la boucle)."""
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
