"""Les rappels côté serveur — l'API de réglage, la composition du contenu, la
condition « déjà ouvert » du matin, et le payload du lien profond.

La planification pure (quel créneau, à quelle minute) est verrouillée dans
`test_notifications.py`. Ici on teste le CÂBLAGE : ce que l'API accepte, ce que
le scheduler compose à partir du vrai calcul du Jour, et ce qui part vraiment
dans la notification (le type de carte, pour que le clic ouvre la bonne).
"""
import datetime as dt
import json

import pytest

import app as application
from moteur import notifications as N

LIEU = 8672912  # Trois-Pistoles
SAISIE = {
    "id": "jean-test", "prenoms_nom": ["Jean", "Test"],
    "annee": 1975, "mois": 7, "jour": 16, "heure": 14, "minute": 30,
    "lieu_id": LIEU,
}
DATE = dt.date(2026, 7, 16)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", tmp_path / "profils")
    application.PROFILS.mkdir()
    monkeypatch.setattr(N, "DOSSIER", tmp_path / "notif")
    monkeypatch.setattr(application, "ACTIVITE_PATH", tmp_path / "activite.jsonl")
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        c.post("/api/profil", json=SAISIE)
        yield c


# ------------------------------------------------- API de réglage

def test_reglage_aller_retour(client):
    r = client.put("/api/notifications/jean-test", json={
        "creneaux": {
            "matin": {"actif": True, "heure": 7},
            "midi": {"actif": True, "heure": 12, "domaine": "metier"},
            "soir": {"actif": False, "heure": 21},
        },
        "subscription": {"endpoint": "https://push.example/abc"},
        "fuseau_notif": "America/Toronto",
    })
    assert r.status_code == 200
    assert r.get_json()["abonne"] is True

    lu = client.get("/api/notifications/jean-test").get_json()
    assert lu["abonne"] is True
    assert lu["creneaux"]["matin"] == {"actif": True, "heure": 7}
    assert lu["creneaux"]["midi"]["domaine"] == "metier"
    assert lu["creneaux"]["soir"]["actif"] is False


def test_reglage_borne_les_entrees_invalides(client):
    """Une heure hors 0-23 ou un domaine inconnu ne doit jamais s'écrire tel
    quel — on retombe sur le défaut plutôt que de stocker un état impossible."""
    client.put("/api/notifications/jean-test", json={
        "creneaux": {
            "matin": {"actif": True, "heure": 99},          # hors bornes
            "midi": {"actif": True, "heure": 12, "domaine": "pas-un-domaine"},
            "soir": {"actif": True, "heure": 20},
        },
        "subscription": {"endpoint": "x"},
        "fuseau_notif": "America/Toronto",
    })
    lu = client.get("/api/notifications/jean-test").get_json()
    assert lu["creneaux"]["matin"]["heure"] == N.HEURE_DEFAUT["matin"]  # borne rejetée
    assert lu["creneaux"]["midi"]["domaine"] == N.DOMAINE_DEFAUT       # domaine rejeté


def test_tout_desactiver_efface_l_abonnement(client):
    client.put("/api/notifications/jean-test", json={
        "creneaux": {"matin": {"actif": True, "heure": 8}},
        "subscription": {"endpoint": "x"}, "fuseau_notif": "America/Toronto",
    })
    r = client.put("/api/notifications/jean-test", json={
        "creneaux": {
            "matin": {"actif": False, "heure": 8},
            "midi": {"actif": False, "heure": 12},
            "soir": {"actif": False, "heure": 20},
        },
    })
    assert r.get_json()["abonne"] is False


# ------------------------------------------------- composition du contenu

def test_contenu_matin_ouvre_la_carte_du_jour(client):
    profil = application._charger("jean-test")
    contenu = application._contenu_rappel(profil, DATE, "matin", N.defaut())
    assert contenu is not None
    assert contenu["carte"] == "jour"
    assert contenu["titre"] == "Ton jour"
    assert contenu["corps"]                       # un vrai texte, pas vide


def test_contenu_midi_porte_le_domaine_choisi(client):
    profil = application._charger("jean-test")
    prefs = N.defaut()
    prefs["creneaux"]["midi"]["domaine"] = "metier"
    contenu = application._contenu_rappel(profil, DATE, "midi", prefs)
    assert contenu is not None
    assert contenu["carte"] == "domaine"
    assert contenu["domaine"] == "metier"         # ce que le clic devra rouvrir
    assert contenu["corps"]


def test_contenu_soir_est_une_pensee_a_mediter(client):
    """La pensée du soir dépend du transit du jour : si le corpus en a une, elle
    doit sortir taguée « mediter » ; sinon on saute (jamais de rappel vide)."""
    profil = application._charger("jean-test")
    contenu = application._contenu_rappel(profil, DATE, "soir", N.defaut())
    if contenu is not None:
        assert contenu["carte"] == "mediter"
        assert contenu["titre"] == "À méditer"


# ------------------------------------------------- « déjà ouvert » (matin)

def test_a_ouvert_aujourdhui_lit_le_journal(client, monkeypatch):
    # Une ouverture aujourd'hui, à l'heure locale de Toronto.
    zone = application.TEMPS.fuseau("America/Toronto")
    aujourdhui_local = dt.datetime(DATE.year, DATE.month, DATE.day, 9, 0, tzinfo=zone)
    ligne = {"t": aujourdhui_local.astimezone(dt.timezone.utc).isoformat(),
             "profil": "jean-test", "type": "ouverture", "vue": "jour"}
    application.ACTIVITE_PATH.write_text(json.dumps(ligne) + "\n", encoding="utf-8")

    assert application._a_ouvert_aujourdhui("jean-test", DATE, "America/Toronto") is True
    assert application._a_ouvert_aujourdhui("jean-test", DATE + dt.timedelta(days=1),
                                            "America/Toronto") is False
    assert application._a_ouvert_aujourdhui("quelqu-un-dautre", DATE,
                                            "America/Toronto") is False


# ------------------------------------------------- payload du lien profond

def test_le_push_transporte_le_type_de_carte(monkeypatch):
    """Le clic sur la notification doit pouvoir ouvrir la bonne carte : `carte`
    (et `domaine` pour le midi) DOIVENT voyager dans le payload."""
    captures = {}
    monkeypatch.setattr(application, "_vapid", lambda: object())
    monkeypatch.setattr(application, "webpush",
                        lambda **kw: captures.update(kw))
    contenu = {"titre": "Le fil du jour", "corps": "un texte",
               "carte": "domaine", "domaine": "metier"}
    application._envoyer_push("jean-test", {"endpoint": "x"}, contenu)
    envoye = json.loads(captures["data"])
    assert envoye["carte"] == "domaine"
    assert envoye["domaine"] == "metier"
    assert envoye["corps"] == "un texte"
    assert envoye["titre"] == "Le fil du jour"
    assert envoye["profil"] == "jean-test"        # pour rouvrir le bon compte au clic
