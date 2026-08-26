# Plan d'action — passe « langage clair » sur tout le corpus (Ta Trame)

> Objectif : rendre TOUS les textes de l'app compréhensibles du plus grand nombre, à la première
> lecture. Doctrine figée dans `data/corpus/CHARTE.md` §« Comprendre à la première lecture » —
> on ne la ré-ouvre plus. ~244 000 mots de prose sur 35 fichiers → chantier de plusieurs sessions.

## Principe directeur
- **Une passe consolidée par section**, jamais des retouches itératives (évite la stratification
  quand les consignes changent — le piège déjà vécu).
- **Partir du fond** (ou du calcul, pour les axes composés), pas empiler sur le texte existant.
- Registre : clair 1re lecture · concret (dire QUOI) · phrases courtes · une image limpide max ·
  verbes actifs · **québécois d'abord** (pas de tic hexagonal, pas de joual) · gender-safe (le
  genre reste optionnel ; on ne s'appuie dessus que si les deux sont connus ET différents).

## Diagnostic chiffré (2026-08-20)
- Le style « aphorisme » est **déjà réglé** (tirets/deux-points bas partout).
- Reste-à-faire = **phrases longues + vocabulaire littéraire + métaphores à décoder**.
- Pires fichiers en phrases longues : **`noeuds.json` (42 % de phrases > 22 mots)**, **`periodes.json` (40 %)**.

## Vague 0 — Outillage (Opus, EN PREMIER)
1. Ajouter à `tests/test_style.py` une cible de **longueur de phrase** (ex. « < ~12 % de phrases
   > 22 mots » sur les fichiers déjà passés au style) → clarté mesurable et non-régressante.
2. Écrire **3 étalons avant/après** (un par type : Jour, portrait narratif, cycle) pour calibrer Sonnet.

## Vagues de réécriture (ordre = visibilité utilisateur)
| Vague | Contenu | Mots | Note |
|---|---|---|---|
| **1 — Le Jour** | `fil.json` + `transits.json` | ~37 k | Vu chaque jour → priorité n°1 |
| **2 — Portrait socle** | `nombres_detail.json` | ~46 k | Le plus gros et central |
| **3 — Portrait ciel** | `ciel_signe_1/2/3` + `ciel_maison_1/2/3` | ~92 k | Sous-découpé : 1 fichier = 1 sous-vague |
| **4 — Le Ciel + aspects** | `ciel_global`, `ciel`, `aspects_1..4` | ~16 k | |
| **5 — Cycles** | `noeuds` (prioritaire), `periodes`, `mois/annees/ages_detail`, `arcanes`, `nombres`, `chinois_*`, `univers/heritages_detail` | ~40 k | `noeuds`+`periodes` d'abord |
| **6 — Relations restant** | `rel_nombres`, `rel_chinois`, `rel_synthese`, `rel_pouls`, `rel_types`, `rel_composite` | ~2 k | Petits, déjà tonés |

Déjà conformes, NE PAS retoucher : `rel_elements_v2.json`, `rel_composite_signe.json`.

## La boucle par vague
1. **Opus** : 3-5 pilotes clarté + brief de chaîne (étalons + règles CHARTE).
2. **Martin** valide les pilotes.
3. **Sonnet** : réécriture en chaîne du reste de la vague (bascule `/model` manuelle).
4. **Opus** : validation (grep tics, `test_style.py`, `pytest`, relecture échantillon).
5. **Martin** : vérif à l'écran (relance Vibe) AVANT la vague suivante.

## Cadence
Une vague ≈ 1-2 sessions. Jamais la suivante sans avoir validé la précédente à l'écran.

## Étalons avant/après (calibrage — un par type de texte)

**JOUR** (`fil.json`, phrase longue + « verdict » abstrait)
- ❌ « Aujourd'hui, une situation ordinaire se transforme vite en verdict sur qui tu es, un mot de
  travers pris comme une preuve plutôt que comme un moment. »
