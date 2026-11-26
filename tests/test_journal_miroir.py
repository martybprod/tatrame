"""Le message complet derrière une note du journal (2026-11-25).

Une note prise depuis un crayon « En action » porte le geste dans
source_texte — et, depuis ce jour, le MIROIR qui le portait dans
source_miroir ; sinon la note rouverte ne montrait que l'action, sans le
message d'origine (retour bêta). Le Jour est déterministe (même profil +
même date = mêmes textes) : le rattrapage completer_journal_retro() recalcule
la journée de chaque vieille note et regreffe son miroir — idempotent,
jamais à côté (une journée introuvable laisse la note telle quelle).
"""
import datetime as dt
import json

import pytest

import app as application

NAISSANCE = dict(annee=1975, mois=7, jour=16, heure=14, minute=30,
                 lat=48.1266, lon=-69.1697, fuseau="America/Toronto")
JOUR_NOTE = dt.date(2026, 7, 16)


@pytest.fixture
def espace(tmp_path, monkeypatch):
    for nom in ("journal", "profils"):
        (tmp_path / nom).mkdir()
    monkeypatch.setattr(application, "JOURNAL", tmp_path / "journal")
    monkeypatch.setattr(application, "PROFILS", tmp_path / "profils")
    return tmp_path


@pytest.fixture
def client(espace):
    application.app.config["TESTING"] = True
    with application.app.test_client() as c:
        yield c


def _poster(client, **corps):
    return client.post("/api/journal/jean-journal", json=corps)


# ------------------------------------------------------- à la prise de note

def test_une_note_garde_son_miroir(client):
    e = _poster(client, texte="Je retiens ça.", source_nom="Aujourd'hui",
                source_texte="Écris une phrase…",
                source_miroir="Tu changes de chapitre aujourd'hui…").get_json()
    assert e["source_texte"] == "Écris une phrase…"
    assert e["source_miroir"] == "Tu changes de chapitre aujourd'hui…"


def test_sans_source_pas_de_miroir(client):
    e = _poster(client, texte="Ma note").get_json()
    assert "source_miroir" not in e


def test_un_miroir_sans_source_ne_veut_rien_dire(client):
    e = _poster(client, texte="Ma note", source_miroir="Orphelin").get_json()
    assert "source_miroir" not in e


def test_le_miroir_est_cappe(client):
    e = _poster(client, texte="x", source_nom="Aujourd'hui", source_texte="g",
                source_miroir="m" * (application.MAX_JOURNAL_SOURCE_TEXTE + 500)).get_json()
    assert len(e["source_miroir"]) == application.MAX_JOURNAL_SOURCE_TEXTE


# ------------------------------------------------------- le rattrapage rétro

def _ecrire_profil(profils, pid="jean-journal"):
    profil = {"id": pid, "complet": True, "fold": 0,
              "prenoms_nom": "Marie Claire Tremblay",
              "naissance": dict(NAISSANCE)}
    (profils / f"{pid}.json").write_text(json.dumps(profil), encoding="utf-8")
    return profil


def _bloc_du_jour(profil):
    """Un bloc réel (miroir, geste) du jour de la note — la vérité du calcul."""
    d = application._jour_pour(profil, JOUR_NOTE)
    candidats = [d.get("titre") or {}]
    candidats += [b for b in (d.get("textes") or {}).values() if isinstance(b, dict)]
    for b in candidats:
        if b.get("miroir") and b.get("geste"):
            return b
    raise AssertionError("aucun bloc miroir+geste ce jour-là : test impossible")


