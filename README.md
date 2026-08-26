# Align

> **Phase 1 livrée (2026-07-16)** — l'app tourne de bout en bout, avec un corpus volontairement réduit.
> Conception d'ensemble : [PROPOSITION.md](PROPOSITION.md) · Charte : [data/corpus/CHARTE.md](data/corpus/CHARTE.md)

Coach de vie quotidien, **100 % local** et **100 % déterministe**, croisant la carte du ciel,
la numérologie et la philosophie du tarot zen.

**Align ne prédit rien. Il tend un miroir.**

## Lancer

```bash
python3.11 -m venv venv
./venv/bin/pip install -r requirements-dev.txt

# données (une fois)
curl -o data/ephem/de440s.bsp https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp
cd data/geo && curl -O https://download.geonames.org/export/dump/CA.zip \
            && curl -O https://download.geonames.org/export/dump/FR.zip \
            && unzip -o '*.zip' && rm *.zip && cd ../..
./venv/bin/python outils/construire_geo.py

./venv/bin/python -m pytest tests/ -q     # 400 tests
./venv/bin/python app.py                  # http://localhost:5073
```

## La thèse : le déterminisme n'est pas une contrainte, c'est le produit

Osho lui-même légitime le calcul contre le tirage (*The Further Shore*, ch. 5) : l'astrologie et le
tarot sont « **a reading of the unconscious of the person. It has nothing much to do with the
future.** » Il ne rejette pas ces outils — **il redéfinit leur objet**. Un calcul ne prédit donc
rien : il cartographie un conditionnement hérité pour permettre de s'en défaire. Un tirage
aléatoire, lui, réintroduirait la logique oraculaire qu'il rejette.

**Et la variété vient du ciel réel, pas d'un dé.** La Lune change de signe tous les 2,5 jours.
Mesuré sur 30 jours consécutifs : **au moins 25 lectures distinctes, sans le moindre aléa**
(`test_chaque_jour_differe_sans_tirage`).

## L'architecture-clé : le LLM fabrique, il ne tourne pas

- **À la construction** (hors ligne, sous charte) : un LLM rédige le corpus → `data/corpus/*.json`
- **À l'exécution** (chez l'utilisateur) : **zéro LLM, zéro réseau**. Python pur + lecture de tables.

Déterminisme **réel** (pas « température 0 », qui dérive au changement de modèle), zéro latence,
zéro RAM, aucun texte sous copyright embarqué, commercialisable.

## Le croisement — le différenciateur

Les autres apps **juxtaposent** les trois disciplines. Align les **croise**, par une charnière qui
n'est pas inventée pour l'occasion :

```
date de naissance ──► carte calculée (Arrien/Greer, 1977)
                          └──► correspondance Golden Dawn (Mathers, 1888)
                                    └──► une planète / un signe / un élément
                                              └──► lu dans le THÈME RÉEL
                                                    ├── RÉSONANCE (le facteur est fort)
                                                    └── TENSION   (il est en difficulté)
```

Les 22 arcanes correspondent **exactement** à 12 signes + 7 planètes classiques + 3 éléments.
La structure se referme sans reste — ce n'est pas une analogie décorative.

⚠️ **La table affichée partout sur le web est fausse** (Le Mat = Uranus, Le Pendu = Neptune,
Le Jugement = Pluton). C'est le système Case/BOTA des années 1920-30. La vraie table attribue des
**éléments** à ces trois cartes — les lettres-mères hébraïques — et c'est ce qui fait tenir le pont.

⚠️ **Rédiger depuis la carte, jamais depuis le nombre** : le 4 numérologique évoque structure et
autorité ; l'arcane 4 est L'Empereur ; mais en lecture zen son sens bascule vers la révolte contre
l'autorité. Dériver l'un de l'autre produit des contresens.

## État du corpus — 467 entrées, ~131 000 mots

