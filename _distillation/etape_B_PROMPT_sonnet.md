# PROMPT SONNET — Personologie, Étape B (corpus)

Tu travailles dans l'app **Align** (`/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP`), un coach de vie 100 % déterministe : aucun LLM au runtime, le corpus est rédigé hors ligne et l'app ne fait que le lire. Tu vas écrire le **corpus de la personologie** (Phase 2, Étape B) et le rendre vert aux tests.

## Contexte — ce qui existe déjà (Étape A, ne pas y toucher)
- `moteur/periodes.py` : découpe le zodiaque en **48 sous-périodes** par degré solaire (12 cuspides + 36 semaines). `periodes.PERIODES` est la LISTE AUTORITAIRE des 48 clés. `periodes.periode_de(lon)` renvoie la sous-période.
- `moteur/noeuds.py` : l'axe des nœuds sud→nord (nord = destination = `noeud_moyen`, sud = nord+180°).
- `tests/test_periodes.py` : 8 tests verts sur le calcul. NE PAS modifier.

Ton travail est UNIQUEMENT du **corpus + plomberie de tests**. Aucun changement dans `periodes.py`/`noeuds.py`/`app.py`/le moteur.

## À LIRE d'abord, dans l'ordre
1. `_distillation/personologie_carte_de_concepts.md` — la MÉTHODE (48 périodes, axe des nœuds sud/nord, cadrage « potentiel + libre arbitre »).
2. `data/corpus/CHARTE.md` — la voix d'Align (obligatoire).
3. `moteur/periodes.py` — pour récupérer la liste EXACTE des 48 clés. Fais-le programmatiquement :
   `PYTHONPATH=. ./venv/bin/python -c "from moteur import periodes; [print(p['cle'], p['type'], p['signe'], p.get('rang')) for p in periodes.PERIODES]"`
4. `data/corpus/nombres_detail.json` — un MODÈLE de format de corpus « portrait » (structure, ton, longueurs).
5. `_distillation/fil_du_jour_SPEC.md` §6 — la discipline de droit d'auteur (concepts oui, prose non).

## ⚖️ DROIT D'AUTEUR — non négociable (l'app est commercialisée)
- Le livre *The Secret Language of Destiny* (Goldschneider & Elffers) est protégé : ses **noms de périodes** (« Week of the Star », « Cusp of Power »… et leurs traductions) et ses **descriptions** sont de l'expression protégée. **Tu n'en reprends AUCUN.**
- ⚠️ La carte de concepts (`personologie_carte_de_concepts.md`) cite quelques noms du livre à titre d'exemple (« Semaine de l'Enfant », « Cuspide du Pouvoir », etc.). **Ce sont ceux du livre — INTERDITS.** Tu inventes les tiens.
- Tu écris les descriptions **à partir du sens astrologique** de chaque sous-période (le signe + sa position : cuspide = mélange de deux signes ; semaine 1/2/3 = début/cœur/fin du signe), **jamais** à partir des textes du livre.
- Un test anti-plagiat (ci-dessous) vérifie qu'aucune suite de 8 mots de ton corpus n'apparaît dans `_distillation/sources/the_secret_language_of_destiny_personology_goldschneider.txt`.

## La voix (rappel CHARTE)
Tutoiement, **constatif** (« Tu es en train de… », jamais « Tu vas… » ni « Tu dois… » — zéro prédiction), déculpabilisant, **non fataliste** (une période/un nœud est un point de départ, pas un verdict — c'est la thèse d'Align). Une chute par entrée, pas d'aphorismes en rafale (zéro tiret cadratin aphoristique, deux-points aphoristiques rares). ⚠️ N'utilise pas le vocabulaire numérologique réservé d'Align comme métaphore sur les nombres (Cap, Voix, Foyer, Reflet, Geste, Source, Trace, Élan, Héritages, Frictions, Appuis, Chantiers) — ici on parle de signes et de nœuds, pas de nombres.

---

## LIVRABLE 1 — `data/corpus/periodes.json` (affiner le signe)
Une entrée par sous-période, **keyée EXACTEMENT par les 48 clés de `periodes.PERIODES`** (ex. `cuspe_poissons_belier`, `belier_1`, `belier_2`, `belier_3`, `cuspe_belier_taureau`, `taureau_1`, …). En-tête `"_charte": "data/corpus/CHARTE.md"` + un `"_note"` décrivant le fichier.

