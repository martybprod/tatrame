# Charte éditoriale de l'app tarot

> Toute entrée du corpus respecte ce document. Sans exception.
> Il n'est pas décoratif : **c'est le produit**. Le moteur calcule, la charte parle.
>
> Cette charte reprend **à l'identique** les règles d'Align (Ta Trame), que Martin a façonnées
> passe après passe. Seuls les exemples et les sections spécifiques sont retargetés pour le tarot.
> La structure (schémas, tirages, moteur) est définie dans `GRAMMAIRE.md` ; la voix est définie ici.

---

## Le principe fondateur

L'app tarot ne prédit rien. Elle **tend un miroir**.

L'argument n'est pas un habillage marketing, il vient de la source même de la philosophie
qui inspire les deux apps. Osho, dans *The Further Shore* :

> « Whenever we are doing anything – astrology, future suggestion, horoscope-readings,
> palmistry, i ching, **tarot** – anything that is concerned with the future, it is basically
> **a reading of the unconscious of the person. It has nothing much to do with the future.** »

Il ne rejette pas ces outils : **il redéfinit leur objet**. Le tarot ne lit pas l'avenir, il
lit le moment présent. Donc :

- **Un tirage ne prédit pas. Il montre un état du présent pour permettre d'agir dessus.**
- Une carte tirée n'est pas un destin, c'est un **éclairage**.
- Formulation-type : *« Voici ce qui se joue en ce moment — non pour t'en enfermer, mais pour que tu le voies. »*

**Corollaire honnête, à assumer sans s'excuser** : le tarot n'a aucune validité prédictive
démontrée. L'app ne prétend pas le contraire. Sa valeur est dans la réflexion qu'il déclenche,
pas dans la véracité d'un signal. C'est dit dans l'app, en clair.

---

## Les quatre règles de rédaction

### 1. Recadrer en conditionnement, jamais en faute
Séquence : **constat → normalisation → déculpabilisation → apprentissage**.

- ✅ « Tu retiens ce qui devrait partir. C'est humain, et ça se travaille. »
- ❌ « Tu es accroché au passé. »

### 2. Désigner le système, jamais l'individu
La personne n'est pas coupable. Elle est la cible d'un mécanisme.

- ✅ « On t'a appris à tenir bon plus longtemps que raison. »
- ❌ « Tu n'oses pas lâcher. »

### 3. L'humour comme désamorçage
Le jeu qui inspire l'app parle des « *so-called* negative cards » — **il refuse la catégorie**.
L'app aussi. Une carte dure n'est pas un mauvais présage : c'est l'endroit où il y a du travail,
donc l'endroit intéressant. La Rupture, l'Emprise, la Tristesse se lisent comme les autres :
une tension nommée, jamais une menace.

### 4. Le registre est CONSTATIF
- ✅ « Tu es en train de… » — présent, observable, non moral
- ❌ « Tu es… » — essentialisation, verdict
- ❌ « Tu vas… » — prédiction, et fausse

---

## Le cadrage qui vient des sources du tarot

*« Bonnes cartes, mauvaises cartes, peu importe ! »* Une carte n'est ni bonne ni mauvaise :
**elle existe**. Pollack, Wen et Greer convergent : une qualité ne vaut que dans le contexte
du moment, et aucune carte n'annonce quoi que ce soit.

→ **La lecture ouvre un canal d'expression. Elle ne fait jamais subir un tirage.**

Les trois autrices lues convergent sur le libre arbitre — la lecture sert la lucidité,
jamais la décision. Des repères « pour éveiller ta réflexion, pas des *il faut* ».

---

## La forme

### Structure d'une fiche-carte
Définie dans `GRAMMAIRE.md` §2 et `data/grammaire/carte.schema.json` — la charte ne la répète pas.
Rappel des champs texte : `mots_cles`, `tension`, `lumiere`, `ombre` (+ `issue`), `questions`,
`lecon`, `image` (geste, seuil, détail), `micro_geste`, et un texte par **position** de tirage.

### Structure de la carte du jour
Quatre temps (voir → écouter → nuancer → faire), définis dans `GRAMMAIRE.md` §4.1.

### Le principe des libellés — un même mot ne peut pas nommer deux choses
Leçon héritée d'Align (« Le Geste » déjà pris par une position numérologique → l'écran dit
« Le pas »). L'app tarot **n'emprunte pas les libellés d'Align** (Le Cap, La Voix, Le Foyer,
Le Reflet, Le Geste, La Source, La Trace, L'Élan) : ce sont les constantes d'une autre app.
Les libellés de nos écrans seront définis en phase 2, uniques dans l'app.

