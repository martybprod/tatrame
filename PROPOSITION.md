# PROPOSITION — Coach de vie quotidien par croisement astro / numérologie / tarot

> Rédigé le 2026-07-15, après lecture des 6 ouvrages du dossier `DOCUMENTS DE RÉFÉRENCE`
> et 4 recherches parallèles (numérologie Phillips · 4 livres d'astrologie · Castells/Osho/concurrence · faisabilité technique).
> Aucune ligne de code écrite. **Rien n'est décidé — ce document est là pour être discuté.**

---

## 1. Le besoin, tel que compris

Une app **sympathique**, de coaching de vie au quotidien, qui croise :

- la **carte du ciel** de la personne (thème natal),
- sa **numérologie** (méthode de Lydie Castells),
- la **philosophie du Tarot Zen d'Osho** — examen de soi, travail sur soi, toujours positif *malgré* ce que disent la carte et les nombres,
- éventuellement d'autres éléments,

pour produire une **analyse croisée ultra-personnalisée** avec de **petits conseils au quotidien**.

Contrainte forte : **100 % déterministe**.

---

## 2. La tension centrale — et sa résolution

« Ultra-personnalisé » et « 100 % déterministe » tirent en sens inverse. Ultra-personnalisé pousse
vers un LLM qui rédige au moment où tu ouvres l'app. 100 % déterministe interdit exactement ça.

**La recherche a résolu cette tension, et dans un sens que je n'attendais pas : le déterminisme
n'est pas une contrainte technique à subir, c'est la thèse du produit.**

Trois appuis convergents, tous documentés :

**1. Osho lui-même légitime le calcul contre le tirage.** Dans *The Further Shore* (ch. 5) :

> « Whenever we are doing anything – astrology, future suggestion, horoscope-readings, palmistry,
> i ching, tarot – anything that is concerned with the future, it is basically **a reading of the
> unconscious of the person. It has nothing much to do with the future.** »

Osho ne rejette pas ces outils : **il redéfinit leur objet**. Ils ne lisent pas l'avenir, ils lisent
le conditionnement présent. Donc un calcul qui part de la date de naissance ne prédit rien — il
**cartographie un conditionnement hérité pour permettre de s'en libérer**. C'est précisément le
cahier des charges d'Osho. Un tirage aléatoire, lui, réintroduirait la logique oraculaire qu'il rejette.
**Notre déterminisme est plus fidèle à Osho qu'un tirage au hasard ne le serait.**

**2. Le tarot calculé est une tradition établie, pas un bricolage.** Les *Birth Cards* d'**Angeles
Arrien** (1977), publiées par **Mary K. Greer** (*Who Are You in the Tarot?*), dérivent la carte de la
date de naissance par une formule. L'app s'inscrit dans une lignée tarologique légitime.

**3. La variété ne vient pas du hasard — elle vient du ciel réel.** La Lune change de signe tous les
2 jours et demi, les aspects se font et se défont, l'année personnelle tourne. **Le ciel bouge tout
seul.** Un conseil du jour entièrement déterminé par (naissance, date) est différent chaque matin
sans qu'aucun tirage aléatoire n'intervienne jamais.

### La conséquence architecturale

**Le LLM est un outil de FABRICATION, pas un composant du produit.**

- **À la construction** (moi, hors ligne, avec les livres) : rédaction du corpus d'interprétations, original.
- **À l'exécution** (l'app chez toi) : **zéro LLM**. Python pur + tables JSON. Même entrée → même sortie, pour toujours, auditable.

C'est le pattern « **packs de connaissance distillés** » de Manto, poussé à son terme : là où Manto
injecte un `indice` dans le prompt d'un LLM au runtime, ici **le LLM a déjà fini son travail avant
que l'app ne démarre**. Bénéfices en cascade : déterminisme réel (pas « température 0 »), zéro
latence, zéro RAM, aucun texte sous copyright embarqué, commercialisable.

---

## 3. Le constat des recherches

### Le corpus tabulable existe — et il est plus gros qu'espéré

**Riske est structurée comme une base de données.** Comptages exacts sur le texte extrait :

| Source | Contenu | Entrées | Longueur médiane |
|---|---|---|---|
| **Riske natal** | planète-en-signe 108 · planète-en-maison 120 · signe-sur-cuspide 144 · aspects 144 · signes solaires 12 | **~528** | 50-125 mots, très homogène |
| **Riske prédictif** (ch. 5 + 9) | lente-en-maison 60 · aspects lents 100 · rapide-en-signe/maison 59 · aspects rapides 99 · ASC diurne ~20 · **17 règles « meilleur jour pour… »** | **~340** | ~60 mots |
| **Dryburgh ch. 9** | **âges de la vie × cycles planétaires** — universelle, ne dépend que de l'âge | ~20 | fort ROI |
| **Von Grüt** | **8 types soli-lunaires** de Rudhyar (formule exacte) + lexique FR « ma capacité à… » | 8 | — |
| **Phillips** | Ruling Numbers 11 · flèches 15 · grille 3×3 · mois×année perso 108 | ~238 | — |

**Trois leçons de conception que la recherche impose :**

1. **Riske factorise au lieu de multiplier** — 3 classes d'aspects (conjonction / carré-opposition /
   sextile-trigone) au lieu de 5, et des **tables additives indépendantes** plutôt qu'un produit
   cartésien. C'est exactement ce qui rend le corpus exploitable.
2. **Dryburgh argumente explicitement contre l'approche par dictionnaire** : elle calcule
   « plusieurs centaines de milliers de cas possibles pour un seul thème » et conclut au « travail
   titanesque ». **Son objection est fondée** — et elle valide la règle : *additionner des tables,
   jamais les multiplier*.
3. **Riske traite ASC et MC comme des planètes** → 12 corps aspectables, pas 10.

### Ce que la numérologie ne donne PAS