- ✅ « Aujourd'hui, un petit rien prend trop de poids. Un mot de travers, et tu le lis comme une
  preuve de ce que tu vaux. C'était juste un moment, pas un jugement sur toi. »

**PORTRAIT narratif** (`nombres_detail`, déjà assez clair → touche LÉGÈRE : métaphore + « Ce n'est pas »)
- ❌ « …quelle échéance est un mensonge poli. Ce qui pousse là-dedans n'est pas la peur, même si ça
  se confond souvent avec elle. C'est un rapport au temps. Le temps est ton matériau. »
- ✅ « …quelle date ne sera pas respectée. Ça ressemble à de la peur, sans en être. C'est ta façon
  de voir le temps : pour toi, il compte pour de vrai. »
  *(Note : ne pas tout réécrire quand c'est déjà clair — corriger le point précis.)*

**CYCLE** (`noeuds`, phrases longues + jargon « cuspide » + mots rares)
- ❌ « Sur cette cuspide, tu portes encore les deux réflexes en même temps… Ces deux talents ont
  chacun leur utilité, l'un a apaisé des tensions que l'autre aurait envenimées, l'autre a débloqué
  des situations où la seule sensibilité serait restée hésitante. »
- ✅ « Tu portes deux réflexes à la fois, et ils ne vont pas toujours ensemble. D'un côté, tu sais
  te fondre dans une situation, sentir ce qui n'est pas dit. De l'autre, une envie de trancher vite
  te pousse à avancer seul. Les deux te servent : ta sensibilité calme des tensions, ta franchise
  débloque ce qui coince. »

## État d'avancement
- [x] Vague 0 — outillage : cible longueur de phrase dans `test_style.py` (cliquet `PASSES_AU_CLAIR`) + 3 étalons ci-dessus
- [x] Vague 1 — Le Jour (`fil.json` : 63 entrées retouchées + 4 pilotes ; `transits.json` : 65 entrées ; `PASSES_AU_CLAIR` étendu, 600 passed)
- [x] Vague 2 — nombres_detail (touche légère ciblée sur les 64 champs à 3+ phrases fusionnées ; 9,0 % de phrases longues, sous la cible 12 % ; listes rythmées préservées ; 601 passed)
- [x] Vague 3 — ciel_signe / ciel_maison (déjà conforme : 2,6-6,5 % de phrases longues sur les 6 fichiers ; 4 tics « du coup » corrigés ; aucune réécriture de fond nécessaire ; 607 passed)
- [x] Vague 4 — Le Ciel + aspects (ciel_global/ciel déjà conformes, 2 tics « du coup » corrigés ; aspects_1-4 : 61 coupures au deux-points + 14 coupures ciblées « et apprendre... », 6,8-10,1 % de phrases longues ; 613 passed)
- [x] Vague 5 — cycles : periodes (104 coupures, 0 %), ages_detail (5,4 %), chinois_natal (0 %), noeuds (204 phrases longues → 0 %, jargon « cuspide » éliminé ×11) + 7 fichiers déjà conformes (mois_detail, annees_detail, arcanes, nombres, chinois_detail, univers_detail, heritages_detail). Tous les 11 fichiers au cliquet ; 624 passed.
- [x] Vague 6 — Relations restant (rel_nombres/rel_chinois/rel_pouls/rel_composite déjà conformes ; rel_synthese et rel_types : 7 phrases coupées, 0 %. Aucun vrai tic — "frictions" était un nom de champ structurel, "du coup" un faux positif dans "du couple". 626 passed, 6 skipped)

## Plan « langage clair » — TERMINÉ (2026-08-20)
Les 6 vagues sont cochées. Tout le corpus utilisateur (~244 000 mots, 35 fichiers) respecte
désormais le registre langage clair : phrases courtes, concret, verbes actifs, une image max,
québécois d'abord, gender-safe. Le cliquet `PASSES_AU_CLAIR` dans `tests/test_style.py` protège
ce travail contre toute régression future.
