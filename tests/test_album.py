"""L'album des cartes — garde-fous de la page /album.

L'album ne réécrit rien : il lit à la source (corpus + dossier d'images) à
chaque visite. Ces tests verrouillent ce CONTRAT, pas le contenu exact (qui
doit pouvoir grandir seul : une carte produite en plus ne doit jamais casser
un test) :

  - les 5 sections attendues, dans l'ordre (majeurs puis les 4 familles) ;
  - 23 majeurs et 4 × 14 mineures — la structure, pas les textes ;
  - TOUTE carte porte un texte (au pire l'invitation classique en repli) ;
  - une URL d'image n'est posée QUE si le fichier existe vraiment ;
  - la page répond 200 et se reconstruit depuis les fichiers réels.
"""
import json
import pathlib

import pytest

import album

RACINE = pathlib.Path(__file__).resolve().parents[1]

SECTIONS_ATTENDUES = ["majeurs", "feu", "eau", "air", "terre"]


@pytest.fixture(scope="module")
def donnees():
    return album.construire_album()


def _toutes(donnees):
    return [c for s in donnees["sections"] for c in s["cartes"]]


# ------------------------------------------------------------- structure

def test_les_cinq_sections_dans_l_ordre(donnees):
    assert [s["id"] for s in donnees["sections"]] == SECTIONS_ATTENDUES


def test_vingt_trois_majeurs(donnees):
    majeurs = donnees["sections"][0]["cartes"]
    assert len(majeurs) == 23
    assert [c["numero"] for c in majeurs] == list(range(23))


def test_quatorze_cartes_par_famille(donnees):
    for section in donnees["sections"][1:]:
        assert len(section["cartes"]) == 14, section["id"]


def test_chaque_carte_a_un_nom(donnees):
    if not donnees["source_noms"]:
        pytest.skip("noms_cartes.json absent — noms non disponibles")
    sans_nom = [c["id"] for c in _toutes(donnees) if not c["nom"].strip()]
    assert not sans_nom, f"cartes sans nom : {sans_nom}"


# ----------------------------------------------------------------- textes

def test_toute_carte_a_un_texte(donnees):
    sans = [c["id"] for c in _toutes(donnees) if not c["textes"]]
    assert not sans, f"cartes sans aucun texte : {sans}"


def test_repli_sur_le_texte_classique_quand_la_famille_n_est_pas_redigee(donnees):
    """Air n'a pas encore son texte : la carte doit tout de même servir
    l'invitation classique (Épées), avec une note honnête — jamais du vide."""
    air = next(s for s in donnees["sections"] if s["id"] == "air")
    for carte in air["cartes"]:
        assert carte["textes"], carte["id"]
        assert carte["note_texte"], carte["id"]
        assert "Épées" in carte["note_texte"]


def test_texte_de_la_famille_quand_il_existe(donnees):
    """Feu a son texte : pas de note de repli, et le texte vient de feu_*."""
    feu = next(s for s in donnees["sections"] if s["id"] == "feu")
    for carte in feu["cartes"]:
        assert carte["textes"], carte["id"]
        assert carte["note_texte"] == "", carte["id"]


# ----------------------------------------------------------------- images

def test_url_image_seulement_si_le_fichier_existe(donnees):
    """Contrat « jamais d'image cassée » : l'album ne pose une URL que pour un
    fichier réellement présent sur le disque."""
    for carte in _toutes(donnees):
        for url in (carte["image"], carte["mini"]):
            if url is None:
                continue
            chemin = RACINE / url.lstrip("/")
            assert chemin.exists(), f"{carte['id']} -> {url} annoncé mais absent"


def test_les_majeurs_ont_tous_leur_image(donnees):
    majeurs = donnees["sections"][0]["cartes"]
    assert all(c["image"] for c in majeurs)


# ------------------------------------------------------------- la page

def test_page_album_repond_200():
    import app as application
    application.app.config["TESTING"] = True
    with application.app.test_client() as client:
        r = client.get("/album")
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    assert "L’album des cartes" in html
    for section in SECTIONS_ATTENDUES:
        assert f'id="s-{section}"' in html


def test_album_est_serialisable_en_json(donnees):
    """La page embarque l'album en JSON pour la lecture au clic : il doit
    rester sérialisable tel quel (pas d'objet non sérialisable caché)."""
    json.dumps(donnees)
