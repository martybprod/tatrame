"""Génère le fichier golden de référence à partir de l'ORACLE (swisseph).

⚠️ swisseph est un outil de DÉVELOPPEMENT UNIQUEMENT.
   Il n'est jamais importé par le moteur, jamais expédié, jamais dans
   requirements.txt. Il sert d'oracle indépendant pour valider notre
   implémentation Skyfield. Voir PROPOSITION.md §6 (verrou juridique AGPL).

Piège vérifié ici plutôt que subi : sans fichiers .se1, swisseph bascule
SILENCIEUSEMENT sur les éphémérides Moshier. On le détecte en lisant le
drapeau RETOURNÉ (et non celui demandé), et on l'inscrit dans le golden.

    python outils/generer_golden.py
"""
import json
import pathlib
import sys

import swisseph as swe

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tests.golden.cas import CAS  # noqa: E402

RACINE = pathlib.Path(__file__).resolve().parents[1]
SORTIE = RACINE / "tests" / "golden" / "attendu.json"

CORPS = [
    ("soleil", swe.SUN), ("lune", swe.MOON), ("mercure", swe.MERCURY),
    ("venus", swe.VENUS), ("mars", swe.MARS), ("jupiter", swe.JUPITER),
    ("saturne", swe.SATURN), ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE),
    ("pluton", swe.PLUTO), ("noeud_moyen", swe.MEAN_NODE),
]

SYSTEMES = [
    ("placidus", b"P"), ("porphyry", b"O"),
    ("signe_entier", b"W"), ("egal", b"E"),
]


def jd_utc(a, m, j, h, mi, s):
    return swe.julday(a, m, j, h + mi / 60 + s / 3600, swe.GREG_CAL)


def decode_moteur(retflag):
    """Quel moteur swisseph a RÉELLEMENT utilisé (pas celui demandé)."""
    if retflag < 0:
        return "erreur"
    if retflag & swe.FLG_MOSEPH:
        return "moshier"
    if retflag & swe.FLG_JPLEPH:
        return "jpl"
    if retflag & swe.FLG_SWIEPH:
        return "swieph"
    return f"inconnu({retflag})"


def main():
    swe.set_ephe_path(None)
    moteurs_vus = set()
    themes = []

    for cas in CAS:
        jd = jd_utc(*cas["utc"])
        corps = {}
        for nom, ip in CORPS:
            xx, rf = swe.calc_ut(jd, ip, swe.FLG_SWIEPH | swe.FLG_SPEED)
            moteurs_vus.add(decode_moteur(rf))
            corps[nom] = {
                "lon": xx[0],
                "lat": xx[1],
                "vitesse_lon": xx[3],
                "retrograde": xx[3] < 0,
            }

        maisons = {}
        for nom, code in SYSTEMES:
            try:
                cusps, ascmc = swe.houses_ex(jd, cas["lat"], cas["lon"], code)
            except swe.Error:
                # Constaté sur pyswisseph 2.10.3.2 : au-delà du cercle polaire,
                # Placidus est indéfini et le wrapper LÈVE au lieu de renvoyer
                # le repli Porphyry du C (il jette les cuspides déjà remplies).
                # Notre moteur doit donc faire le repli lui-même — et c'est
                # exactement ce que le golden encode ici.
                maisons[nom] = {"indefini": True}
                continue
            maisons[nom] = {
                "cuspides": list(cusps[:12]),
                "asc": ascmc[0],
                "mc": ascmc[1],
                "armc": ascmc[2],
            }

        eps = swe.calc_ut(jd, swe.ECL_NUT, swe.FLG_SWIEPH)[0][0]

        themes.append({
            "id": cas["id"],
            "note": cas["note"],
            "piege": cas["piege"],
            "utc": list(cas["utc"]),
            "lat": cas["lat"],
            "lon": cas["lon"],
            "jd_ut": jd,
            "obliquite": eps,
            "corps": corps,
            "maisons": maisons,
        })

    # Attendu : les corps réels tombent en 'moshier' (pas de .se1 embarqué) ;
    # le nœud moyen sort en 'swieph' car il est purement analytique (polynôme
    # de Meeus) et ne lit aucun fichier. Toute autre combinaison est suspecte.
    if moteurs_vus - {"moshier", "swieph"}:
        raise SystemExit(f"✗ moteur swisseph inattendu : {moteurs_vus}")

    doc = {
        "_avertissement": (
            "Généré par outils/generer_golden.py depuis l'oracle swisseph. "
            "NE PAS ÉDITER À LA MAIN. swisseph est dev-only, jamais expédié."
        ),
        "oracle": {
            "bibliotheque": "pyswisseph",
            "version_swisseph": swe.version,
            "moteur_reel": sorted(moteurs_vus),
            "note_moteur": (
                "Aucun fichier .se1 n'est embarqué dans pyswisseph : swisseph "
                "bascule SILENCIEUSEMENT sur Moshier (demandé FLG_SWIEPH=2, "
                "retourné 260 = SPEED|MOSEPH). Détecté en lisant le drapeau "
                "RETOURNÉ, jamais celui demandé. Moshier est précis à ~1\" sur "
                "1900-2100, soit 60x sous le seuil astrologique (1'), donc bon "
                "pour valider. Le noeud_moyen sort en 'swieph' (258) car il est "
                "purement analytique (polynôme) et ne lit aucun fichier. "
                "Les MAISONS ne dépendent pas de l'éphéméride (pure trigo sur "
                "ARMC + obliquité + latitude) : cette comparaison-là est exacte."
            ),
        },
        "themes": themes,
    }
    SORTIE.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"✓ {len(themes)} thèmes -> {SORTIE.relative_to(RACINE)}")
    print(f"  oracle : swisseph {swe.version}, moteur réel = {sorted(moteurs_vus)}")


if __name__ == "__main__":
    main()
