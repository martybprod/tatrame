"""Les thèmes de référence du filet golden.

Écrits AVANT le moteur, délibérément : ces cas sont le contrat que
l'implémentation doit honorer, et le filet qui permettra un jour de changer
de source d'éphémérides sans rien casser.

Chaque cas est choisi pour exercer un piège précis, documenté dans `piege`.
Les cas sans piège particulier couvrent le cas nominal.
"""

# Instants exprimés en UTC : la conversion heure locale -> UTC est testée
# séparément (tests/test_temps.py). Ici on isole éphémérides + maisons.
CAS = [
    # ---------------------------------------------------------------- nominal
    dict(
        id="greenwich-midi-2000",
        note="Cas canonique : Greenwich, midi UTC, J2000 pile.",
        utc=(2000, 1, 1, 12, 0, 0),
        lat=51.4779, lon=0.0,
        piege=None,
    ),
    dict(
        id="quebec-1975-ete",
        note="Québec, été 1975. Le cas de référence de Martin.",
        utc=(1975, 7, 16, 18, 30, 0),   # 14h30 EDT
        lat=46.8139, lon=-71.2080,
        piege=None,
    ),
    dict(
        id="paris-1980",
        note="Paris, cas nominal européen.",
        utc=(1980, 5, 20, 7, 15, 0),
        lat=48.8566, lon=2.3522,
        piege=None,
    ),
    dict(
        id="montreal-2024",
        note="Montréal, époque récente.",
        utc=(2024, 3, 15, 16, 0, 0),
        lat=45.5088, lon=-73.5878,
        piege=None,
    ),

    # ------------------------------------------------- latitudes qui font mal
    dict(
        id="whitehorse-60n",
        note="Whitehorse, 60,7°N. Placidus se dégrade nettement ici.",
        utc=(1968, 11, 3, 20, 0, 0),
        lat=60.7212, lon=-135.0568,
        piege="placidus-degrade",
    ),
    dict(
        id="tromso-69n",
        note="Tromsø, 69,6°N — AU-DELÀ du cercle polaire (66°33'). "
             "Placidus est mathématiquement INDÉFINI : l'arc semi-diurne "
             "n'existe pas pour certains degrés. Doit se replier sur Porphyry "
             "sans lever d'exception ni boucler.",
        utc=(1990, 12, 21, 11, 0, 0),
        lat=69.6492, lon=18.9553,
        piege="placidus-indefini",
    ),
    dict(
        id="longyearbyen-78n",
        note="Longyearbyen, 78,2°N. Cas extrême, bien au-delà du cercle polaire.",
        utc=(2001, 6, 21, 0, 0, 0),
        lat=78.2232, lon=15.6469,
        piege="placidus-indefini",
    ),

    # ----------------------------------------------------- géométries limites
    dict(
        id="quito-equateur",
        note="Quito, latitude ~0. tan(phi) -> 0 dans les formules d'ASC.",
        utc=(1985, 9, 23, 15, 30, 0),
        lat=-0.1807, lon=-78.4678,
        piege="latitude-zero",
    ),
    dict(
        id="sydney-sud",
        note="Sydney, hémisphère sud. Signe de la latitude inversé.",
        utc=(1993, 2, 11, 23, 45, 0),
        lat=-33.8688, lon=151.2093,
        piege="hemisphere-sud",
    ),
    dict(
        id="ushuaia-sud-profond",
        note="Ushuaia, 54,8°S. Hémisphère sud ET haute latitude.",
        utc=(1977, 6, 30, 6, 0, 0),
        lat=-54.8019, lon=-68.3030,
        piege="hemisphere-sud",
    ),
    dict(
        id="antiméridien",
        note="Suva, Fidji — longitude proche de +180°. Enroulement de la longitude.",
        utc=(2010, 4, 5, 22, 10, 0),
        lat=-18.1416, lon=178.4419,
        piege="longitude-180",
    ),

    # ------------------------------------------- singularités du temps sidéral
    dict(
        id="armc-zero",
        note="Instant choisi pour que l'ARMC soit proche de 0° "
             "(passage du point vernal au méridien) — cas de quadrant.",
        utc=(2000, 9, 22, 11, 47, 0),
        lat=45.0, lon=0.0,
        piege="armc-limite",
    ),
    dict(
        id="minuit-pile",
        note="Minuit UTC pile : frontière de jour julien.",
        utc=(1960, 1, 1, 0, 0, 0),
        lat=40.7128, lon=-74.0060,
        piege="frontiere-jour",
    ),

    # ----------------------------------------------- bornes de l'éphéméride
    dict(
        id="borne-basse-1900",
        note="1900 : borne basse de notre plage de naissances utile. "
             "DE440s couvre 1849-2150, donc large marge.",
        utc=(1900, 1, 15, 9, 0, 0),
        lat=48.8566, lon=2.3522,
        piege="borne-temporelle",
    ),
    dict(
        id="borne-haute-2100",
        note="2100 : borne haute utile (transits lointains).",
        utc=(2100, 6, 15, 12, 0, 0),
        lat=48.8566, lon=2.3522,
        piege="borne-temporelle",
    ),

    # --------------------------------------------------- rétrogradations
    dict(
        id="mercure-retro-2024",
        note="Mercure rétrograde (avril 2024). La vitesse doit être négative.",
        utc=(2024, 4, 15, 12, 0, 0),
        lat=45.5088, lon=-73.5878,
        piege="retrogradation",
    ),
    dict(
        id="mars-retro-2022",
        note="Mars rétrograde (novembre 2022).",
        utc=(2022, 11, 15, 12, 0, 0),
        lat=48.8566, lon=2.3522,
        piege="retrogradation",
    ),
    dict(
        id="mercure-station-2024",
        note="Mercure proche de sa station directe (25 avril 2024) : "
             "vitesse ~0, le cas où un signe de vitesse mal calculé se voit.",
        utc=(2024, 4, 25, 12, 0, 0),
        lat=48.8566, lon=2.3522,
        piege="station",
    ),

    # --------------------------------------------------------- Lune rapide
    dict(
        id="lune-rapide",
        note="La Lune bouge ~13°/jour : la moindre erreur d'instant se voit "
             "sur elle en premier. Sentinelle de précision temporelle.",
        utc=(2005, 8, 8, 3, 21, 0),
        lat=46.8139, lon=-71.2080,
        piege="corps-rapide",
    ),
]

# Les pièges qu'on veut voir couverts. Le test échoue si l'un n'est plus exercé
# (garde-fou contre une suppression de cas par mégarde).
PIEGES_ATTENDUS = {
    "placidus-degrade", "placidus-indefini", "latitude-zero",
    "hemisphere-sud", "longitude-180", "armc-limite", "frontiere-jour",
    "borne-temporelle", "retrogradation", "station", "corps-rapide",
}
