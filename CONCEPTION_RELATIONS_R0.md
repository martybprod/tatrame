# Relations — Phase R0 : conventions figées + schéma de données

> Livrable de la Phase R0 (cadrage). Produit par **Opus**. Aucun code applicatif.
> C'est le contrat que la Phase R1 implémentera. Tout est ancré dans le moteur RÉEL
> (`aspects.py`, `chinois.py`, `numerologie.py`, `croisement.py`) — vérifié, pas supposé.
> Voir la vue d'ensemble dans [CONCEPTION_RELATIONS.md](CONCEPTION_RELATIONS.md).

---

## 1. Les conventions Relations — **tranchées**

Même schéma que `/api/conventions` (chaque règle = `regle` / `source` / `detail`, avec
`source ∈ {imprimé, tranché par Align, tranché par Align appuyé sur les sources}`). Les cinq
premières sont des **conventions de calcul** → à publier dans l'écran « Les Règles ». Les deux
dernières sont des **principes de conception** → documentées ici.

### C1 — Pas de score global de compatibilité *(à publier)*
- **règle** : Align ne donne **aucune note ni pourcentage** de compatibilité. Il lit des
  **axes** (nombres, ciel, chinois), chacun avec son badge `résonance / tension / neutre`.
- **source** : tranché par Align, appuyé sur les sources.
- **détail** : les 7 ouvrages refusent d'une seule voix le verdict « oui/non » (Arroyo :
  « méfie-toi du langage binaire et fataliste » ; Skymates : « aucune configuration n'est bonne
  ou mauvaise »). Un chiffre unique se lit comme un destin — exactement ce qu'Align refuse. On
  réutilise le vocabulaire de badges **déjà** dans `croisement.py` (`resonance`/`tension`/`neutre`).

### C2 — Orbes de synastrie = les orbes natales d'Align *(à publier)*
- **règle** : un aspect entre deux thèmes utilise les **mêmes orbes** que le thème natal :
  conjonction 8°, sextile 6°, carré 8°, trigone 8°, opposition 8° ; **12 corps aspectables**
  (10 planètes + ASC + MC) ; **3 classes** (conjonction / carré-opposition / sextile-trigone).
- **source** : tranché par Align.
- **détail** : les livres divergent (orbes 5–7° en synastrie). Align **ne mélange pas deux
  barèmes** — il réutilise `aspects.ASPECTS` et `aspects.CORPS_ASPECTABLES` tels quels. La
  logique d'angle/orbe de `aspects._ecart()` s'applique identiquement entre deux thèmes.

### C3 — Lecture bidirectionnelle des paires *(à publier)*
- **règle** : chaque paire se lit **dans les deux sens** (ce que A vit face à B, ce que B vit
  face à A). L'app montre les deux.
- **source** : imprimé (Decoz : « lire les deux sens, 5+8 et 8+5 » ; Skymates : chaque
  interaspect se lit dans les deux sens).
- **détail** : la perspective change le ressenti ; masquer un sens fausse la lecture.

### C4 — Le côté chinois réutilise le moteur existant *(à publier)*
- **règle** : l'affinité chinoise entre deux naissances se calcule sur les branches d'année :
  **triangle** (三合 trine, même élément produit), **harmonie** (六合), **choc** (六沖, branche
  +6 mod 12), **nuisance** (六害), **identique**, **neutre** — dans cet ordre de priorité.
- **source** : imprimé (Lau) + tranché par Align (réutilise `chinois.relation_branches`, déjà
  vérifié contre Joey Yap).
- **détail** : `relation_branches(i_A, i_B)` est **déjà codée** et symétrique en usage. L'opposé
  du cercle n'est **jamais un verdict** — « le signe qui demande le plus de médiation ». Le
  cycle des 5 éléments (génération/contrôle) est une **2ᵉ couche chinoise** ajoutée en R1.

### C5 — Composite : repli explicite quand le lieu de rencontre est inconnu *(à publier, R3)*
- **règle** : le thème composite (R3) se calcule par **milieu des points** (angle court). Le
  lieu de la 1ʳᵉ rencontre étant presque toujours inconnu, **repli** : composite **sans
  maisons** (planètes + aspects seulement). Le midpoint géographique des deux naissances est une
  variante possible, présentée comme telle.