⚠️ **Phillips ne contient ni mois personnel ni jour personnel.** Sa granularité la plus fine est
mois × année personnelle (108 entrées). **Le conseil quotidien ne peut donc pas venir de la
numérologie** — il vient du ciel, qui bouge tous les jours. La numérologie fournit le **fond**
(portrait, année, cycle de 9 ans) ; le ciel fournit le **jour**.

Autres divergences de Phillips vs le marché, à trancher : **pas de maître-nombre 33** (rejeté
explicitement), **pas de Ruling Number 1**, et surtout **année personnelle calée sur l'année civile,
pas sur l'anniversaire**.

### Lydie Castells — le constat honnête

**C'est elle qui donne la réponse**, en note de bas de page de *Numérologie* (2018) :

> « La différence entre les nombreux numérologues […] n'est pas le support qu'ils utilisent — car,
> **à quelques exceptions près, ce sont les mêmes calculs mathématiques** —, mais l'interprétation
> qu'ils en font, ainsi que leurs intentions profondes (sont-ils orientés problèmes ou solutions ?). »

Autrement dit : **le socle de calcul est de la numérologie pythagoricienne classique.** Son
innovation est *structurelle et sémantique* — la métaphore de l'arbre (2 racines + tronc = « triangle
fondamental »), un vocabulaire propre, une posture non-divinatoire, une hiérarchisation de la lecture.

Correspondances identifiées : 1ʳᵉ racine ≈ **chemin de vie** · 2ᵉ racine ≈ **expression** · tronc ≈
**clé de l'âme** (nombre intime). Elle utilise **11, 22 et 33**, une **grille d'inclusion** rebaptisée
« qualités innées / à développer », et des **défis**. Pas de dettes karmiques. **Aucun croisement avec
l'astrologie — le croisement est ton invention, pas la sienne.**

⚠️ **Ses formules exactes ne sont publiées nulle part.** La page ICERNS « Calculs et Méthodologie »
renvoie aux livres payants ; aucun praticien certifié ne les publie — c'est délibéré. **L'annexe
« Faites vos calculs ! » (p. 291-307) du livre de 2018 contient tout ce qui manque. 24 €.**

⚠️ « **Numérologie Stratégique®** » est une marque INPI, avec un écosystème (ICERNS, école QUALIOPI,
praticiens certifiés) structuré pour protéger l'exclusivité. Ligne de sécurité nette : **les calculs
pythagoriciens sont libres et non protégeables ; le vocabulaire et la métaphore ne le sont pas.**

### Le pont Golden Dawn — le vrai différenciateur

Les 22 arcanes majeurs correspondent **exactement** à **12 signes + 7 planètes classiques + 3 éléments**.
Ce n'est pas une analogie décorative : c'est la structure historique (Mathers, *Book T*, 1888), et les
3 « éléments » (0, 12, 20) correspondent aux lettres-mères hébraïques.

⚠️ La quasi-totalité du web affiche Le Mat = Uranus, Le Pendu = Neptune, Le Jugement = Pluton — **c'est
faux**, c'est le système Case/BOTA des années 1920-30. La table authentique a été récupérée.

**L'Osho Zen préserve la structure intacte** (numérotation Rider-Waite : 8 = Force, 11 = Justice) → les
correspondances s'appliquent **sans permutation**. Le renommage est purement sémantique.

**Conséquence : le croisement des trois systèmes est structurellement motivé, pas juxtaposé.** La carte
de naissance pointe vers une planète ou un signe, qu'on va lire **dans le thème natal réel de la
personne**. Personne n'exploite ça — ni Co-Star, ni The Pattern, ni AstroMatrix (qui juxtapose).

⚠️ **Ne jamais dériver l'interprétation du nombre** : le 4 numérologique (stabilité, autorité) →
L'Empereur → mais **The Rebel** chez Osho, sens quasi opposé. **Rédiger depuis la carte, jamais depuis le nombre.**

### Le marché — relevé à la source sur l'App Store FR

**Le mobile francophone est vide, mais pas pour la raison que je croyais d'abord.**

| App | Éditeur | FR ? | Note FR (avis) | Modèle |
|---|---|---|---|---|
| **Co-Star** | Co-Star Astrology Society (US) | ❌ **anglais seul** | 4,7 (~2 800) | Freemium |
| **The Pattern** | Pattern Home (US) | ❌ **anglais seul** | **3,9** (235) | 83,99 €/an |
| **CHANI** | Chani Nicholas (US) | ❌ **anglais seul** | 4,8 (258) | 109,99 €/an |
| **Nebula** | Spiritual Nebula (**Chypre**) | ✅ **22 langues** | 4,2 (**5 500**) | 137,99 € à vie + crédits voyance |
| **Mon horoscope du Jour** | SF Factory (**Paris**) | ✅ | **4,6 (9 300)** | Gratuit + pub |

**Le fait structurant** : les trois apps US premium **ne sont pas traduites**. Le seul international
qui ait investi le français est **Nebula**, et il le fait pour vendre des crédits de voyance (plaintes
convergentes : offre à 1 € → prélèvement de 39-49 €).

**Et surtout : les trois grands sites FR — Astrotheme, Evozen, Asiaflash — n'ont AUCUNE app mobile.**
Le web FR est occupé, **le mobile FR est vide**. Le leader FR (« Mon horoscope du Jour », 9 300 avis,
soit **plus du triple de Co-Star** sur le même store) est un horoscope générique gratuit financé par
la pub — et des avis récents se plaignent qu'il **bascule vers l'anglais**. Il lâche son avantage.

⚠️ **Correction importante par rapport à une première lecture : le croisement astro + numérologie +
tarot n'est PAS un espace vierge. Nebula le fait déjà intégralement** (thème natal, transits,
synastrie, tarot, numérologie, chiromancie, rêves). Moonly (6 M+ téléchargements) et Astrotalk aussi.

