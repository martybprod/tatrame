# Charte éditoriale d'Align

> Toute entrée du corpus respecte ce document. Sans exception.
> Il n'est pas décoratif : **c'est le produit**. Le moteur calcule, la charte parle.

---

## Le principe fondateur

Align ne prédit rien. Align **tend un miroir**.

L'argument n'est pas un habillage marketing, il vient de la source même de la philosophie
qui inspire l'app. Osho, dans *The Further Shore* :

> « Whenever we are doing anything – astrology, future suggestion, horoscope-readings,
> palmistry, i ching, tarot – anything that is concerned with the future, it is basically
> **a reading of the unconscious of the person. It has nothing much to do with the future.** »

Il ne rejette pas ces outils : **il redéfinit leur objet**. Ils ne lisent pas l'avenir, ils
lisent le conditionnement présent. Donc :

- **Un calcul ne prédit pas. Il cartographie un conditionnement hérité pour permettre de s'en défaire.**
- La date de naissance n'est pas un destin, c'est un **point de départ**.
- Formulation-type : *« Voici le schéma que tu as reçu — non pour t'y enfermer, mais pour que tu le voies. »*

**Corollaire honnête, à assumer sans s'excuser** : l'astrologie n'a aucune validité prédictive
démontrée. Align ne prétend pas le contraire. Sa valeur est dans la réflexion qu'elle déclenche,
pas dans la véracité d'un signal. C'est dit dans l'app, en clair.

---

## Les quatre règles de rédaction

### 1. Recadrer en conditionnement, jamais en faute
Séquence : **constat → normalisation → déculpabilisation → apprentissage**.

- ✅ « Tu remets à demain ce qui te fait peur. C'est humain, et ça se travaille. »
- ❌ « Tu es procrastinateur. »

### 2. Désigner le système, jamais l'individu
La personne n'est pas coupable. Elle est la cible d'un mécanisme.

- ✅ « On t'a appris à te taire pour ne pas déranger. »
- ❌ « Tu n'oses pas t'affirmer. »

### 3. L'humour comme désamorçage
Le jeu qui inspire l'app parle des « *so-called* negative cards » — **il refuse la catégorie**.
Align aussi. Une tension n'est pas un mauvais présage : c'est l'endroit où il y a du travail,
donc l'endroit intéressant.

### 4. Le registre est CONSTATIF
- ✅ « Tu es en train de… » — présent, observable, non moral
- ❌ « Tu es… » — essentialisation, verdict
- ❌ « Tu vas… » — prédiction, et fausse

---

## Le cadrage qui vient de l'astrologie française

*« Bon thème, mauvais thème, peu importe ! »* Une énergie n'est ni bonne ni mauvaise :
**elle existe**. Un « mauvais » thème signifie seulement que les énergies « ne disposent pas
de canaux d'expression adaptés ».

→ **Le conseil du jour ouvre un canal d'expression. Il ne fait jamais subir un transit.**

Les trois autrices lues convergent sur le libre arbitre — « never depend upon astrology to make
decisions for you » ; des repères « pour éveiller ta réflexion, pas des *il faut* ».

---

## La forme

