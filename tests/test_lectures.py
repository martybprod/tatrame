"""La lecture de fond des arcanes — garde-fou de COMPLÉTUDE symbolique.

La promesse du bouton « Comprendre cette carte » : expliquer l'image qu'on a
sous les yeux. Donc chaque symbole présent SUR LA CARTE doit être nommé dans
sa lecture. Un symbole visible et passé sous silence est une promesse non
tenue (demande de Martin, 2026-09-15 : tous les symboles, pas seulement deux).

Source des inventaires : le kit de production du deck
(`_distillation/osho_tarot_KIT_PRODUCTION_majeurs.md`, §4-5) croisé avec les
images validées. Un arcane sans `lecture` est sauté — le filet grandit avec
les lots rédigés, il ne bloque jamais l'écriture.
"""
import json
import pathlib
import re
import unicodedata

RACINE = pathlib.Path(__file__).resolve().parent.parent

#: Symboles requis par arcane — mots-clés, insensibles à la casse, aux accents
#: et aux apostrophes. Un mot-clé couvre ses dérivés (« oiseau » matche
#: « oiseaux »). Liste = ce qui est VISIBLE sur l'image VALIDÉE
#: (_distillation/cartes_validees/ — la référence, pas les itérations).
SYMBOLES_REQUIS = {
    0: ["falaise", "manteau", "rose blanche", "chien", "oiseau",
        "arc-en-ciel", "rivière", "soleil", "brume", "montagne"],
    1: ["eau", "poisson", "oiseau", "fleur", "racine", "étoil", "voile",
        "fils d'or"],
    2: ["colonne", "galax", "croissant", "couronne", "feuille", "cristal",
        "dauphin", "eau"],
    3: ["ruban", "mains", "robe", "motif", "bassin", "feu", "eau"],
    4: ["temple", "colonnes", "cascades", "bélier", "aigle", "lierre",
        "rivière", "fleurs", "soleil", "montagnes"],
    5: ["vide", "nue", "bras", "œuf", "lumière", "étoile", "spirale"],
    6: ["mains", "colombes", "serpent", "soleil", "collines", "arbre",
        "fruits"],
    7: ["avance", "flammes", "sphinx", "croissants", "étoil"],
    8: ["œuf", "falaises", "gouffre", "rocher", "coque", "bec", "herbe",
        "oiseau", "huit", "brume"],
    9: ["nuit", "neige", "montagnes", "capuchon", "bâton", "lumière",
        "poitrine", "étoile à six branches", "ombre"],
    10: ["roue", "galaxies", "saisons", "hiver", "lune", "glaçons",
         "automne", "citrouilles", "printemps", "été", "fleurs", "blé",
         "yin yang", "serpent", "sphinx", "rocher"],
    11: ["tissage", "pieds nus", "ciseaux", "fil rouge", "toile", "archer",
         "flèche", "centre", "cible", "balance", "plateaux", "laine"],
    12: ["tête en bas", "cadre", "ailes", "pieds", "temple", "cercle doré",
         "compas", "nuages"],
    13: ["épée", "fleur", "lotus", "silhouette", "yin yang", "rose blanche",
         "serpent", "peau", "chaîne brisée", "cheval blanc"],
    14: ["coupée en deux", "nuit", "aigle", "jour", "soleil", "montagnes",
         "rivière", "cygne", "bec à bec", "reflet", "eau"],
    15: ["emmaillotée", "bandelettes", "fils", "main", "marionnette",
         "flamme", "socle", "chaîne", "reflet", "libre"],
    16: ["métier à tisser", "tapisserie", "tour", "couronnée", "fend",
         "braises", "tisserande", "fils dorés"],
    17: ["médite", "nuages", "yeux fermés", "paumes", "pleine lune",
         "étoilé", "oiseau", "branche", "lac", "reflète"],
    18: ["arbre", "croissant", "étoiles", "pierres levées", "racines",
         "dorées", "anneau", "clé", "couronne", "chaînettes"],
    19: ["jardin", "tablier", "arrosoir", "tournesol", "soleil", "visage",
         "rayonne", "abeilles", "fleurs", "boutons"],
    20: ["escalier", "pierre", "lampe", "deux mains", "cœur", "fils tressés",
         "étoilé", "arbre nu", "papillon", "balustrade"],
    21: ["tisserande", "métier", "mandala", "étoiles", "galaxies", "navette",
         "rayon de soleil", "centre", "arc-en-ciel", "papillon", "vierge"],
}


def _plier(texte):
    """Minuscules, accents et apostrophes retirés — la comparaison symbolique."""
    décomposé = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(c for c in décomposé if not unicodedata.combining(c))
    return sans_accents.replace("'", "")


def lectures_ecrites():
    """Les lectures rédigées à ce jour : {numéro arcane: texte}."""
    arcanes = json.loads(
        (RACINE / "data" / "corpus" / "arcanes.json").read_text(encoding="utf-8")
    )["arcanes"]
    return {int(k): e["lecture"] for k, e in arcanes.items()
            if e.get("lecture")}


