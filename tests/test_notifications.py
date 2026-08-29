"""Les rappels du jour — la mécanique pure, sans navigateur ni scheduler réel.

Aucun test ici n'envoie de vraie notification : la livraison passe par le
centre de notifications du système, hors de portée de pytest. Ce qu'on
verrouille, c'est ce qui EST vérifiable — la planification des créneaux, la
fenêtre déterministe, la migration des anciens fichiers, et la persistance —
pour que le job du scheduler, quand il tourne, s'appuie sur une mécanique déjà
prouvée juste.
"""
import datetime as dt
import zoneinfo

from moteur import notifications as N

FUSEAU = "America/Toronto"
PROFIL = "martin-boucher"


def _instant_utc(heure_locale, minute_locale, mois=7, jour=17):
    """Un instant UTC correspondant à cette heure locale à Toronto (vraie
    conversion de fuseau — gère le décalage EDT/EST et le passage de minuit,
    contrairement à un +4 h naïf qui déborderait dès 20 h locale)."""
    local = dt.datetime(2026, mois, jour, heure_locale, minute_locale,
                        tzinfo=zoneinfo.ZoneInfo(FUSEAU))
    return local.astimezone(dt.timezone.utc)


def _prefs(**creneaux):
    """Des préférences complètes ; chaque kwarg surcharge un créneau.
    Ex. `_prefs(matin={"actif": True, "heure": 8})`."""
    p = N.defaut()
    p["fuseau_notif"] = FUSEAU
    p["subscription"] = {"endpoint": "https://push.example/abc"}
    for nom, val in creneaux.items():
        p["creneaux"][nom] = val
    return p


# ------------------------------------------------- fenêtre déterministe

def test_offset_est_deterministe():
    """Même profil, même créneau, même jour ⇒ toujours la même minute. C'est
    tout le contrat : ça respire d'un jour à l'autre, jamais d'un dé."""
    a = N.offset_minutes(PROFIL, "matin", "2026-07-17")
    b = N.offset_minutes(PROFIL, "matin", "2026-07-17")
    assert a == b


def test_offset_reste_dans_la_fenetre():
    for jour in range(1, 29):
        o = N.offset_minutes(PROFIL, "soir", f"2026-07-{jour:02d}")
        assert 0 <= o < N.FENETRE_MIN


def test_offset_bouge_selon_le_jour_et_le_creneau():
    """Deux jours différents (ou deux créneaux) ne doivent pas tomber pile à la
    même minute — sinon l'heure ne « respirerait » pas du tout."""
    jours = {N.offset_minutes(PROFIL, "matin", f"2026-07-{j:02d}") for j in range(1, 29)}
    assert len(jours) > 1  # ça varie bien d'un jour à l'autre
    assert (N.offset_minutes(PROFIL, "matin", "2026-07-17")
            != N.offset_minutes(PROFIL, "soir", "2026-07-17"))


def test_minute_cible_est_heure_plus_offset():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    attendu = 8 * 60 + N.offset_minutes(PROFIL, "matin", "2026-07-17")
    assert N.minute_cible(PROFIL, prefs, "matin", "2026-07-17") == attendu


# ------------------------------------------------- creneaux_a_envoyer

