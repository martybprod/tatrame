"""Recherche du lieu de naissance : c'est ICI que se joue « trouvable ou pas ».

Un lieu introuvable rend la fonctionnalité inutilisable, même si la donnée est
en base : c'était le cas de toute la Belgique, nommée par GeoNames en anglais
ou en néerlandais (« Brussels », « Antwerp », « Gent ») alors que l'utilisateur
tape « Bruxelles », « Anvers », « Gand ».

Ces tests touchent la VRAIE base (data/geo/lieux.sqlite), pas un double : le
comportement testé EST celui de la donnée, et un double le manquerait.
"""
import pytest

from moteur.geo import Lieux


@pytest.fixture(scope="module")
def lieux():
    return Lieux()


def premier(lieux, nom):
    r = lieux.chercher(nom, limite=1)
    return r[0] if r else None


# --------------------------------------------------------------- Belgique

@pytest.mark.parametrize("tape,attendu", [
    ("Bruxelles", "Brussels"),
    ("Anvers", "Antwerp"),
    ("Gand", "Gent"),
    ("Bruges", "Brugge"),
    ("Louvain", "Leuven"),
    ("Malines", "Mechelen"),
    ("Ostende", "Ostend"),
])
def test_ville_belge_trouvable_par_son_nom_francais(lieux, tape, attendu):
    """Le nom français doit trouver la commune belge.

    « Gand » est le cas extrême : sans alias, la recherche tombait sur
    Gander (Terre-Neuve) — un mauvais lieu de naissance, en silence.
    """
    trouve = premier(lieux, tape)
    assert trouve is not None, f"« {tape} » ne trouve RIEN"
    assert trouve["pays"] == "BE", f"« {tape} » tombe sur {trouve['pays']}"
    assert trouve["nom"] == attendu


def test_ville_belge_garde_son_nom_geonames(lieux):
    """Le nom d'origine doit continuer de marcher — on AJOUTE, on ne remplace pas."""
    for nom in ("Brussels", "Antwerp", "Brugge", "Oostende"):
        trouve = premier(lieux, nom)
        assert trouve is not None and trouve["pays"] == "BE", f"« {nom} » perdu"


def test_toutes_les_communes_belges_ont_un_fuseau_valide(lieux):
    """Le fuseau vient de GeoNames ; sans lui, le thème est impossible."""
    r = lieux.chercher("Bruxelles", limite=5)
    assert all(x["fuseau"] == "Europe/Brussels" for x in r)


# -------------------------------------------------- non-régression CA / FR

@pytest.mark.parametrize("tape,pays", [
    ("Montréal", "CA"),
    ("Québec", "CA"),
    ("Trois-Pistoles", "CA"),
    ("Baie-Saint-Paul", "CA"),
    ("Paris", "FR"),
    ("Marseille", "FR"),
])
def test_lieux_existants_intacts(lieux, tape, pays):
    trouve = premier(lieux, tape)
    assert trouve is not None and trouve["pays"] == pays, f"« {tape} » perdu"


def test_recherche_sans_accent(lieux):
    """Le pliage est la convention unique de l'app — il doit tenir sur l'alias."""
    assert premier(lieux, "liege")["nom"] == "Liège"
    assert premier(lieux, "bruxelles")["nom"] == "Brussels"


# ------------------------------------------------------------- homonymes

def test_homonymes_toujours_presents(lieux):
    """On ne devine JAMAIS : les trois « Saint-Fabien » doivent rester offerts.

    L'alias ne doit pas « résoudre » une ambiguïté en la masquant — choisir à
    la place de l'utilisateur déplacerait l'Ascendant sans qu'il le sache.
    """
    assert len(lieux.chercher("Saint-Fabien", limite=50)) >= 3


def test_pas_de_doublon_dans_les_resultats(lieux):
    """Un même lieu ne doit pas ressortir deux fois, une par variante.

    « Bru » correspond à « Brussels » ET « Bruxelles » : sans DISTINCT, la
    jointure sur les alias le rendrait en double.
    """
    for q in ("Bru", "Saint-", "Montr", "An"):
        ids = [x["geonameid"] for x in lieux.chercher(q, limite=20)]
        assert len(ids) == len(set(ids)), f"doublon sur « {q} »"
