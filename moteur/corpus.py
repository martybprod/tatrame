"""Le corpus — des tables de texte, lues, jamais générées.

C'est ici que se tient la promesse d'Align : **zéro LLM au runtime**.
Un LLM a rédigé ces textes hors ligne, sous charte (data/corpus/CHARTE.md) ;
l'app ne fait que les LIRE. Le modèle a fini son travail avant qu'elle démarre.

Conséquences en cascade : déterminisme RÉEL (pas « température 0 », qui dérive
au changement de version de modèle), zéro latence, zéro RAM, aucun texte sous
copyright embarqué, commercialisable.

Règle d'or du corpus : on ADDITIONNE des tables indépendantes, on ne les
multiplie JAMAIS. On écrit N + M entrées, pas N × M.
"""
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "data" / "corpus"

#: Les seuls axes répartis sur plusieurs fichiers. Liste EXPLICITE, et pas une
#: fusion automatique de toutes les clés : `lexique.json` et `ciel.json`
#: portent tous deux une clé `phases` sans être le même axe — les fusionner
#: mélangerait un glossaire et des textes du jour.
AXES_FUSIONNES = frozenset({"astre_signe", "astre_maison", "aspects_paires"})


class Corpus:
    """Charge les tables une fois. Aucun accès disque ensuite."""

    def __init__(self, dossier=DOSSIER):
        self.dossier = dossier
        self.tables = {}
        #: Vues logiques : plusieurs FICHIERS alimentent un même AXE.
        #: `ciel_signe_1/2/3.json` portent tous la clé `astre_signe` — écrits
        #: par des rédacteurs différents (c'est ce qui évite les tics), mais
        #: l'app doit les lire comme une seule table.
        self.axes = {}

        for fichier in sorted(dossier.glob("*.json")):
            table = json.loads(fichier.read_text(encoding="utf-8"))
            self.tables[fichier.stem] = table
            for cle, contenu in table.items():
                if cle.startswith("_") or not isinstance(contenu, dict):
                    continue
                if cle not in AXES_FUSIONNES:
                    continue
                fusion = self.axes.setdefault(cle, {})
                doublons = fusion.keys() & contenu.keys()
                if doublons:
                    # Deux rédacteurs sur la même entrée = un texte écrasé en
                    # silence, donc du travail perdu sans que personne le voie.
                    raise ValueError(
                        f"{fichier.name} : entrées déjà définies ailleurs dans "
                        f"l'axe « {cle} » → {sorted(doublons)[:5]}"
                    )
                fusion.update(contenu)

    def lire(self, table, *chemin, defaut=None):
        """Lit une entrée. Renvoie `defaut` si elle manque — jamais d'exception.

        `table` peut être un FICHIER (`nombres`) ou un AXE logique
        (`astre_signe`, réparti sur trois fichiers). Les axes priment : c'est
        eux que le code métier nomme.

        Une entrée absente est un TROU DE CORPUS, pas une panne : le corpus se
        construit par vagues, et l'app doit rester utilisable et DIRE ce qui
        manque plutôt que de tomber.
        """
        noeud = self.axes.get(table, self.tables.get(table))
        for cle in chemin:
            if not isinstance(noeud, dict):
                return defaut
            noeud = noeud.get(str(cle))
            if noeud is None:
                return defaut
        return noeud

    def manquants(self, table, *chemin_parent, attendus=()):
        """Quelles clés manquent — pour piloter la rédaction, pas pour deviner."""
        noeud = self.lire(table, *chemin_parent, defaut={}) or {}
        return [c for c in attendus if str(c) not in noeud]

    def inventaire(self):
        """Ce que le corpus contient réellement. Affiché en Phase 1."""
        compte = {}
        for nom, table in self.tables.items():
            for cle, valeur in table.items():
                if cle.startswith("_"):
                    continue
                if isinstance(valeur, dict):
                    compte[f"{nom}.{cle}"] = len([k for k in valeur if not k.startswith("_")])
        return compte
