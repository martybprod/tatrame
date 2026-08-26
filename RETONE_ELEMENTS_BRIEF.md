# Brief de chaîne — les 45 templates restants de l'axe éléments (Ta Trame)

> **Statut** : doctrine + moteur + 5 étalons validés par Martin (2026-08-19). À exécuter **en Sonnet**.
> Opus a posé le mécanisme et écrit 5 templates pilotes ; Sonnet écrit les **45 restants**.
> Cible : `data/corpus/rel_elements_v2.json` (on AJOUTE des clés au fichier existant).
> Respecte `data/corpus/CHARTE.md` §« Comprendre à la première lecture » (langage clair).

---

## 0. Ce qu'on fait

L'axe éléments compare, pour 5 points personnels, l'élément d'une personne et de l'autre. Chaque
combinaison `{point}_{paire}` a un **template** que `app.py::_texte_elements` remplit au rendu avec
les **prénoms**. Il faut écrire les 45 templates manquants (5 sont déjà faits, ne pas y toucher).

**Chaque template = une seule clé JSON** de la forme :
```json
"lune_feu-terre": { "texte": "Côté émotions, {terre} a besoin de calme…" }
```

---

## 1. Les 4 règles d'écriture (doctrine « langage clair »)

1. **Clair à la première lecture.** Concret, on dit QUOI. Mots de tous les jours. Verbes actifs.
   Ordre naturel (sujet → verbe → complément). UNE idée par phrase, phrases courtes. Pas de
   métaphore à décoder, pas de phrase à tiroirs, pas de chute à chaque phrase.
2. **Les NOMS** (via jetons, voir §2), jamais « l'un/l'autre » quand on peut nommer.
3. **Gender-safe** : aucun genre en base → **jamais « elle/il », jamais d'adjectif accordé**
   (« lente/lent », « contente/content »). **Que des verbes** pour décrire les personnes.
4. **Registre québécois d'abord** (France ensuite) : pas de tic hexagonal (« du coup », « rien ne
   prend », « un truc », « bosser », « carrément ») ; mais **pas de joual** (« pantoute », « pogner »,
   « niaiser »). Le naturel québécois qu'un Français comprend sans effort.

Ton conservé : **non-verdict**, chaleureux, complémentarité, une clôture constructive
(« Ça marche quand… »). Longueur cible : **70-100 mots, 5 à 6 phrases**.

---

## 2. ⚠️ Les JETONS (le point technique à ne pas rater)

Le moteur remplace les jetons par les prénoms. **N'écris jamais un prénom en dur.**

- **Paires d'éléments DIFFÉRENTS** → jetons d'élément : `{feu}` `{air}` `{terre}` `{eau}`.
  Chaque jeton = la personne qui a CET élément. Ex. `air-eau` → utilise `{air}` et `{eau}`.
- **Paires d'éléments IDENTIQUES** (les `neutre` : `air-air`, `eau-eau`, `feu-feu`, `terre-terre`)
  → les deux ont le même élément, donc jetons `{a}` et `{b}` (= les deux prénoms).

**Élision : n'y pense pas.** Écris naturellement « pendant que {terre} », « l'élan de {feu} » : le
moteur élide tout seul (« pendant qu'Arianne », « d'Arianne »). Ne pré-élide jamais un jeton.

La checklist §6 indique pour chaque clé les jetons exacts à employer.

---

## 3. Le sens des éléments, par domaine (pour écrire CONCRET)

**Grammaire des relations** (déjà calculée, pour info) : même élément = *neutre* ; Feu+Air ou
Terre+Eau = *résonance* ; tout autre croisement = *tension*.

| Élément → | **Soleil** (qui on est) | **Lune** (émotions) | **Vénus** (amour) | **Mars** (action) | **Asc** (première impression) |
|---|---|---|---|---|---|
| **Feu** | fonce, décide vite | réagit vite et fort | va droit vers ce qui plaît | fonce, s'impatiente | a l'air énergique, direct |
| **Air** | pense, a besoin d'échanger | se calme en parlant, met des mots | aime les mots, le jeu, la variété | agit par les idées, discute | a l'air vif, curieux, sociable |
| **Terre** | solide, concret, veut du durable | a besoin de calme et de stabilité | aime les gestes, les preuves | avance par étapes, sans se presser | a l'air posé, fiable |
| **Eau** | sensible, profond | ressent tout, capte l'ambiance | a besoin d'émotion, de sentir avant | agit au ressenti, en douceur | a l'air sensible, doux |

**Amorce de domaine** (pour varier quand un même couple a la même paire sur 2 points) :
Soleil « Au fond, … » · Lune « Côté émotions, … » · Vénus « En amour, … » · Mars « Quand vient le
temps d'agir, … » · Asc « Au premier contact, … » *(varie la formulation, ne la répète pas mot pour mot)*.

---

## 4. La structure d'un texte (selon l'état)