### Longueurs
| Type | Cible |
|---|---|
| Texte de position (tirage) | 50-85 mots |
| Liaison entre cartes | 20-40 mots |
| Phrase de seuil | 15-30 mots |
| Clôture | 40-70 mots |
| `lumiere` / `ombre` | 50-85 mots |
| `questions`, `lecon`, `micro_geste` | 1 phrase |

*(Align : jour 30-85, portrait 120-180, nuance 20-40. Nos types diffèrent ; la discipline est
la même — chaque cible est mesurée par les tests, `tables.json.seuils_moteur`.)*

---

## Le tutoiement

L'app **tutoie**. Chaleureux, direct, jamais familier jusqu'à la désinvolture.
Le ton d'un ami lucide qui te connaît bien — pas d'un oracle, pas d'un coach de performance.

**Ce qu'on n'est pas** : le ton cinglant et anxiogène qui a fait le succès d'une app américaine
et qui lui vaut aujourd'hui le reproche d'attiser l'angoisse pour retenir l'attention.
L'app assume d'être douce. C'est un positionnement, pas une timidité.

---

## ⚠️ LE STYLE — la règle d'or et les quatre tics

**Le diagnostic d'Align, mesuré sur les 131 000 mots** : le problème n'est pas la longueur des
phrases, c'est que **le corpus écrit en aphorismes** — plus d'une phrase sur trois porte une chute
(tirets cadratins, deux-points). Ce n'est pas un défaut de qualité, c'est un défaut de **densité**.
Quand *chaque* phrase veut placer sa formule, aucune ne porte, et le lecteur doit se battre pour
entrer. **Un ami lucide ne parle pas en aphorismes.**

### La règle d'or

> **UNE chute par entrée, pas par phrase.**
> Le reste est plat, parlé, facile. Une phrase a le droit de ne rien prouver.

### Les quatre tics à tuer

| Tic | ❌ | ✅ |
|---|---|---|
| **1. Le concept abstrait en sujet** | « Le passage, ici, se joue en silence. » | « Tu traverses ça en silence. » |
| **2. La chute au tiret** | « On te remarque, on te propose — et la visibilité ne trie pas : elle amplifie. » | « On te remarque, on te propose. La visibilité ne trie pas. Elle amplifie tout. » |
| **3. Le deux-points aphoristique** | « Le désir de trancher : ça fait des mois que ça traîne. » | « Ça fait des mois que ça traîne, et l'envie de trancher monte. » |
| **4. Le verdict nié en ouverture** | « Ce n'est pas de la lâcheté — on t'a appris… » | « On t'a appris qu'il fallait être prêt. Personne ne l'est jamais. » |

### Cibles chiffrées (mesurées par les tests du corpus)

| Mesure | Cible |
|---|---|
| Tirets cadratins / 100 phrases | **< 8** |
| Deux-points / 100 phrases | **< 10** |
| Ouvertures sur un concept abstrait / 100 | **< 3** |
| « Ce n'est pas… » en ouverture / 100 | **< 2** |

### Le test qui tranche

Lis l'entrée **à voix haute**. Si tu dois reprendre ton souffle au milieu d'une phrase, ou si tu
t'entends « faire une phrase », c'est à réécrire. **Ça doit sonner comme quelqu'un qui te parle,
pas comme quelqu'un qui écrit.**

### Ce qu'on NE touche PAS

- Le **fond** : les scènes concrètes, les constats justes, le recadrage en conditionnement.
- Les **aphorismes qui portent vraiment** — un par entrée, gardé, à sa place.
- La **vulgarisation** déjà acquise.

**On ne réécrit pas ce qui est dit. On réécrit la façon de le dire.**

---

## Le ton positif — de la privation vers la ressource

> Le ton penche trop souvent vers le manque. On le retourne vers la ressource —
> **sans jamais sacrifier la lucidité**.

**On retourne la FORME, jamais le fond.** La substance (le constat juste, la boussole, la clarté)
reste intacte ; seule la façon de la présenter passe de la privation à la ressource.

### Les quatre mouvements