def _instant_pour_cible(prefs, creneau, date_iso="2026-07-17", retard=0):
    """L'instant UTC qui place l'horloge locale sur la minute-cible du créneau
    (+ un éventuel retard, pour simuler un tick du scheduler pas pile à l'heure)."""
    cible = N.minute_cible(PROFIL, prefs, creneau, date_iso) + retard
    return _instant_utc(cible // 60, cible % 60)


def test_creneau_actif_part_a_sa_minute_cible():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    instant = _instant_pour_cible(prefs, "matin")
    assert N.creneaux_a_envoyer(PROFIL, prefs, instant) == ["matin"]


def test_creneau_dans_la_tolerance_du_scheduler():
    """Le tick tombe quelques minutes après la cible : encore dans la fenêtre."""
    prefs = _prefs(midi={"actif": True, "heure": 12})
    instant = _instant_pour_cible(prefs, "midi", retard=7)
    assert N.creneaux_a_envoyer(PROFIL, prefs, instant, tolerance_min=10) == ["midi"]


def test_creneau_hors_fenetre_ne_part_pas():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    trop_tot = _instant_pour_cible(prefs, "matin", retard=-1)
    trop_tard = _instant_pour_cible(prefs, "matin", retard=15)
    assert N.creneaux_a_envoyer(PROFIL, prefs, trop_tot, tolerance_min=10) == []
    assert N.creneaux_a_envoyer(PROFIL, prefs, trop_tard, tolerance_min=10) == []


def test_creneau_desactive_ne_part_jamais():
    prefs = _prefs(soir={"actif": False, "heure": 20})
    instant = _instant_pour_cible(prefs, "soir")
    assert N.creneaux_a_envoyer(PROFIL, prefs, instant) == []


def test_creneau_deja_envoye_aujourdhui_ne_repart_pas():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    prefs = N.marquer_envoye(prefs, "matin", "2026-07-17")
    instant = _instant_pour_cible(prefs, "matin")
    assert N.creneaux_a_envoyer(PROFIL, prefs, instant) == []


def test_couverture_un_seul_tick_toutes_les_10_min_ne_manque_aucun_creneau():
    """La garantie qui fait tenir tout le système : quelle que soit la minute
    cible (donc quel que soit l'offset), UN tick toutes les 10 min finit
    toujours par tomber dans sa fenêtre — jamais un rappel oublié."""
    prefs = _prefs(midi={"actif": True, "heure": 12})
    cible = N.minute_cible(PROFIL, prefs, "midi", "2026-07-17")
    # On balaie une journée de ticks espacés de 10 min, phase arbitraire (à :03).
    touche = False
    for m in range(3, 24 * 60, 10):
        instant = _instant_utc(m // 60, m % 60)
        if "midi" in N.creneaux_a_envoyer(PROFIL, prefs, instant, tolerance_min=10):
            touche = True
    assert touche, f"aucun tick n'a atteint la cible {cible} — fenêtre non couverte"


def test_sans_fuseau_rien_ne_part():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    prefs["fuseau_notif"] = None
    assert N.creneaux_a_envoyer(PROFIL, prefs, _instant_utc(8, 0)) == []


def test_fuseau_invalide_rien_ne_part():
    prefs = _prefs(matin={"actif": True, "heure": 8})
    prefs["fuseau_notif"] = "Pas/UnFuseau"
    assert N.creneaux_a_envoyer(PROFIL, prefs, _instant_utc(8, 0)) == []


def test_date_locale_pas_la_date_utc():
    """Le jour calendaire doit venir du fuseau de l'utilisateur, pas d'UTC."""
    # 23h30 à Toronto (EDT, UTC-4) le 16 juillet == 03h30 UTC le 17 juillet
    instant = dt.datetime(2026, 7, 17, 3, 30, tzinfo=dt.timezone.utc)
    assert N.date_locale(instant, FUSEAU) == dt.date(2026, 7, 16)


def test_date_locale_sans_fuseau():
    assert N.date_locale(_instant_utc(8, 0), None) is None


# ------------------------------------------------- suivi d'envoi (anti-doublon)

def test_marquer_envoye_ne_mute_pas_l_original():
    prefs = N.defaut()
    maj = N.marquer_envoye(prefs, "matin", "2026-07-17")
    assert prefs["dernier_envoi"]["matin"] is None
    assert maj["dernier_envoi"]["matin"] == "2026-07-17"


def test_deja_envoye_aujourdhui():
    prefs = N.marquer_envoye(N.defaut(), "soir", "2026-07-17")
    assert N.deja_envoye_aujourdhui(prefs, "soir", "2026-07-17")
    assert not N.deja_envoye_aujourdhui(prefs, "soir", "2026-07-18")
    assert not N.deja_envoye_aujourdhui(prefs, "matin", "2026-07-17")


# ------------------------------------------------- domaine du midi

def test_domaine_midi_defaut_si_non_choisi():
    prefs = N.defaut()
    del prefs["creneaux"]["midi"]["domaine"]
    assert N.domaine_midi(prefs) == N.DOMAINE_DEFAUT


def test_domaine_midi_respecte_le_choix():
    prefs = _prefs(midi={"actif": True, "heure": 12, "domaine": "metier"})
    assert N.domaine_midi(prefs) == "metier"


# ------------------------------------------------- migration des anciens fichiers

def test_migration_ancien_format_actif_reporte_matin_et_soir(tmp_path, monkeypatch):
    """Un fichier d'AVANT (2 créneaux fixes, `actif` global) doit se lire sans
    rien perdre : l'abonnement survit, l'ancien `actif` allume matin et soir."""
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    ancien = {
        "actif": True,
        "subscription": {"endpoint": "https://push.example/vieux"},
        "fuseau_notif": FUSEAU,
        "dernier_envoi": {"matin": "2026-07-16", "soir": None},
    }
    (tmp_path / "un-ancien.json").write_text(__import__("json").dumps(ancien), encoding="utf-8")
    prefs = N.lire("un-ancien")
    assert prefs["subscription"]["endpoint"] == "https://push.example/vieux"
    assert prefs["creneaux"]["matin"]["actif"] is True
    assert prefs["creneaux"]["soir"]["actif"] is True
    assert "midi" in prefs["creneaux"]
    assert prefs["dernier_envoi"]["matin"] == "2026-07-16"
    assert prefs["dernier_envoi"]["midi"] is None  # créneau neuf, pas d'historique


def test_migration_ancien_inactif_laisse_tout_eteint(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    ancien = {"actif": False, "subscription": None, "fuseau_notif": None,
              "dernier_envoi": {"matin": None, "soir": None}}
    (tmp_path / "eteint.json").write_text(__import__("json").dumps(ancien), encoding="utf-8")
    prefs = N.lire("eteint")
    assert not any(prefs["creneaux"][c]["actif"] for c in ("matin", "soir"))


# ------------------------------------------------- persistance (fichier réel)

def test_lire_sans_fichier_renvoie_les_defauts(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    prefs = N.lire("personne-inconnue")
    assert prefs["subscription"] is None
    assert prefs["creneaux"]["matin"]["actif"] is True
    assert prefs["creneaux"]["soir"]["actif"] is False


def test_ecrire_puis_lire_aller_retour(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    prefs = _prefs(midi={"actif": True, "heure": 13, "domaine": "metier"})
    N.ecrire("martin-boucher", prefs)
    assert N.lire("martin-boucher") == prefs
    # écriture atomique : aucun fichier .tmp ne doit rester derrière
    assert not list(tmp_path.glob("*.tmp"))


def test_profils_actifs_exige_abonnement_et_un_creneau_actif(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "DOSSIER", tmp_path)
    N.ecrire("abonne-avec-creneau", _prefs(matin={"actif": True, "heure": 8}))
    tout_eteint = _prefs(matin={"actif": False, "heure": 8},
                         midi={"actif": False, "heure": 12},
                         soir={"actif": False, "heure": 20})
    N.ecrire("abonne-tout-eteint", tout_eteint)
    sans_abo = _prefs(matin={"actif": True, "heure": 8})
    sans_abo["subscription"] = None
    N.ecrire("sans-abonnement", sans_abo)
    assert N.profils_actifs() == ["abonne-avec-creneau"]


def test_profils_actifs_sans_dossier(tmp_path, monkeypatch):
    """Avant le premier abonnement, le dossier n'existe pas encore — ne doit
    jamais faire tomber le scheduler."""
    monkeypatch.setattr(N, "DOSSIER", tmp_path / "n-existe-pas-encore")
    assert N.profils_actifs() == []
