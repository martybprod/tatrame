# Le message du jour — enrichissement et routeur multi-disciplines

> Doc exploratoire, rédigé le 2026-07-17. Répond à trois demandes de Martin :
> (1) le message principal du jour manque de variété — l'enrichir ;
> (2) explorer un **routeur** qui, chaque jour, croise carte du ciel +
> numérologie + astrologie chinoise et **choisit la discipline la plus
> pertinente** plutôt que de toujours tout empiler ;
> (3) chiffrer le coût et dire si Sonnet peut s'en charger.
>
> Tout ce qui suit reste dans la thèse : **100 % déterministe, zéro LLM au
> runtime, zéro tirage.** Le LLM ne sert qu'à écrire le corpus hors ligne.

---

## 0. Le constat, mesuré

Le message principal du jour (le « miroir » + le « geste » en tête d'écran)
vient de la **dominante** : le transit le plus fort du jour. Son texte est lu
ainsi (`app.py`, `/api/jour`) :

```
transits_precis[transitante_classe_natale]   ← le précis, s'il existe
  sinon transits_generiques[transitante_classe]  ← le générique
```

État actuel du corpus `transits.json` :

| table | clé | entrées écrites | réellement atteignables |
|---|---|---|---|
| `transits_generiques` | `transitante_classe` | 30 | **15** |
| `transits_precis` | `transitante_classe_natale` | **0** | 0 |

**Pourquoi 15 et pas 30 ?** La dominante est toujours un *déclencheur*, donc
une planète **rapide** (`RAPIDES = lune, mercure, venus, soleil, mars`). Les
15 génériques des planètes lentes existent mais ne mènent jamais la journée :
elles ne sont pas le titre. Donc **le titre du jour puise dans ~15 textes**, et
**aucun ne nomme la partie de toi qui est touchée**. « La Lune bouscule quelque
chose » — jamais « la Lune bouscule ton Mars natal, ton élan ».

C'est là toute la marge. Deux chantiers, indépendants l'un de l'autre.

---

## Chantier A — enrichir le titre **sans** nouvelle discipline

**L'idée** : remplir `transits_precis`. Le moteur est **déjà prêt** — il essaie
le précis avant le générique. Il ne manque que le texte.

**L'espace exact** : 5 planètes rapides × 3 classes × 12 cibles natales
(les 10 planètes + Ascendant + Milieu du Ciel) = **180 entrées possibles**.
Chaque entrée peut **nommer** la cible : « Mars presse ton Soleil natal »
parle de ton identité et de ton allant ; « Mars presse ton Saturne natal »
parle de ta patience et de tes limites. Même transit, deux parties de toi,
deux messages.

**Le gain** : le titre du jour passe d'un pool de ~15 à jusqu'à **180**, et
surtout il devient **personnel** (il désigne le point natal réel touché, calculé
dans TON thème). C'est la variété qui vient du ciel réel, pas d'un tirage — la
thèse, appliquée au titre.

**C'est de l'ADDITION, pas un produit.** On n'écrit pas 10×3×12×(tous les
signes)… On écrit 180 entrées fixes, universelles, lues telles quelles. La règle
d'or tient (l'objection « travail titanesque » de Dryburgh reste respectée).

### Structure
Mêmes champs que le générique : `miroir` (~40 mots, le constat du jour) +
`geste` (~40 mots, une action concrète). Clé : `transitante_classe_natale`,
ex. `mars_carre-opposition_soleil`.

### Le piège à éviter (leçon des passes précédentes)
180 entrées « X touche ton Y natal » sont un terrain idéal pour le **mur du
corpus** : les rédacteurs tomberont dans un gabarit (« Aujourd'hui X réveille
ton Y, tu ressens… »). Parade, déjà éprouvée sur les nombres :
- rédiger **par cible natale** (un agent = tout ce qui touche ton Soleil natal),
  pas par gabarit — la cible donne le fond (Soleil = identité, Lune = besoins,
  Mars = élan, Saturne = limites…), la planète rapide donne la couleur ;
- **ne jamais donner un fichier-modèle** à recopier ;
- contrôle **par compte de suites de 8 mots partagées** (pas le Jaccard, trop
  laxiste), seuil strict, comme le garde-fou
  `test_les_nombres_ne_se_recopient_pas_sur_un_meme_chiffre`.

