# Brief de re-tonage — section « Relations » (Ta Trame)

> **Statut** : brief d'exécution validé par Martin (2026-08-18). À exécuter **en Sonnet**, en chaîne.
> **Rôle du brief** : Opus a fixé la direction (doctrine + banque d'images + périmètre). Sonnet
> rédige chaque entrée en suivant ce document, sans réinventer la doctrine.
> Document de travail — supprimable une fois la chaîne terminée et validée.

---

## 0. Objectif

Retirer de la section Relations toute **négativité de ton** (le mot mécanique « frotte / friction »,
le registre « endurer / à passer », la hiérarchie où la tension menace l'appui) et la remplacer par
des **images plus riches et variées**. Fondé sur la CHARTE, règle 3 :
« une tension n'est pas un mauvais présage : c'est l'endroit où il y a du travail, donc l'endroit
intéressant ». Cohérent avec le reste de l'app, qui dit déjà `tension → « bouscule »`.

**Décisions cadrées :**
1. La clé JSON `"frictions"` (schéma des paires de `rel_nombres`) **reste inchangée** (interne, zéro
   migration). Seul le *label affiché* change.
2. **Variété** de vocabulaire exigée : pas de mot-tampon unique. On alterne bouscule / relief / vif /
   accordage / mouvement… (voir §2 la banque d'images).
3. **Périmètre** : réécriture-imagerie **complète des textes d'ÉTAT** (`rel_elements`, `rel_chinois`,
   `rel_aspects_cadre`, `rel_pouls`, `rel_synthese`, + pied de `rel_composite`, + `rel_types`).
   **`rel_nombres` est gardé factuel pour l'instant** — on n'y touche PAS aux valeurs, seulement au
   label d'affichage (dans `index.html`).

**Garde-fous :**
- Ne PAS régresser ce qui est déjà bon. Les textes `resonance` (air-feu, eau-terre, harmonie, trine…)
  sont déjà positifs : on les **harmonise** (purge d'un éventuel mot négatif, cohérence d'images),
  on ne les réécrit pas de fond en comble.
- Garder le **sens** de chaque entrée (ce que l'axe dit reste vrai — on change l'habillage, pas le fond).
- Respecter les **longueurs** de la CHARTE : nuance/état ≈ 20-40 mots ; amorce ≈ 15-30 mots.
- Registre **constatif** (« ce lien a… », « le ciel vient… »), jamais prédictif ni moral.

---

## 1. La doctrine (l'image de fond)

La tension d'un lien n'est ni un grincement ni une épreuve : c'est **du relief**. Trois gestes :

- **① Le relief plutôt que le frottement.** Un lien lisse n'accroche à rien. Là où « ça bouscule »,
  c'est là où le lien a du grain, de la dimension, de quoi rester éveillé.
- **② L'accordage plutôt que l'endurance.** On ne « traverse » pas une tension : on **accorde** deux
  tempos, deux langues, deux façons. Travail d'artisan, pas corvée subie.
- **③ Le mouvement plutôt que l'usure** (pour le pouls du jour). Le ciel ne « tire pas dessus » : il
  **passe la main sur cet endroit du lien et le réveille**. Une journée qui met du mouvement, qui
  repart demain autrement. **Jamais** « un jour à passer ».

But : les deux pôles cessent de s'opposer (appui *vs* friction). Ils deviennent **deux qualités de
vie du lien** — ce qui porte, et ce qui fait bouger.

---

## 2. La banque d'images (à faire TOURNER — variété obligatoire)

Chaque famille = une manière différente de dire « ça bouge / ça a du relief ». **Règle de
répartition : dans un même fichier, ne pas réutiliser deux fois la même famille.** Cocher au fur
et à mesure.

| Famille | Images / mots-clés | Bon pour |
|---|---|---|
| **Relief / grain** | du relief, du grain, de la dimension, un point vif, ce qui donne prise, l'endroit vivant | synthèse, aspects |
| **Accordage / musique** | accorder deux cordes, trouver l'intervalle, deux voix qui cherchent l'accord, un léger réglage | éléments (air-eau), aspects |
| **Deux tempos / allures** | deux vitesses au même but, l'un lance / l'autre assoit, deux rythmes à marier | éléments (air-terre, feu-terre) |
| **Deux langues / traduction** | deux langues à traduire, apprendre le parler de l'autre | éléments (air-eau) |
| **Température / cuisson** | une intensité à doser, la chaleur qui réchauffe (jamais « faire bouillir / éteindre ») | éléments (eau-feu) |
| **Mouvement / réveil** | vient remuer, réveiller, passer la main dessus, mettre en mouvement | pouls (carré/opp) |
| **Roue / relief du parcours** | les deux bouts de la roue, ce qui empêche de s'endormir | chinois (choc) |
| **Pli / note qui revient** | un pli à défroisser, une note qui revient et qu'on apprivoise | chinois (nuisance) |
| **Contenir / donner forme** | une main qui contient sans serrer, la berge qui guide le courant | chinois (contrôle) |

---

## 3. Mots BANNIS (grep de contrôle en fin de chaîne)

`frotte`, `friction(s)` *(en texte affiché — la clé JSON reste)*, `tire dessus`, `à traverser`,
`à passer`, `rien qu'un … à passer`, `demande le plus de soin`, `efface`, `épuisant`, `se noyer`,
`lourd` *(au sens pénible)*, `malentendu constant`, `prise de pouvoir`, `déborder`, `éteindre` /
`s'éteint` *(au sens négatif)*, `agace`.

Contrôle final attendu :
```
grep -rnoiE "frotte|friction|tire dessus|à traverser|à passer|demande le plus de soin|efface|épuisant|se noyer|prise de pouvoir|éteind|s'éteint|agace" \
  data/corpus/rel_elements.json data/corpus/rel_chinois.json data/corpus/rel_aspects_cadre.json \
  data/corpus/rel_pouls.json data/corpus/rel_synthese.json data/corpus/rel_composite.json data/corpus/rel_types.json
# -> aucune occurrence (hors clé JSON "frictions" de rel_nombres, non concernée)
```

---

## 4. Exemples-étalon (le niveau visé — calibrage)

**`rel_synthese.mixte`**
> ✅ « Ce lien a du relief : de vrais appuis, et de vrais endroits qui vous font bouger. Les deux
> coexistent — et c'est cette double présence qui l'empêche de s'endormir. »

**`rel_pouls.classe.carre-opposition`**
> ✅ « Le ciel du jour passe la main sur cet endroit de votre lien et le réveille : une journée qui
> demande un léger accordage à deux — et demain, il sera ailleurs. »

**Composition Vénus/Mars** — corriger le **gabarit** (`app.py::_texte_pouls`) : retirer la parenthèse
technique redondante `(… de votre lien)` et alléger les nuances de point (voir §5.D). Cible :
> ✅ « Aujourd'hui, Vénus vient réveiller le désir et l'allant de votre lien. »

---

## 5. Worklist fichier par fichier

Pour chaque entrée : garder le SENS, appliquer une image de la §2 (variée), longueur cible, purge des
mots §3.

### A. `data/corpus/rel_elements.json` — 4 états `tension` à réimager + purge dans les `neutre`
- **air-eau** *(tension)* — actuel finit sur « pas tout à fait la même langue… traduire ». Famille :
  **deux langues / traduction**. Garder l'idée « l'un dit, l'autre ressent » ; enlever le côté
  « impression de ne pas se parler ».
- **air-terre** *(tension)* — « idées vs concret, rythme différent ». Famille : **deux tempos**
  (l'un dans les mots, l'autre dans le posé) — « même endroit, deux chemins ».
- **eau-feu** *(tension)* — actuel : « faire bouillir / malentendu constant ». Famille :
  **température / cuisson**, versant positif : une intensité à doser, la chaleur qui réchauffe.
  **Bannir** « bouillir / éteindre / malentendu constant ».
- **feu-terre** *(tension)* — « deux vitesses à accorder ». Famille : **deux allures** (l'un lance,
  l'autre assoit) — NE PAS reprendre l'image tempo d'air-terre (varier : ici « fondation / élan »).
- **eau-eau** *(neutre)* — purge « lourd / se noyer » → garder l'intimité, dire le manque de point
  d'appui sans noyade (« sans un peu de terre ferme pour poser tout ça »).
- **feu-feu** *(neutre)* — purge « épuisant » → « deux élans en même temps, qui gagnent à ce que l'un
  ralentisse parfois pour l'autre ».
- air-feu / eau-terre *(resonance)*, terre-terre / air-air *(neutre)* : **harmoniser seulement**
  (déjà bons).

### B. `data/corpus/rel_chinois.json`
- **branches.choc** *(tension)* — déjà « bouscule » : garder l'esprit, enrichir. Famille : **roue**
  (les deux bouts de la roue, ce qui empêche de s'endormir). Enlever « demande le plus de travail »
  s'il pèse.
- **branches.nuisance** *(tension)* — actuel : « accroc / frottement léger / agace ». Famille :
  **pli / note qui revient**. Bannir « frottement / agace ».
- **elements.controle** — actuel : « garde de déborder / prise de pouvoir ». Famille : **contenir /
  donner forme** (la berge qui guide le courant). Bannir « déborder / prise de pouvoir ».
- **elements.meme** — purge « redondant » → dire le partage + la nuance qui manque, sans le mot.
- harmonie / trine / genere *(resonance)*, identique / neutre : harmoniser seulement.

### C. `data/corpus/rel_aspects_cadre.json`
- **carre-opposition.amorce** — actuel : « se tirent dans des sens différents… ajustement conscient ».
  Famille : **relief / grain** ou **accordage**. Reframe : deux directions qui, tenues ensemble,
  donnent de l'amplitude au lien ; ce point s'invente plutôt qu'il ne va de soi.
- conjonction / sextile-trigone : harmoniser seulement (déjà positifs).

### D. `data/corpus/rel_pouls.json`
- **classe.carre-opposition** — voir étalon §4. Famille : **mouvement / réveil**. Bannir « tire
  dessus / tension à traverser / rien qu'un jour à passer ».
- **classe.conjonction / sextile-trigone** — harmoniser (déjà bons : « l'allume », « tend la main »).
- **point.\*** (12 nuances) — **retirer le suffixe redondant « … de votre lien »** de chaque nuance
  (le gabarit corrigé le rajoutera proprement une seule fois — voir §6.B). Ex. mars : « le désir et
  l'allant » ; venus : « la tendresse entre vous » (déjà sans suffixe → OK). Garder court (≤ 8 mots),
  imagé, positif.
- **cadre / pied** — vérifier le ton, léger lissage si besoin.

### E. `data/corpus/rel_synthese.json`
- **dominante.tension_forte** — actuel : « demande le plus de soin / point de friction ». Reframe :
  « ce qui revient le plus, sur plusieurs axes à la fois : l'endroit le plus vivant du lien, celui
  qui vous demande le plus d'invention. » Famille : **relief**.
- **dominante.mixte** — voir étalon §4.
- **dominante.resonance_forte / neutre** — harmoniser (déjà bons).
- **pied.\*** — vérifier ; RAS a priori.

### F. `data/corpus/rel_composite.json`
- **pied** — « s'éteint doucement, souvent sans qu'on sache pourquoi » : garder l'idée « nourri il
  donne de l'élan / laissé de côté il s'assoupit », **sans** « s'éteint ». (Le bloc `diagnostic`
  ajouté récemment est déjà au bon ton — ne pas y toucher.)

### G. `data/corpus/rel_types.json`
- **travail.conseil** — « bien des frictions » → « bien des accrochages qu'on n'a jamais dits » ou
  reformuler sans « friction ».
- **famille.cadrage** — « les affinités et les frictions » → « ce qui rapproche et ce qui accroche ».
- **famille.conseil** — « Ce qui frotte en famille… » → « Ce qui accroche en famille vient rarement
  du jour même… ». Bannir « frotte ».
- **amour.cadrage** — « pèse le plus lourd » : ici « lourd » = « compte le plus » (pas péjoratif) —
  reformuler léger si possible (« ce qui se joue entre vos deux ciels compte le plus »).

---

## 6. Changements hors corpus

### A. `templates/index.html` — labels & badge
- l.2370 : `« Ça frotte : »` → **`« Ça bouscule : »`** (label stable de la paire de nombres).
- l.2378 : résumé éléments `« X appuis, Y frictions »` → **`« X appuis, Y reliefs »`**.
- l.2341 : le badge affiche le mot brut `T(etat)` (→ « TENSION » en majuscules). Remplacer par un
  libellé Relations stable : **resonance → « appui », tension → « bouscule », neutre → « neutre »**
  (petite table locale, ou réutiliser `nomEtat()` si son `court` convient). *(Le badge est de la
  chrome répétée : un mot STABLE par état — la variété d'images vit dans la prose du corpus, pas ici.)*

### B. `app.py` — `_texte_pouls` (composition du pouls)
- Retirer la parenthèse technique redondante « (`{point_nom}` de votre lien) » de la phrase composée,
  pour ne plus doubler « … de votre lien ». Vérifier la phrase finale : « Aujourd'hui, {planète} vient
  réveiller {nuance de point}. » Adapter le gabarit dans `_texte_pouls` **et** son rendu dans
  `index.html` (bloc pouls) en conséquence.

---

## 7. Validation en fin de chaîne
1. `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('data/corpus/rel_*.json')]"` → JSON valide.
2. Le grep de contrôle §3 ne renvoie rien.
3. `python -m pytest -q` → suite verte (les tests verrouillent la structure/couverture, pas le texte —
   mais on vérifie qu'aucune clé n'a sauté).
4. Relecture rapide à l'écran (tiroir « Le vous », « Vos éléments », « Vos nombres », pouls du jour).
