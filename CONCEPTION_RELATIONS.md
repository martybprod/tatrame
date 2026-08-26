# Conception — l'onglet « Relations » d'Align

> Proposition de conception, **aucun code écrit**. Rédigée le 2026-08-17 après distillation
> des 7 ouvrages relations (`_distillation/cartes_de_concepts_relations_astro.md`) et
> inventaire du moteur existant. À valider / amender avant toute implémentation.

---

## 0. Résumé en une page

**Ce qu'on veut** : un 6ᵉ onglet « Relations » qui lit la dynamique entre **deux personnes**,
d'abord la **compatibilité amoureuse**, mais aussi d'**autres types de liens** (travail,
parent-enfant, ami, associé…).

**La contrainte non négociable = la thèse d'Align** : 100 % déterministe, 100 % local, zéro
LLM au runtime. Le LLM ne sert qu'à **fabriquer le corpus hors ligne**, l'app ne fait tourner
que du Python + JSON. Deux mêmes personnes + même type de relation → **sortie strictement
identique et rejouable**. On ne prédit pas, on **cartographie un lien** pour mieux le vivre.

**La bonne nouvelle** : le moteur calcule **déjà** presque tout ce qu'il faut. Il ne manque
pas de calcul lourd, il manque **une couche de mise en relation à deux** + **du corpus**.

**Le piège à éviter absolument** : le **mur du corpus** version « paires ». Une grille
« 12 signes × 12 signes × N types de relations × M couches » explose en milliers d'entrées et
tue le projet (comme The Pattern est mort de la répétition). La parade est la **règle d'or
déjà éprouvée d'Align : on ADDITIONNE des tables indépendantes, on ne les MULTIPLIE jamais.**
Tout le design ci-dessous découle de cette règle.

---

## 1. Ce qui est DÉJÀ calculable (inventaire du moteur)

Chaque profil (`data/profils/*.json`) contient déjà **tout le nécessaire** pour deux personnes :
`naissance` = { année, mois, jour, **heure, minute**, lieu, **lat, lon**, fuseau } + `prenoms_nom`.
Donc, sans **aucun** nouveau calcul astronomique/numérique, on dispose pour A et pour B de :

| Brique | Module existant | Ce qu'on en tire pour deux personnes |
|---|---|---|
| Thème natal complet (10 planètes + ASC + MC, maisons) | `ephemerides.py`, `maisons.py`, `theme.py` | Éléments de chaque luminaire, Vénus, Mars, Mercure ; positions pour la synastrie |
| Aspects intra-thème (3 classes, orbes tranchées) | `aspects.py` (`aspects_entre`) | **La logique d'angle/orbe se réemploie telle quelle** pour les aspects ENTRE deux thèmes |
| **135 textes d'aspects déjà rédigés** | `data/corpus/aspects_1..4.json` | Un aspect « ma Vénus / ton Mars » a le **même sens symbolique** qu'un aspect intra-thème → **réutilisables** |
| Astrologie chinoise + relations | `chinois.py` | **`relation_branches()` code déjà 六沖 choc / 三合 trine / 六合 harmonie / 六害 nuisance** — appliqué jour↔naissance, marche à l'identique **naissance A ↔ naissance B** |
| Signe chinois natal + élément | `chinois.py` (`pilier_annee`) | Triangle d'affinité + opposé + élément de chacun |
| Numérologie date **et** nom | `numerologie.py` | Cap (chemin de vie), Voix, Foyer, Élan de chacun — croisables |
| Nœuds lunaires | `noeuds.py` | Descendant / axe des nœuds (attirance, Skymates) |
| Croisement & badges résonance/tension | `croisement.py` | Le vocabulaire « ça appuie / ça frotte / neutre » existe déjà, réutilisable par axe |

**Conclusion** : le chantier Relations est à **~90 % du corpus + ~10 % de code de liaison**,
pas un chantier de moteur. C'est exactement le profil de risque qu'Align sait gérer.

---

## 2. Les entrées : A + B + un type de relation

### 2.1 Les deux personnes (dégradation gracieuse selon les données)

- **Personne A** = le profil actif par défaut.
- **Personne B** = soit **un autre profil existant**, soit un **« contact » léger** ajouté à la
  volée. Tout le monde ne connaît pas son heure de naissance → on **dégrade proprement** :

