"""La couche temps : là où se perdent les thèmes.

Ces tests n'ont pas besoin d'oracle : ce sont des FAITS historiques et
calendaires vérifiables, pas des modèles. Ils tiennent lieu de contrat.
"""
from datetime import datetime, timezone

import pytest

from moteur import temps


def test_tzdata_epingle_et_force():
    """La faille de déterminisme n°1, et son correctif.

    Sans reset_tzpath, zoneinfo lit /usr/share/zoneinfo (macOS embarquait
    2026b quand ce module a été écrit, pendant que pip fournissait 2026.3) :
    les thèmes dériveraient au gré des mises à jour du système, en silence.
    """
    import zoneinfo
    assert zoneinfo.TZPATH == (), "TZPATH doit être vide -> zoneinfo utilise le paquet pip"
    assert temps.VERSION_IANA == "2026c", (
        f"version IANA inattendue : {temps.VERSION_IANA}. "
        "Le golden a été établi sur 2026c — revalider avant de bouger."
    )


# ------------------------------------------------- Québec / Montréal

def test_quebec_1975_heure_avancee():
    """Été 1975 au Québec : heure avancée (UTC-4)."""
    utc, avis = temps.vers_utc(1975, 7, 16, 14, 30, "America/Toronto")
    assert utc == datetime(1975, 7, 16, 18, 30, tzinfo=timezone.utc)
    assert avis is None


def test_quebec_1975_fevrier_le_canada_ne_suit_pas_les_usa():
    """Le piège de 1975, et il est vicieux.

    Les États-Unis sont passés à l'heure d'été le 23 février 1975 (loi
    d'urgence sur l'énergie) ; le Canada ne l'a PAS fait et est resté à
    l'heure normale jusqu'au 27 avril. Tout raccourci « Québec = heure de
    l'Est américaine » donne une heure de trop sur cette fenêtre — laquelle
    contient le cas de référence de Martin.
    """
    utc_ca, _ = temps.vers_utc(1975, 3, 15, 10, 0, "America/Toronto")
    utc_us, _ = temps.vers_utc(1975, 3, 15, 10, 0, "America/New_York")
    assert utc_ca == datetime(1975, 3, 15, 15, 0, tzinfo=timezone.utc)   # EST
    assert utc_us == datetime(1975, 3, 15, 14, 0, tzinfo=timezone.utc)   # EDT
    assert (utc_ca - utc_us).total_seconds() == 3600


def test_bascules_1975_exactes():
    """Les dates de bascule canadiennes de 1975, au quart d'heure."""
    zone = temps.fuseau("America/Toronto")
    avant, _ = temps.vers_utc(1975, 4, 27, 1, 30, "America/Toronto")
    apres, _ = temps.vers_utc(1975, 4, 27, 3, 30, "America/Toronto")
    assert avant.hour == 6      # 01h30 EST -> 06h30 UTC
    assert apres.hour == 7      # 03h30 EDT -> 07h30 UTC
    assert temps.est_inexistante(datetime(1975, 4, 27, 2, 30), zone)


# ------------------------------------------------ ambigu / inexistant

def test_heure_ambigue_signalee_et_non_devinee():
    """Le retour à l'heure normale crée une heure vécue deux fois.

    Python renvoie silencieusement fold=0. Nous devons remonter le doute :
    une heure d'écart, c'est ~15° d'Ascendant, soit un demi-signe.
    """
    utc0, avis = temps.vers_utc(2024, 11, 3, 1, 30, "America/Toronto", fold=0)
    assert avis is not None and avis["type"] == "heure_ambigue"
    assert len(avis["choix"]) == 2

    utc1, _ = temps.vers_utc(2024, 11, 3, 1, 30, "America/Toronto", fold=1)
    assert (utc1 - utc0).total_seconds() == 3600, "les deux lectures doivent différer d'une heure"


def test_heure_inexistante_signalee():
    """Le passage à l'heure d'été escamote une heure : elle n'existe pas."""
    _, avis = temps.vers_utc(2024, 3, 10, 2, 30, "America/Toronto")
    assert avis is not None and avis["type"] == "heure_inexistante"


