# Brief de chaîne — Vague 1 « langage clair » : Le Jour (Ta Trame)

> À exécuter **en Sonnet**. Doctrine + outillage + pilotes posés par Opus (2026-08-20).
> Cibles : `data/corpus/fil.json` (608 entrées) et `data/corpus/transits.json` (722 entrées).
> Suit `data/corpus/CHARTE.md` §« Comprendre à la première lecture » et `PLAN_LANGAGE_CLAIR.md`.

## 0. Le but
Passer TOUS les textes du Jour au registre « langage clair » : compris du plus grand nombre, à la
**première lecture**. On ne change pas le FOND (le constat juste, la scène, le geste), on change la
**façon de le dire**.

## 1. Les 6 réflexes (à appliquer phrase par phrase)
1. **Phrases courtes.** Coupe toute phrase > ~22 mots en deux. Vise 15-20 mots. Le point d'abord.
2. **Dire QUOI, concret.** Le lecteur ne doit jamais se demander « de quoi on parle ? ». Remplace
   l'abstrait par du concret (« Ta tête remplit les trous » plutôt que « L'esprit comble les trous »).
3. **Mot de tous les jours**, jamais le mot chic ou littéraire.
4. **Verbes actifs, ordre naturel** (sujet → verbe → complément). Pas de participe détaché.
5. **Une image max, limpide.** Jamais une métaphore qu'il faut décoder ; si elle demande un effort,
   dis la chose en clair.
6. **Québécois d'abord** : pas de tic hexagonal (« du coup », « rien ne prend », « un truc »…),
   mais PAS de joual (« pantoute », « pogner »).

## 2. Ce qu'on NE touche PAS
- Le **fond** : la scène concrète, le constat, le recadrage en conditionnement.
- Le **tutoiement** (« tu ») — c'est le registre du Jour, on le garde.
- Les **gestes** déjà clairs et actionnables (la plupart le sont) — n'y touche que s'ils sont
  longs ou abstraits.
- La structure des entrées à 3 phases (`approche`/`coeur`/`retrait`) : chaque phase garde sa
  fonction (voir CHARTE) ; on clarifie sa prose, on ne la fusionne pas.
- Le champ `pensee_soir` : même traitement clarté que `miroir`.

## 3. Champs à traiter
- `fil.json` : `miroir` et `geste` de chaque entrée (et sous-champs des entrées à phases).
- `transits.json` : `miroir`, `geste`, `pensee_soir` (dans `transits_generiques` ET `transits_precis`,
  y compris les phases `approche`/`coeur`/`retrait`).

## 4. Pilotes-étalons (déjà écrits dans `fil.json`)
- `soi.miroir` : « Aujourd'hui, un petit rien prend trop de poids. Un mot de travers, et tu le lis
  comme une preuve de ce que tu vaux. C'était juste un moment, pas un jugement sur toi. »
- `soi_tension.miroir` : « Aujourd'hui, tu te compares aux autres, et tu ressors perdant presque à
  chaque fois. Ce classement n'existe nulle part, sauf dans ta tête. »
- `ressources_tension.miroir` : « L'argent te travaille ces jours-ci. Une envie monte, tu te
  compares, et le « assez » recule à mesure que tu en gagnes. Plus tu en as, plus il t'en faut. »
- `echanges_tension.miroir` (touche LÉGÈRE) : « …Ta tête remplit les trous toute seule, et souvent
  elle se trompe. »

Règle d'or vue sur les pilotes : **certaines entrées demandent un gros rewrite, d'autres une simple
retouche — on corrige le point précis, on ne réécrit pas ce qui est déjà clair.**

## 5. Validation en fin de vague
1. JSON valide : `python3 -c "import json; [json.load(open(f)) for f in ('data/corpus/fil.json','data/corpus/transits.json')]"`.
2. Tics hexagonaux : `grep -noiE "du coup|rien ne prend|pantoute|pogner|niaiser" data/corpus/fil.json data/corpus/transits.json` → rien.
3. **Ajouter `fil` et `transits` au cliquet** `PASSES_AU_CLAIR` dans `tests/test_style.py`.
4. `python -m pytest -q` → suite verte (le test `test_phrases_courtes` vérifie alors « < 12 % de
   phrases > 22 mots » sur les deux fichiers, ET `test_pas_d_aphorisme` reste vert).
5. Relecture à voix haute d'un échantillon : ça doit sonner comme quelqu'un qui parle.
6. Cocher la Vague 1 dans `PLAN_LANGAGE_CLAIR.md`.
