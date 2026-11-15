# GRAMMAIRE — le moteur de lecture du tarot (spécification v1)

> **Statut** : v1, rédigée le 2026-11-08, en attente de la relecture de Martin avant toute écriture de corpus.
> **Sources** : les trois cartes de concepts de `TAROT_APP/_distillation/cartes_concepts/` — Wen (la syntaxe), Pollack (la sémantique), Greer (l'usage) — et les décisions prises avec Martin le 2026-11-08.
> **Rôle de ce document** : verrouiller la grammaire AVANT d'écrire les cartes. C'est le contrat entre le corpus et le moteur. Tout ce qui n'est pas ici est un choix d'écriture libre ; tout ce qui est ici est une règle, et la plupart deviennent des tests.

---

## 0. Les choix fondés (validés avec Martin, 2026-11-08)

1. **Le tirage est la source de variété**, comme le ciel l'est dans Ta Trame. La lecture, elle, est **100 % déterministe** : même tirage + même question ⇒ exactement le même texte, pour toujours. Aucun LLM, aucun réseau au runtime.
2. **Pas de cartes renversées.** La nuance vient d'une facette **lumière / ombre** par carte, avec quatre modes d'ombre (amoindri, retourné, subi, différé). Ce choix est sourcé trois fois : Wen (les quatre modes), Greer (l'arc de sens), Pollack (la qualité bloquée, jamais l'inverse).
3. **Tirages v1** : la carte du jour + le tirage à trois (grammaire causale). La croix celtique attend le volume.
4. **La question** : ouverte par défaut, intentions guidées qui **habillent** la lecture, question libre affichée telle quelle — jamais analysée.
5. **Format** : app web responsive dans le moule Ta Trame (Flask + vanilla, port dans `services.json`). Rien à embarquer sur le téléphone : pas de « petit modèle », la question ne se pose plus.
6. **La voix est celle d'Align.** La charte éditoriale de Ta Trame s'applique à tout texte du corpus, à l'identique : `data/corpus/CHARTE.md` (règles de rédaction, règle d'or du style, banque de formes, Ginette, interdits). La grammaire définit la **structure** ; la charte définit la **voix**. Chaque texte passe par le validateur de charte (`verifier_texte`, `chercher_doublon`) avant d'entrer dans le corpus.

---

## 1. Le jeu (ontologie) — **79 cartes, pas 78**

Le jeu compte **79 cartes** (source de vérité des noms : `ATRO_PLUS/_distillation/noms_cartes.json` ; inventaire généré : `data/grammaire/jeu.json`) :

| Groupe | Nombre | Identifiants | Ce que c'est |
|---|---|---|---|
| **Majeurs** | 22 | `major_00` … `major_21` | les grandes forces du chemin, en trois registres |
| **Mineurs** | 40 | `feu_02` … `terre_10` (4 familles × 10 degrés) | le quotidien : une famille (terrain) × un degré (étape) |
| **Figures** | 16 | `*_page`, `*_chevalier`, `*_reine`, `*_roi` (4 familles × 4 rangs) | des manières d'être — jamais des personnes typées |
| **Hors cycle** | 1 | `master` (**Éveil**) | la 79ᵉ carte, fidèle au jeu Osho Zen |

### Éveil, la carte hors cycle (conception verrouillée avec Martin, 2026-11-11)

