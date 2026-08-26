"""L'axe des nœuds lunaires — la couche « but de vie », version Align.

📐 L'IDÉE (libre)
Les deux nœuds de la Lune, opposés à 180°, dessinent un axe : le nœud SUD
(d'où l'on vient — l'acquis, les automatismes) et le nœud NORD (où l'on va —
ce qu'on est venu apprendre). Align lit cet axe dans ses 48 sous-périodes.
La structure est réutilisable ; les 48 « voies » nommées et décrites du livre
sont de l'expression protégée — Align n'en reprend rien et écrira la sienne.

⚠️ Align calcule le nœud ASCENDANT (nord) dans `theme["corps"]["noeud_moyen"]`
(voir ephemerides.noeud_moyen). Le nord est donc la DESTINATION ; le sud est
son opposé (nord + 180°). Ce module ne fait que calculer — aucun texte.
"""
from moteur import periodes
from moteur.theme import signe_de


def axe(theme):
    """L'axe sud→nord d'un thème : d'où l'on vient, où l'on va."""
    nord_lon = theme["corps"]["noeud_moyen"]["lon"] % 360.0
    sud_lon = (nord_lon + 180.0) % 360.0
    return {
        "sud": {"lon": sud_lon, **signe_de(sud_lon),
                "periode": periodes.periode_de(sud_lon)},
        "nord": {"lon": nord_lon, **signe_de(nord_lon),
                 "periode": periodes.periode_de(nord_lon)},
        # Clé de traçabilité : la paire de sous-périodes qui définit la voie.
        "cle": f"{periodes.periode_de(sud_lon)['cle']}__{periodes.periode_de(nord_lon)['cle']}",
    }
