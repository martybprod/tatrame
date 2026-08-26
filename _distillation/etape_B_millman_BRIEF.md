# PROMPT SONNET — Millman « But-de-vie », Étape B (corpus)

Tu travailles dans **Align / Ta Trame** (`/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP`),
un coach de vie **100 % déterministe** : aucun LLM au runtime, le corpus est rédigé hors ligne et
l'app ne fait que le lire. Tu vas intégrer deux idées distillées de l'ouvrage *Votre Chemin de Vie*
(Dan Millman) : **A) une vérification du cycle de neuf ans** et **C) les 17 lois spirituelles comme
leviers du jour**. (La piste B — nombre composé de relation — est reportée : voir la carte.)

## ⚠️⚠️ PRIORITÉ ABSOLUE, AVANT TOUT LE RESTE : LE LANGAGE CLAIR
C'est **la** règle qui prime sur toutes les autres. Elle est figée dans `data/corpus/CHARTE.md`
(§ « Comprendre à la première lecture »). Rappel des réflexes, non négociables :
- **Compris du plus grand nombre, à la première lecture** (âge de lecture ~13 ans). Clair ≠ bébête.
- **Dire QUOI, concrètement.** Jamais « ça chauffe » sans dire quoi ni comment.
- **Le mot de tous les jours**, pas le mot chic. Concret, pas abstrait.
- **Verbes actifs, ordre naturel** (sujet → verbe → complément). Pas de participe détaché, pas d'inversion.
- **UNE seule image par entrée, limpide.** Jamais deux empilées, jamais une à décoder.
- **UNE chute par entrée, pas par phrase.** Le reste est plat, parlé, facile.
- **Québécois d'abord** (France ensuite) : pas de tic hexagonal (« du coup », « bosser », « un truc »,
  « carrément »…), et surtout **pas de joual** (pas de « pantoute », « pogner »). Le naturel québécois,
  pas le folklore.
- **Le test à voix haute** : si tu t'entends « faire une phrase », ou si une phrase demande une
  relecture, tu coupes ou réécris. Ça doit sonner comme quelqu'un qui parle.
- Cibles mesurées par `tests/test_style.py` : < 8 tirets cadratins / 100 phrases, < 10 deux-points / 100,
  et **< 12 % de phrases de plus de 22 mots** (cliquet `PASSES_AU_CLAIR`).

**Aucune entrée n'est acceptée si elle échoue le langage clair, même si le fond est juste.**

## À LIRE d'abord, dans l'ordre
1. `data/corpus/CHARTE.md` — la voix d'Align, EN ENTIER. Obligatoire.
2. `_distillation/votre_chemin_de_vie_carte_de_concepts.md` — la carte de concepts (sections F, G, I).
3. `_distillation/PLAN_LANGAGE_CLAIR.md` — les étalons avant/après (calibrage du registre).
4. `data/corpus/annees_detail.json` — pour la piste A (le cycle est DÉJÀ là, champ `la_place_dans_le_cycle`).
5. `data/corpus/nombres_detail.json` — MODÈLE de format « portrait » (structure, ton, longueurs).
6. `moteur/numerologie.py` — pour la piste C : la fonction `cap()` et sa `valeur`/`base` (1-9), clé du routage.

## ⚖️ DROIT D'AUTEUR — non négociable (l'app est commercialisée)
- L'ouvrage de Dan Millman est protégé. Tu reprends les **concepts et la structure** (le principe de
  chaque loi, l'idée du levier, la phase du cycle), **jamais la prose**, jamais les exemples chiffrés,
  jamais les descriptions par nombre de naissance.
- Les **noms des 17 lois** (Flexibilité, Choix, Responsabilité, Équilibre, Méthode, Comportements,
  Discipline, Perfection, Moment présent, Non-jugement, Foi, Attentes, Honnêteté, Volonté supérieure,
  Intuition, Action, Cycles) sont des **mots français courants**, pas une marque : tu peux les employer.
  Mais **tu écris chaque texte à partir du concept**, en tes mots, dans la voix d'Align.