- **Option A, fidèle Osho** : elle reste dans le paquet et peut sortir à n'importe quel tirage (1/79 par carte tirée, ~1 tirage de trois sur 27 en contient une). L'exclure serait mentir sur le jeu.
- **Fiche à forme propre — « Le regard »** : la seule carte sans positions narratives, parce qu'elle n'est pas *dans* la situation, elle la regarde. Sa fiche porte : mots-cles, tension, lumiere, ombre (avec issue), **le_regard** (3 variantes de la phrase d'exception, la graine en choisit une — documenté et reproductible comme la facette), questions, lecon, image, micro_geste.
- **Dans les trois cartes** : le libellé de la position est remplacé par « le regard » et la variante seedée s'affiche à la place du texte ; le moteur saute les liaisons qui la concernent.
- **Dans la carte du jour** : la fiche se lit comme les autres (le regard remplace le texte du jour), sans repère visuel spécial — la phrase suffit à signaler la rareté (choix Martin : pas de badge, pas d'en-tête).
- Interrupteur de configuration : `jeu.exclure_hors_cycle` (défaut : `false`). Si un jour on préfère un jeu « propre » à 78, c'est une ligne, pas un chantier.

### Les axes qui portent tout le moteur

- **Familles** (4) : feu (élan, projet), eau (lien, intériorité), air (idée, parole), terre (corps, ressources). Deux actives (feu, air), deux réceptives (eau, terre). → `tables.json.familles`
- **Degrés** (10) : ouverture, mise en relation, premier fruit, cadre, secousse, circulation, évaluation, mouvement, bilan, achèvement. → `tables.json.degres`
- **Registres des majeurs** (Pollack, trois séries de sept) : seuil (Foi), extérieur (I–VII), intérieur (VIII–XIV), transpersonnel (XV–XXI), hors cycle (Éveil). Une étiquette qui empêche de mélanger les plans dans un même paragraphe.
- **Éléments des majeurs** : proposition Wen (`jeu.json`), répartition 6 feu / 6 terre / 6 eau / 4 air. **Attribution d'école, à valider par Martin** — nos majeurs portent déjà des correspondances Ta Trame (planètes, signes) qui sont une autre couche ; les deux coexistent, seul l'élément alimente le moteur.
- **Colonnes des majeurs** (7) : notre reconstruction à partir des trois séries de sept de Pollack — signalée comme inférence, pas comme thèse du livre. → `tables.json.colonnes`
- **Conflit nombre × famille** : le nombre et la famille peuvent se renforcer OU se contredire, et la contradiction est signifiante (le 8 d'air : le mouvement empêché). Chaque fiche mineure porte une `note_grille` qui dit l'accord ou le conflit — jamais de moyenne molle.

---

## 2. La fiche-carte (le schéma de données)

Schéma complet : `data/grammaire/carte.schema.json`. Exemples remplis : `data/grammaire/exemples/major_13.json` (un majeur), `eau_08.json` (un mineur).

| Champ | Contenu | Source du concept | Longueur cible |
|---|---|---|---|
| `mots_cles` | 3 à 6 mots — de quoi la carte parle | Greer, étage 1 | — |
| `tension` | `{pousse, retient}` — deux verbes | Pollack : une fiche porte une tension, pas une définition | 1 verbe chacun |
| `lumiere` | la qualité quand elle circule | Pollack : fluide/entravé, jamais bien/mal | 50–85 mots |
| `ombre` | `{mode, texte, issue}` | Wen : les quatre modes. **L'issue est obligatoire** (« la chaîne large » de Pollack : toute ombre contient sa porte) | 50–85 + 1–2 phrases |
| `questions` | 2 à 4 questions ouvertes | Greer, étage 2 — « l'or pur » : la carte devient une interlocutrice | — |
| `lecon` | ce que la carte demande d'apprendre | Greer, étage 3 (retravaillé : pas d'affirmation performative) | 1 phrase |
| `image` | `{geste, seuil, detail}` — notre carte, pas celle de Waite | Pollack : la posture dit la fonction ; décrire AVANT d'interpréter | 1 phrase chacun |
| `micro_geste` | une action minuscule faisable en 24 h | Greer (« la percée »), Wen (« le conseil ») | 1 phrase |
| `positions` | **table A** — un texte par position active : `jour`, `amene`, `se_joue`, `essayer` | Wen : la position porte la phrase | 50–85 mots chacun |

Trois règles de fabrication :

- les textes de `positions` sont écrits **pour la position** : même carte, deux positions ⇒ deux phrases différentes (test anti-étiquette) ;
- l'`issue` de l'ombre est un champ requis : un test pytest refuserait une fiche où l'ombre se ferme sur un mur ;
- chaque fiche porte `source_referentielle` : la traçabilité vers les cartes de concepts (jamais de texte de source).

---

## 3. Les relations (la grammaire d'assemblage)

C'est l'étage qui rend le moteur possible : on n'écrit pas les combinaisons, on **détecte des types de liens** et on sort une phrase par type.

### 3.1 La liaison élémentaire (colonne vertébrale du tirage à trois)

Table symétrique 4 × 4 (`tables.json.liaisons`), une phrase écrite par type de liaison :

| Rencontre | Effet | La phrase-type dit |
|---|---|---|
| feu + air | **renforce** | l'élan trouve de l'air, l'ensemble prend de l'ampleur |
| eau + terre | **renforce** | l'émotion trouve son contenant, ça s'installe |
| feu + terre | **neutralise** | l'action et le concret se compensent, sans victoire |
| air + eau | **neutralise** | la pensée et le sentiment se tempèrent mutuellement |
| feu + eau | **tension** | ce que l'une demande, l'autre l'éteint — la tension est le sujet |
| air + terre | **tension** | ce que l'idée veut, le concret l'alourdit — la tension est le sujet |
| même élément | pas une liaison | c'est l'**écho de famille** (§3.2) |

Le moteur lie **les paires adjacentes** : carte 1 → carte 2, carte 2 → carte 3 (le sens de lecture). Une carte sans élément (Éveil) court-circuite la liaison.

### 3.2 Les échos (des phrases d'un même moule, une par type)

| Écho | Déclencheur (seuil) | Ce que la phrase dit |
|---|---|---|
| **Écho de nombre** | ≥ 2 cartes du même degré (`seuils.echo_nombre_min`) | ce que la personne cherche vraiment, via le degré répété (8 = réussir le geste, 5 = traverser la secousse…) |
| **Écho de famille** | ≥ 2 mineurs de la même famille | le registre dominant : « tu traverses beaucoup de… en ce moment » — une période, jamais un type |
| **Écho de colonne** | ≥ 2 majeurs de la même colonne | « le même motif, à deux étages » (notre reconstruction, signalée) |
| **Suite numérique** | 2 mineurs de degrés consécutifs | un enchaînement : une étape ouvre sur la suivante |
| **Glissement de figure** | 2 figures : même famille / même rang | monter ou descendre d'un cran / changer de registre — sans genre, sans classe sociale |

### 3.3 Les motifs de champ (des comptages, des phrases de cadrage)

| Motif | Règle | Effet |
|---|---|---|
| **Majeurs présents** | ≥ 2 (`seuils.majeurs_passage_de_vie`) | phrase « passage de vie » — la situation dépasse le quotidien |
| **Aucun majeur** | 0 | phrase « affaire courante et malléable » — bonne nouvelle : ça se manipule |
| **Famille absente** | une famille absente ET ≥ 2 mineurs dans le tirage | « et si l'absence de X était le sujet ? » — l'absence est une donnée |
| **Figures nombreuses** | ≥ 2 figures | les rôles et relations occupent le terrain |
| **Éveil sort** | la carte hors cycle dans le tirage | phrase d'exception (rare, posée, sans interprétation lourde) |

Les seuils sont dans `tables.json.seuils_moteur` — c'est un bouton de réglage, à calibrer pendant le pilote.

---

## 4. Les tirages v1

→ `data/grammaire/tirages.json`

### 4.1 La carte du jour (`jour`) — 1 carte, 4 temps

1. **Voir** — l'image seule, avec trois consignes de description (ce que je remarque / ce que je ressens / ce que je n'avais pas vu). On ne livre pas encore la signification.
2. **Écouter** — deux ou trois questions de la fiche, jamais plus.
3. **Nuancer** — la facette du jour (lumière ou ombre), formulée comme une position sur l'arc. **Le choix vient de la graine du tirage** : documenté, reproductible, et assumé comme une lentille — pas une affirmation sur la personne.
4. **Faire** — le micro-geste.

### 4.2 Trois cartes — situation, nœud, levier (`causale_3`)

| Position | Libellé | La position demande |
|---|---|---|
| 1 | **ce que j'amène** | ce qui a formé la situation : acquis, habitudes, base inconsciente |
| 2 | **ce qui se joue** | la tension actuelle — où est le nœud |
| 3 | **ce que je peux essayer** | le levier : ce qui est à mettre en œuvre, **jamais ce qui va arriver** |

- **L'écart assumé** : chez Greer, la dernière position prédit ; chez nous elle propose. C'est le seul glissement fait aux sources, et il est structurant.
- **Le rituel en deux temps** (Wen : l'ordre de pose n'est pas l'ordre de lecture) : les cartes sont d'abord **posées face cachée** une à une dans leurs positions, puis **révélées une à une** au choix de celui qui tire. L'ordre de révélation lui appartient — la lecture suit ses révélations.
- **L'ordre de lecture** est 1 → 2 → 3 (l'ordre de pose). Le raffinement de Wen (poser le présent d'abord) attendra l'UX de la phase 2.

### 4.3 Les grammaires futures (réservées, non implémentées)

Temporelle, théâtrale, anthropologique (esprit/corps/souffle — signature Greer : à créditer ou adapter), décisionnelle. Une même donne pourra se relire avec plusieurs grilles sans retirer (les « permutations » de Greer). On ne code rien de tout ça avant que le pilote ait validé la sensation.

---

## 5. La composition du texte (le pipeline du moteur)

```
ENTRÉE : tirage_id, graine, question, intention
1. TIRAGE     mélange Fisher-Yates seedé → cartes + positions (stocké dans le journal)
2. SEUIL      phrase d'ouverture : le motif dominant (majeurs ? famille dominante ? sinon ouverture neutre)
3. CARTES     pour chaque carte, dans l'ordre de lecture :
                 le texte de position (table A de la fiche)
                 + 1–2 phrases de description d'image (voir, avant d'interpréter)
4. LIAISONS   pour chaque paire adjacente : phrase de liaison élémentaire OU écho de famille
5. MOTIFS     les échos et motifs de champ dont les seuils sont atteints (max 2 par lecture —
              au-delà, le moteur choisit les plus forts ; c'est Pollack : « le déversement de
              détails est un échec, pas une richesse »)
6. CLÔTURE    retour sur la carte-ressource : sa question + son micro-geste + une question ouverte
SORTIE  : un texte de ~350–450 mots (tirage à trois) ou ~150–200 mots (carte du jour)
```

**Règle de la carte-ressource** (la clôture revient toujours sur une ressource, jamais sur un verdict) : on prend la carte avec le plus de « forces d'entrée » — liaisons renforcées reçues + échos — départage par position (essayer > se_joue > amene), puis par identifiant. Déterministe, court à coder, et c'est la garantie anti-catastrophisme de l'app.

**Gabarits de synthèse** (Greer : un gabarit de phrase fait plus pour l'appropriation qu'un paragraphe d'explication) :

- une carte — « Aujourd'hui, il s'agit de…, et je peux… » ;
- trois cartes — « Ce que j'amène… ; ce qui se joue… ; ce que je peux essayer… » ;
- deux cartes en tension — « D'un côté…, de l'autre…, et entre les deux… ».

---

## 6. La question et les intentions

- **Question par défaut** : « Qu'est-ce que je dois regarder en ce moment ? » (le socle de Greer — elle ouvre, elle ne pronostique pas).
- **La question s'écrit avant de tirer** et reste affichée pendant la lecture (Greer : la forme écrite est un contrat).
- **Recadrage** : l'écran propose des reformulations écrites (réservoir Wen/Greer) : « est-ce que je vais… » → « qu'est-ce qui se joue dans… » ; « pourquoi… » → « qu'est-ce que cette situation m'apprend sur… ». On n'analyse **jamais** une question libre : elle est affichée telle quelle.
- **Intentions guidées** (amour, travail, décision, soi) : en v1, elles **habillent** la lecture — la question-type, la phrase de seuil, la question de clôture. Elles ne touchent **jamais** au tirage (mélange honnête, aucune pondération). Des textes par domaine pourront s'ajouter en phase 3 si le pilote le justifie — ce serait la table A × intentions, un volume à part, pas un changement de moteur.

---

## 7. Déontologie et tests

La déontologie n'est pas une préface : c'est une suite de tests pytest (`tables.json.deontologie`).

| Test | Ce qu'il vérifie |
|---|---|
| `test_liste_noire` | aucun interdit de lexique dans le corpus (« tu vas », « bientôt », « destin », « il faut »…) — en excluant les **contextes niés** (le piège connu : « pas ce que tu dois faire » n'est pas un « tu dois ») |
| `test_interdits_contenu` | pas de mort annoncée, pas de conseil médical/juridique/financier, pas de tiers sans consentement, pas de date, pas de oui/non |
| `test_ombre_issue` | chaque fiche a une `issue` non vide, reliée à son ombre |
| `test_positions_differentes` | même carte, deux positions : aucune suite de 8 mots commune |
| `test_longueurs` | bornes par champ (`seuils_moteur`) |
| `test_schema` | chaque fiche valide `carte.schema.json` |
| `test_ouvertures` | anti-tic : aucun premier mot (ou moule syntaxique) > 10 % des ouvertures du corpus assemblé |
| `test_doublons_inter_cartes` | ≤ 4 suites de 8 mots partagées entre deux fiches quelconques |
| `test_pas_de_titre_en_ouverture` | aucun texte de carte n'ouvre par son nom (l'anti-tic n° 1 d'un corpus de tarot) |

Critère d'écriture de Wen, difficile à automatiser mais bon à écrire sur le mur : **un bon texte de carte ne confirme pas tout ce qu'on pensait déjà** — s'il ne surprend jamais, c'est du biais.

---

## 8. Le tirage honnête (aléatoire et reproductible)

- Le mélange est un **Fisher-Yates seedé** (`random.Random(graine)`), la graine étant dérivée de (horodatage + identité locale + compteur de tirage du jour). Pas de biais, pas de « pondération par intention ».
- La graine est **stockée dans le journal** avec le tirage : chaque lecture reste **reproductible** — on peut rouvrir un tirage de mars et retrouver exactement le même texte. C'est la version tarot de la règle Ta Trame : rien ne se régénère, tout se recalcule pareil.
- Le choix lumière/ombre de la carte du jour vient de la même graine. Assumé : c'est une lentille de lecture, pas une vérité sur la personne — et c'est ce qui empêche de tout lire « en lumière » par complaisance.

---

## 9. Ce qu'on ne fait pas (et pourquoi)

| On ne fait pas | Pourquoi |
|---|---|
| Cartes renversées | remplacées par la facette lumière/ombre (sourcé 3 fois) |
| Le signifiant, la première opération (4 piles) | un appareil de cartomancienne, pas un protocole d'app |
| La carte d'essence / cartes d'identité calculées | la date de naissance ne fixe pas une nature — fatalisme doux, machine à profils |
| Le oui/non et la datation par famille | une précision illusoire |
| La directionnalité visuelle (regards, couleurs du ciel) | nos cartes ne sont pas dessinées avec cette grille — ces règles produiraient du bruit |
| La lecture pour autrui | l'app est solitaire ; les tirages à deux sont une extension possible, pas un socle |
| Le karma, les vies antérieures, la manifestation | hors philosophie Align |
| Un corpus par domaine dès la v1 | intentions = habillage en v1 ; la table domaine × carte est un chantier de phase 3, à décider sur preuve |

---

## 10. La suite : le corpus pilote (~10 %, phase 1)

**Portée** : 10 cartes enrichies sur le moule complet + le moteur + une maquette d'écran.

| Choix | Cartes | Pourquoi celles-là |
|---|---|---|
| 4 majeurs | Foi (`major_00`, seuil), Union (`major_06`, extérieur), Transformation (`major_13`, intérieur — **exemple déjà écrit**), Silence (`major_17`, transpersonnel) | un par registre + une carte « dure » pour tester la chaîne large (Emprise remplacerait Silence si tu préfères) |
| 4 mineurs | Voyage (`feu_08`), Lâcher-prise (`eau_08` — **exemple déjà écrit**), Culpabilité (`air_08`), Simplicité (`terre_08`) | les quatre familles, tous de **degré 8** → exerce l'écho de nombre dans un vrai tirage |
| 2 figures | Partage (`feu_reine`), Contrôle (`air_roi`) | deux rangs différents, le test personne/facette |

**Livraison** : moteur Python pur (tirage seedé, composition, échos), les 10 fiches validées par les tests de §7, une maquette HTML des deux écrans. **Le jalon** : tu lis trois ou quatre lectures produites, et on décide si la sensation est bonne — avant d'engager les 79.

---

### Décisions ouvertes (à trancher au fil du chantier)

1. **Éléments des majeurs** : la table Wen par défaut ; si tu veux une autre répartition (ou celle du jeu Osho), c'est `jeu.json` à éditer — le moteur suit.
2. **Éveil** : dans le jeu par défaut, interrupteur prévu. Tu confirmes ?
3. **Le nom du tirage à trois** sur l'écran (« Trois cartes — situation, nœud, levier » est un libellé de travail, pas un nom de produit).
4. **Seuils du moteur** (fréquence des motifs) : à calibrer sur le pilote, pas avant.