| # | Le tic | ❌ | ✅ |
|---|---|---|---|
| **A. Le bon état dit par l'absence du mauvais** | « l'argent **ne te pèse pas** » | « **tu es plus tranquille** avec l'argent » |
| **B. Instruire par l'interdit** (dire quoi NE PAS faire) | « **Tu n'as pas à** suivre un rythme… » | « **Écoute** ton rythme, **avance** à ta mesure » |
| **C. Le qualificatif à revers** (sous-entend que la norme est mauvaise) | « …aujourd'hui, **pour une fois** » | *(on le supprime — il vole la bonne nouvelle qu'il annonce)* |
| **D. Cadrer autour d'un manque** plutôt qu'une ouverture | « mérite d'être écoutée, **pas dépassée par principe** » | « **mérite toute ton attention** » |

### Le garde-fou — pas de positivisme toxique

- **On ne nie JAMAIS une vraie tension.** Pour une carte dure, le positif =
  « voici l'ouverture, voici ce sur quoi tu as prise » (règle 3 : *la tension est l'endroit
  intéressant*), **jamais** « tout va bien ».
- **On garde les négations honnêtes et utiles** : « Rien de grave », « sans forcer »,
  « on ne brûle rien ». Ce n'est **pas** un chercher-remplacer de tous les « ne… pas ».

### Pense à Ginette

La lectrice-cible : **Ginette Tremblay**, peu d'éducation, mais elle aime qu'on lui parle
d'elle **clairement**. Tout doit lui être compréhensible du premier coup, **sans sacrifier le
style**. Un mot qui demande de l'éducation ou un décodage → du courant.
Quand Martin dit **« Pense à Ginette »**, c'est le rappel de relire de son point de vue.

### Comprendre à la première lecture (langage clair)

**Le principe** : tout ce que dit l'app doit être compris **du plus grand nombre, à la première
lecture**. On écrit pour un âge de lecture d'environ 13 ans (Cutts) — *4 Français sur 10 ne
comprennent pas ce qu'ils lisent* (Gani). Clair ne veut PAS dire bébête : la simplicité n'est
pas de la condescendance. On garde la finesse, on enlève l'effort.

**Les cinq réflexes :**

1. **Dire QUOI, concrètement.** Le lecteur ne doit jamais se demander « de quoi on parle ? ».
   - ❌ « Entre ces deux cartes, ça chauffe vite et fort. » *(chauffe quoi ? comment ?)*
   - ✅ « La première carte pousse vers l'action, la seconde demande d'attendre. »
2. **Le mot de tous les jours**, pas le mot chic. Concret plutôt qu'abstrait.
   - ❌ « une intensité rare, à doser » · ✅ « c'est fort, et il faut trouver la bonne mesure »
3. **Verbes actifs, ordre naturel** (sujet → verbe → complément). Pas de participe détaché, pas
   d'inversion « littéraire ».
   - ❌ « Trouvé à deux, le bon dosage transforme… » · ✅ « À deux, vous trouvez la bonne mesure, et… »
4. **Une seule image par entrée, et limpide.** L'image est permise (c'est une force du corpus)
   mais **jamais deux empilées, jamais une qu'il faut décoder**. Si l'image demande un effort, on
   dit la chose en clair à la place.
5. **Le test de la première lecture.** Si une phrase demande une relecture pour être comprise, on
   la coupe ou on la réécrit.

**Registre québécois d'abord (France ensuite).** Le public visé est **québécois en premier**.
On écrit un français **standard, compris partout**, mais on **évite les tics hexagonaux** qui
sonnent étrangers à une oreille québécoise — et on **ne tombe pas dans le joual**.

| ❌ Tic hexagonal | ✅ Neutre / québécois |
|---|---|
| « du coup » | « résultat, » · « alors » · rien du tout (couper) |
| « un truc », « bosser », « carrément », « grave » | le mot standard |

---

## Les leçons de la passe des messages du jour (Align, 2026-08 → 09) — toutes reprises

**1. Le jargon du moteur est interdit.** Le lecteur ne voit pas le moteur : le texte ne doit
pas raconter ses engrenages. On n'écrit jamais « en position de conseil », « le tirage indique »,
« la liaison feu-eau », « ce motif de répétition ». **L'écran montre la position ; le texte parle
de ta vie.** On écrit le vécu au présent, jamais la mécanique :

| ❌ | ✅ |
|---|---|
| « En position de conseil, la carte propose… » | « Tu peux essayer… » |
| « Cette liaison met en tension tes deux cartes » | « La première pousse, la seconde freine. » |
| « Le tirage signale une répétition du huit » | « Deux cartes disent la même chose : le mouvement. » |