### Phasage proposé (maîtrise du coût)
Le précis **complète** le générique sans le remplacer : une entrée absente
retombe proprement sur le générique. On peut donc remplir **par vagues**, des
cibles les plus personnelles aux moins :
1. **Vague 1** — cibles luminaires + personnelles : Soleil, Lune, Vénus, Mars,
   Mercure natals. 5 rapides × 3 classes × 5 cibles = **75 entrées**.
2. **Vague 2** — cibles sociales/angles : Saturne, Jupiter, ASC, MC. **60**.
3. **Vague 3** — cibles lentes : Uranus, Neptune, Pluton. **45**.

Chaque vague est utile seule, testable, et le reste retombe sur le générique.

---

## Chantier B — le ROUTEUR et la métrique de saillance

**Le principe demandé par Martin** : ne pas toujours empiler les trois
disciplines. Un jour, c'est le ciel qui parle le plus fort ; un autre, c'est un
basculement numérologique ; un autre, l'astrologie chinoise. **Un routeur choisit
la voix du jour.**

### Ce que le routeur décide — et ce qu'il ne touche pas
Le routeur décide **uniquement du TITRE** (le grand message en tête). Tout le
reste de l'écran — l'année, le mois, la traversée de vie, la phase lunaire, la
carte de l'année — **reste affiché comme contexte**. Le routeur ne cache rien,
il **élit la voix qui mérite la grosse place aujourd'hui**. Risque minimal :
c'est une généralisation du `dominante = declencheurs[0]` actuel, étendue à
plusieurs disciplines.

### Les candidats (chacun émet une saillance normalisée s ∈ [0,1])
| candidat | d'où vient s | déjà calculé ? |
|---|---|---|
| **Ciel — transit** | la `force` de la dominante (0-1, déjà tunée) | ✅ oui |
| **Numérologie — bascule** | impulsion autour du 1er janvier (année) et du 1er du mois (mois), décroissante | à ajouter (trivial) |
| **Lune — pic** | impulsion autour de la Nouvelle/Pleine Lune exacte (`progression` déjà là) | ✅ presque |
| **Chinois — jour** | force de la relation entre le pilier du jour et le pilier natal (choc 沖 / harmonie 合 = fort, neutre = faible) | après lecture des livres |

### La formule (déterministe, stable)
Chaque candidat produit `s` par une **formule fixe** propre à sa discipline mais
comparable une fois normalisée :
- **transit** : `s = force_dominante` (une conjonction exacte de Mars sur ton
  Soleil ≈ 0,9 ; un sextile large de la Lune ≈ 0,3). Rien à inventer, ça existe.
- **bascule numéro** : `s = clamp(1 − distance_en_jours / fenêtre)`. Fenêtre
  année ≈ 5 j (gros événement), mois ≈ 2 j. Nul le reste du temps.
- **pic lunaire** : `s = clamp(1 − |progression_du_pic|)` sur Nouvelle et Pleine.
- **chinois** : `s = poids(relation pilier-du-jour ↔ pilier natal)`. À caler
  après les livres.

**Routeur = `argmax(s)`** avec un **départage fixe et documenté** en cas
d'égalité (ex. ciel > numéro > lune > chinois — ordre à figer). Déterministe de
bout en bout : `s` ne dépend que de (date de naissance, date du jour).

### Exemple
- Jour plat, mais 1er janvier → le ciel donne `s≈0,25`, la bascule d'année
  `s≈0,9` → **le titre devient « nouvelle année personnelle »**, pas un faible
  trigone de Lune.
- Mars exact sur ton Soleil natal, un 17 du mois → transit `s≈0,9` gagne, le
  reste reste en contexte.

### Anti-répétition
Le Chantier A dédensifie déjà énormément la voix « ciel ». Le routeur ajoute la
variété **inter-disciplines** les jours saillants. Option à **mesurer** : un
petit malus déterministe de « fraîcheur » (recalculer les gagnants des K
derniers jours — pure fonction de la date — et défavoriser légèrement une
discipline qui vient de gagner, pour départager les quasi- égalités). À n'ajouter
que si la validation empirique montre une monotonie.

### Validation AVANT d'écrire un mot de corpus
Le routeur se prototype **sans corpus, en Python pur** : simuler 365+ jours sur
plusieurs profils, journaliser la distribution des gagnants et le taux de
répétition du titre. On **règle les fenêtres et les poids** jusqu'à une
distribution saine (aucune discipline ne monopolise, répétition basse). Cette
étape est **gratuite en tokens** (aucun LLM) et dérisque tout le reste.