- **source** : tranché par Align.
- **détail** : on **n'invente pas** un lieu faux pour dresser des maisons trompeuses ; on dit ce
  qu'on calcule et ce qu'on omet.

### P6 — Le type de relation est une **lentille**, pas un facteur *(principe de conception)*
- Le type (amour, travail, parent-enfant, ami, famille) **ne change pas le calcul** : il
  **sélectionne les couches mises en avant** et le **registre de lecture**. Interdiction d'une
  grille multiplicative signe×signe×type (= mur du corpus). Appui : Arroyo (« le poids dépend du
  type de relation »), Lau (8 rôles, 10 types).

### P7 — Dégradation gracieuse selon les données de B *(principe de conception, à publier en clair dans l'UI)*
- Date seule → nombres (Cap) + signe chinois d'année + Soleil (souvent). Date+heure+lieu →
  tout (Lune, ASC, maisons, synastrie complète). Date+nom → + numérologie du nom.
- L'app **affiche ce qui manque** (comme elle le fait déjà pour le corpus). Jamais de faux-semblant.

---

## 2. Le schéma de données — les tables de corpus (figées pour R1)

Toutes les tables vivent dans `data/corpus/` (comme l'existant), en JSON UTF-8, **additives**
(aucune n'est indexée par un produit d'axes). Champs communs au ton d'Align : phrases courtes,
tutoiement, une chute par entrée, jamais de prédiction.

### 2.1 `rel_nombres.json` — paires de Cap (chemin de vie)
Clé = **paire non ordonnée** `"min-max"` sur les Cap réduits 1–9 (les maîtres 11/22/33 sont
réduits à 2/4/6 pour la compatibilité, comme le fait Decoz ; convention à publier si on la retient).

```json
{
  "3-7": {
    "en_bref": "Deux façons d'habiter le monde qui se cherchent.",
    "vers_min": "Face à un 7, le 3 ...",       // ce que le PLUS PETIT nombre vit
    "vers_max": "Face à un 3, le 7 ...",       // ce que le PLUS GRAND nombre vit
    "atouts": "Ce qu'ils construisent bien ensemble ...",
    "frictions": "Là où ça frotte ...",
    "conditions": "Pour que ça marche : ..."   // le cadrage constructif (Lau)
  },
  "5-5": {
    "en_bref": "...",
    "meme": "Deux 5 : ...",                    // paires identiques → un seul texte (pas de sens A/B)
    "atouts": "...", "frictions": "...", "conditions": "..."
  }
}
```
- **Décompte** : 9 identiques + 36 mixtes = **45 entrées**.
- `vers_min` / `vers_max` portent la lecture bidirectionnelle (C3) sans dupliquer la clé.

### 2.2 `rel_harmoniques.json` — la méta-règle numérologique (Decoz)
Une petite table de **cadrage** calculée depuis les deux Cap, en surplomb de la paire :
```json
{
  "identiques":  { "note": "Vous vibrez au même nombre : ..." },
  "ecart_deux":  { "note": "Un écart de deux : une fluidité naturelle ..." },
  "opposes":     { "note": "Aux deux bouts (1/9, 2/8...) : forte attirance, pont à bâtir ..." },
  "autre":       { "note": "" }
}
```
- **Décompte** : **4 entrées**. Règle de sélection déterministe : `identiques` si égaux ;
  `opposes` si {1,9}/{2,8}/{3,7}/{4,6} ; `ecart_deux` si |a−b|=2 ; sinon `autre`.

### 2.3 `rel_elements.json` — résonance des éléments (Arroyo, Skymates)
Clé = **paire d'éléments non ordonnée**, appliquée aux points personnels (Soleil, Lune, Vénus,
Mars, ASC) de chacun :
```json
{
  "feu-air":   { "en_bref": "...", "texte": "...", "etat": "resonance" },
  "terre-eau": { "en_bref": "...", "texte": "...", "etat": "resonance" },
  "feu-eau":   { "en_bref": "...", "texte": "...", "etat": "tension"   },
  "feu-feu":   { "en_bref": "...", "texte": "...", "etat": "neutre"    }
}
```
- **Décompte** : C(4,2)=6 mixtes + 4 identiques = **10 entrées**. `etat` réutilise le vocabulaire
  de badges de `croisement.py` (résonance Feu-Air/Terre-Eau ; tension éléments qui « ne parlent
  pas la même langue » ; même élément = neutre/fluide selon Arroyo).