| Données de B connues | Couches disponibles |
|---|---|
| Date seule | Numérologie (Cap), signe chinois d'année + élément, Soleil occidental (souvent) |
| Date + heure + lieu | **Tout** : Lune, Ascendant, maisons, synastrie complète, chinois avec ascendant d'heure |
| Date + nom complet | + numérologie du nom (Voix, Foyer, Élan) |

  L'app **dit ce qui manque** (comme elle le fait déjà pour le corpus) : « Sans l'heure de
  naissance de B, on ne peut pas lire la Lune ni l'Ascendant — on s'en tient aux nombres, au
  signe solaire et au signe chinois. » Honnêteté, jamais de faux-semblant.

- **Vie privée** : ajouter la naissance d'un tiers reste **100 % local** (fidèle à la thèse).
  Une ligne de cadrage dans l'UI (« ces données restent sur ton appareil »).

### 2.2 Le type de relation = une LENTILLE, pas une multiplication

C'est **la** décision d'architecture. Les livres convergent :
- Arroyo : « le poids d'une compatibilité dépend du type de relation » (colocataire ≠ amant ≠ associé).
- Lau : **8 rôles** (famille, amoureux, associé, patron, ami, enseignant, opposant, médiateur)
  et **10 types de relation** (permanente, essentielle, mentorale, compétitive, contrôlante…).

→ On calcule **une seule fois** les affinités entre A et B (nombres, chinois, ciel). Le **type
de relation ne change pas le calcul** : il **sélectionne quelles couches on met en avant** et
**dans quel registre on lit**. C'est de l'**addition d'une table de cadrage**, pas une
explosion combinatoire.

| Type | Couches mises en avant | Registre de lecture |
|---|---|---|
| **Amour / couple** | Soleil-Lune, **Vénus-Mars**, arc de l'intimité (maisons 4→8), composite | désir, tendresse, sécurité, chimie |
| **Travail / associé** | **Mercure** (communication), **Saturne** (durée, structure), éléments | fiabilité, rôles, cap commun |
| **Parent-enfant** | **Lune** (sécurité, maison 4), Saturne (cadre, autorité), Cap/leçons | soin, transmission, cadre bienveillant |
| **Ami** | Mercure, éléments, **triangle chinois**, Jupiter | complicité, liberté, jeu |
| **Famille (fratrie…)** | Lune, éléments, opposés chinois, nœuds | loyauté, héritage, frictions anciennes |

**Une seule mécanique, N lentilles.** Ajouter un type de relation = ajouter **une ligne de
cadrage + un ordre de priorité**, pas un nouveau corpus complet.

---

## 3. Les couches de lecture (toutes additives, toutes déterministes)

### Couche A — Les nombres (Decoz + Buchanan)
- **Axe central** : le croisement des deux **Cap** (chemin de vie), 1–9. Lu dans **les deux
  sens** (A vu par B, B vu par A) — Decoz insiste : la perspective change le ressenti.
- **Harmoniques calculables** (Decoz) : nombres **identiques** = synchronie ; **écart de 2** =
  naturellement fluide ; **opposés** (1/9…) = attirance forte à pont conscient. C'est une
  **petite table de 4–5 règles**, pas 81 récits.
- **Croisements fins** : Voix (expression), Foyer (intime), Élan — en appui, jamais seuls.