### Structure d'une entrée de portrait
Empruntée à la structure de la source numérologique (une **structure** n'est pas un texte) :

1. **Ce qui anime** — la poussée, nommée sans jugement
2. **Comment l'alimenter** — le canal d'expression qui convient
3. **Ce qui arrive si on ne l'alimente pas** — la version contrariée, décrite sans menace

### Structure d'une entrée du jour
1. **Le miroir** — une phrase. Ce qui se joue, au présent.
2. **Le pas** — une action concrète, faisable aujourd'hui, petite.

*(Le champ JSON historique reste `geste` — 250+ entrées, pas de migration. Mais à
l'écran on affiche « Le pas » : « Le Geste » est déjà une position numérologique
d'Align, un même mot ne peut pas nommer deux choses. Et un cap se tient pas à pas.
Les deux libellés affichés — Le miroir, Le pas — sont des constantes uniques dans
`templates/index.html` : `LBL_MIROIR` / `LBL_PAS`.)*

### Les trois phases (approche / cœur / retrait) — TROIS QUESTIONS, pas trois intensités

Un transit serré domine plusieurs jours de suite. Pour qu'un même passage ne
radote pas, l'entrée existe en trois variantes — **mais ce ne sont pas la même
scène à trois intensités**. C'est le défaut qui tue : trois paraphrases du même
constat, où l'utilisateur a l'impression de relire le même texte. Chaque phase
répond à une **question différente** du lecteur, et change donc d'OBJET :

| Phase | Question du lecteur | Ce qu'elle apporte de NEUF | Le geste |
|---|---|---|---|
| **approche** | *Comment vais-je reconnaître que ça commence ?* | Un **signal faible** précis : le détail concret, corporel ou situationnel, par lequel le transit se fait connaître *avant* de parler fort. | Observer, nommer — sans agir. Un repérage, une notation. |
| **cœur** | *Qu'est-ce que ça fait, là, au plus fort ?* | Le **vécu présent** à son intensité, et la mécanique précise que seul le sommet révèle (pourquoi ça cogne, ce qui se joue maintenant). | Une action concrète, celle qui marche au moment du pic. |
| **retrait** | *Qu'est-ce qu'il reste, quand ça lâche ?* | Le **résidu** : un enseignement, un changement durable, un repère pour la prochaine fois. Regard en arrière ou en avant, jamais le présent immédiat. | Garder une trace, tirer la leçon, préparer la suite. |

**Le test qui tranche** : si on peut résumer les trois phases par le même constat,
c'est raté — c'est de la reformulation. approche parle d'un *signal* (ce qui
s'installe), cœur d'un *vécu* (le pic), retrait d'un *résidu* (ce qui reste).
Trois objets différents, difficiles à paraphraser.

*La phase affichée est dérivée du ciel réel (exactitude + direction applicative),
voir `app.py::_phase_du_transit`. Une entrée à texte unique (`miroir`+`geste`) reste
valide ; la convertir en trois phases n'est obligatoire que pour les passages qui
dominent plusieurs jours (sinon le texte gèle sur « cœur »).*

### Longueurs
| Type | Cible |
|---|---|
| Portrait (nombre, arcane, signe) | 120-180 mots |
| Jour (miroir + geste) | 30-85 mots |
| Nuance / modulation | 20-40 mots |

---

## Le tutoiement

Align **tutoie**. Chaleureux, direct, jamais familier jusqu'à la désinvolture.
Le ton d'un ami lucide qui te connaît bien — pas d'un oracle, pas d'un coach de performance.

**Ce qu'on n'est pas** : le ton cinglant et anxiogène qui a fait le succès d'une app américaine
et qui lui vaut aujourd'hui le reproche d'attiser l'angoisse pour retenir l'attention.
Align assume d'être doux. C'est un positionnement, pas une timidité.

---

## ⚠️ LE STYLE — le chantier de la 3e passe d'usage

> Retour de Martin : *« On a un chantier important sur la manière de parler. Le vocabulaire ou la
> manière de tourner les phrases est parfois difficile d'approche. »*

**Le diagnostic, mesuré sur les 131 000 mots** — le problème n'est PAS la longueur des phrases
(médiane 15 mots, c'est bien). C'est que **le corpus écrit en aphorismes** : sur 8 565 phrases,
**1 363 tirets cadratins** et **1 728 deux-points**. Plus d'une phrase sur trois porte une chute.

**Et ce n'est pas un défaut de qualité, c'est un défaut de DENSITÉ.** « Le Diable n'est pas en toi,
il est dans le catalogue » est excellent. Mais quand *chaque* phrase veut placer sa formule, aucune
ne porte, et le lecteur doit se battre pour entrer. **Un ami lucide ne parle pas en aphorismes.**

*(Honnêteté sur l'origine : mes propres consignes ont produit ça, en poussant les rédacteurs à la
variété et à la formule sans jamais leur donner le droit d'être simples.)*

### La règle d'or

> **UNE chute par entrée, pas par phrase.**
> Le reste est plat, parlé, facile. Une phrase a le droit de ne rien prouver.

### Les quatre tics à tuer

| Tic | ❌ | ✅ |
|---|---|---|
| **1. Le concept abstrait en sujet** *(258 cas)* | « L'action, ici, se joue en silence. » | « Tu agis en silence. » |
| **2. La chute au tiret** *(393 cas)* | « On te remarque, on te propose — et la visibilité ne trie pas : elle amplifie. » | « On te remarque, on te propose. La visibilité ne trie pas. Elle amplifie tout. » |
| **3. Le deux-points aphoristique** *(1 728 cas)* | « Le désir de trancher : ça fait des mois qu'une situation traîne. » | « Ça fait des mois qu'une situation traîne, et l'envie de trancher monte. » |
| **4. Le verdict nié en ouverture** *(206 cas)* | « Ce n'est pas de la lâcheté — on t'a appris… » | « On t'a appris qu'il fallait être prêt. Personne ne l'est jamais. » |

### Cibles chiffrées (mesurées par `tests/test_style.py`)

| Mesure | Avant | Cible |
|---|---|---|
| Tirets cadratins / 100 phrases | 15-25 | **< 8** |
| Deux-points / 100 phrases | 17-30 | **< 10** |
| Ouvertures sur un concept abstrait / 100 | 0-6 | **< 3** |
| « Ce n'est pas… » en ouverture / 100 | — | **< 2** |

### Le test qui tranche, version style

Lis l'entrée **à voix haute**. Si tu dois reprendre ton souffle au milieu d'une phrase, ou si tu
t'entends « faire une phrase », c'est à réécrire. **Ça doit sonner comme quelqu'un qui te parle,
pas comme quelqu'un qui écrit.**

### Ce qu'on NE touche PAS

- Le **fond** : les scènes concrètes, les constats justes, le recadrage en conditionnement.
- Les **aphorismes qui portent vraiment** — un par entrée, gardé, à sa place.
- La **vulgarisation** déjà acquise.

**On ne réécrit pas ce qui est dit. On réécrit la façon de le dire.**

### Comprendre à la première lecture (langage clair)

> Retour de bêta-testeurs (2026-08-19) : *les phrases sont parfois trop difficiles, trop
> « littéraires ».* La règle des aphorismes ci-dessus règle la DENSITÉ ; celle-ci règle la
> COMPRÉHENSION. Fondée sur *Oxford Guide to Plain English* (Cutts) et *Écrire pour le Web* (Gani).

**Le principe** : tout ce que dit Align doit être compris **du plus grand nombre, à la première
lecture**. On écrit pour un âge de lecture d'environ 13 ans (Cutts) — *4 Français sur 10 ne
comprennent pas ce qu'ils lisent* (Gani). Clair ne veut PAS dire bébête : la simplicité n'est
pas de la condescendance. On garde la finesse, on enlève l'effort.

**Les cinq réflexes :**

1. **Dire QUOI, concrètement.** Le lecteur ne doit jamais se demander « de quoi on parle ? ».
   - ❌ « Entre vous, ça chauffe vite et fort. » *(chauffe quoi ? comment ?)*
   - ✅ « L'un de vous agit vite, l'autre a besoin de temps pour sentir les choses. »
2. **Le mot de tous les jours**, pas le mot chic. Concret plutôt qu'abstrait.
   - ❌ « une intensité rare, à doser » · ✅ « c'est fort entre vous, et il faut trouver la bonne mesure »
3. **Verbes actifs, ordre naturel** (sujet → verbe → complément). Pas de participe détaché, pas
   d'inversion « littéraire ».
   - ❌ « Trouvé à deux, le bon dosage transforme… » · ✅ « À deux, vous trouvez la bonne mesure, et… »
4. **Une seule image par entrée, et limpide.** L'image est permise (c'est une force d'Align) mais
   **jamais deux empilées, jamais une qu'il faut décoder**. Si l'image demande un effort, on dit la
   chose en clair à la place. *(Cela affine la consigne antérieure « images riches et variées » :
   désormais une image FORTE et CLAIRE, pas plusieurs.)*
5. **Le test de la première lecture.** Si une phrase demande une relecture pour être comprise, on
   la coupe ou on la réécrit. Complète le test « à voix haute » ci-dessus.

**Registre québécois d'abord (France ensuite).** Le public visé est **québécois en premier**.
On écrit un français **standard, compris partout**, mais on **évite les tics hexagonaux** qui
sonnent étrangers à une oreille québécoise — et on **ne tombe pas dans le joual** (qui perdrait la
France et le registre soigné). Le naturel québécois, pas le folklore.

| ❌ Tic hexagonal | ✅ Neutre / québécois |
|---|---|
| « du coup » | « résultat, » · « alors » · rien du tout (couper) |
| « rien ne prend » | « ça reste froid » · « ça marche pas » |
| « un truc », « bosser », « carrément », « grave » | le mot standard |

*(À l'inverse, on n'écrit pas en joual — pas de « pantoute », « pogner », « niaiser » : ça exclurait
la France et casserait le ton. Le curseur : ce qu'un Québécois dirait sans y penser, qu'un Français
comprend sans effort.)*

**Ce qui ne change pas :** le fond, le recadrage en conditionnement, la chaleur, le non-verdict,
et « une chute par entrée ». On enlève l'effort de lecture, pas la justesse.

---

## Les conventions de calcul — publiées, jamais tues

Align **affiche ses règles** (écran « Les Règles », `/api/conventions`), et dit pour chacune si
elle est **imprimée dans une source** ou **tranchée par Align** là où les sources se taisent.

C'est un angle mort du marché : deux conventions contradictoires coexistent en numérologie
française (É = 5 comme E, ou é = 1 avec sa valeur propre), **elles donnent des résultats différents
pour le même nom, et aucune app ne dit laquelle elle applique**. Se prétendre déterministe sans
publier ses règles n'aurait aucun sens — le déterminisme doit être *reproductible* **et**
*auditable*.

| Règle | Décision | Provenance |
|---|---|---|
| **Accents** | transparents — É = 5 comme E | **imprimé** (et confirmé par STÉPHANE = 34) |
| **Trait d'union** | ne fusionne pas — deux unités | **imprimé** |
| **Apostrophes** | ignorées — D'Artagnan → DARTAGNAN, un mot | **tranché par Align** |
| **Particules** | **gardées**, soudées au nom : de Gaulle → DEGAULLE | **tranché par Align** |
| **Année personnelle** | bascule le **1er janvier** | **tranché**, appuyé sur les sources |

*Les particules **comptent** : la source exige l'état civil EXACT, or « de Gaulle » **est** l'état
civil. Rien n'est jeté. Mais une particule n'est pas un nom — elle en introduit un : elle se soude
donc au mot qui suit, et l'unité de calcul reste le nom civil entier. Même règle que l'apostrophe :
élidée (D'Artagnan) ou espacée (de Gaulle), une particule se comporte pareil.*

*🔢 **Une élégance arithmétique à connaître** : « de » = D(4) + E(5) = **9**, et 9 est l'élément
neutre des racines numériques — ajouter « de » ne change donc **jamais** la valeur finale. Ce n'est
pas un hasard, c'est une nécessité. Mais ça décale la somme brute de 9, et **le sous-nombre, lui,
bascule** : « Caza » vaut 13 (un héritage), « de Caza » vaut 22 (un maître). Écarter les particules
aurait été invisible sur la valeur et pourtant destructeur sur la lecture fine — la meilleure raison
de les garder.*

### Deux horloges, et c'est voulu

- La couche **numérologique** bat sur le **calendrier** (année personnelle, carte de l'année).
- La couche **astrologique** bat sur l'**anniversaire** (le retour solaire, quand le Soleil
  retrouve son degré natal — de l'astronomie, pas une convention).

Elles ne se contredisent pas : ce sont des **tables indépendantes qu'on additionne**, jamais un
produit. Les forcer à s'aligner serait une élégance de façade, payée d'une infidélité aux deux
sources.

---

## Le vocabulaire d'Align

Notre métaphore est celle de l'**orientation** — accordée au nom. Elle est **originale** :
le vocabulaire de la source numérologique (arbre, racines, tronc, écorce, branches, feuilles,
fruits, « triangle fondamental », « dynamique de vie », « mémoire familiale ») relève d'une
marque déposée et n'est **jamais** employé.

### ⚠️ Ce qui est interdit, c'est la MÉTAPHORE — pas les mots français

Précision qui a manqué et qui a fait des dégâts : l'interdit porte sur **le système d'images
appliqué aux NOMBRES**, pas sur les mots eux-mêmes dans leur usage ordinaire.

| ❌ Interdit | ✅ Permis |
|---|---|
| « ta **racine** » pour désigner un nombre | « tes **racines** » = ta famille, d'où tu viens *(c'est le nom d'Align pour la maison 4)* |
| « ton **tronc** », « ton **écorce** » | « le **tronc** d'un arbre » dans une image ordinaire |
| « tes **fruits** » pour un nombre | « les **fruits** de ton travail » |

**Le test** : est-ce que le mot sert à NOMMER une position numérologique ? Alors non. Sinon, c'est
du français, et le français est à tout le monde.

*(Vécu : une consigne « jamais racine » a poussé des rédacteurs à réécrire quatre passages
parfaitement innocents — dont « un rapport instable aux racines », qui parlait de famille. Une
interdiction trop large coûte du texte juste et ne protège de rien de plus.)*

| Terme Align | Ce que c'est |
|---|---|
| **Le Cap** | la direction de fond |
| **La Voix** | ce qui s'exprime au-dehors |
| **Le Foyer** | le centre intérieur |
| **Le Reflet** | l'image renvoyée |
| **Le Geste** | la manière d'agir |
| **La Source** | ce qui nourrit affectivement |
| **La Trace** | ce qu'on cherche à accomplir |
| **L'Élan** | l'énergie de l'ensemble |
| **Les Héritages** | ce qui a été reçu (13/14/16/19) |
| **Les Frictions** | les écarts à travailler |
| **Les Appuis** | les qualités présentes |
| **Les Chantiers** | les qualités à construire |

**« Héritage » et « chantier », pas « dette » ni « manque ».** Le choix des mots *est* la charte :
on ne doit rien, on a reçu ; il ne manque rien, il y a à bâtir.

---

## Interdits absolus

### Juridiques
- ❌ Le nom « Osho », « Osho Zen Tarot », ses noms de cartes, ses images, ses textes.
  Marque UE valide (confirmée définitivement en 2017), images © 1994, textes protégés jusque ~2060.
  **On s'inspire de la philosophie — libre. On ne touche pas au jeu.**
- ❌ « Numérologie Stratégique® », « arbre personnel », « triangle fondamental » — marque INPI.
- ❌ Tout texte des ouvrages de référence. Ils donnent le **schéma de données**
  (quels axes, quelle granularité, quelle longueur), **jamais la prose**.

### Éditoriaux
- ❌ Prédire un événement (« tu rencontreras… »)
- ❌ Prescrire (« tu dois… », « il faut… »)
- ❌ Essentialiser (« tu es quelqu'un de… »)
- ❌ Faire peur pour retenir l'attention
- ❌ Flatter sans contenu
- ❌ Jargon non expliqué (« ton Saturne en maison XII est en carré… »)
- ❌ Énumérer. **Une** chose par jour.

---

## Le mur du corpus

Une app déterministe meurt de la **répétition**, pas du calcul. Le reproche fait à une app
concurrente est sans appel : *« les readings cessent de sembler personnels dès qu'on voit les
cinq mêmes descripteurs recyclés chez tous ses amis »*.

**Trois parades, toutes structurelles :**
1. **Additionner des tables indépendantes, jamais les multiplier.** On écrit N + M entrées,
   pas N × M. Le produit cartésien est un piège : il explose en centaines de milliers de cas.
2. **La variété vient du ciel réel**, qui bouge tout seul. Aucun tirage, jamais.
3. **Chaque entrée doit tenir seule.** Si elle pourrait s'appliquer à n'importe qui,
   elle est à réécrire.

**Le test qui tranche** : lis l'entrée en te demandant *« est-ce que ça pourrait être écrit
dans un horoscope de magazine ? »* Si oui, jette et recommence.
