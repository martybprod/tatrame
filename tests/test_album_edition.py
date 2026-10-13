"""L'édition des textes depuis l'album — la SEULE écriture du corpus.

L'album est aussi un bureau d'édition : on y modifie un texte, et « Appliquer »
le réécrit dans SON fichier. Comme ça touche le disque, le contrat doit être
explicite et verrouillé :

  - chaque texte affiché sait OÙ il vit (``cible_ecriture``) ;
  - une cible inconnue arrête TOUT le lot avant la moindre écriture ;
  - on sauvegarde avant d'écrire, et le format du corpus ne bouge pas ;
  - la route refuse un visiteur qui n'est pas admin.

Les tests d'écriture tournent sur un faux corpus, isolé (rien de réel n'est
touché). Le dernier test, lui, tourne sur le VRAI corpus : c'est le filet de
couverture — tout texte que l'album montre doit pouvoir s'écrire quelque part.
"""
import json
import pathlib

import pytest

import album

RACINE = pathlib.Path(__file__).resolve().parents[1]


def _ecrire(chemin, donnees):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")


@pytest.fixture
def faux_corpus(tmp_path, monkeypatch):
    """Un corpus minimal, isolé : rien de réel n'est touché par ces tests."""
    corpus = tmp_path / "data" / "corpus"
    travail = tmp_path / "_distillation"
    _ecrire(corpus / "arcanes.json", {"arcanes": {
        "4": {"nom": "Liberté", "lecture": "Texte ancien."}}})
    _ecrire(corpus / "mineurs.json", {
        "_note": "corpus de test",
        "feu_8": {"invitation": "Invitation feu.", "comprendre": "Long feu."},
        "epees_3": {"invitation": "Invitation épées."},
        "coupes_reine": {"invitation": "Invitation coupes."},
    })
    _ecrire(travail / "corpus_mineurs_eau.json", {
        "_note": "corpus de travail",
        "eau_9": {"invitation": "Invitation eau.", "comprendre": "Long eau."}})
    monkeypatch.setattr(album, "CORPUS", corpus)
    monkeypatch.setattr(album, "DISTILLATION", travail)
    return corpus, travail


# ------------------------------------------------------------- les cibles

def test_cible_majeur(faux_corpus):
    corpus, _ = faux_corpus
    chemin, cle = album.cible_ecriture("maj-4", "lecture")
    assert chemin == corpus / "arcanes.json"
    assert cle == ["arcanes", "4", "lecture"]


def test_cible_mineure_du_corpus_de_l_app(faux_corpus):
    corpus, _ = faux_corpus
    chemin, cle = album.cible_ecriture("feu-8", "comprendre")
    assert chemin == corpus / "mineurs.json"
    assert cle == ["feu_8", "comprendre"]


def test_cible_mineure_du_corpus_de_travail(faux_corpus):
    _, travail = faux_corpus
    chemin, cle = album.cible_ecriture("eau-9", "invitation")
    assert chemin == travail / "corpus_mineurs_eau.json"
    assert cle == ["eau_9", "invitation"]


def test_famille_non_redigee_ecrit_dans_la_couleur_classique(faux_corpus):
    """Air n'est pas encore écrit : le texte AFFICHÉ est celui d'Épées, et
    c'est là — sa vraie maison — qu'on l'écrit. Sinon l'édition ne
    s'appliquerait à rien de visible."""
    corpus, _ = faux_corpus
    chemin, cle = album.cible_ecriture("air-3", "invitation")
    assert chemin == corpus / "mineurs.json"
    assert cle == ["epees_3", "invitation"]


def test_cible_inconnue_refusee(faux_corpus):
    assert album.cible_ecriture("maj-4", "nom") is None
    assert album.cible_ecriture("maj-99", "lecture") is None
    assert album.cible_ecriture("inexistant-3", "invitation") is None
    assert album.cible_ecriture("feu-8", "nom") is None


# ------------------------------------------------------------- l'écriture

def test_appliquer_ecrit_et_sauvegarde(faux_corpus):
    corpus, _ = faux_corpus
    rapport = album.appliquer(
        [{"carte": "maj-4", "champ": "lecture", "texte": "Texte neuf : éàü."}])

    donnees = json.loads((corpus / "arcanes.json").read_text(encoding="utf-8"))
    assert donnees["arcanes"]["4"]["lecture"] == "Texte neuf : éàü."
    assert donnees["arcanes"]["4"]["nom"] == "Liberté"        # rien d'autre n'a bougé

    # Format du corpus préservé : indentation 2, accents bruts, newline final.
    brut = (corpus / "arcanes.json").read_text(encoding="utf-8")
    assert brut.endswith("\n")
    assert '\n  "arcanes": {\n' in brut
    assert "éàü" in brut and "\\u00e9" not in brut

    # La sauvegarde contient l'ÉTAT D'AVANT.
    assert len(rapport) == 1
    sauvegarde = pathlib.Path(rapport[0]["sauvegarde"])
    assert sauvegarde.exists()
    ancien = json.loads(sauvegarde.read_text(encoding="utf-8"))
    assert ancien["arcanes"]["4"]["lecture"] == "Texte ancien."