def test_chaque_symbole_de_la_carte_est_nomme_dans_la_lecture():
    """Le filet demandé par Martin : la lecture nomme TOUS les symboles."""
    for numero, texte in sorted(lectures_ecrites().items()):
        requis = SYMBOLES_REQUIS.get(numero)
        assert requis, f"arcane {numero} : inventaire de symboles manquant — " \
                       f"complète SYMBOLES_REQUIS en même temps que la lecture"
        plié = _plier(texte)
        manquants = [s for s in requis if _plier(s) not in plié]
        assert not manquants, (
            f"arcane {numero} ({numero}) : la lecture ne nomme pas "
            f"{', '.join(manquants)} — tout symbole visible doit être expliqué"
        )


def test_lecture_assez_profonde_et_structuree():
    """La profondeur demandée : trois temps (image, lecture, leçon) et assez
    de matière pour expliquer les symboles, pas les énumérer."""
    for numero, texte in sorted(lectures_ecrites().items()):
        paragraphes = [p for p in texte.split("\n\n") if p.strip()]
        assert len(paragraphes) >= 3, f"arcane {numero} : moins de 3 temps"
        assert len(texte.split()) >= 180, f"arcane {numero} : trop court"


# ─── Passe mécanique (data/corpus/RELECTURE.md, passe 4) ─────────────
MOTIFS_SALES = [
    (r"  +", "double espace"),
    (r"\b(le le|la la|les les|de de|à à|et et|un un|au au|que que|qui qui)\b",
     "mot répété"),
    (r"[a-zà-ÿ]+[,;.][a-zà-ÿ]", "ponctuation collée"),
    (r"\.\.(?!\.)", "point double"),
    (r"\bde['’][aeiouyéèàù]", "élision cassée (de + voyelle)"),
]


def test_aucune_coquille_mecanique_dans_les_textes_de_cartes():
    """Les coquilles attrapées en relance (mots collés, « de'être »…) ne
    doivent plus arriver jusqu'à Martin. Balayage des trois champs écrits."""
    arcanes = json.loads(
        (RACINE / "data" / "corpus" / "arcanes.json").read_text(encoding="utf-8")
    )["arcanes"]
    for k in map(str, range(22)):
        for champ in ("invitation", "invitation_personnelle", "lecture"):
            if champ not in arcanes[k]:
                continue
            texte = arcanes[k][champ]
            for motif, label in MOTIFS_SALES:
                trouve = re.search(motif, texte)
                assert not trouve, (
                    f"arcanes {k} ({champ}) : {label} — "
                    f"« …{texte[max(0, trouve.start() - 25):trouve.end() + 25]}… »"
                )


# Le nom de l'app ne se met jamais en scène dans une carte : le lecteur lit
# une carte, pas une marque (demande de Martin, 2026-09-15 — « Align » est en
# plus l'ANCIEN nom, et même « Ta Trame » n'a rien à faire dans ce contexte).
MOTIF_MARQUE = re.compile(r"\bAlign\b|Ta Trame|ta trame", re.I)


def textes_affiches_de_cartes():
    """Tous les textes qu'un lecteur voit sur une carte : arcanes.json (3
    champs × 22) et mineurs.json (invitation des 56). Les clés internes
    (préfixées « _ », notes de travail) sont exclues."""
    for nom_fichier, champs in (
            ("arcanes.json", ("invitation", "invitation_personnelle", "lecture")),
            ("mineurs.json", ("invitation",))):
        contenu = json.loads(
            (RACINE / "data" / "corpus" / nom_fichier).read_text(encoding="utf-8"))
        for cle, entree in contenu.items():
            if cle.startswith("_") or not isinstance(entree, dict):
                continue
            for champ in champs:
                if isinstance(entree.get(champ), str):
                    yield f"{nom_fichier} {cle} ({champ})", entree[champ]


def test_aucune_marque_dans_les_textes_de_cartes():
    """Ni l'ancien nom ni le nom actuel de l'app dans un texte de carte."""
    for chemin, texte in textes_affiches_de_cartes():
        assert not MOTIF_MARQUE.search(texte), (
            f"{chemin} : le nom de l'app n'apparaît pas dans un texte de "
            f"carte — « {texte[:60]}… »"
        )


# ─── Équilibre des formules de transmission (demande de Martin, 2026-09-15 :
# « On t'a appris » revenait tout le temps) — même logique que le test des
# ouvertures : une formule ne peut pas dominer les conditionnements.
FORMULES_TRANSMISSION = {
    r"on t'a appris": 4,
    r"schéma décrit": 5,
    r"schéma ne parle pas": 3,
    r"schéma parle": 3,
}


def test_les_formules_de_transmission_restent_equilibrees():
    """Le cadrage « reçu, pas de ta faute » est la voix des conditionnements,
    mais une seule formule ne peut pas la porter à elle seule."""
    conditionnements = [
        e["conditionnement"] for e in json.loads(
            (RACINE / "data" / "corpus" / "arcanes.json").read_text(
                encoding="utf-8"))["arcanes"].values()
        if e.get("conditionnement")
    ]
    for motif, plafond in FORMULES_TRANSMISSION.items():
        n = sum(1 for t in conditionnements
                if re.search(motif, t, re.I))
        assert n <= plafond, (
            f"la formule « {motif} » sert {n} conditionnements "
            f"(plafond {plafond}) : varie les portes d'entrée du cadrage "
            f"(« Tu as grandi avec », « La règle reçue… », « Autour de toi, "
            f"on répétait que… »)"
        )