**Donc le différenciateur n'est pas « on croise trois disciplines » — ça se fait déjà.** Le
différenciateur est le quadruplet **français natif + local/privé + déterministe + achat unique**.
Ce qui reste distinctif côté contenu, c'est que les autres **juxtaposent** les disciplines quand nous
les **croisons structurellement** (le pont Golden Dawn) — c'est plus fin, mais c'est un argument de
qualité éditoriale, pas de catégorie. À ne pas survendre.

Deux enseignements de la concurrence :

- **Co-Star** (~30 M d'inscrits) : le ton court et cinglant a créé le marché, mais reproches
  documentés — ne traite en réalité que Soleil/Lune/Ascendant → textes génériques ; accusée
  d'accentuer le négatif pour l'engagement (*fearmongering*) ; **erreurs de calcul avérées** (maisons
  Porphyry au lieu de Placidus) ; « écrit par des robots » revient constamment. Une analyse
  académique (ASAP/Review, oct. 2025) soutient que le recours à l'IA **mine sa revendication
  d'astrologie « data-driven »**. *(Reste ouvert : son moteur est-il un vrai LLM ou de la NLG
  templatisée ? La recherche n'a pas tranché.)*
- **The Pattern** : bonne narration, mais *« les readings cessent de sembler personnels dès qu'on voit
  les cinq mêmes descripteurs recyclés chez tous ses amis »*. **C'est le mur du déterministe naïf :
  corpus trop petit.** C'est le risque n°1 de ce projet — voir §7.
- **Numerologist.com** : reproche unanime — *la lecture payante répète la gratuite « avec du
  remplissage »*. Ce grief désigne en creux exactement ce qui manque.
- **Fool's Dog** (100+ decks de tarot) affiche une position **anti-IA explicite** — preuve qu'un
  positionnement anti-IA revendiqué est commercialement tenable.

### 🎯 Un angle mort à exploiter : les accents en numérologie française

Deux conventions FR **contradictoires** coexistent : É = 5 (comme E, transparent) ou é/è/ç = 1 (valeur
propre). **Elles donnent des résultats différents pour le même nom, et aucune app ne dit laquelle elle
applique.** Pour une app qui se revendique déterministe, c'est exactement le genre de chose qui se
documente et se publie. Petit détail, fort signal.

### ⚠️ Deux chiffres à ne JAMAIS reprendre

- **« Le marché FR de la voyance pèse 3-4 Md€ »** — ça ne tient pas. La source est l'**INAD**, qui
  malgré son nom n'est ni un institut public ni un organisme statistique, mais **une structure du
  secteur, juge et partie**. L'INAD reconnaît lui-même que **l'INSEE chiffrait le secteur à ~70 M€**.
  Écart de **40 à 55×**. L'« étude Xerfi » que citent les blogs **n'existe pas** au catalogue Xerfi.
- **« Boom de l'astrologie chez les jeunes »** — contesté. L'Ifop 2022 (44 %) **a été commandé et payé
  par un médium professionnel** (indiqué p. 3 du rapport, jamais mentionné par la presse). À
  l'inverse, **Michel Dubois (CNRS) mesure que la croyance en l'astrologie RECULE de 9 points entre
  2007 et 2021**, et que seuls 7 % des adultes la tiennent pour une science (vs ~30 % en 1989).

**Ne bâtis rien sur ces chiffres. Les dénoncer est un angle plus solide que les citer.**

---

## 4. Le concept — « L'Éphéméride » (nom de travail)

Le mot dit les deux choses à la fois : la **table astronomique** qui donne la position des astres, et
le **calendrier qu'on effeuille chaque matin**. Tout le produit est là.

Cinq écrans, par ordre d'importance :

### Le Jour — le cœur de l'app
Ouvert chaque matin. **Une** configuration dominante du jour (pas dix), formulée en miroir, plus
**un geste concret**. Le moteur classe les configurations actives par force et n'en retient que la ou
les deux premières. Registre : « tu es en train de… » (présent, observable), jamais « tu es… »
(essentialisation) ni « tu vas… » (prédiction).

### Le Portrait — lu une fois, relu parfois
Le thème natal, les nombres et la carte de naissance, **croisés** — pas juxtaposés. Structuré par
« ma capacité à… » (Von Grüt) et par les domaines en formulation possessive (Dryburgh : « Ma personne,
Mes ressources, Mes racines… »). Chaque section porte une **lumière et une ombre** (patron Von Grüt),
sans jugement.

### Le Cycle — où j'en suis dans le temps long
Année personnelle, carte de l'année, transits des planètes lentes, et la **table des âges de la vie**
de Dryburgh (retour de Saturne à 29½, opposition d'Uranus à 42…) — universelle, ~20 entrées, coût
quasi nul, forte valeur de coaching.

### Le Miroir — le journal
L'utilisateur note ; l'app ne juge pas, ne score pas, ne relance pas. Le contraire d'un tracker.

### Le Ciel — la carte, pour qui veut voir
Le thème dessiné, les positions, les aspects. Pour la crédibilité et la curiosité.

---

## 5. Le moteur de croisement

C'est le cœur technique, et ce qui n'existe nulle part ailleurs.

```
  naissance (date, heure, lieu)  ──►  éphémérides  ──►  thème natal
        │                                                    │
        │                                                    ├── planètes en signes/maisons
        │                                                    ├── aspects (3 classes)
        │                                                    ├── angles, dignités, configurations
        │                                                    └── type soli-lunaire (8)
        │
        ├──►  numérologie (pythagoricienne)  ──►  nombres + grille + année personnelle
        │
        └──►  carte de naissance (Arrien/Greer)  ──►  arcane majeur
                                                          │
                                              ┌───────────┘
                                              ▼
                                    correspondance Golden Dawn
                                    (12 signes + 7 planètes + 3 éléments)
                                              │
                                              ▼
                            ═══ LE CROISEMENT ═══
                     l'arcane pointe vers une planète/un signe
                     → qu'on lit dans le thème RÉEL de la personne
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
               RÉSONANCE            TENSION
        (le facteur est fort    (le facteur est en
         dans le thème)          difficulté/absent)
                    │                   │
                    └─────────┬─────────┘
                              ▼
                    matière de travail sur soi
                    (jamais un verdict)
```

**Le jour** se calcule pareil : transits du jour → configurations actives → classées par force
(orbe, vitesse, angularité) → la ou les deux plus fortes → croisées avec l'année personnelle et la
carte de l'année → **une** phrase-miroir + **un** geste.

**Architecture à deux étages, reprise de Riske** (c'est explicitement son modèle, et il est fait pour
une app de conseil quotidien) :

- **Planètes lentes / cycles / éclipses = le POTENTIEL** (tendance de fond, dormante).
- **Planètes rapides (Soleil, Lune, Mercure, Vénus, Mars) = les DÉCLENCHEURS** — elles donnent le
  timing à un ou deux jours près. « The energy will remain dormant until other transits come into play. »
- **La Lune fixe le jour.** Son signe donne le ton, mais **un aspect dur l'annule** — règle
  déterministe explicite chez Riske.

**La règle d'or, imposée par Dryburgh :** additionner des tables indépendantes, **jamais** chercher le
produit cartésien.

---

## 6. Architecture technique

Cohérente avec l'écosystème : Flask + vanilla, `data/` en JSON, store par profil, port **5073**
(libre, hors ports « unsafe » des navigateurs), à inscrire dans `services.json` + Vibe.

### Le calcul — et le verrou juridique

**Le point le plus structurant du projet, et il faut le trancher avant la première ligne de code.**

| Voie | Licence | Conséquence |
|---|---|---|
| **pyswisseph** | **AGPL-3.0 pure** | Tout est déjà là (23 systèmes de maisons, astéroïdes, nœuds). **Mais : aucune option commerciale, et le projet est dormant** (dernier commit de code 2023-06-04, aucune wheel au-delà de Python 3.11). |
| **Swiss Ephemeris (C)** | AGPL **ou** pro **700 CHF** | Forfait unique, **valide 99 ans**, redistribution incluse, code fermé permis. Abordable. |
| **Skyfield + DE440s** | **MIT** + domaine public | Aucune contamination, jamais. **Mais il faut coder les maisons soi-même.** |

⚠️ **Le piège est que payer Astrodienst ne suffit pas.** Les 700 CHF débloquent la bibliothèque C,
**pas le wrapper Python** : `pyswisseph` est en AGPL *seule*, son auteur n'offre aucune licence
commerciale, et il ne maintient plus le projet. Pour fermer le code il faudrait écrire sa propre
liaison ctypes/cffi vers `libswe`. Et **tous** les wrappers alternatifs sont AGPL (kerykeion, immanuel ;
flatlib est abandonné depuis 2021 et son MIT de façade ne couvre pas swisseph).

⚠️ **Le déclencheur est plus large qu'on ne croit.** La licence Astrodienst se déclenche à la
distribution **ou** à « l'activation d'un service public ». **Une app Flask exposée par ton tunnel
Cloudflare est le cas d'école** — même sans distribuer un seul fichier. Et le contrat (§2) attrape
explicitement le contournement par micro-service : une app qui « ne contient pas de code de calcul
mais le demande à un serveur » est considérée comme contenant Swiss Ephemeris.

✅ **Aujourd'hui, en local et pour toi seul, tu ne dois rien.** Le déclencheur n'est ni la
distribution ni un service public. Le choix est entièrement ouvert — **et c'est maintenant qu'il coûte
le moins cher.**

**Recommandation : Skyfield (MIT) + DE440s + module de maisons maison**, derrière une interface
`EphemerisProvider` à deux implémentations. Tu développes vite avec pyswisseph comme **oracle de
référence pour tes tests golden**, tu construis l'implémentation Skyfield en parallèle et tu valides
l'une contre l'autre. Si tu commercialises un jour, tu débranches swisseph — **et tu ne l'auras jamais
expédié.**

Ce qu'il faut coder : ASC/MC (trigonométrie fermée, ~30 lignes), Whole Sign/Equal/Porphyry (triviaux),
**Placidus** (itératif, pas de solution fermée — ~1-2 jours avec validation), nœud moyen (polynôme de
Meeus), vitesse/rétrogradation (différences finies). **Garde-fou obligatoire** : Placidus dégénère
au-delà du cercle polaire → **repli automatique sur Porphyry + itération bornée**, exactement ce que
fait swisseph. Précision : non-enjeu (DE440 vs Swiss Ephemeris divergent de l'ordre de la
milliseconde d'arc ; l'astrologie travaille à la minute d'arc — 4 ordres de grandeur sous le seuil).

**Maisons : Placidus.** Consensus des 3 livres qui se prononcent, et tous leurs thèmes d'exemple. Riske
précise que **les angles sont identiques dans tous les systèmes** — le risque se limite aux cuspides
intermédiaires. (Co-Star s'est fait épingler pour avoir utilisé Porphyry.)

### Géo + fuseau horaire — vérifié empiriquement sur ta machine

⚠️ **`cities500` échouerait sur le Québec.** 2 145 des 2 702 lieux québécois ont `population=0` dans
GeoNames, et ~1 100 municipalités n'existent que comme `ADM3`, couche que les fichiers `cities*`
excluent par conception. Trois-Pistoles, Rivière-Éternité, Notre-Dame-du-Portage : **absents**. Même
Baie-Saint-Paul (7 146 hab.) manque de `cities15000`.

✅ **Recette validée** : `CA.zip` + `FR.zip` filtrés sur `feature_class='P' OR feature_code IN
('ADM3','ADM4')` → 139 956 lignes → **18 Mo de SQLite indexé**. Tous les villages manquants résolvent.
Licence **CC BY 4.0** → attribution GeoNames visible obligatoire.

✅ **GeoNames fournit déjà le fuseau IANA par lieu** (champ 18), concordant avec timezonefinder sur
tous les points testés → **on se passe de la lib et on économise ~90 Mo**.

⚠️ **Faille de déterminisme actuelle** : macOS embarque tzdata **2026b**, le paquet pip est **2026.3**.
`ZoneInfo()` lit `/usr/share/zoneinfo` et **ignore silencieusement le paquet pip** → tes calculs
dépendraient de la version macOS, qui bouge à chaque mise à jour système. **Fix : épingler
`tzdata==2026.3` + forcer `zoneinfo.reset_tzpath(to=[])`** et journaliser `IANA_VERSION` dans chaque thème.

⚠️ **Trois limites historiques irréductibles**, à afficher plutôt qu'à masquer :
- **Montréal avant 1970** : tzdata a fusionné `America/Montreal` → `America/Toronto`. Le LMT devient
  faux de **23 min (≈ 5,8° d'Ascendant)** avant 1884, et les règles montréalaises 1917-1973 sont
  perdues → **une heure pleine d'écart** pour les naissances de fin octobre/novembre 1949-1950.
- **France zone libre 1940-44** : `Europe/Paris` ne modélise que la zone occupée. Écart d'une heure
  dans deux fenêtres précises (1940-06-14→1941-05-04 et 1941-10-05→1942-03-09).
- **LMT** : tzdata donne le LMT de la ville *de référence*, pas du lieu de naissance (Québec vs
  Toronto ≈ 32 min ; Marseille +12 min vs Paris). **À calculer soi-même : `longitude × 240 s`.**

🎭 **Une ironie qui mérite d'être connue** : la doc de tzdata admet que ses données d'avant 1970
viennent souvent « *d'ouvrages d'astrologie sans citations, dont les compilateurs ont manifestement
inventé des entrées* ». Valider l'app contre un atlas astrologique **et** contre tzdata ne serait donc
pas deux vérifications indépendantes. Il n'existe pas d'équivalent ouvert de l'atlas ACS (en faillite) :
**tzdata + LMT calculé est le plafond réaliste.**

**Heures ambiguës** (changement d'heure) : un écart d'une heure déplace l'Ascendant de ~15°. Python
renvoie silencieusement un résultat par défaut, **sans exception**. → **détecter et faire trancher
l'utilisateur**, jamais deviner.

### Empreinte disque

| Composant | Taille |
|---|---|
| DE440s (1849-2150, domaine public) | 32 Mo |
| SQLite lieux (CA+FR, P+ADM3/ADM4, indexé) | 18 Mo |
| tzdata épinglé | 2,5 Mo |
| Corpus JSON | ~2 Mo |
| **Total** | **~55 Mo** |

### Garanties de déterminisme

- **Zéro LLM au runtime.** C'est la garantie principale — tout le reste en découle.
- Vendoriser et **hasher (SHA-256) au démarrage** : DE440s, base de villes, tzdata. Refus de démarrer si écart.
- `requirements.txt` **entièrement épinglé** (`==`), numpy compris. **Python 3.11.15** (déjà l'interpréteur de l'écosystème).
- **Tests golden écrits AVANT le code** : ~20 thèmes de référence, tolérance 1e-6°, incluant Québec
  1975 avec DST, une heure ambiguë de bascule automnale, France 1943, une naissance à 60°N (repli
  Placidus), un cas hémisphère sud, un cas équateur. **C'est le filet qui permettra de changer
  d'implémentation d'éphémérides sans rien casser.**
- Jamais de `set` sur le chemin de sortie (ordre non déterministe) — `list`/`tuple` ou tri explicite.
- Jamais de `datetime.now()` dans le calcul : tout en UTC explicite, l'instant passé en paramètre.
- Arrondir **à l'affichage seulement**, jamais en cours de calcul.

---

## 7. Le vrai risque : le mur du corpus

**Ce n'est pas le juridique — les marques s'évitent facilement. C'est l'éditorial.**

The Pattern est mort de ça : *« les readings cessent de sembler personnels dès qu'on voit les cinq
mêmes descripteurs recyclés chez tous ses amis »*. Co-Star aussi, en ne traitant réellement que
Soleil/Lune/Ascendant → « écrit par des robots ».

**Un corpus trop petit se voit en trois semaines.** C'est la seule chose qui peut tuer ce projet.

### Le chantier, chiffré honnêtement

| Bloc | Entrées | Notes |
|---|---|---|
| Astro natal | ~528 | schéma Riske, texte original |
| Astro quotidien | ~340 | schéma Riske prédictif |
| Numérologie | ~150 | calculs classiques, vocabulaire propre |
| Tarot (22 majeurs + 56 mineures) | 78 | rédigé **depuis la carte**, jamais depuis le nombre |
| Âges de la vie | ~20 | Dryburgh, fort ROI |
| Types soli-lunaires | 8 | Von Grüt |
| Règles de croisement / résonance | ~100 | **le différenciateur** |
| **Total** | **≈ 1 220** | **~100-150k mots originaux** |

⚠️ **Les quatre livres sont sous copyright** (Llewellyn, Eyrolles), avec interdiction explicite de
reproduction. Ils fournissent le **schéma de données** — quelles entrées, quels axes, quelles orbes,
quelle longueur cible — **jamais le texte**. Les ~1 220 entrées seront rédigées en original, sous
charte éditoriale. C'est aussi ce qui rend l'app commercialisable.

### La charte éditoriale — la couche Osho

**Osho n'est pas un module, c'est la charte qui s'applique à chaque texte du corpus.** Quatre règles,
tirées du traitement des cartes « négatives » du jeu :

1. **Recadrer en conditionnement, jamais en faute.** Constat → normalisation → déculpabilisation → apprentissage.
2. **Désigner le système, jamais l'individu.** La personne n'est pas coupable, elle est la cible.
3. **Humour comme désamorçage.** Le jeu parle des « *so-called* negative cards » — il refuse la catégorie.
4. **Registre constatif** : « tu es en train de… », jamais « tu es… » ni « tu vas… ».

Ce que Dryburgh apporte au cadrage : *« Bon thème, mauvais thème, peu importe ! »* — une énergie n'est
ni bonne ni mauvaise, elle existe ; un « mauvais » thème signifie seulement que les énergies « ne
disposent pas de canaux d'expression adaptés ». **Le conseil du jour devient « ouvrir un canal
d'expression », pas « subir un transit ».** C'est exactement la philosophie demandée.

Les trois autrices convergent sur le libre arbitre — Riske : *« never depend upon astrology to make
decisions for you »*, des repères « pour éveiller ta réflexion, pas des "il faut" ». **Cohérence
philosophique confortable.**

### Honnêteté épistémique

Manto porte un `niveau_preuve: limité` honnête, Cochrane à l'appui. **Ce projet mérite la même
droiture, et elle est plus facile qu'il n'y paraît** : l'astrologie n'a aucune validité prédictive
démontrée, et **le cadrage Osho résout le problème au lieu de le contourner**. L'app ne prétend pas
prédire — elle offre un **miroir structuré pour l'examen de soi**, dont la valeur est dans la
réflexion qu'il déclenche, pas dans la véracité du signal. C'est à la fois intellectuellement honnête
et fidèle à la source. **À dire clairement dans l'app, sans s'excuser.**

---

## 8. Ce qu'on ne peut pas faire

### 🔴 Osho — impasse juridique dans l'UE, et le concurrent existe déjà en français

**C'est le point le plus grave du dossier, et il est plus dur que je ne le pensais d'abord.**

**L'app officielle existe, elle est vivante, et elle est déjà traduite en français** : *Osho Zen Tarot*,
éditeur **Osho International Corp.**, 8,99 € en achat unique, **v4.17 (mai 2025)**, 79 cartes,
hors-ligne, **12 langues dont le FR**.
→ Note **US 4,7 (172 avis)** mais **FR 3,8 (18 avis)** — les avis français critiquent explicitement la
relecture de la traduction. *Le français existe, mais il est mal fini.* **C'est la seule brèche.**

**Statut juridique — le split US/UE joue contre nous :**

| | 🇺🇸 États-Unis | 🇪🇺 Union européenne |
|---|---|---|
| Marque « OSHO » | **ANNULÉE** pour généricité (TTAB, 13/01/2009) ; « OSHO ZEN TAROT » explicitement annulée | **VALIDE** — EUTM n° 001245300, Osho International Foundation (Zurich). Contestation **rejetée définitivement**, Tribunal de l'UE, T-670/15, 11/10/2017 |

⚠️ **La victoire américaine de 2009 est un faux espoir** : elle ne porte que sur la **marque**, jamais
sur le **copyright des images**, et ne vaut pas en Europe.

| Élément | Verdict |
|---|---|
| Les **79 images** (Ma Deva Padma) | 🔴 **© 1994 Osho International Foundation** — déclaré par l'artiste elle-même. **Négocier avec Padma ne servirait à rien : elle n'a rien à céder.** Point d'arrêt absolu. |
| **Textes/commentaires d'Osho** | 🔴 Décès 1990 → protégés jusque ~2060 dans l'UE. |
| Le nom **« OSHO »** | 🔴 Interdit en UE à titre de marque. |
| Les **noms des 79 cartes** | 🟠 Zone grise. Titres isolés probablement trop courts pour le droit d'auteur — mais la **liste structurée** peut relever du droit *sui generis* des bases de données, et les reproduire **sert de preuve d'intention**. Ne protège de rien. |
| Le **concept « tarot zen non-prédictif »** | 🟢 **Libre.** Les idées ne sont pas protégeables. |

**Il faut le dire nettement : une app tierce « Osho Zen Tarot » n'est pas viable dans l'UE.** Cumul
rédhibitoire — marque confirmée en dernier ressort, copyright intégral sur images **et** textes,
titulaire unique, actif, procédurier (10 ans de contentieux), qui **occupe déjà le créneau avec une
app maintenue et traduite en français**.

✅ **Voie praticable : la philosophie, jamais le jeu.** Le concept « miroir du présent plutôt que
prédiction » est libre. **Notre propre jeu de concepts, nos propres visuels, zéro référence à Osho** —
ni dans le nom, ni dans les images, ni dans les textes, ni dans les noms de cartes. C'est une
**contrainte de conception, pas un risque à gérer**. Ce qui est acquis (la philosophie) est justement
ce qui nous intéressait ; c'est l'exécution qui doit être entièrement neuve.

*(À noter : la structure Golden Dawn — 22 arcanes ↔ 12 signes + 7 planètes + 3 éléments — est du
domaine public (Mathers, 1888). Notre pont ne dépend en rien d'Osho.)*

### Autres interdits

- **Ni « Numérologie Stratégique® », ni « arbre personnel », ni « triangle fondamental »** (marque INPI).
  → Calculs pythagoriciens (libres depuis des siècles) + notre vocabulaire et notre métaphore.
- **Aucun texte des 4 livres d'astrologie ni du Phillips.** Schéma oui, texte non.

⚠️ Rien de ce qui précède n'est un avis juridique. Si le projet va vers la commercialisation, le
périmètre « inspiration Osho » mérite une validation par un conseil en PI.

---

## 9. Plan de développement proposé

**Phase 0 — Le spike de calcul (LE risque technique).** Skyfield + DE440s + ASC/MC + Placidus, validés
contre astro.com sur les ~20 thèmes golden (dont hautes latitudes, DST ambigu, hémisphère sud). Tests
écrits avant le code. Chaîne géo (SQLite CA+FR) + tzdata épinglé + LMT calculé. **Si ça ne passe pas,
tout le reste est théorique.** ~3-5 jours.

**Phase 1 — Le squelette avec un corpus RÉDUIT (~150 entrées).** Portrait + Jour de bout en bout, avec
juste assez de texte pour juger le ressenti. **But : valider l'UX et le ton AVANT d'écrire 1 220
entrées.** C'est le garde-fou contre le chantier inutile. On ouvre l'app 15 matins de suite et on voit
si ça tient.

**Phase 2 — Le corpus complet.** Le gros du travail : agents en parallèle, par lots, sous charte
éditoriale, avec passe de vérification. C'est là que passent les semaines.

**Phase 3 — Le croisement et les cycles.** Moteur de résonance/tension, année personnelle, carte de
l'année, âges de la vie.

**Phase 4 — Finition.** Le Ciel (thème dessiné), le Miroir (journal), voix optionnelle (Voice Station),
thème visuel.

**L'ordre est délibéré : le risque technique d'abord, le ressenti ensuite, le volume en dernier.**

---

## 10. Décisions (Martin, 2026-07-15)

1. ✅ **Commercialisation = scénario crédible → Skyfield (MIT) dès maintenant.**
   Conséquences actées : module de maisons à coder (ASC/MC, Placidus itératif avec repli Porphyry
   borné, Whole Sign/Equal), nœud moyen par polynôme de Meeus, vitesse par différences finies.
   pyswisseph utilisable **en dev uniquement, comme oracle de test golden** — jamais expédié.
   → Le corollaire commercial : **achat unique**, pas d'abonnement. C'est cohérent avec le local/privé
   (« vos données ne sortent pas de votre appareil, il n'y a rien à vous vendre en plus ») et ça nous
   distingue frontalement de Nebula (crédits de voyance) et de CHANI/The Pattern (~84-110 €/an).

2. ✅ **Le livre de Castells est obtenu** — `DOCUMENTS DE RÉFÉRENCE/Numérologie_9782212597790.epub`.
   Cible : l'annexe « Faites vos calculs ! », p. 291-307.

3. ✅ **CASTELLS EST LA SOURCE DE RÉFÉRENCE POUR LA NUMÉROLOGIE — elle l'emporte sur Phillips en cas
   de divergence.** *(Décidé le 2026-07-15.)*

   **Livre vérifié et analysé** : Castells & Durandy, *Numérologie*, Eyrolles, ISBN 9782212597790,
   90 167 mots, annexe p. 291-308. **Algorithmes reconstruits et validés 71/72 (98,6 %)** contre les
   exemples chiffrés et les 5 portraits (Jobs, Obama, Veil, Federer, Rowling). *(La date OPF dit 2021,
   mais le contenu date de 2017-18 — c'est le fichier qui a été refabriqué, pas le livre.)*

   ### ⚠️ La décision doit être NUANCÉE — la recherche a révélé un VIDE, pas une divergence

   **Castells n'a AUCUN module prévisionnel.** Recherche exhaustive sur les 90 000 mots :
   « mois personnel » → **0 occurrence**. « jour personnel » → **0**. « clé des saisons » → **0**.
   « anniversaire » → **0**. « année personnelle » → **1 seule**, anecdotique.

   Sa seule formule est glissée dans une phrase p. 69 : `année_perso = red_full(tronc + année_en_cours)`
   — **algébriquement identique à la formule classique** (le tronc ≡ jour + mois mod 9). **La bascule
   anniversaire vs 1ᵉʳ janvier n'est spécifiée nulle part.**

   → **Conséquence : « Castells > Phillips » N'A PAS D'OBJET sur la couche temporelle.** Ce n'est pas
   une divergence à arbitrer, c'est un **silence** — et un silence ne peut pas l'emporter. **Castells
   est une méthode de PORTRAIT STATIQUE (7 clés), pas de dynamique temporelle.**

   → **Ça confirme l'architecture** : le conseil quotidien vient du **ciel**, qui bouge tous les jours.
   La numérologie fournit le **fond**, jamais le jour. *(Aucune des deux sources n'a de jour personnel.)*

   ### La règle, corrigée

   | Couche | Source | Motif |
   |---|---|---|
   | **Portrait natal** | ✅ **Castells** | Plus riche, validée à 98,6 % |
   | **Couche temporelle** | ⚠️ **Castells est muette** → Phillips (mois × année perso, 108 entrées) ou rien | On ne peut pas suivre un silence |
   | **Le JOUR** | 🌌 **Le ciel** | Ni l'une ni l'autre n'a de jour personnel |

   ### 🎁 Les deux grilles sont COMPLÉMENTAIRES, pas concurrentes

   **Découverte importante** : la grille de Castells se construit **uniquement sur les LETTRES** du nom
   (la date n'y entre pas) ; celle de Phillips **uniquement sur la DATE**. **Elles ne se recouvrent en
   rien.** → Garder les deux n'est pas un mélange incohérent, c'est une **addition légitime** : grille
   des lettres (Castells) + grille 3×3 et 15 flèches de la date (Phillips, validées 15/15). À renommer.
   **La règle « ne jamais mélanger les deux méthodes sur le même nombre » reste absolue** — mais ici il
   n'y a pas de même nombre.

   ### Ce que Castells apporte, et que Phillips n'a pas

   1. 🔑 **Les « mémoires familiales » 13/14/16/19** — une **DEUXIÈME famille de sous-nombres**, avec
      hiérarchie de pondération explicite (p. 306-307 : jour/année/racines/tronc = *très forte* →
      feuilles/fruits = *forte* → 1ᵉʳ prénom/nom = *relative* → autres prénoms = *faible*). **L'apport
      le plus original et le plus exploitable.**
      ⚠️ **Distinction capitale, validée sur les 5 portraits** : un **maître-nombre** trouvé dans
      n'importe quelle route **devient la valeur** ; une **mémoire familiale** ne devient **jamais** la
      valeur — c'est un **drapeau annexe**.
   2. 🔑 **Le système multi-routes** : chaque nombre se calcule par 2 à 4 routes donnant toutes le même
      réduit mais des **sous-nombres différents** → plusieurs lectures d'une même valeur.
   3. **33 actif**, traité comme **variante de 6** (jamais axe autonome). **44 n'existe pas.**
   4. Grille fondée sur les lettres (voir ci-dessus).

   ### ✅ La convention des accents — TRANCHÉE, noir sur blanc

   **Castells est TRANSPARENTE** : p. 291, encadré « En pratique », **textuellement** `é, è = e` ·
   `ä = a` · `ç = c`. **É vaut 5 comme E.** Ce n'est pas une inférence — c'est écrit, **et confirmé par
   l'exemple chiffré p. 296** où `STÉPHANE = 34`, total atteignable uniquement avec É = 5.

   → Implémentation : NFD + suppression des marques `Mn`. **À publier dans l'app** — aucune app FR ne
   documente sa convention.
   → *Réserve honnête : le livre ne nomme que `é è ä ç` ; généraliser à `ê î ô û à ù ï` est une
     inférence, mais très sûre (les 3 exemples couvrent aigu, grave, tréma et cédille).*

   ### ✅ Le trait d'union — spécifié, et structurant

   Il **ne fusionne pas** les prénoms : il les garde **séparés comme deux unités de calcul** dont on
   additionne les totaux. → **Le découpage en tokens est la variable la plus sensible de tout
   l'algorithme** (les routes réduisent *par token*).

   ### ⚠️ Trois zones grises à arbitrer (le livre est muet — ne pas deviner)

   1. **Apostrophes et particules** (D'Artagnan, van, de) : **0 occurrence** dans les 90 000 mots.
      1 token ou 2 ? Le réduit final est le même, **mais les sous-nombres diffèrent** — or ce sont eux
      qui portent les maîtres et les mémoires, c'est-à-dire toute la valeur de la méthode.
   2. **Bascule de l'année personnelle** : anniversaire ou 1ᵉʳ janvier ? « L'année en cours » suggère le
      civil, mais c'est une inférence lexicale.
   3. **La « route 4 »** (lignes feuilles + fruits) : suggérée p. 295 (« vous trouverez *peut-être* un
      maître-nombre »), **aucun exemple ne la démontre**, et l'interprétation littérale casse le
      portrait de Jobs.

   ### 🐛 Deux anomalies du livre, à ne pas reproduire

   - **Simone Veil est calculée sous son NOM D'ÉPOUSE**, alors que l'en-tête annonce « née Simone
     Jacob ». « Simone Jacob » ne reproduit aucun de ses 8 nombres ; « Simone Veil » les donne **8/8**.
     Cohérent avec sa propre règle (nom d'épouse si porté plus longtemps — 68 ans), mais l'en-tête est
     trompeur.
   - **J. K. Rowling, seconde racine** : le livre annonce **22**, les 4 routes documentées donnent
     **13/4**. Aucune variante de nom testée ne produit 22, et la seule règle qui y mènerait est
     **réfutée par le livre lui-même** (elle casserait le fruit de Rowling et la racine de Jobs).
     Erreur du livre, ou nom de naissance non divulgué. Sans propagation.

   ⚠️ **Une couche non publiée existe** : l'algorithme complet des mémoires familiales est
   explicitement hors périmètre de l'annexe (« du fait de la complexité des algorithmes »), le livre
   renvoyant à son site. **Ce qu'on a est le repérage des mémoires, pas l'algorithme des auteurs.**

   ### Ligne de sécurité (inchangée)

   On prend les **calculs** (pythagoriciens, libres depuis des siècles), **jamais** le vocabulaire
   (racine/tronc/écorce/branche/feuille/fruit, « mémoire familiale », « dynamique de vie ») ni la
   métaphore de l'arbre — marque INPI. **Tous les axes seront renommés.**

   Le livre offre ~**93 entrées d'interprétation** (~300-670 mots), à granularité *1 nombre × 1 axe*,
   **sans aucun croisement à deux facteurs** — le croisement est laissé au lecteur. **C'est exactement
   ce que notre app doit produire, et personne ne le fait.** Le pattern réutilisable est sa
   sous-structure : *ce qui anime → comment alimenter cette énergie → ce qui arrive si elle ne l'est
   pas*. C'est une **structure**, pas un texte — et elle épouse parfaitement le cadrage de Dryburgh
   (« ouvrir un canal d'expression »).

4. ✅ **Phase 1 à corpus réduit (~150 entrées) avant tout engagement de volume.**
   Portrait + Jour de bout en bout, ouverts 15 matins de suite, pour juger le ton et le ressenti
   **avant** d'écrire les 1 220. Le périmètre v1 (garder ou non les 144 signe-sur-cuspide et les 56
   arcanes mineures) se tranchera à la lumière de ce test, pas à l'avance.

5. ⏳ **Le nom** — « L'Éphéméride » est une proposition (le mot porte à la fois la table astronomique
   et le calendrier qu'on effeuille chaque matin). Non tranché.

### Questions restées ouvertes

- **Le moteur réel de Co-Star** (vrai LLM ou NLG templatisée ?) et l'existence d'un backlash anti-IA
  caractérisé. La recherche n'a pas tranché. Intéressant pour le positionnement, **non bloquant** pour
  l'architecture.
- **Le segment « astro technique »** (TimePassages, Astrogold, Astro-Charts, Astrotalk) — non couvert,
  et c'est pourtant le plus proche de notre positionnement déterministe.
- **Aucune donnée publique de téléchargements ou de revenus** d'apps d'astrologie spécifique à la
  France. Trou réel, pas lacune de recherche.