- Un test anti-plagiat (ci-dessous) vérifie qu'aucune suite de 8 mots de ton corpus n'apparaît dans
  `_distillation/sources/votre_chemin_de_vie_dan_millman.txt`.

## Vocabulaire réservé d'Align — NE PAS l'employer comme métaphore
`Cap, Voix, Foyer, Reflet, Geste, Source, Trace, Élan, Héritages, Frictions, Appuis, Chantiers` nomment
des positions numérologiques d'Align. **N'utilise aucun de ces mots pour désigner autre chose.**
En particulier : le pas d'action d'une entrée du jour s'appelle **`le_pas`** (jamais « le geste » —
`Le Geste` est déjà une position). La loi s'appelle « la Loi de l'Action », ça ne pose pas de conflit.

---

## LIVRABLE A — vérifier (et non dupliquer) le cycle de neuf ans

**Constat de départ (à respecter absolument) : le cycle de neuf ans de Millman EST DÉJÀ intégré**
dans `data/corpus/annees_detail.json`, champ `la_place_dans_le_cycle`, et déjà en langage clair
(la métaphore de l'escalier à neuf marches : « ouvrir, mûrir, montrer, construire, respirer,
s'engager, regarder, récolter, finir »). **Tu n'ajoutes AUCUN nouveau champ « saison ».** Bolt-on une
deuxième image (jardin, saisons) casserait la règle « une seule image par entrée » et le mur du corpus.

Ton travail sur A est donc une **passe de VÉRIFICATION**, entrée par entrée (années 1 à 9) :
1. Le rôle de la marche est-il **juste** au regard de la phase de Millman (carte de concepts, section I) ?
   1 semer · 2 coopérer · 3 percer/vulnérabilité · 4 enraciner · 5 fleurir/opportunités · 6 donner/partager ·
   7 gratitude/leçons · 8 récolter · 9 achever/retourner la terre.
2. Chaque marche a-t-elle un **rôle DISTINCT** des voisines (pas de paraphrase entre années 5 et 6, etc.) ?
3. Le langage clair est-il tenu ?

**Livrable A = un rapport court** (`_distillation/verif_cycle_neuf_ans.md`) : pour chacune des 9 années,
« conforme » ou « à ajuster : <quoi, en une ligne> ». **Ne modifie `annees_detail.json` que pour les
années réellement faibles** (probablement 0 à 2), et par une **retouche ciblée**, jamais une réécriture.
Si tout est conforme, dis-le : ne touche à rien.

---

## LIVRABLE C — les 17 lois comme leviers (le vrai chantier)

### C.1 — `data/corpus/lois.json`
17 entrées, une par loi, keyées par slug dé-accentué :
`flexibilite, choix, responsabilite, equilibre, methode, comportements, discipline, perfection,
moment_present, non_jugement, foi, attentes, honnetete, volonte_superieure, intuition, action, cycles`.
En-tête `"_charte": "data/corpus/CHARTE.md"` + un `"_note"` décrivant le fichier et sa source (concepts
de Millman, prose originale).

Chaque entrée :
```json
"flexibilite": {
  "nom": "La loi de la souplesse",
  "en_un_mot": "<2-4 mots : l'idée nue>",
  "le_principe": "<50-90 mots : ce que la loi observe, en langage clair, constatif, déculpabilisant. Le concept de Millman dit en mots de tous les jours, avec UNE image claire max. Non fataliste.>",
  "le_pas": "<25-55 mots : une action concrète, petite, faisable aujourd'hui, qui applique la loi. Le registre « Le pas » des entrées du jour.>"
}
```
Consignes de fond (par loi, tirées de la carte section G — jamais du texte source) :
- **nom** : un titre Align, clair et sobre. « La loi de la souplesse » plutôt que « La Loi de la Flexibilité »
  si ça sonne plus parlé — mais garde le mot courant, pas le mot chic. Les 17 noms sont distincts.
- Reste **constatif** (« Tu es en train de… », jamais « Tu vas… » ni « Tu dois… ») et **non fataliste**
  (une loi est un levier qu'on choisit d'actionner, pas une fatalité).
- **Anti-mur du corpus** : les 17 lois ne doivent pas se paraphraser entre elles. Chacune éclaire une
  mécanique différente (souplesse ≠ non-jugement ≠ acceptation du présent — précise ce qui les distingue).
- Longueur d'une entrée : profil « Nuance/modulation » élargi. Pas de portrait de 180 mots : une loi est
  un levier, pas un chapitre.

### C.2 — la table de routage `nombre → lois`
Chaque chemin a **quelques lois qui le travaillent en priorité** (carte, concept 31). Livrer un bloc
`"_routage"` DANS `lois.json` (ou un fichier `data/corpus/lois_routage.json` si plus propre), keyé par
la **valeur de base du Cap** (1 à 9 — c'est `numerologie.cap(...)["base"]`) :
```json
"_routage": {
  "1": ["choix", "action", "flexibilite"],
  "2": ["responsabilite", "equilibre", "flexibilite"],
  "...": "..."
}
```
- 2 à 3 lois par nombre de base, tirées de la logique de Millman (ex. la loi de l'Équilibre nomme
  explicitement ce que chaque nombre 1-9 doit équilibrer ; l'Intuition est clé pour 6 et 9 ; la Méthode
  et les Comportements pour 4 ; la Discipline pour 5 ; le Non-jugement et la Perfection pour 6 ; etc.).
- **Table ADDITIVE, jamais un produit** : on route par le seul Cap (1-9) en v1. On n'invente pas une
  matrice nombre × loi. Le raffinement (router aussi par d'autres positions) est un futur possible, hors
  scope ici. **Signale ce choix dans le `_note`.**
- Le 0 (dons intérieurs) et les nombres maîtres : ne PAS créer d'entrées de routage spéciales en v1 ;
  s'en tenir à la base 1-9. Le noter.

### C.3 — la plomberie moteur (petite, à confier à Opus après validation du corpus)
`lois.json` est un corpus lisible ; **le câblage** (une fonction qui, depuis le Cap, sert la ou les lois
prioritaires, et éventuellement une « loi du jour ») est une étape Opus séparée. **Ne l'écris pas ici** :
mentionne-la comme suite, pour que Martin décide du point d'entrée (écran portrait ? fil du jour ?).

---

## PLOMBERIE DES TESTS (obligatoire, sinon la suite casse)
1. **Langage clair** : ajouter `lois` (et `lois_routage` s'il existe) au cliquet `PASSES_AU_CLAIR` dans
   `tests/test_style.py`, et faire passer les cibles (phrases longues < 12 %, tirets < 8/100, deux-points
   < 10/100). C'est la condition d'acceptation n°1.
2. **Anti-plagiat** : ajouter un test qui vérifie qu'aucune suite de 8 mots de `lois.json` n'apparaît dans
   `_distillation/sources/votre_chemin_de_vie_dan_millman.txt` (même patron que le test personologie).
3. **Intégrité JSON** : `lois.json` a bien 17 entrées + `_charte` + `_note` ; les 17 `nom` sont distincts ;
   le `_routage` couvre les 9 bases 1-9 ; chaque loi citée dans `_routage` existe dans `lois.json`.
4. `pytest` vert de bout en bout avant de rendre.

## Définition de « terminé »
- [ ] `_distillation/verif_cycle_neuf_ans.md` rédigé ; `annees_detail.json` retouché seulement si nécessaire.
- [ ] `data/corpus/lois.json` : 17 lois + `_routage` (bases 1-9), langage clair tenu, anti-mur respecté.
- [ ] `tests/test_style.py` : `lois` au cliquet, cibles vertes.
- [ ] test anti-plagiat vert.
- [ ] `pytest` vert.
- [ ] Un échantillon de 3 lois relu à voix haute : ça sonne comme quelqu'un qui parle.

## ⚠️ Rappel de cadence (mémoire projet)
La rédaction de masse du corpus est une tâche de **phase Sonnet**. Opus prépare ce brief et validera à la
fin (grep tics, `test_style.py`, relecture). La **bascule `/model` est manuelle** : à la phase Sonnet,
Opus s'arrête et demande la bascule à Martin — pas de sous-agents.