| Axe | Entrées | Mots |
|---|---|---|
| **`astre_signe`** — les 12 astres × 12 signes (*comment* ça s'exprime) | **144** | **~40 000** |
| **`astre_maison`** — les 10 astres × 12 maisons (*où* ça se joue) | **120** | **~47 000** |
| `nombres_detail` — les 12 Caps approfondis | 12 | 11 963 |
| `annees_detail` — les 9 années approfondies | 9 | 9 198 |
| `arcanes` (22, avec lectures résonance/tension) | 22 | 5 379 |
| `nombres` (cap 12 · foyer 11 · année perso 9) | 32 | 3 557 |
| `transits` · `ciel` · `ciel_global` · `lexique` | 128 | ~13 000 |
| **Total** | **467** | **~131 000** |

**`astre_signe` + `astre_maison` = 264 entrées, jamais 144 × 120.** C'est la règle d'or : on
ADDITIONNE des tables indépendantes. Le produit ferait 17 280 cases — l'objection de Dryburgh
(« travail titanesque ») est fondée, et c'est le piège qui a tué The Pattern.

L'app **affiche ce qui manque** au lieu de le cacher.

## Le Ciel — l'idée globale, puis la profondeur à la demande

« *Une idée globale, mais qu'on peut facilement aller en demander plus.* »

Le Ciel jetait un tableau de treize lignes sans jamais dire l'essentiel. `moteur/synthese.py` le
calcule désormais, **déterministiquement** :

1. **Le trio** — Soleil, Lune, Ascendant. Le plus parlant, donc le premier. *(Et le corpus dit
   pourquoi ces trois-là : ce sont les plus rapides — le Soleil change de signe chaque mois, la
   Lune tous les 2,5 jours, l'Ascendant toutes les 2 heures. C'est là que deux personnes se
   distinguent vraiment.)*
2. **Ce qui domine, ce qui manque** — élément (seuil 4/10), modalité (5/10). Un thème **équilibré**
   est une information, pas un vide à masquer.
3. **Les concentrations**, **qui mène** (le maître de l'Ascendant, avec son état), **ce qui se voit
   le plus** (le barème de `force_planete`, réutilisé — deux barèmes divergeraient).

Puis **chaque ligne est cliquable** : ~900 mots par astre, ses deux lectures **additionnées**
(signe = *comment* · maison = *où*) plus ses liens, nommés sans jargon :
> *la Lune frotte contre Mars · les deux tirent dans des sens différents — ça demande un arbitrage,
> **ce n'est pas un malheur**.*

## L'honnêteté sur les planètes lentes

Uranus, Neptune et Pluton mettent 7 à 21 ans à traverser un signe : **leur signe est générationnel**.
Un horoscope vend « Pluton en Scorpion = tu es intense » à des dizaines de millions de gens nés
entre 1983 et 1995. Align le **dit** :

> *« Vraie pour une génération, donc utile pour personne. »*

Chaque entrée porte un champ `generationnel` qui l'explique — et son pendant, `pourquoi_c_est_personnel`,
sur l'axe maison : **la maison dépend de l'heure de naissance, donc elle est vraiment à toi.**
C'est le seul endroit où ces trois astres deviennent individuels.

## Le style — « une chute par entrée, pas par phrase »

Retour d'usage : *« la manière de tourner les phrases est parfois difficile d'approche »*.

**Le diagnostic n'était pas celui qu'on croyait.** Les phrases ne sont pas longues (médiane
15 mots). Le corpus écrivait en **aphorismes** : 1 363 tirets cadratins et 1 728 deux-points sur
8 565 phrases. Plus d'une phrase sur trois portait une chute.

**Défaut de densité, pas de qualité.** « Le Diable n'est pas en toi, il est dans le catalogue » est
excellent. Mais quand *chaque* phrase veut placer sa formule, aucune ne porte.
*(Origine honnête : les consignes de rédaction ont produit ça, en poussant à la variété et à la
formule sans jamais donner le droit d'être simple.)*

| | Avant | Après |
|---|---|---|
| Tirets cadratins / 100 phrases | 15-25 | **0** |
| Deux-points / 100 phrases | 17-30 | **0-1** |
| Longueur en mots | — | **−2,5 %** |
| Nombre de phrases | — | **+30 %** *(les chutes deviennent des phrases courtes — l'effet voulu)* |

**Les 14 fichiers du corpus sont passés au style, sans exception.** Le fond n'a pas bougé : mêmes
scènes, mêmes constats, mêmes recadrages. `tests/test_style.py` mesure et verrouille. **La chute porte mieux maintenant que le reste ne se bat plus avec elle.**

## Les trois échelles de temps

L'**année** donne le chapitre (cycle de 9 ans) · le **mois** donne la saison (cycle de 9 mois) ·
le **ciel** donne la journée. Elles s'additionnent, comme tout le reste.

⚠️ **Il n'y a PAS de « jour personnel »** — ni Phillips ni Castells n'en documentent un, et
l'inventer serait de la doctrine maison. Le jour vient du ciel, qui bouge tout seul. C'est publié
dans « Les Règles ».

⚠️ **Le mois personnel vient de la numérologie pythagoricienne classique**, pas des deux sources de
référence (l'une n'en parle pas, l'autre n'a aucun module de prévision). Choix d'Align, publié
comme tel.

## La vulgarisation — « un nombre nu ne dit rien »

Le diagnostic de la première session d'usage : Align parlait en **nombres nus**. « Le Cap 9 »,
« héritage 19 », « chantiers [6, 8] », « 6 sur 9 », « maison 10 », « balsamique », « son maître
mercure » — un nombre sans nom est la chose la plus opaque qui soit.

**Trois parades :**

1. **`data/corpus/lexique.json`** — chaque terme technique reçoit un nom en français clair et une
   explication d'une phrase. Rien n'atteint l'écran nu.
   `maison 10` → *ce que tu montres* · `balsamique` → *Fin de cycle* · `résonance` → *ton ciel appuie*
2. **Chaque nombre porte son nom** (`en_un_mot` du corpus approfondi) :
   *Le Cap 9 · **le lien*** · *Ton année 6 · **les liens***
3. **Le « ⌄ » repliable** — l'explication est disponible partout, jamais imposée.

Avant : `Lune en Lion, maison 10 · nouvelle`
Après : **La Lune éclaire ce que tu montres · Nouvelle Lune**

## Les détails — « les gens aiment ça »

Chaque nombre et chaque année sont **cliquables** et ouvrent un panneau plein écran :
**~1 100 mots** par entrée, contre ~130 avant.

Sections : *le mouvement · au quotidien · avec les autres · où ça peut s'exprimer · le piège*
(Caps) — *de quoi il s'agit · ce qui arrive souvent · ce qui aide · ce qui nuit · ta place dans le
cycle · comment savoir que ça a marché* (années).

**Le champ le plus important est le dernier** : `si_tu_ne_te_reconnais_pas`. Un nombre n'est pas un
verdict, c'est une hypothèse à éprouver — et le corpus le dit, en toutes lettres, sur chaque entrée.

## Les profils

Créer, **changer**, **modifier**, supprimer. La modification manquait, et ça bloquait l'usage :
l'heure de naissance est ce dont on doute le plus, et c'est ce qui déplace le plus l'Ascendant.
Corriger 14h30 → 03h00 fait passer l'Ascendant de 8° Scorpion à 28° Gémeaux — vérifié.

⚠️ **Piège trouvé en testant** : les profils créés avant l'ajout du champ `lieu_id` devenaient
**immodifiables** — le blocage même qu'on levait. Le serveur retrouve désormais le lieu par ses
coordonnées, toujours enregistrées (`Lieux.par_coordonnees`).

## Le vrai risque : le mur du corpus

Une app déterministe meurt de la **répétition**, pas du calcul. C'est ce qui a coulé The Pattern :
*« les readings cessent de sembler personnels dès qu'on voit les cinq mêmes descripteurs recyclés
chez tous ses amis »*.

**Trois parades, toutes structurelles :**
1. **Additionner des tables indépendantes, jamais les multiplier** — on écrit N + M entrées, pas
   N × M (`test_les_cles_sont_additives_jamais_cartesiennes`).
2. **La variété vient du ciel**, qui bouge tout seul.
3. **Des tests mesurent les tics** que la relecture humaine ne voit pas (`tests/test_corpus.py`).

**Le tic est arrivé pour de vrai, et c'est instructif** : un bloc avait ses 9 miroirs sur 9 ouverts
par « Tu es en train de… », les deux autres blocs 0 sur 50. Chaque rédacteur respectait sa consigne ;
le tic est né **entre** eux, invisible depuis chacun. Seule la vue d'ensemble le révèle — d'où
`test_aucune_ouverture_ne_domine`, qui mesure le corpus **assemblé**.

Même chose à l'échelle d'un écran : deux gestes peuvent s'ouvrir pareil le même matin alors que le
corpus global est varié. Les tables sont écrites séparément mais **lues ensemble** →
`jour.gestes_redondants` le détecte à la lecture, et l'app n'affiche qu'un des deux.

## Architecture

```
moteur/
  ephemerides.py   Skyfield + DE440s — positions, obliquité, ARMC, nœud
  maisons.py       ASC/MC + Placidus/Porphyry/signe entier/égal — trigo pure
  temps.py         heure locale -> UTC, LMT, heures ambiguës, limites historiques
  geo.py           recherche de lieu (SQLite GeoNames, une connexion par thread)
  theme.py         assemblage du thème natal
  numerologie.py   calculs pythagoriciens — vocabulaire Align
  tarot.py         cartes calculées + pont Golden Dawn
  aspects.py       aspects (3 classes), dignités, force d'une planète
  croisement.py    LE croisement — résonance / tension
  jour.py          le moteur du Jour — deux étages, une dominante
  corpus.py        lecture des tables (jamais de génération)
app.py             Flask, port 5073
data/corpus/       CHARTE.md + les tables JSON
tests/             400 tests
```

## Les conventions, publiées

Align **affiche ses règles de calcul** (écran « Les Règles », `/api/conventions`) et dit pour
chacune si elle est **imprimée dans une source** ou **tranchée par Align**.

C'est un angle mort du marché : deux conventions contradictoires coexistent en numérologie
française (É = 5 comme E, ou é = 1), **elles donnent des résultats différents pour le même nom, et
aucune app ne dit laquelle elle applique**. Déterministe doit vouloir dire *reproductible* **et**
*auditable*.

| Règle | Décision | Provenance |
|---|---|---|
| Accents | transparents — É = 5 comme E | **imprimé** (confirmé par STÉPHANE = 34) |
| Trait d'union | ne fusionne pas — deux unités | **imprimé** |
| Apostrophes | ignorées — D'Artagnan → DARTAGNAN | **tranché** (source muette) |
| Particules | **gardées**, soudées : de Gaulle → DEGAULLE | **tranché** (source muette) |
| Année personnelle | bascule le **1er janvier** | **tranché**, appuyé sur les sources |
| Maisons | Placidus, repli Porphyry annoncé | consensus des ouvrages |

**Deux horloges, et c'est voulu** : la couche numérologique bat sur le **calendrier** (année
personnelle + carte de l'année, même bascule — elles s'affichent ensemble) ; la couche astrologique
bat sur l'**anniversaire** (le retour solaire est de l'astronomie, pas une convention). Ce sont des
tables **indépendantes qu'on additionne** — les aligner de force serait une élégance de façade.

## Le vocabulaire d'Align

La métaphore de la source numérologique (arbre, racines, tronc, écorce…) relève d'une **marque
INPI**. Align a la sienne — celle de l'orientation, accordée à son nom :

**Le Cap** (la direction de fond) · **La Voix** (ce qui s'exprime) · **Le Foyer** (le centre
intérieur) · **Le Reflet** · **Le Geste** · **La Source** · **La Trace** · **L'Élan** ·
**Les Héritages** (13/14/16/19) · **Les Frictions** · **Les Appuis** · **Les Chantiers**

*« Héritage » et « chantier », pas « dette » ni « manque ».* On ne doit rien, on a reçu ; il ne
manque rien, il y a à bâtir. **Le choix des mots est la charte.**

## Interdits, vérifiés par les tests

- ❌ **Osho** — marque UE valide (T-670/15, 2017), images © 1994 OIF, textes protégés jusque ~2060,
  app officielle déjà en français. **La philosophie est libre ; le jeu ne l'est pas.**
- ❌ **« Numérologie Stratégique® »**, « arbre personnel », « triangle fondamental » — marque INPI.
  **Les calculs pythagoriciens sont libres depuis des siècles ; le vocabulaire ne l'est pas.**
- ❌ Tout texte des ouvrages de référence — ils donnent le **schéma de données**, jamais la prose.
- ❌ Prédire, prescrire, essentialiser, faire peur pour retenir l'attention.

`tests/test_corpus.py` les vérifie à chaque exécution. *(Nuance apprise : c'est l'ACTE d'énoncé qui
est interdit, pas la chaîne — « demande-toi de quoi tu as envie, **pas ce que tu dois faire** »
récuse la prescription au lieu de la commettre. Une regex naïve la condamnait à tort.)*

## Déterminisme — les règles tenues

- **Zéro LLM, zéro réseau, zéro aléa au runtime.**
- **Éphémérides vérifiées par SHA-256** au chargement — refus de démarrer sinon.
- **`tzdata` épinglé et forcé** (`reset_tzpath(to=[])`) : sinon `zoneinfo` lit
  `/usr/share/zoneinfo` et suit les mises à jour de macOS → les thèmes dériveraient en silence.
- **Aucun `datetime.now()` dans le moteur** — il vit dans la couche transport, et `?date=…` rejoue
  n'importe quelle journée à l'identique.
- **Itérations bornées** (Placidus, max 100), **aucun `set`** sur le chemin de sortie,
  **arrondi à l'affichage seulement**.

## Précision (Phase 0, contre l'oracle swisseph)

| | écart max | marge sous le seuil astrologique (1′) |
|---|---|---|
| **ASC / MC** | **0,000000″** | exact |
| **Cuspides Placidus** | **0,000134″** | exact en pratique |
| Planètes (pire cas : la Lune) | 2,14″ | 28× |

Les écarts planétaires résiduels ne sont pas nos erreurs : c'est l'écart entre DE440 (numérique) et
Moshier (analytique), et **Moshier est le moins précis des deux** — nos valeurs sont *meilleures*
que celles de l'oracle.

## ⚖️ pyswisseph est dev-only, et ce n'est pas négociable

**AGPL-3.0 pure, sans option commerciale**, projet dormant (dernier commit de code : 2023-06-04).
Payer les 700 CHF à Astrodienst débloquerait la bibliothèque C, **pas ce wrapper Python**. Il ne vit
que dans `requirements-dev.txt`, comme **oracle indépendant** du filet golden : deux moteurs sans
code commun qui s'accordent, c'est une vraie preuve.

`moteur/` ne l'importe jamais — et le moteur tourne sans lui, c'est vérifié.

## Lancement par Vibe Station

Align est inscrit dans `services.json` (racine `/PROJETS_IA/`) — et **c'est tout ce qu'il fallait** :
le serveur de Vibe relit le manifeste à chaque appel d'API, donc le bouton est apparu sans une ligne
de code. `run.sh` suit la convention de l'écosystème (Vibe le cherche avant `app.py`) et fait
`exec` pour que le PID vu par Vibe soit celui du vrai serveur — sinon « Arrêter » tuerait un wrapper
en laissant l'app orpheline sur le port.

Cycle **Arrêter → Démarrer** vérifié en conditions réelles depuis l'interface.

⚠️ Piège de l'écosystème : « Démarrer » ne recharge PAS le code d'une app déjà en écoute
(`isRunning` est vrai dès que le port répond). Après une modification : **STOP puis START**, jamais
seulement START.

## Licences

| Composant | Licence |
|---|---|
| Skyfield | MIT |
| DE440s (JPL/NASA) | domaine public |
| GeoNames | **CC BY 4.0 — attribution visible dans l'app** |
| tzdata (IANA) | domaine public |
| pyswisseph | AGPL-3.0 — **dev only, jamais expédié** |