def test_le_rattrapage_regreffe_le_miroir(espace):
    profil = _ecrire_profil(espace / "profils")
    bloc = _bloc_du_jour(profil)
    note = {"id": "a1", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": bloc["geste"]}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 1
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == bloc["miroir"]


def test_le_rattrapage_se_dit_par_le_geste_quand_le_nom_a_varie(espace):
    """Les libellés d'angle ont varié au fil des versions : une note dont le
    nom d'origine n'existe plus est retrouvée par son geste, pas abandonnée."""
    profil = _ecrire_profil(espace / "profils")
    d = application._jour_pour(profil, JOUR_NOTE)
    fil = (d.get("textes") or {}).get("fil") or {}
    if not (fil.get("miroir") and fil.get("geste")):
        pytest.skip("le fil du jour n'a pas de bloc miroir+geste ce jour-là")
    note = {"id": "a2", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Famille", "source_texte": fil["geste"]}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 1
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == fil["miroir"]


def test_le_rattrapage_trouve_aussi_les_voix_du_titre(espace):
    """Le routage a changé depuis août (mur des voix, bascule numérologique) :
    une note prise sur le titre d'ALORS se retrouve par son geste dans la voix
    elle-même (chinois, numéro, lune), même si le titre recalculé dit autre chose."""
    profil = _ecrire_profil(espace / "profils")
    n = profil["naissance"]
    sc = application.chinois.saillance_chinoise(n["annee"], n["mois"], n["jour"], JOUR_NOTE)
    candidats = [
        f"{sc['relation']}_{application.chinois.ELEMENT_SLUG[sc['element_du_jour']]}",
        sc["relation"],
    ]
    rel = next((application.corpus.lire("chinois_detail", "relations", c)
                for c in candidats
                if isinstance(application.corpus.lire("chinois_detail", "relations", c), dict)
                and application.corpus.lire("chinois_detail", "relations", c).get("geste")
                and application.corpus.lire("chinois_detail", "relations", c).get("miroir")), None)
    if rel is None:
        pytest.skip("pas de texte chinois miroir+geste ce jour-là")
    note = {"id": "a8", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": rel["geste"]}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 1
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == rel["miroir"]


def test_le_rattrapage_est_idempotent(espace):
    profil = _ecrire_profil(espace / "profils")
    bloc = _bloc_du_jour(profil)
    note = {"id": "a3", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": bloc["geste"]}
    chemin = espace / "journal" / "jean-journal.json"
    chemin.write_text(json.dumps([note], ensure_ascii=False), encoding="utf-8")
    application.completer_journal_retro()
    avant = chemin.read_text(encoding="utf-8")
    assert application.completer_journal_retro() == 0
    assert chemin.read_text(encoding="utf-8") == avant


def test_une_note_deja_completee_n_est_pas_touchee(espace):
    _ecrire_profil(espace / "profils")
    note = {"id": "a4", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": "n'importe quel geste",
            "source_miroir": "Déjà là."}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 0
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == "Déjà là."


def test_une_note_de_tirage_n_est_pas_touchee(espace):
    """Le tirage gardé porte déjà son instantané lisible (son résumé) : rien à
    regreffer — et surtout pas un miroir du jour, qui n'a rien à voir."""
    _ecrire_profil(espace / "profils")
    note = {"id": "a5", "texte": "Tirage gardé.", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Tarot · La croix", "source_texte": "1. ce qui couvre — Confiance",
            "tirage": {"v": 1, "tirage": "croix", "mode": 11, "graine": 42}}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 0
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert "source_miroir" not in entree


def test_une_geste_introuvable_laisse_la_note_telle_quelle(espace):
    """Corpus changé, geste disparu : on ne devine pas — la note reste intacte."""
    _ecrire_profil(espace / "profils")
    note = {"id": "a6", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": "Un geste qui n'existe plus."}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 0
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert "source_miroir" not in entree


def test_un_profil_inconnu_laisse_ses_notes_intactes(espace):
    note = {"id": "a7", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": "Peu importe."}
    (espace / "journal" / "profil-efface.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 0
    entree = json.loads(
        (espace / "journal" / "profil-efface.json").read_text(encoding="utf-8"))[0]
    assert "source_miroir" not in entree


def test_un_geste_retire_du_corpus_est_dans_le_registre(espace, monkeypatch):
    """Le geste a été reformulé depuis la note : il n'existe plus dans aucun
    bloc du Jour — le registre (outils/registre_gestes.py, généré depuis
    l'histoire du corpus) garde sa dernière paire geste → miroir connue."""
    _ecrire_profil(espace / "profils")
    monkeypatch.setattr(application, "_REGISTRE_GESTES_RETIRES", {
        "Choisis aujourd'hui, entre deux options d'argent, celle qui te laisse le plus léger.":
            {"miroir": "L'argent demandait sa part de décision ce mois-ci.",
             "table": "data/corpus/fil.json"},
    })
    note = {"id": "a9", "texte": "Ma note", "cree_le": "2026-09-10T09:30:00-04:00",
            "source_nom": "Famille",
            "source_texte": "Choisis aujourd'hui, entre deux options d'argent, celle qui te laisse le plus léger."}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 1
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == "L'argent demandait sa part de décision ce mois-ci."


def test_le_rattrapage_trouve_aussi_les_domaines_d_explorer(espace):
    """La personne choisit SON domaine (Explorer) : chaque domaine a SA
    résolution du jour, différente du fil du jour. Une note prise sur
    « Mots » doit retrouver l'entrée du domaine Mots, pas celle du ciel."""
    profil = _ecrire_profil(espace / "profils")
    d = application._jour_pour(profil, JOUR_NOTE)
    j = d["jour"]
    fil = (d.get("textes") or {}).get("fil") or {}
    choisi = None
    for slug, label in application.DOMAINE_LABELS.items():
        for cle in application.J._cles_fil_domaine(slug, j.get("dominante"), j.get("phase")):
            texte = application.corpus.lire("fil", cle)
            if texte and texte.get("miroir") and texte.get("geste") \
                    and texte.get("geste") != fil.get("geste"):
                choisi = (label, texte)
                break
        if choisi:
            break
    if not choisi:
        pytest.skip("aucun domaine distinct du fil du jour ce jour-là")
    label, texte = choisi
    note = {"id": "a10", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": label, "source_texte": texte["geste"]}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    assert application.completer_journal_retro() == 1
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == texte["miroir"]


def test_le_registre_reel_est_lisible():
    """Le registre embarqué : chaque geste retiré porte un miroir, sinon il
    n'aurait pas sa place dedans (le rattrapage n'en tirerait rien)."""
    for geste, info in application._REGISTRE_GESTES_RETIRES.items():
        assert isinstance(info, dict) and info.get("miroir"), geste[:50]


# ------------------------------------------------------- la page d'admin

def test_la_page_admin_du_journal_exige_le_mot_de_passe(client):
    assert client.get("/admin/journal").status_code == 403
    # une relance anonyme ne passe pas non plus
    r = client.post("/admin/journal")
    assert r.status_code == 403


def test_la_page_admin_affiche_l_etat_des_notes(client, espace, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", espace / "profils")
    monkeypatch.setattr(application, "JOURNAL", espace / "journal")
    with client.session_transaction() as sess:
        sess["admin_ok"] = True
    _ecrire_profil(espace / "profils")
    notes = [
        {"id": "b1", "texte": "Une", "cree_le": "2026-07-16T09:30:00-04:00",
         "source_nom": "Aujourd'hui", "source_texte": "un geste", "source_miroir": "un miroir"},
        {"id": "b2", "texte": "Deux", "cree_le": "2026-07-15T09:30:00-04:00",
         "source_nom": "Aujourd'hui", "source_texte": "un geste perdu"},
    ]
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps(notes, ensure_ascii=False), encoding="utf-8")
    page = client.get("/admin/journal").get_data(as_text=True)
    assert "complète" in page and "GESTE INTROUVABLE" in page
    assert "un miroir" in page and "un geste perdu" in page


def test_la_relance_d_admin_regreffe_une_note(client, espace, monkeypatch):
    monkeypatch.setattr(application, "PROFILS", espace / "profils")
    monkeypatch.setattr(application, "JOURNAL", espace / "journal")
    with client.session_transaction() as sess:
        sess["admin_ok"] = True
    profil = _ecrire_profil(espace / "profils")
    bloc = _bloc_du_jour(profil)
    note = {"id": "b3", "texte": "Ma note", "cree_le": "2026-07-16T09:30:00-04:00",
            "source_nom": "Aujourd'hui", "source_texte": bloc["geste"]}
    (espace / "journal" / "jean-journal.json").write_text(
        json.dumps([note], ensure_ascii=False), encoding="utf-8")
    r = client.post("/admin/journal")
    assert r.status_code == 302
    entree = json.loads(
        (espace / "journal" / "jean-journal.json").read_text(encoding="utf-8"))[0]
    assert entree["source_miroir"] == bloc["miroir"]
