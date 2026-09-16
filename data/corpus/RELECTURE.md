# Passe de relecture — textes des cartes (avant tout lot)

> Obligatoire avant de présenter un lot à Martin, et avant toute production
> en masse. Chaque lot a coûté une correction de sa part ; les défauts
> récurrents sont connus et listés ici. La passe se fait DANS L'ORDRE.

## 1. Vérité image (le piège n° 1 — cause de la moitié des corrections)

- Ouvrir l'image **VALIDÉE** (`_distillation/cartes_validees/`), jamais une
  itération du dossier racine. Vérifier par empreinte (md5) si un doute.
- Lister ce qui est **visible** : objets, couleurs, nombres, positions,
  directions. Puis relire le texte affirmation par affirmation :
  - nombres comptés sur l'image (branches, colombes, colonnes…) ;
  - positions et directions (devant/derrière — ATTENTION : un personnage qui
    marche vers nous projette son ombre DEVANT, vers le bas du cadre) ;
  - couleurs (le code élément : 🔥 rouge · 💧 bleu · 🌬️ blanc · ⛰️ brun) ;
  - tenues et matières (pas de motif inventé, pas de glyphe supposé).
- **Ne jamais écrire comme un fait ce que l'image ne montre pas**
  (leçon du reflet qui « échangeait les deux mondes », corrigée 2026-09-15 :
  chaque oiseau se reflète sous lui-même). L'interprétation se marque comme
  telle, ou se déroule (« on dirait que », « c'est comme si ») — ou saute.
  Idem pour les métaphores énoncées en fait physique (« les ailes poussent
  dans cette position » → « c'est dans la pause qu'on fabrique ses ailes »).
- Règle : **le texte suit la carte. Jamais l'inverse.** En cas d'écart,
  corriger le texte ; la carte ne se refait que si Martin décide.

## 2. Source symbolique

- Inventaire du kit (`_distillation/osho_tarot_KIT_PRODUCTION_majeurs.md` §5)
  et, en profondeur, l'EPUB `TAROT/OSHO/osho-zen-tarot_BOOK.epub` (« This
  Card » de la carte). L'EPUB donne les SYMBOLES et le SENS — jamais la prose.
- Tout symbole visible sur l'image doit être NOMMÉ dans la lecture
  (filet automatique : `tests/test_lectures.py`, `SYMBOLES_REQUIS`).

## 3. Ginette, à voix haute

- Lire chaque texte en entier, à voix haute, comme si on le disait à Ginette.
- Chasser : les phrases qu'il faut relire ; les images qui demandent un
  décodage (le « huit couché » s'explique, la « lanterne » absente de
  l'image ne se mentionne pas) ; les mots chics ; les références à une
  iconographie traditionnelle que la carte ne montre pas.
- **Chasser les formules compressées** (leçon de « produire est devenu le
  prix du repos », corrigée 2026-09-15) : un concept abstrait en sujet,
  une métaphore-prix, une histoire entière pliée en une formule. Test : si
  la phrase se dit plus simplement en la déroulant (« On t'a appris à… »),
  on la déroule.
- **Pas d'anatomie dans les textes adressés à la personne** (leçon de « ta
  lumière est dans la poitrine », corrigée 2026-09-15) : on parle de la
  personne entière (« en toi »). Les parties du corps restent dans les
  descriptions de l'image de la carte, où elles sont une précision visuelle.
- **Rattacher chaque complément au bon verbe** (leçon de « une lampe allumée
  à deux mains », corrigée 2026-09-15 : on lit « allumée avec les mains ») :
  le complément de moyen se place près du verbe qui le gouverne, ou on
  explicite ce verbe (« tenue à deux mains »). Vérifier de même les
  gérondifs (« en serrant les fils » — qui serre ?).
- **Un pronom en tête de phrase a son référent dans la phrase d'avant**
  (leçon de « Le savoir n'enlève rien. Ça rend les choix plus libres. »,
  corrigée 2026-09-15) : jamais un « Ça » ou un « Il » qui pointe deux
  phrases plus haut. Et pas de participe qui suppose un agent inexistant
  (« a été choisie » — personne n'a choisi, c'est reçu).
- Un mot qui sonne sombre ou fort pour rien → le mot plus chaud (« habitée »
  plutôt que « possédée »).

## 4. Passe mécanique (scriptée dans le filet)

- Doux espaces, mots répétés, espace avant ponctuation, points doubles.
- Coquilles connues : élisions cassées, mots collés. (Lancer
  `tests/test_lectures.py` — les vérifications mécaniques y vivent.)

## 5. Charte (filets automatiques existants)

- `tests/test_corpus.py` : registres interdits, doublons.
- `tests/test_style.py` : tirets cadratins, deux-points aphoristiques,
  ouvertures abstraites.
- `tests/test_lectures.py` : complétude symbolique + structure 3 temps.

## Livrable d'un lot

Invitations (monde + perso) + lecture, pour chaque carte, puis :
`pytest tests/test_lectures.py tests/test_corpus.py tests/test_style.py`.
Aucun lot ne part sans les cinq passes ci-dessus.