**2. Les métaphores économiques sont interdites.** « coûte », « coûté », « plus cher »
transforment une journée en facture. On nomme l'**effort demandé**, la **perte** ou le
**manque** — jamais un prix :

| ❌ | ✅ |
|---|---|
| « Qu'est-ce que ça coûterait d'ouvrir la main ? » | « Qu'est-ce qui se passe quand tu gardes la main fermée une minute de plus ? » |
| « Voir grand te coûte moins cher » | « Voir grand te demande moins d'effort » |

**3. La temporalité suit le tirage, jamais un calendrier.** La carte du jour se dit
« **aujourd'hui** ». Le tirage à trois décrit « **en ce moment** ». Jamais de date, jamais de
« bientôt », jamais de délai.

**4. « Dedans » et « se sent » impersonnels sont interdits.** « ton dedans », « ce qui se
sent » détachent le ressenti de la personne. On le rattache à son sujet humain :
« ton dedans » → « **ton humeur** » ; « une lourdeur du dedans » → « **une lourdeur d'humeur** ».

**5. L'ouverture affirmative directe.** Commencer par la chose, pas par son absence :
« Il y a de la place à l'intérieur » → « **Tu es plus disponible à l'intérieur** ». Le
sujet en tête de phrase, la ressource, pas le constat clé en main.

**6. La déculpabilisation se varie, jamais en série.** Le « C'est qu'on t'a appris à… » est
puissant mais s'épuise à la répétition. Règle : **au plus un par entrée**, et on alterne les
formes — « par prudence plus que par peur », « une vieille habitude », « c'est un vieux
réflexe » — ou on le supprime quand ce n'est pas indispensable.

**7. Le « d'où ça vient » n'est pas obligatoire.** L'explication du réflexe se garde
**seulement quand elle éclaire**. Si elle ajoute de la longueur sans ajouter de compréhension,
on la coupe.

---

## La banque de formes — les textes de position (2026-10-21, reprise d'Align)

**Le diagnostic, mesuré sur le corpus Align.** 85 des 100 invitations ouvraient par
« Aujourd'hui » ; 21 passaient par « tu as envie de » ; 49 finissaient sur un impératif ;
la recette « une seule chose » revenait 20 fois. Chaque texte respectait la charte — c'est leur
**assemblage** qui formait un squelette unique : *ancrage → constat → envie → normalisation →
geste impératif*. Les tests comptaient les mots copiés (suites de 8), pas les formules :
ils n'ont rien vu.

**La règle.** Un texte de position adopte **une forme** prise dans la banque, et **la forme suit
ce que la carte est** — pas un dé, pas une rotation mécanique. On ne paraphrase pas le même
message : on change de geste d'écriture.

### La banque (7 formes)

| Forme | Ce qu'elle fait | Marqueur |
|---|---|---|
| **Météo** | le climat du jour posé sans adresse ni geste | « Certaines saisons ne montrent rien dehors… » |
| **Miroir** | renvoie un comportement observable, au présent | « Tu es en train de rester au bord d'un groupe… » |
| **Offre** | fait remarquer ce qui est déjà là | « Tu peux remarquer les endroits où… » |
| **Question** | la carte demande au lieu de prescrire | « Quelle chose concrète pourrait être ton premier indice ? » |
| **Permission** | lève une obligation, déculpabilise par le droit | « Tu as le droit d'ouvrir la main. » |
| **Image** | une seule image concrète et limpide porte le message | « Une plante ne demande pas la permission de fleurir. » |
| **Geste déguisé** | l'action dans une petite scène, jamais à l'impératif | « Quelqu'un lave sa tasse, les deux mains dessus. » |

### Le mapping — la forme suit la carte (indicatif, pas mécanique)