def test_appliquer_un_lot_avec_cible_inconnue_n_ecrit_rien(faux_corpus):
    """Une clé inconnue arrête le lot ENTIER : jamais de demi-écriture."""
    corpus, _ = faux_corpus
    avant = (corpus / "arcanes.json").read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        album.appliquer([
            {"carte": "maj-4", "champ": "lecture", "texte": "Nouveau."},
            {"carte": "maj-4", "champ": "inexistant", "texte": "…"},
        ])
    assert (corpus / "arcanes.json").read_text(encoding="utf-8") == avant
    assert not (corpus / "_sauvegardes").exists()


def test_appliquer_refuse_un_texte_vide(faux_corpus):
    with pytest.raises(ValueError):
        album.appliquer([{"carte": "maj-4", "champ": "lecture", "texte": "   "}])


def test_appliquer_ecrit_dans_deux_fichiers_en_un_lot(faux_corpus):
    corpus, travail = faux_corpus
    rapport = album.appliquer([
        {"carte": "maj-4", "champ": "lecture", "texte": "Neuf majeur."},
        {"carte": "eau-9", "champ": "comprendre", "texte": "Neuf eau."},
    ])
    ecrits = {pathlib.Path(r["fichier"]).name for r in rapport}
    assert ecrits == {"arcanes.json", "corpus_mineurs_eau.json"}
    assert json.loads((travail / "corpus_mineurs_eau.json").read_text(
        encoding="utf-8"))["eau_9"]["comprendre"] == "Neuf eau."


def test_le_texte_ecrit_ressort_tel_quel_dans_l_album(faux_corpus):
    """Boucle complète : après écriture, l'album relit le corpus et sert le
    texte neuf — une seule ligne, sans reprise."""
    album.appliquer([{"carte": "feu-8", "champ": "invitation",
                      "texte": "Nouvelle invitation.\n\nSecond paragraphe."}])
    carte = next(c for s in album.construire_album()["sections"]
                 for c in s["cartes"] if c["id"] == "feu-8")
    bloc = next(b for b in carte["textes"] if b["champ"] == "invitation")
    assert bloc["paragraphes"] == ["Nouvelle invitation.", "Second paragraphe."]


# ------------------------------------------------------------- la route

def _client():
    import app as application
    application.app.config["TESTING"] = True
    return application.app.test_client()


def _lire_lecture_maj4(corpus):
    return json.loads((corpus / "arcanes.json").read_text(
        encoding="utf-8"))["arcanes"]["4"]["lecture"]


def test_route_refuse_un_visiteur_non_admin(faux_corpus):
    corpus, _ = faux_corpus
    with _client() as client:
        r = client.post("/api/album/enregistrer", json={"modifications": [
            {"carte": "maj-4", "champ": "lecture", "texte": "Intrusion."}]})
    assert r.status_code == 403
    assert _lire_lecture_maj4(corpus) == "Texte ancien."


def test_route_refuse_une_liste_vide(faux_corpus):
    with _client() as client:
        with client.session_transaction() as sess:
            sess["admin_ok"] = True
        r = client.post("/api/album/enregistrer", json={"modifications": []})
    assert r.status_code == 400


def test_route_ecrit_quand_on_est_admin(faux_corpus):
    corpus, _ = faux_corpus
    with _client() as client:
        with client.session_transaction() as sess:
            sess["admin_ok"] = True
        r = client.post("/api/album/enregistrer", json={"modifications": [
            {"carte": "maj-4", "champ": "lecture", "texte": "Écrit par la route."}]})
    assert r.status_code == 200
    corps = r.get_json()
    assert corps["ok"] is True
    assert corps["rapport"][0]["modifications"][0]["cle"] == "arcanes.4.lecture"
    assert _lire_lecture_maj4(corpus) == "Écrit par la route."


def test_route_explique_une_cible_inconnue(faux_corpus):
    with _client() as client:
        with client.session_transaction() as sess:
            sess["admin_ok"] = True
        r = client.post("/api/album/enregistrer", json={"modifications": [
            {"carte": "maj-4", "champ": "inexistant", "texte": "…"}]})
    assert r.status_code == 400
    assert "cible inconnue" in r.get_json()["erreur"]


# ------------------------------------------- rechargement à chaud du corpus

def test_le_corpus_se_recharge_sans_redemarrer(tmp_path):
    """Le cœur du « ça s'applique vraiment » : après une écriture, le corpus
    EN MÉMOIRE doit dire le neuf — l'app n'est jamais redémarrée pour ça."""
    from moteur.corpus import Corpus

    _ecrire(tmp_path / "essai.json", {"truc": {"a": "avant"}})
    c = Corpus(tmp_path)
    assert c.lire("essai", "truc", "a") == "avant"

    _ecrire(tmp_path / "essai.json", {"truc": {"a": "après"}})
    c.recharger()
    assert c.lire("essai", "truc", "a") == "après"


# --------------------------------------------------- filet sur le vrai corpus

def test_chaque_texte_affiche_a_une_cible():
    """Filet de couverture : TOUT texte que l'album montre doit pouvoir être
    écrit quelque part. Un bloc sans cible serait un texte qu'on édite… sans
    que rien ne s'enregistre."""
    album_data = album.construire_album()
    sans = []
    for section in album_data["sections"]:
        for carte in section["cartes"]:
            for bloc in carte["textes"]:
                if album.cible_ecriture(carte["id"], bloc["champ"]) is None:
                    sans.append((carte["id"], bloc["champ"]))
    assert not sans, f"textes sans cible d'écriture : {sans[:8]}"