Chaque entrée :
```json
"belier_2": {
  "nom": "<un nom ORIGINAL Align, 2-4 mots, évocateur mais sobre>",
  "essence": "<une ligne : la saveur de cette sous-période en une phrase>",
  "texte": "<90-140 mots : comment ce cran précise le signe — ce qui anime, ce que ça donne au quotidien, le piège ; constatif, déculpabilisant, non fataliste>"
}
```
- **Cuspides** : décris le MÉLANGE des deux signes voisins (la cuspide `cuspe_belier_taureau` = le feu du Bélier qui rencontre la terre du Taureau). `nom` propre à Align.
- **Semaines 1/2/3** : décris la nuance de position dans le signe (entrée / cœur / fin), pas une redite du signe. Différencie-les nettement (anti-mur du corpus : les 3 semaines d'un même signe ne doivent pas se paraphraser).
- Les 48 `nom` sont tous distincts.

## LIVRABLE 2 — `data/corpus/noeuds.json` (d'où tu viens → où tu vas)
La couche « but de vie », **à résolution de SIGNE** (12 signes ; le nœud est lu par son signe — la résolution 48-périodes est une raffinement futur). Keyé par slug de signe dé-accentué : `belier, taureau, gemeaux, cancer, lion, vierge, balance, scorpion, sagittaire, capricorne, verseau, poissons`. En-tête `_charte` + `_note`.

Chaque entrée a DEUX facettes (l'app lira `origine` du signe du nœud sud + `destination` du signe du nœud nord — table ADDITIVE, jamais 12×12) :
```json
"belier": {
  "origine": "<80-130 mots : nœud SUD en Bélier = l'acquis, d'où tu viens (les automatismes, les talents faciles hérités) ; à intégrer, pas à fuir>",
  "destination": "<80-130 mots : nœud NORD en Bélier = où tu vas, ce que tu es venu apprendre/oser ; un cap, jamais une obligation>"
}
```
Cadrage obligatoire (carte de concepts) : le sud = le sillon usé (confortable mais limitant), le nord = la croissance (inconfortable car neuve, mais c'est la direction). **Intégrer les deux, pas abandonner le sud.** Jamais fataliste, jamais prédictif.

---

## PLOMBERIE DES TESTS (à faire, sinon la suite globale casse)
1. **`tests/test_style.py`** :
   - Ajoute `"periodes"` et `"noeuds"` à l'ensemble `PASSES_AU_STYLE`.
   - Ajoute `"essence", "texte", "origine", "destination"` à `CHAMPS_DE_PROSE`.
2. **`tests/test_corpus.py`** :
   - Ajoute `"essence", "texte", "origine", "destination"` à son `CHAMPS_DE_PROSE` (sinon `test_champs_tous_controles` échoue sur les champs > 15 mots). (`nom` est court, pas nécessaire.)
3. **Nouveau `tests/test_periodes_corpus.py`** :
   - **Couverture périodes** : chaque `p["cle"]` de `periodes.PERIODES` a une entrée dans `periodes.json` avec `nom`, `essence`, `texte` non vides.
   - **Noms uniques** : les 48 `nom` sont distincts.
   - **Couverture nœuds** : les 12 signes dé-accentués ont chacun `origine` + `destination` non vides dans `noeuds.json`.
   - **Longueurs** : `texte` 90-140 mots ; `origine`/`destination` 80-130 mots (bornes un peu élargies tolérées).
   - **Anti-plagiat** : aucune suite de 8 mots (normalisée : minuscules, sans accents, ponctuation→espace) d'un `texte`/`origine`/`destination`/`essence` n'apparaît dans `_distillation/sources/the_secret_language_of_destiny_personology_goldschneider.txt`. Saute le test si le fichier source est absent (`pytest.skip`). Inspire-toi de `tests/test_fil.py::test_aucun_8gramme_dans_les_sources` (même technique).

## BOUCLE DE VALIDATION (jusqu'au vert)
Lance `./venv/bin/python -m pytest tests/ -q` et corrige jusqu'à **0 échec**. Attention en particulier à :
- `test_corpus.py::test_aucun_texte_en_double` (aucune chaîne ≥ 40 car identique : garde les `essence`/`nom` courts et distincts, les `texte` naturellement uniques) ;
- `test_corpus` (interdits : pas de « tu vas »/« tu dois » oracle, pas de marques) ;
- `test_style` (tirets cadratins < 8/100 phrases, deux-points < 10/100).

## À NE PAS FAIRE
- Ne touche pas `moteur/`, `app.py`, les templates (le câblage + l'affichage = Étape C, séparée).
- Ne reprends aucun nom ni texte du livre.
- Ne mets pas de clé lente/aléatoire : ce corpus est lu par le signe/la période, calculés.

## Livrable final attendu
`data/corpus/periodes.json` (48), `data/corpus/noeuds.json` (12×2), les 3 fichiers de tests à jour, `pytest tests/ -q` **tout vert**. Termine par un résumé court (nb d'entrées, tests au vert, choix de nommage notables).