### 2.4 `rel_chinois.json` — le lien entre deux animaux
Deux sous-tables, **par TYPE de relation** (pas par animal → additif) :
```json
{
  "branches": {
    "choc":      { "en_bref": "...", "texte": "...", "etat": "tension" },
    "harmonie":  { "en_bref": "...", "texte": "...", "etat": "resonance" },
    "trine":     { "en_bref": "...", "texte": "...", "etat": "resonance" },
    "nuisance":  { "en_bref": "...", "texte": "...", "etat": "tension" },
    "identique": { "en_bref": "...", "texte": "...", "etat": "neutre" },
    "neutre":    { "en_bref": "...", "texte": "...", "etat": "neutre" }
  },
  "elements": {
    "genere":  { "texte": "L'un nourrit l'autre : ..." },   // cycle de génération
    "controle":{ "texte": "L'un tempère l'autre : ..." },   // cycle de contrôle
    "meme":    { "texte": "Même élément : ..." },
    "neutre":  { "texte": "" }
  }
}
```
- **Décompte** : 6 (branches) + 4 (éléments) = **10 entrées**. Clés `branches` = sortie directe
  de `relation_branches`.

### 2.5 Les aspects de synastrie — **réutilisation** + fin cadre
- **Réutilise `aspects_1..4.json` (135 textes existants)** comme description du sens de chaque
  aspect. On **n'en réécrit pas 135**.
- Nouveau fichier **mince** `rel_aspects_cadre.json` : une amorce de synastrie **par classe**
  (3 entrées) qui pose le « entre vous » avant de dérouler le texte réutilisé :
```json
{
  "conjonction":        { "amorce": "Vos {a} et {b} se superposent : ..." },
  "carre-opposition":   { "amorce": "Vos {a} et {b} se tirent : ..." },
  "sextile-trigone":    { "amorce": "Vos {a} et {b} se répondent : ..." }
}
```
- **Décompte** : **3 entrées neuves** + réutilisation des 135.
- **Convention de réutilisation (à tenir)** : on réutilise d'abord ; on n'écrit un texte de
  synastrie dédié **que là où la réutilisation sonne faux** (découvert par revue en R1). Ces
  surcharges éventuelles iront dans un `rel_aspects.json` clé `classe_pointA_pointB`, **au cas
  par cas**, jamais les 63 combinaisons d'office.

### 2.6 `rel_synthese.json` — le message dominant + clôtures
```json
{
  "dominante": {
    "resonance_forte": "Ce qui ressort le plus : ...",
    "tension_forte":   "Ce qui demande le plus de soin : ...",
    "mixte":           "..."
  },
  "pied": {
    "non_verdict": "Rien ici n'est un verdict : un lien se vit, il ne se calcule pas.",
    "conditions":  "Ce qui fait tenir un lien : ..."
  }
}
```
- **Décompte** : ~**6 entrées**. La règle du « double whammy » (Arroyo) choisit la dominante :
  l'axe dont le badge est le plus marqué, et si plusieurs couches disent la même chose → c'est le cœur.

### 2.7 Récapitulatif du corpus **NEUF** pour R1 (socle amour)
| Table | Entrées neuves |
|---|---|
| `rel_nombres.json` | 45 |
| `rel_harmoniques.json` | 4 |
| `rel_elements.json` | 10 |
| `rel_chinois.json` | 10 |
| `rel_aspects_cadre.json` | 3 |
| `rel_synthese.json` | 6 |
| **Total NEUF R1** | **~78 entrées** (+ réutilisation des 135 aspects existants) |