### Couche B — Le ciel occidental (Arroyo + Skymates)
Ordre de lecture **hiérarchique** (évite la surcharge, donne le fil du texte) :
1. **Éléments** des points personnels (Soleil, Lune, Vénus, Mars, ASC) → indice de résonance
   (Feu-Air / Terre-Eau s'accordent ; polarités opposées se complètent). **Entièrement calculable.**
2. **Triade Soleil-Lune-Ascendant** croisée (le pilier d'entente profonde).
3. **Vénus-Mars** (goûts, désir) — surtout pour l'amour.
4. **Mercure** (la rencontre des esprits) — surtout travail/ami.
5. **Aspects précis entre les deux thèmes** (synastrie) : on réemploie `aspects.py` pour
   l'angle/orbe **et les 135 textes d'aspects déjà écrits** ; on repère le **« message
   dominant »** (un thème qui revient = le cœur du lien).
6. Jupiter/Saturne puis lentes, seulement si elles touchent un point personnel.

### Couche C — Le côté chinois (Lau ×2)
- **Triangle d'affinité** : même reste modulo 4 (Rat-Dragon-Singe, etc.) = calculable en une ligne.
- **Opposé du cercle** : branche n+6 mod 12 = calculable. **Non fatal** : « le signe qui demande
  le plus de médiation », jamais un verdict.
- **Relations fines déjà codées** : `relation_branches(A, B)` → choc / trine / harmonie / nuisance.
- **Cycle des 5 éléments** (Handbook) : génération (Bois→Feu→Terre→Métal→Eau) vs contrôle —
  deuxième couche chinoise, **calculable**, absente du seul livre « Relationships » (noté dans
  les cartes) mais présente dans le Handbook.

### Couche D — « Le vous » / le composite (Skymates 2) — *avancé, phase 2*
- Le **thème composite** = milieu des points des deux thèmes → un « 3ᵉ portrait », celui de
  **l'entité-couple**, distinct de chacun. **Calcul purement mathématique** (midpoint), donc
  parfaitement déterministe et implémentable.
- Registre différent : pas « êtes-vous compatibles ? » mais « **à quoi ressemble le lien que
  vous formez ?** » — sa vitalité, ses besoins, son masque social.
- Diagnostic de haut niveau réutilisable : le composite ressemble-t-il à A, à B, aux deux, ou à
  personne (les 4 cas « Choc des cultures / Féodal / Démocratie » de Skymates 2, reformulés).

---

## 4. La synthèse : un message dominant, **pas un score-verdict**

Les 7 livres l'exigent d'une seule voix, et **la charte d'Align l'exige déjà** :
- **Pas de % de compatibilité** qui se lit comme un destin. La note 1–5 étoiles de Lau **tente**
  le score global — on la **refuse** au niveau global (elle enfermerait), on garde des **badges
  par axe** (« ça appuie / ça frotte / neutre », déjà dans le moteur).
- La sortie = **résonances + frictions + « conditions pour que ça marche »** (le cadrage
  constructif de Lau : compromis, cap commun, médiateur, temps). Jamais « oui/non ».
- **Règle de synthèse** = le « double whammy » d'Arroyo/Skymates : quand plusieurs couches
  disent la même chose, c'est **le cœur du lien** → on le met en tête, on ne noie pas.
- Ton **déculpabilisant** non négociable : « aucune configuration n'est bonne ou mauvaise »,
  « la friction signale un besoin de communication, pas un verdict ».

---

## 5. Extension élégante — « le pouls de votre lien aujourd'hui »

Comme le **Fil du jour** colore chaque matin par le ciel réel, on peut coder **les transits du
jour au thème composite** → un **message relationnel quotidien** et déterministe (« aujourd'hui,
le ciel touche le Vénus de votre lien — une bonne journée pour… »). La variété vient du ciel,
zéro tirage. Cohérent avec l'ADN d'Align. **Optionnel, après le socle.**

---

## 6. Le corpus : décompte **borné et additif** (le nerf de la guerre)

Le seul vrai risque est le volume. Voici pourquoi il reste **maîtrisable** (ordre de grandeur,
à affiner) :

| Table | Entrées | Note |
|---|---|---|
| Paires de Cap (nombres) | ~45 (9×9 non ordonnées, lues 2 sens) | + petite table harmoniques (~5) |
| Résonance d'éléments | ~10–15 | Feu/Air/Terre/Eau croisés |
| Aspects de synastrie | **0 nouveau** | **réutilise les 135 textes existants** |
| Chinois : triangles + opposés + 4 relations | ~15–20 | logique déjà codée |
| Chinois : cycle des 5 éléments | ~10 | génération/contrôle |
| Composite (phase 2) | ~40–60 | planète-en-signe/maison du « nous » (additif) |
| Cadrage par type de relation | ~5 types × qq lignes | **lentille, pas corpus complet** |
| **Total socle (hors composite)** | **~130–180 entrées** | comparable à une passe existante |

**On reste dans l'ordre de grandeur d'UNE passe déjà livrée** (ex. les 180 `transits_precis`),
**parce qu'on additionne des tables indépendantes**. Toute tentation de faire
« signe×signe×type » nous ramènerait à des milliers d'entrées → **interdite**.

**Garde-fous corpus à reprendre tels quels** (leçons déjà chèrement apprises) :
- rédaction par **agents parallèles, un par « fond conceptuel » distinct**, **jamais** de
  fichier-modèle à recopier (sinon copie à 70 %) ;
- détecteur de **verbatim (suites de 8 mots)** + Jaccard, **champ par champ** ;
- test « aucune ouverture/geste ne domine » sur le corpus **assemblé** ;
- contrôle qui **voit 100 % des entrées gardées** (le trou le plus grave : tester 104/467).

---

## 7. L'apport des AUTRES ouvrages (au-delà des 7)

Le matériel pertinent ne se limite pas aux 7 livres — et une partie est **déjà distillée** dans
`_distillation/cartes_de_concepts.md` (24 ouvrages de coaching) :
- **Attached** (Levine & Heller) — styles d'attachement (sécure/anxieux/évitant) ;
- **Hold Me Tight** (Sue Johnson, EFT) — les conversations du couple, la « danse » des besoins ;
- **Les 5 langages de l'amour** (Chapman) — comment chacun donne/reçoit l'affection.

Ces trois-là **ne se calculent pas** depuis une date de naissance — mais ils sont **l'or du
registre de conseil** : ils nourrissent la couche « **conditions pour que ça marche** » (la
partie non-astrologique, humaine, qui fait atterrir la lecture). Ex. : une friction Lune-Mars en
synastrie se **conclut** par un conseil inspiré d'EFT (« nommer le besoin sous la colère »),
sans jamais citer le livre. **Personologie** (Secret Language of Destiny, déjà distillée) ajoute
la notion de **voie/voie opposée** (compagnons de route vs miroirs karmiques) réutilisable.

→ Répartition claire : **astrologie/chinois/numérologie = ce qui se CALCULE** ; **coaching
relationnel = la VOIX du conseil** qui clôt chaque lecture. Les deux s'additionnent.

---

## 8. UI — l'onglet « Relations »

- **6ᵉ bouton de nav** (il en existe 5 : jour, apercu, portrait, ciel, regles). Icône à créer
  (deux anneaux entrelacés, ou deux silhouettes) — cohérente avec le jeu SVG maison.
- **Flux** : choisir **A** (profil actif par défaut) → **B** (autre profil ou contact rapide) →
  **type de relation** (segmented control : Amour / Travail / Parent-enfant / Ami / Famille).
- **Sortie**, en réutilisant les composants existants (`tiroir()`, `aide()`, badges) :
  1. **En-tête de synthèse** : le message dominant + badges par grand axe.
  2. **Tiroirs repliés** (comme « Les sphères de ta vie ») : « Vos nombres », « Vos ciels »
     (éléments, luminaires, aspects), « Côté chinois », et — phase 2 — « Le vous » (composite).
  3. Chaque ligne **cliquable → détail** (~même patron que le Ciel/le Portrait).
  4. Pied : « conditions pour que ça marche » + rappel non-fataliste + « ce qui manque » si B est incomplet.
- **Les Règles** : ajouter les **conventions Relations** à l'écran `/api/conventions` (voir §9).

---

## 9. Conventions à trancher **et publier** (l'ADN « auditable » d'Align)

Comme pour les accents ou l'année au 1ᵉʳ janvier, on **tranche et on publie** (vert = sourcé,
ambre = choix d'Align là où les sources divergent) :
- **Orbes de synastrie** : reprendre les orbes déjà tranchées d'Align (`aspects.py`), pas celles
  (divergentes) des livres.
- **Lecture bidirectionnelle** des paires (A→B et B→A) : on montre les deux.
- **Pas de score global** : décision de produit à publier (« Align lit des axes, pas une note »).
- **Composite** : lieu de la 1ʳᵉ rencontre inconnu le plus souvent → convention de repli
  (midpoint géographique, ou composite sans maisons) — à trancher et afficher.
- **Chinois** : frontière Li Chun (~4 fév) déjà gérée ; réutiliser.

---

## 10. Découpage proposé en phases — **avec répartition Opus / Sonnet**

> **Principe de répartition** (déjà éprouvé sur Align : « Opus orchestre, Sonnet rédige ») :
> - 🧠 **Opus** = ce qui demande de la profondeur : architecture, **moteur déterministe**
>   multi-fichiers, **tests écrits AVANT le code** (et mutation-testés), conventions à trancher,
>   intégration délicate, **orchestration** des agents rédacteurs (briefs + fusion + garde-fous
>   anti-verbatim).
> - ✍️ **Sonnet** = ce qui est mécanique ou bien cadré : **rédaction du corpus** en agents
>   parallèles (un par « fond conceptuel », jamais de fichier-modèle), icône SVG, câblage UI
>   qui réutilise des composants existants, tables de cadrage répétitives.
>
> Rappel : le changement de modèle est **manuel** (`/model`) — ce tableau dit seulement quel
> modèle est le mieux adapté à chaque tâche.

### Phase R0 — cadrage & conventions
| Tâche | Modèle |
|---|---|
| Valider ce doc, arbitrer le périmètre | 🧠 Opus (+ toi) |
| Trancher les conventions §9 (orbes, pas de score, repli composite, bidirectionnel) | 🧠 Opus |
| Figer le **schéma de données JSON** des tables + le décompte de corpus | 🧠 Opus |
| Dessiner l'**icône de nav** SVG (2 anneaux/silhouettes) | ✍️ Sonnet |

### Phase R1 — socle amour, données complètes
| Tâche | Modèle |
|---|---|
| Nouveau module de liaison à deux (synastrie via `aspects.py`, résonance d'éléments, croisement des Cap, `relation_branches` A↔B) | 🧠 Opus |
| Câblage de la **réutilisation des 135 aspects** existants (mapping synastrie → corpus) | 🧠 Opus |
| **Tests écrits AVANT le moteur** : rejouabilité, dégradation gracieuse, anti-verbatim, couverture | 🧠 Opus |
| **Corpus** : paires de Cap (~45, 2 sens), harmoniques (~5), résonance d'éléments (~10-15), chinois triangles/opposés/relations (~15-20) — **agents parallèles, un par fond** | ✍️ Sonnet |
| Orchestration de ces agents (briefs distincts, fusion, détecteur 8-mots) | 🧠 Opus |
| Écran « Relations » + tiroirs (réutilise `tiroir()`/`aide()`/badges), type « Amour » seul | ✍️ Sonnet |
| Intégration nav + routage `app.py`/`index.html` (touche des fichiers centraux) | 🧠 Opus (revue) · ✍️ Sonnet (pose) |

### Phase R2 — les autres types de relation
| Tâche | Modèle |
|---|---|
| Concevoir le **mécanisme de lentille** (une table de cadrage + ordre de priorité par type) | 🧠 Opus |
| Rédiger les **lignes de cadrage** Travail / Parent-enfant / Ami / Famille | ✍️ Sonnet |
| Rédiger la **voix de conseil** (couche « conditions pour que ça marche », à partir du coaching déjà distillé : Attached, Hold Me Tight, 5 langages) | ✍️ Sonnet |
| Garde-fou anti-verbatim sur ces nouvelles tables | 🧠 Opus |

### Phase R3 — le composite (« le vous »)
| Tâche | Modèle |
|---|---|
| Calcul **midpoint** (milieu des points) + Midheaven/maisons composites + diagnostic 4 cas (Choc/Féodal/Démocratie/…) | 🧠 Opus |
| **Tests** du composite (vs un thème de référence, rejouabilité) | 🧠 Opus |
| **Corpus du couple-entité** (~40-60 : planète-en-signe / planète-en-maison du « nous ») — agents parallèles | ✍️ Sonnet |

### Phase R4 (option) — « le pouls du lien aujourd'hui »
| Tâche | Modèle |
|---|---|
| Transits du jour au composite (réutilise `jour.py`/`routeur.py`) | 🧠 Opus |
| Corpus des messages relationnels quotidiens | ✍️ Sonnet |

**Lecture d'ensemble** : Opus tient **l'ossature** (moteur, tests-avant, conventions,
orchestration) ; Sonnet abat **le volume rédactionnel** (le gros du corpus, l'UI de réutilisation,
l'icône). C'est exactement le partage qui a permis les passes précédentes d'Align sans exploser
le budget.

---

## 11. Ce qu'on NE fera PAS (garde-fous)

- ❌ Pas de **score/pourcentage de compatibilité** global (enferme, prédit).
- ❌ Pas de **grille multiplicative** signe×signe×type (mur du corpus garanti).
- ❌ Pas de **LLM au runtime** (casse le déterminisme = la thèse).
- ❌ Pas de reprise des **noms/textes** des auteurs (Doers/Thinkers, « solarisation »,
  archétypes nommés, descriptions par signe) — vocabulaire **100 % Align**.
- ❌ Pas de **prédiction** (« vous allez rompre / vous marier ») — un miroir du présent.
- ❌ Pas de ton **fataliste ou culpabilisant** — « conditions pour que ça marche », jamais un verdict.

---

## 12. Décision demandée

1. **Le principe « une mécanique, N lentilles »** pour couvrir amour + autres types — OK ?
2. **Le périmètre de la Phase R1** (amour, données complètes, réutilisation des 135 aspects) — OK ?
3. **Le contact léger** (ajouter B sans forcément l'heure, dégradation gracieuse) — OK ?
4. **Pas de score global**, sortie par axes + synthèse — OK ?
5. Le **composite** et **le pouls du jour** en phases ultérieures — OK ?