---

## Chantier C — l'astrologie chinoise : MOTEUR BÂTI ET VALIDÉ (2026-07-17)

`moteur/chinois.py` + `tests/test_chinois.py` (8 tests). Le mécanisme retenu :
la relation entre l'**animal du jour** (pilier du jour 干支) et l'**animal de
naissance** (pilier de l'année — ne demande que l'année, pas l'heure) donne une
**saillance 0-1** et une clé de corpus (`relation_animalNatal`, ex.
`choc_singe`). Relations : 沖 choc, 六合 harmonie, 三合 trine, 害 nuisance,
identité, neutre.

**Ce qui est validé (sans livre) :**
- Piliers d'année : 5/5 contre références connues (2020 庚子, 1984 甲子,
  2024 甲辰, 1972 壬子, 2000 庚辰).
- Frontière ~Li Chun (~4 fév) : un natif de janvier retombe sur l'animal de
  l'an d'avant.
- Structure des relations (chocs = oppositions, trines, harmonies).
- Cycle des jours continu (60 j).

**Ce qui reste À CONFIRMER sur Walters (via l'Archiviste) :**
1. **L'ancre du cycle des jours** — quelle date est un 甲子 (jiǎzǐ). Hypothèse
   actuelle : 2000-01-07. Ne change PAS la distribution des relations sur
   l'année, seulement quel jour porte quelle relation. Une seule date connue
   suffit à la caler.
2. **La convention de début d'année** — Nouvel An lunaire vs Li Chun 立春. À
   trancher et publier comme les conventions numérologiques.
3. **Le grounding interprétatif du corpus** — ce que « veut dire » chaque
   relation, dans les mots de Walters (pour ne pas écrire un horoscope
   générique). ~20-30 entrées additives (`relation × animal`, ou plus simple
   `relation` seule si le sens ne dépend pas de l'animal).

**Validation du routeur À 4 VOIX (365 jours réels) :**

| voix | 3 voix | **4 voix** |
|---|---|---|
| ciel | 95 % | **71 %** |
| chinois | — | **26 %** |
| lune | 3 % | 2 % |
| numéro | 2 % | 1,4 % |

La 4ᵉ voix **rééquilibre la distribution sans réglage** : le ciel reste la voix
du quotidien, le chinois devient un solide second (~26 %), numéro/lune restent
des ponctuations rares. La moitié des jours sont neutres côté chinois (il se
tait). C'est la **lecture A** (« le ciel mène, les autres interrompent quand
c'est saillant »), désormais variée grâce au chinois — sans malus de fraîcheur.

### Reste de l'esquisse (hypothèses confirmées par la construction)

- La brique qui a du sens pour un message **quotidien déterministe**, c'est le
  **pilier du jour** (干支 du jour, cycle sexagésimal) croisé au **pilier natal**
  (au minimum l'**animal + élément de l'année de naissance**, calculable sans
  heure exacte). Les relations classiques entre branches — **六合** (harmonie),
  **三合** (trine), **沖** (choc/opposition), **害/刑** — donnent une saillance
  naturelle : un jour en choc avec ton animal natal « parle fort ».
- Cela reste **100 % calculable** et déterministe (le pilier du jour est une
  fonction du calendrier ; l'animal natal, de l'année — le calendrier chinois
  demande juste la date du Nouvel An lunaire, tabulable).
- Corpus visé : les **relations** (harmonie/choc/neutre × contexte), en
  **addition** — pas les 60×60 combinaisons de piliers (produit interdit).

**Questions ouvertes pour après les livres :**
1. Quelle profondeur natale ? Année seule (animal+élément), ou aussi mois/jour
   (pilier du jour de naissance) ? L'année seule suffit-elle pour un message
   quotidien pertinent ?
2. Quel Nouvel An de référence (lunaire vs solaire 立春) ? À trancher et publier,
   comme les conventions numérologiques.
3. Le cycle des **10 000 caractères / cycles de chance** (大運/流年) est-il dans
   les livres, et pertinent, ou hors-scope pour du quotidien ?
4. Combien de relations distinctes à écrire (l'ordre de grandeur des ~20-40
   entrées additives) ?

---

## Validation du prototype — résultats (2026-07-17)

Le routeur est **codé** (`moteur/routeur.py`) et **simulé sur 365 jours de ciel
réel** pour trois profils (aucun LLM, aucune rédaction). Résultat :

| profil | ciel | numéro | lune | chinois | titres « ciel » DISTINCTS (clé précise) |
|---|---|---|---|---|---|
| Martin | 95,1 % | 2,2 % | 2,7 % | 0 % | **102** |
| Julie | 95,3 % | 1,1 % | 3,6 % | 0 % | **114** |
| Kevin | 95,6 % | 1,1 % | 3,3 % | 0 % | **117** |

**Deux enseignements majeurs :**

1. **Le Chantier A est validé et chiffré.** Une année produit **~100 à 117
   titres « ciel » DISTINCTS** (clé précise `transitante_classe_natale`), contre
   ~15 aujourd'hui. Remplir `transits_precis` multiplie la variété du titre par
   ~7, et chaque titre nomme le point natal touché. Les plus fréquents
   (`lune_carre-opposition_soleil`, ~12×/an) sont les aspects mensuels de la
   Lune — inévitables, mais gérables avec un bon corpus.

2. **Le ciel monopolise le titre à ~95 %** — et c'est une **décision de produit
   à trancher**, pas un bug. Le ciel change tous les jours (c'est la thèse), donc
   il gagne par défaut ; numéro et lune ne surgissent que sur leurs pics rares
   (nouvel an, changements de mois, Nouvelle/Pleine Lune). Deux lectures :
   - **(A) « le ciel est la voix du quotidien »** — les autres voix
     n'interrompent que sur les vrais grands moments. C'est honnête et propre, et
     le Chantier A rend ces 95 % de jours-ciel très variés. Le réglage actuel.
   - **(B) « plus de rotation »** — tu veux entendre plus souvent la
     numérologie, la lune, le chinois. Il faudrait alors relever leurs poids
     (ex. garantir que le 1er du mois la bascule mensuelle prenne la tête, ou
     ajouter le malus de fraîcheur).

   ⚠️ Ce réglage se **finalisera après avoir branché la voix chinoise**, qui
   ajoutera une 4ᵉ source de saillance et déplacera la distribution. Régler le
   curseur maintenant serait prématuré. La bonne séquence : brancher le chinois,
   re-simuler, puis choisir A ou B avec les vrais chiffres.

**« Plus longue série identique » : 58 à 88 jours** — mais c'est la même VOIX
(« ciel »), pas le même TITRE : le contenu change chaque jour. Ce n'est une
répétition à corriger que si l'on veut plus de rotation (lecture B).

---

## Coût et « Sonnet peut-il ? »

Deux natures de travail, à ne pas confondre :

- **Le code** (routeur, métrique de saillance, calcul du pilier chinois, harnais
  de validation) : **peu coûteux**, c'est de la logique déterministe. Le
  prototype du routeur ne consomme quasiment rien (pas de LLM). À faire en Opus
  par prudence d'architecture, mais c'est léger.
- **Le corpus** (les 180 entrées précises du Chantier A, puis les messages
  chinois) : c'est **le gros du coût en tokens**, mais c'est un travail
  **mécanique et bien cadré** — exactement ce que **Sonnet fait bien** et moins
  cher. On garde Opus pour l'architecture et les garde-fous anti-répétition,
  Sonnet pour la rédaction en série.

**Ordre de grandeur** (indicatif) : le Chantier A complet ≈ 180 entrées × ~80
mots ≈ 14 000 mots de corpus, comparable aux passes « aspects » ou « nombres »
déjà faites. Faisable **par vagues** pour lisser la dépense, chaque vague
livrant une amélioration utilisable seule.

---

## Ordre de marche proposé

1. **Prototype du routeur en Python pur** (métrique + validation 365 j), zéro
   corpus, zéro token de rédaction → on voit la distribution et on règle.
2. **Chantier A, vague 1** (75 entrées précises, cibles personnelles) → le titre
   du jour gagne d'un coup en variété et en personnalisation. Sonnet.
3. **Petit corpus de titres** pour les voix numéro-bascule et pic-lunaire (~5
   entrées) → le routeur a de quoi parler quand il élit ces voix.
4. **Chantier C** après lecture des livres chinois : conventions tranchées,
   calcul du pilier, corpus des relations.
5. Vagues 2 et 3 du Chantier A au fil de l'eau.

Chaque étape est **indépendante, testable, et retombe proprement** si la
suivante n'est pas encore là. Rien ne casse la thèse déterministe.