def test_heure_normale_sans_avis():
    """Le cas courant ne doit produire AUCUN bruit."""
    for a, m, j, h in [(1980, 5, 20, 9), (2024, 6, 15, 14), (1999, 1, 1, 0)]:
        _, avis = temps.vers_utc(a, m, j, h, 0, "Europe/Paris")
        assert avis is None, f"faux positif sur {j}/{m}/{a} {h}h"


def test_ambigu_et_inexistant_sont_disjoints():
    """Les deux prédicats ne doivent jamais être vrais ensemble.

    `est_ambigue` seul ne sait pas distinguer un trou d'un recouvrement :
    d'où la soustraction explicite dans son implémentation.
    """
    zone = temps.fuseau("America/Toronto")
    trou = datetime(2024, 3, 10, 2, 30)
    double = datetime(2024, 11, 3, 1, 30)
    assert temps.est_inexistante(trou, zone) and not temps.est_ambigue(trou, zone)
    assert temps.est_ambigue(double, zone) and not temps.est_inexistante(double, zone)


# ------------------------------------------------------------- LMT

def test_lmt_depuis_la_longitude_du_lieu():
    """1° de longitude = 240 s, calculés depuis le lieu et non depuis la zone."""
    utc = temps.utc_depuis_tsm(1880, 6, 15, 12, 0, -73.5878)   # Montréal
    ecart = (datetime(1880, 6, 15, 12, 0) - utc).total_seconds()
    assert abs(ecart - (-73.5878 * 240.0)) < 1e-6
    assert abs(ecart / 60 + 294.35) < 0.1     # ≈ -4 h 54 min


def test_lmt_evite_l_erreur_de_23_minutes_de_tzdata():
    """La raison d'être de utc_depuis_tsm().

    tzdata donne à Montréal le LMT de TORONTO (-5:17:32) au lieu du sien
    (-4:54:16) : 23 minutes d'erreur, soit ≈ 5,8° d'Ascendant.
    """
    zone = temps.fuseau("America/Montreal")
    lmt_tzdata = datetime(1880, 6, 15, 12, 0, tzinfo=zone).utcoffset().total_seconds()
    lmt_vrai = -73.5878 * 240.0
    ecart_min = abs(lmt_tzdata - lmt_vrai) / 60.0
    assert 20 < ecart_min < 26, (
        f"écart tzdata/réel attendu ~23 min, obtenu {ecart_min:.1f} min. "
        "Si ce test change, tzdata a modifié son traitement de Montréal."
    )


# --------------------------------------------- limites historiques

@pytest.mark.parametrize("annee,mois,jour,fuseau,attendu", [
    (1880, 6, 15, "America/Montreal", "temps moyen local"),
    (1950, 11, 1, "America/Montreal", "PROPRES règles"),
    (1975, 3, 15, "America/Toronto", "23 février"),
    (1941, 1, 15, "Europe/Paris", "ZONE OCCUPÉE"),
    (1943, 6, 1, "Europe/Paris", "Alsace-Moselle"),
])
def test_limites_annoncees(annee, mois, jour, fuseau, attendu):
    """Chaque limite connue doit se SIGNALER, jamais se taire."""
    avis = temps.limites_connues(annee, mois, jour, fuseau, longitude=-73.5878)
    assert any(attendu in a for a in avis), f"limite non signalée : {attendu!r} dans {avis}"


def test_france_1943_ete_hors_fenetre_de_divergence():
    """Ne pas crier au loup : l'été 1941 et 1943 ne divergent PAS.

    Les fenêtres réelles sont 1940-06-14→1941-05-04 et 1941-10-05→1942-03-09,
    plus étroites que le « 1940-44 » qu'on lit partout.
    """
    avis = temps.limites_connues(1943, 6, 1, "Europe/Paris")
    assert not any("ZONE OCCUPÉE" in a for a in avis)


def test_epoque_recente_sans_avertissement_historique():
    assert temps.limites_connues(2024, 6, 15, "America/Toronto") == []
