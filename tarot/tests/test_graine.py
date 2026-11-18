"""La graine d'un tirage doit survivre à un aller-retour JavaScript (2026-11-17).

JavaScript lit les nombres JSON en flottants : au-delà de 2^53, la graine
revenait arrondie et « rejouer la même donne » (reprise d'un tirage en cours,
tirage gardé dans le journal, ?graine=) donnait un AUTRE mélange.
"""
import app

LIMITE_JS = 2 ** 53


def test_les_graines_tirees_tiennent_dans_un_flottant():
    client = app.app.test_client()
    for _ in range(40):
        g = client.get("/api/tirage?mode=3").get_json()["graine"]
        assert 0 <= g < LIMITE_JS


def test_une_graine_rejoue_exactement_la_meme_donne():
    client = app.app.test_client()
    for mode in (1, 3, 5, 10, 11):
        a = client.get(f"/api/tirage?mode={mode}&graine=987654321").get_json()
        b = client.get(f"/api/tirage?mode={mode}&graine=987654321").get_json()
        assert [c["id"] for c in a["cartes"]] == [c["id"] for c in b["cartes"]]


def test_une_graine_lue_par_javascript_rejoue_la_meme_donne():
    """Aller-retour par un flottant, comme le navigateur : float(g) == g."""
    client = app.app.test_client()
    d = client.get("/api/tirage?mode=11").get_json()
    g = d["graine"]
    assert int(float(g)) == g
    r = client.get(f"/api/tirage?mode=11&graine={int(float(g))}").get_json()
    assert [c["id"] for c in r["cartes"]] == [c["id"] for c in d["cartes"]]
