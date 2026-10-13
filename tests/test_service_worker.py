"""Le service worker — un seul contrat, mais il a coûté cher.

`page_swr` met TOUJOURS la page en cache sous la clé `/`, et cette clé contient
le corps de la DERNIÈRE navigation, quelle qu'elle soit. Servir cette entrée
pour n'importe quelle autre adresse rend donc la mauvaise page : Martin ouvre
`/admin/commentaires` et reçoit l'album mis en cache à l'instant d'avant —
formulaire de connexion jamais vu, donc aucun bouton d'édition (vécu le
2026-10-12).

Le contrat, désormais : **seule la racine `/` passe par le cache ; toute autre
navigation va au réseau.** Ce test le verrouille en lisant le fichier, faute de
pouvoir exécuter un service worker sous pytest.
"""
import pathlib
import re

SW = pathlib.Path(__file__).resolve().parents[1] / "static" / "sw.js"


def _source():
    return SW.read_text(encoding="utf-8")


def _bloc_navigation(js):
    """Le bout de code qui traite les navigations (avant la branche /static/)."""
    debut = js.index('if (event.request.mode === "navigate")')
    fin = js.index('if (url.pathname.startsWith("/static/"))', debut)
    return js[debut:fin]


def test_seule_la_racine_passe_par_le_cache_de_page():
    bloc = _bloc_navigation(_source())
    assert 'url.pathname === "/"' in bloc, \
        "la navigation doit être filtrée sur la racine, sinon le worker rend " \
        "le corps de la dernière navigation à la mauvaise adresse"
    assert bloc.count("page_swr(event)") == 1


def test_le_cache_de_page_est_bien_SOUS_la_condition():
    """L'ordre compte : si `respondWith(page_swr(...))` sortait de la
    condition, le filtre ne servirait à rien."""
    bloc = _bloc_navigation(_source())
    condition = bloc.index('url.pathname === "/"')
    appel = bloc.index("page_swr(event)")
    assert condition < appel


def test_les_autres_pages_ne_sont_pas_detournees():
    """Aucune autre adresse ne doit être associée au cache de page."""
    bloc = _bloc_navigation(_source())
    for page in ("/album", "/admin", "/static"):
        assert ('pathname === "%s"' % page) not in bloc


def test_le_worker_est_servi_a_la_racine():
    """Un service worker ne contrôle que sa propre portée : servi sous
    /static/, il ne verrait jamais l'app. La route doit rester `/sw.js`."""
    app_py = (SW.parent.parent / "app.py").read_text(encoding="utf-8")
    assert re.search(r'@app\.get\("/sw\.js"\)', app_py)
