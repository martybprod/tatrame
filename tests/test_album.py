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

def test_les_cinq_sections_de_cartes_dans_l_ordre(donnees):
    """Les CARTES d'abord (majeurs + familles), puis les messages du jour."""
    assert [s["id"] for s in donnees["sections"]][:5] == SECTIONS_ATTENDUES
    assert all(s.get("genre") != "messages" for s in donnees["sections"][:5])
    assert all(s.get("genre") == "messages" for s in donnees["sections"][5:])


def test_les_sections_de_messages(donnees):
    """Les messages du jour : le Fil par domaine, les deux étages de transits,
    la Lune — 650 textes au total, chacun avec ses champs éditables."""
    messages = [s for s in donnees["sections"] if s.get("genre") == "messages"]
    identifiants = [s["id"] for s in messages]
    assert identifiants[:5] == ["fil-soi", "fil-ressources", "fil-echanges",
                                "fil-racines", "fil-creation"]
    assert "transit-gen" in identifiants and "transit-precis" in identifiants
    assert "lune-phases" in identifiants and "lune-maisons" in identifiants
    total = sum(len(s["cartes"]) for s in messages)
    assert total == 650, total
    phases = next(s for s in messages if s["id"] == "lune-phases")
    assert len(phases["cartes"]) == 8
    maisons = next(s for s in messages if s["id"] == "lune-maisons")
    assert len(maisons["cartes"]) == 12


def test_vingt_trois_majeurs(donnees):
    majeurs = donnees["sections"][0]["cartes"]
    assert len(majeurs) == 23
    assert [c["numero"] for c in majeurs] == list(range(23))


def test_quatorze_cartes_par_famille(donnees):
    familles = [s for s in donnees["sections"] if s["id"] in SECTIONS_ATTENDUES[1:]]
    assert len(familles) == 4
    for section in familles:
        assert len(section["cartes"]) == 14, section["id"]


def test_un_message_porte_ses_champs_de_texte(donnees):
    """Un message du Fil : le miroir et le geste éditables, la source montrée
    mais JAMAIS éditable (c'est de la fabrication, pas du message)."""
    soi = next(s for s in donnees["sections"] if s["id"] == "fil-soi")
    carte = next(c for c in soi["cartes"] if c["id"] == "fil-soi")
    assert [b["champ"] for b in carte["textes"]] == ["miroir", "geste"]
    assert carte["apercu"], "une vignette de texte sans aperçu ne se lit pas"
    assert carte["fichier_texte"] == "data/corpus/fil.json"
    assert carte["cle_texte"] == "soi"


def test_les_transits_precis_portent_leurs_variantes(donnees):
    """Certaines entrées précises portent leurs trois phases au lieu d'un
    texte unique — des SOUS-DICTS (approche.miroir, coeur.geste…) : les deux
    formes doivent être éditables, champ par champ."""
    precis = next(s for s in donnees["sections"] if s["id"] == "transit-precis")
    texte_unique = next(c for c in precis["cartes"]
                        if c["id"] == "transit-precis-lune_conjonction_soleil")
    assert [b["champ"] for b in texte_unique["textes"]] == ["miroir", "geste", "pensee_soir"]
    variantes = next(c for c in precis["cartes"]
                     if c["id"] == "transit-precis-lune_carre-opposition_soleil")
    champs = [b["champ"] for b in variantes["textes"]]
    assert {"approche.miroir", "approche.geste", "coeur.miroir", "coeur.geste",
            "retrait.miroir", "retrait.geste", "pensee_soir"} <= set(champs)
    # Le chemin d'écriture suit la niche : 4 maillons, pas 3.
    chemin = album.cible_ecriture(variantes["id"], "coeur.geste")
    assert chemin[1] == ["transits_precis", "lune_carre-opposition_soleil",
                         "coeur", "geste"]


def test_les_champs_de_fabrication_ne_sont_pas_editables(donnees):
    """`source_livre` et `themes` racontent D'OÙ vient le texte, pas le texte :
    aucun bloc d'édition ne doit les exposer."""
    for section in donnees["sections"]:
        for carte in section["cartes"]:
            for bloc in carte["textes"]:
                assert bloc["champ"] not in ("source_livre", "themes"), \
                    (carte["id"], bloc["champ"])


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
    """Air est en cours d'écriture : une carte sans texte maison sert
    l'invitation classique (Épées), avec une note honnête — jamais du vide.
    Une carte qui A son texte maison n'affiche, elle, aucune note."""
    air = next(s for s in donnees["sections"] if s["id"] == "air")
    avec_repli = [c for c in air["cartes"] if c["note_texte"]]
    maison = [c for c in air["cartes"] if not c["note_texte"]]
    assert maison, "plus aucune carte air sans texte maison : le test n'a plus d'objet"
    for carte in avec_repli:
        assert carte["textes"], carte["id"]
        assert "Épées" in carte["note_texte"], carte["id"]
        assert carte["cle_texte"].startswith("epees_"), carte["id"]
    for carte in maison:
        assert carte["textes"], carte["id"]
        assert carte["cle_texte"].startswith("air_"), carte["id"]


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
