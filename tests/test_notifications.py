"""Les rappels du jour — la mécanique pure, sans navigateur ni scheduler réel.

Aucun test ici n'envoie de vraie notification : la livraison passe par le
centre de notifications du système, hors de portée de pytest. Ce qu'on
verrouille, c'est ce qui EST vérifiable — la sélection de contenu, le calcul
du créneau, et la persistance — pour que le job du scheduler, quand il tourne,
s'appuie sur une mécanique déjà prouvée juste.
"""
import datetime as dt

from moteur import notifications as N


# ------------------------------------------------- contenu_notification

def test_contenu_lit_le_bon_champ_selon_le_creneau():
    titre = {"source": "ciel", "miroir": "l'observation du jour", "geste": "l'action du jour"}
    assert N.contenu_notification(titre, "matin") == "l'observation du jour"
    assert N.contenu_notification(titre, "soir") == "l'action du jour"


def test_contenu_absent_ne_fabrique_jamais_un_texte():
    """Un champ manquant (aspect natal sans corpus, relation chinoise sans
    geste) doit renvoyer None — jamais une notification vide ou bancale."""
    assert N.contenu_notification({"source": "ciel", "miroir": None, "geste": None}, "matin") is None
    assert N.contenu_notification({"source": "ciel"}, "soir") is None
    assert N.contenu_notification(None, "matin") is None


# ------------------------------------------------- creneau_courant

FUSEAU = "America/Toronto"


def _instant_utc(heure_locale, minute_locale, mois=7, jour=17):
    """Un instant UTC qui correspond à cette heure locale à Toronto en été (EDT, UTC-4)."""
    return dt.datetime(2026, mois, jour, heure_locale + 4, minute_locale, tzinfo=dt.timezone.utc)


def test_creneau_pile_a_l_heure():
    assert N.creneau_courant(_instant_utc(8, 0), FUSEAU) == "matin"
    assert N.creneau_courant(_instant_utc(17, 0), FUSEAU) == "soir"


def test_creneau_dans_la_fenetre_de_tolerance():
    """Le scheduler tourne par intervalles, jamais pile à l'heure : une
    fenêtre après l'heure cible absorbe ce décalage."""
    assert N.creneau_courant(_instant_utc(8, 7), FUSEAU, tolerance_min=10) == "matin"


def test_creneau_hors_fenetre_ne_matche_rien():
    assert N.creneau_courant(_instant_utc(8, 15), FUSEAU, tolerance_min=10) is None
    assert N.creneau_courant(_instant_utc(7, 59), FUSEAU, tolerance_min=10) is None


def test_creneau_avant_l_heure_ne_declenche_jamais_en_avance():
    """Un rappel du matin ne doit jamais arriver la veille au soir à cause
    d'un mauvais calcul de fuseau."""
    assert N.creneau_courant(_instant_utc(7, 30), FUSEAU) is None


def test_creneau_sans_fuseau_ou_fuseau_invalide():
    assert N.creneau_courant(_instant_utc(8, 0), None) is None
    assert N.creneau_courant(_instant_utc(8, 0), "Pas/UnFuseau") is None


def test_date_locale_pas_la_date_utc():
    """Le jour calendaire doit venir du fuseau de l'utilisateur, pas d'UTC —
    sinon un envoi juste après minuit UTC daterait le titre du mauvais jour
    pour quelqu'un dont le fuseau est en retard sur UTC."""
    # 23h30 à Toronto (EDT, UTC-4) le 16 juillet == 03h30 UTC le 17 juillet
    instant = dt.datetime(2026, 7, 17, 3, 30, tzinfo=dt.timezone.utc)
    assert N.date_locale(instant, FUSEAU) == dt.date(2026, 7, 16)


def test_date_locale_sans_fuseau():
    assert N.date_locale(_instant_utc(8, 0), None) is None


# ------------------------------------------------- suivi d'envoi (anti-doublon)

def test_marquer_envoye_ne_mute_pas_l_original():
    """Comme le reste du moteur : une fonction renvoie une COPIE, jamais une
    mutation en place — sinon un appelant qui garde l'ancien dict se trompe."""
    prefs = dict(N.DEFAUT, dernier_envoi=dict(N.DEFAUT["dernier_envoi"]))
    maj = N.marquer_envoye(prefs, "matin", "2026-07-17")
    assert prefs["dernier_envoi"]["matin"] is None
    assert maj["dernier_envoi"]["matin"] == "2026-07-17"


def test_deja_envoye_aujourdhui():
    prefs = N.marquer_envoye(N.DEFAUT, "soir", "2026-07-17")
    assert N.deja_envoye_aujourdhui(prefs, "soir", "2026-07-17")
    assert not N.deja_envoye_aujourdhui(prefs, "soir", "2026-07-18")
    assert not N.deja_envoye_aujourdhui(prefs, "matin", "2026-07-17")


# ------------------------------------------------- persistance (fichier réel)

def test_lire_sans_fichier_renvoie_les_defauts(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    prefs = N.lire("personne-inconnue")
    assert prefs["actif"] is False
    assert prefs["subscription"] is None


def test_ecrire_puis_lire_aller_retour(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    prefs = {"actif": True, "subscription": {"endpoint": "https://push.example/abc"},
             "fuseau_notif": "America/Toronto", "dernier_envoi": {"matin": "2026-07-17", "soir": None}}
    N.ecrire("martin-boucher", prefs)
    assert N.lire("martin-boucher") == prefs
    # écriture atomique : aucun fichier .tmp ne doit rester derrière
    assert not list(tmp_path.glob("*.tmp"))


def test_profils_actifs_exige_actif_et_abonnement(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    N.ecrire("actif-et-abonne", {**N.DEFAUT, "actif": True, "subscription": {"endpoint": "x"}})
    N.ecrire("actif-sans-abonnement", {**N.DEFAUT, "actif": True, "subscription": None})
    N.ecrire("inactif", {**N.DEFAUT, "actif": False, "subscription": {"endpoint": "x"}})
    assert N.profils_actifs() == ["actif-et-abonne"]


def test_profils_actifs_sans_dossier(tmp_path, monkeypatch):
    """Avant le premier abonnement, le dossier n'existe pas encore — ne doit
    jamais faire tomber le scheduler."""
    monkeypatch.setattr(N, "DOSSIER", tmp_path / "n-existe-pas-encore")
    assert N.profils_actifs() == []