- **Tension** : dis ce que fait chacun (concret, par jeton) → ce qui accroche entre les deux →
  « ce n'est pas un défaut, juste deux façons de… » → ce que chacun apporte (complémentarité) →
  « Ça marche quand {X}… et que {Y}… ».
- **Résonance** : dis ce que fait chacun → comment ça circule bien entre eux → le petit risque
  (facilité qu'on gaspille / qu'on tient pour acquise) → « Ça reste [beau/vivant] longtemps quand… ».
- **Neutre (même élément)** : dis le trait qu'ils PARTAGENT → l'aisance que ça donne → le revers
  (deux pareils manquent de contraste / même angle mort) → « Ça tient bien quand l'un des deux… ».

---

## 5. Les 5 étalons (déjà dans le fichier — le niveau visé)

- `soleil_feu-feu` (neutre) : « Au fond, {a} et {b} fonctionnent au même rythme : les deux décident
  vite et passent à l'action sans attendre. […] Ça tient bien quand l'un des deux accepte, de temps
  en temps, de ralentir un peu pour deux. »
- `asc_eau-eau` (neutre) : « {a} et {b} donnent tous les deux une impression sensible, à fleur de
  peau. Vous captez vite l'ambiance d'un lieu […] Ça reste doux quand l'un des deux garde les pieds
  sur terre pendant que l'autre ressent. »
- `lune_feu-terre` (tension) : « Côté émotions, {terre} a besoin de calme et de stabilité […] {feu}
  réagit vite et fort […] Ça s'apaise quand {feu} baisse le ton d'un cran, et que {terre} accepte
  qu'un orage passe souvent vite et sans danger. »
- `mars_feu-terre` (tension) : « Quand vient le temps d'agir, {feu} veut avancer tout de suite […]
  {terre} préfère y aller étape par étape […] Ça marche quand {feu} accepte quelques étapes, et que
  {terre} se permet de foncer une fois de temps en temps. »
- `venus_air-feu` (résonance) : « En amour, {feu} fonce vers ce qui lui plaît, et {air} met des mots
  dessus […] Ça reste beau longtemps quand, de temps en temps, vous posez tout pour juste être ensemble. »

*(Note : `lune_feu-terre` et `mars_feu-terre` ont la MÊME paire mais des textes différents — le
domaine change. Fais pareil partout.)*

---

## 6. La checklist des 45 clés à écrire (exhaustive)

### NEUTRE — 18 clés (jetons `{a}/{b}`)
soleil_air-air · lune_air-air · venus_air-air · mars_air-air · asc_air-air
soleil_eau-eau · lune_eau-eau · venus_eau-eau · mars_eau-eau
lune_feu-feu · venus_feu-feu · mars_feu-feu · asc_feu-feu
soleil_terre-terre · lune_terre-terre · venus_terre-terre · mars_terre-terre · asc_terre-terre

### RÉSONANCE — 9 clés
soleil_air-feu · lune_air-feu · mars_air-feu · asc_air-feu   *(jetons `{air}/{feu}`)*
soleil_eau-terre · lune_eau-terre · venus_eau-terre · mars_eau-terre · asc_eau-terre   *(jetons `{eau}/{terre}`)*

### TENSION — 18 clés
soleil_air-eau · lune_air-eau · venus_air-eau · mars_air-eau · asc_air-eau   *(jetons `{air}/{eau}`)*
soleil_air-terre · lune_air-terre · venus_air-terre · mars_air-terre · asc_air-terre   *(jetons `{air}/{terre}`)*
soleil_eau-feu · lune_eau-feu · venus_eau-feu · mars_eau-feu · asc_eau-feu   *(jetons `{eau}/{feu}`)*
soleil_feu-terre · venus_feu-terre · asc_feu-terre   *(jetons `{feu}/{terre}`)*

**Déjà fait, NE PAS réécrire** : soleil_feu-feu, asc_eau-eau, lune_feu-terre, mars_feu-terre, venus_air-feu.

---

## 7. Validation en fin de chaîne
1. `python3 -c "import json; d=json.load(open('data/corpus/rel_elements_v2.json')); print(len([k for k in d if not k.startswith('_')]),'clés (attendu 50)')"` → **50**.
2. JSON valide (même commande sans erreur).
3. Grep tics hexagonaux : `grep -noiE "du coup|rien ne prend|pantoute|pogner|niaiser" data/corpus/rel_elements_v2.json` → rien.
4. Grep genre risqué : `grep -noiE "\b(elle|il)\b" data/corpus/rel_elements_v2.json` → inspecter (ne doit viser aucune personne ; « il y a », « il faut » sont OK).
5. Jetons cohérents : chaque valeur `texte` d'une clé à éléments différents contient bien ses deux
   jetons d'élément ; chaque clé même-élément contient `{a}` ET `{b}`.
6. `python -m pytest -q` → suite verte.
7. Relecture à voix haute d'un échantillon : ça doit sonner comme quelqu'un qui parle, pas qui écrit.