- **Un As** = une **Offre** (l'énergie neuve se remarque, elle ne se commande pas).
- **Un 5** = un **Miroir** (la friction s'observe avant de se corriger).
- **Une figure** (page, chevalier, reine, roi) = une **Permission** ou un **Geste déguisé**
  (une posture à s'autoriser, pas une tâche).
- **L'élément garde sa pente** : la Terre peut garder le geste concret (c'est sa nature),
  l'Air pose des questions, l'Eau donne des permissions, le Feu offre.
- La **Météo** reste le domaine des majeurs ; un mineur peut l'emprunter, rarement.
- **La position garde la sienne** : « ce que je peux essayer » privilégie le **Geste déguisé**
  et la **Permission** ; « ce qui se joue » privilégie le **Miroir** et la **Question**.

### Les plafonds (mesurés par les tests du corpus)

| Mesure | Plafond |
|---|---|
| « Aujourd'hui » en **ouverture** | ≤ 30 % des textes d'une famille |
| Chaque recette (« une seule chose », la durée imposée, « même petite ») | ≤ 8 % d'une famille, donc ~1 carte sur 14 |
| Une même forme | ≤ 3 cartes par famille de 14 |

- « Aujourd'hui » **en cours de texte** reste libre — seul l'ancrage systématique fatiguait.

---

## La description de la carte — décrire la carte, pas le prompt (règle Align, 2026-10-26, née sur NOTRE Huit de Terre)

**La règle — un élément ne reste que s'il a une fonction.** Trois fonctions, pas quatre :

| Fonction | Exemple (Huit de Terre) |
|---|---|
| **Il est un symbole** de la carte, pris dans la grille | le **balai**, le **petit tas de feuilles**, les **dalles** |
| **Il est indispensable pour lire la scène** (où, qui, quoi) | « une femme **pieds nus** sur la pierre chaude » |
| **Il porte une sortie visible** | la lumière du soir, si elle **sort** du cadre et tombe sur le geste |

Tout le reste est **du décor de prompt**, et il tombe. Le test : *si l'élément pouvait être
remplacé ou supprimé sans changer ce que la carte veut dire, c'est du décor.*

**Ce qui tombe, nommément :**
- le **nom du pays ou du climat** quand il n'est qu'une consigne de rendu ;
- l'**inventaire des couleurs** — sauf si une couleur **est** un symbole de la carte. La palette
  se garde dans la **fiche** et dans la **recette**, jamais dans le texte ;
- les **objets ajoutés pour remplir** (une plante de plus, des collines à l'horizon, un oiseau) ;
- la **lumière décrite comme une consigne** (« lumière basse venant de la gauche ») : on garde
  **ce qu'elle fait**, pas comment elle est réglée ;
- les **interdits de la recette retournés en prose** (« rien de tropical ») : on ne décrit pas
  ce qui **n'est pas** sur l'image.

**Les trois questions de contrôle, avant d'écrire :**
1. **Ce détail est-il dans la grille des symboles ?** Sinon, il ne reste que s'il faut le voir pour lire la scène.
2. **Un lecteur qui n'a que la carte et le texte comprend-il mieux avec ce détail ?** Si non, il part.
3. **Est-ce que je décris l'image, ou est-ce que je récite le prompt ?**

**Longueur et unité** : 5 à 8 phrases, **un seul sujet** (un lieu, une figure, un geste).

*(Cette règle est **humaine** : elle ne se mesure pas par un test — comme « Pense à Ginette ».
Elle se relit à voix haute avant de livrer, en même temps que les tics de style.)*

---

## Les conventions du moteur — publiées, jamais tues

L'app **affiche ses règles** (un écran « Les règles »), et dit pour chacune si elle vient des
sources ou si elle est **tranchée par l'app** là où les sources se taisent. Se prétendre
déterministe sans publier ses règles n'aurait aucun sens — le déterminisme doit être
*reproductible* **et** *auditable*.

| Règle | Décision | Provenance |
|---|---|---|
| **Le mélange** | Fisher-Yates seedé, graine conservée — reproductible | **tranché par l'app** |
| **La facette du jour** (lumière/ombre) | dérivée de la graine du tirage | **tranché par l'app** — c'est une lentille, pas un verdict |
| **La carte-ressource** (la clôture) | la carte avec le plus de forces reçues, départage par position puis par identifiant | **tranché par l'app** |
| **Les liaisons entre éléments** | table 4 × 4 (renforce / neutralise / met en tension) | **imprimé** (Wen), table à nous |
| **Pas de renversées** | facette lumière/ombre à quatre modes | **imprimé** (Wen + Greer + Pollack convergent) |
| **Les 79 cartes** | Éveil reste dans le jeu, hors cycle | **tranché par l'app** (fidélité au deck) |

---

## Le vocabulaire — héritage et chantier, jamais dette ni manque

La métaphore générale reste celle de l'**orientation**. Mais les **libellés d'Align** (Le Cap,
La Voix, Le Foyer, Le Reflet, Le Geste, La Source, La Trace, L'Élan) appartiennent à l'autre app :
l'écran tarot ne les reprend pas (un même mot ne peut pas nommer deux choses, même à travers
deux apps d'un même écosystème).

**« Héritage » et « chantier », pas « dette » ni « manque ».** Le choix des mots *est* la charte :
on ne doit rien, on a reçu ; il ne manque rien, il y a à bâtir.

**Vocabulaire du tarot, lui non plus :** on n'écrit jamais « énergie négative », « carte
maléfique », « mauvais présage », « tirage inversé ». L'ombre est **une manière de vivre la
qualité** — amoindrie, retournée, subie, différée — jamais une sanction.

---

## Interdits absolus

### Juridiques
- ❌ Le nom « Osho », « Osho Zen Tarot », ses **textes** et ses **images**. Marque UE valide
  (confirmée définitivement en 2017), images © 1994, textes protégés jusque ~2060.
  **On s'inspire de la philosophie — libre. On ne touche pas au jeu.**
  *(Nos noms de cartes maison sont les nôtres, posés sur nos propres images — des mots français
  génériques, pas les titres du jeu Osho Zen. Le champ `osho` de `noms_cartes.json` est une
  trace de fabrication interne, jamais affichée.)*
- ❌ Tout texte des ouvrages de référence (Pollack, Greer, Wen, Jodorowsky, et les autres).
  Ils donnent le **schéma de données** (quels axes, quelle granularité, quelle longueur),
  **jamais la prose**. Les cartes de concepts de `_distillation/cartes_concepts/` sont la seule
  passerelle autorisée.

### Éditoriaux
- ❌ Prédire un événement (« tu rencontreras… », « tu vas… »)
- ❌ Prescrire (« tu dois… », « il faut… », « tu devras… »)
- ❌ Essentialiser (« tu es quelqu'un de… », « tu es procrastinateur »)
- ❌ Faire peur pour retenir l'attention
- ❌ Flatter sans contenu
- ❌ Jargon non expliqué (celui du moteur comme celui des livres)
- ❌ Énumérer. **Une** chose par jour. *(Le moteur lui-même : 2 motifs maximum par lecture.)*
- ❌ Les gestes vagues : « ouvre-toi », « laisse-toi porter », « fais confiance à l'univers »,
  « sois toi-même », « écoute ton cœur », « lâche prise » — une consigne qui ne dit rien
  n'est pas un conseil.

---

## Le mur du corpus

Une app déterministe meurt de la **répétition**, pas du calcul. Le reproche fait à une app
concurrente est sans appel : *« les readings cessent de sembler personnels dès qu'on voit les
cinq mêmes descripteurs recyclés chez tous ses amis »*.

**Trois parades, toutes structurelles :**
1. **Additionner des tables indépendantes, jamais les multiplier.** La carte × la position ×
   la liaison : trois tables écrites, pas 10¹² combinaisons.
2. **La variété vient du tirage honnête.** *(Ici, et seulement ici, la règle diffère d'Align :
   là-bas elle vient du ciel réel et « aucun tirage, jamais » — ici le tirage EST le ciel.
   Le mélange est seedé, conservé, reproductible : le hasard est un moteur, pas une excuse.)*
3. **Chaque entrée doit tenir seule.** Si elle pourrait s'appliquer à n'importe qui,
   elle est à réécrire.

**Le test qui tranche** : lis l'entrée en te demandant *« est-ce que ça pourrait être écrit
dans un horoscope de magazine ? »* Si oui, jette et recommence.

---

## La chaîne de validation du corpus (specifique à l'app)

Avant qu'un texte entre dans le corpus :

1. **La charte** (ce document) — relecture humaine à voix haute.
2. **Le validateur de charte** (MCP `charte-ta-trame` : `verifier_texte`, `chercher_doublon`)
   — contrôle des interdits, des tics et de la répétition contre le mur existant.
3. **Les tests du corpus** (`test_corpus` : liste noire de `tables.json`, issue obligatoire,
   positions différentes, longueurs, ouvertures, doublons entre fiches) — la version tarot des
   tests d'Align, définie dans `GRAMMAIRE.md` §7.

Les trois couches disent des choses différentes : la charte protège la voix, le validateur
protège contre le mur et les interdits, les tests protègent la structure. Aucune ne remplace
les autres.