→ **En dessous** de l'estimation initiale (130–180) : la réutilisation des aspects fait le gros
du travail. On reste très loin du mur du corpus.

### 2.8 Tables des phases ultérieures (figées comme intention, pas pour R1)
- **R2** `rel_types.json` — par type de relation : `{ ordre_couches: [...], cadrage: "...",
  conseil: "..." }` (~5 entrées) ; la voix de conseil puise dans le coaching déjà distillé
  (Attached, Hold Me Tight, 5 langages).
- **R3** `rel_composite_*.json` — planète-du-« nous »-en-signe / en-maison (~40-60, additif).
- **R4** `rel_pouls.json` — messages du transit du jour au composite.

---

## 3. Le modèle de données « personne B » (contact léger)

- **Décision** : un contact est un **profil minimal**, stocké dans **`data/contacts/*.json`**
  (dossier neuf, même plomberie que `data/profils/`, mais liste séparée pour ne pas polluer le
  sélecteur de profils principaux).
- **Schéma** : identique à un profil, mais `naissance` peut **omettre** `heure/minute/lieu/
  lat/lon/fuseau`. Champs neufs : `"contact": true`, `"complet": <bool>` (true si heure+lieu
  présents → synastrie possible). `prenoms_nom` optionnel (active la numérologie du nom).
- **B peut aussi être un profil existant** : le sélecteur propose profils **et** contacts.
- **Vie privée** : stockage 100 % local (fidèle à la thèse) ; une ligne d'UI le dit.

---

## 4. Le module de liaison (esquisse d'API, pour cadrer R1 — Opus codera)

`moteur/relations.py`, fonctions pures et déterministes :
- `paire_nombres(cap_a, cap_b) -> {cle, sens, harmonique}`
- `resonance_elements(theme_a, theme_b) -> [{points, elements, etat}]`
- `synastrie(theme_a, theme_b) -> [interaspects triés par orbe]` (réutilise `aspects.ASPECTS`)
- `lien_chinois(natal_a, natal_b) -> {branche_rel, element_rel}` (réutilise `relation_branches`)
- `croiser_relation(a, b, type_relation) -> {synthese, axes[], manques[]}` (applique la lentille P6)
- Dégradation gracieuse : chaque fonction renvoie `None`/`manque` proprement si une donnée de B
  est absente ; `croiser_relation` agrège les `manques` pour l'UI (P7).

---

## 5. Tests à écrire **AVANT** le moteur R1 (Opus, mutation-testés)
- **Rejouabilité** : (A, B, type) identiques → sortie identique, octet pour octet.
- **Symétrie contrôlée** : `croiser_relation(A,B)` et `(B,A)` cohérents (mêmes axes, sens inversés).
- **Dégradation gracieuse** : B sans heure → aucune exception, `manques` renseigné, couches
  nombres/chinois/solaire présentes.
- **Couverture corpus** : toute clé calculable (45 paires, 10 éléments, 6 relations chinoises,
  3 classes d'aspects) tombe sur un texte ; garde-fou qui **voit 100 % des entrées** (leçon du
  trou 104/467).
- **Anti-verbatim** : détecteur 8-mots + Jaccard **champ par champ** sur le corpus assemblé.
- **Non-fatalisme** : le corpus Relations passe les tests de charte existants (pas de prédiction,
  pas d'essentialisation).

---

## 6. Ce que R0 laisse ouvert (à confirmer avant R1)
1. **Maîtres nombres en compatibilité** : les réduire à 2/4/6 (Decoz) ou garder 11/22/33 avec
   une table dédiée ? *Reco : réduire pour la paire, mentionner le maître en note — plus simple,
   fidèle à Decoz. À publier comme convention.*
2. **Réutilisation des aspects** : valider le principe « réutilise d'abord, écris du neuf seulement
   là où ça sonne faux » (vs écrire un corpus de synastrie dédié). *Reco : réutiliser — c'est
   l'énorme dividende, et la revue R1 trouvera les rares cas à surcharger.*
3. **Icône de nav** : 2 variantes en cours de production (agent Sonnet) — à choisir.
