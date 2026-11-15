# Brief de production — famille Feu (12 fiches restantes)

> **Pour les agents-rédacteurs.** Tu produis des fiches JSON du corpus tarot, prêtes pour la reformulation de Martin. Le produit est bilingue : concepts justes, langue simple, voix d'un ami lucide. Lis ce brief EN ENTIER, puis `data/corpus/CHARTE.md` (la charte complète), puis deux fiches voix de référence : `data/corpus/cartes/major_13.json` (Transformation) et `data/corpus/cartes/feu_08.json` (Voyage — même famille, déjà reformulée par Martin).

## Sorties

- Écris **un fichier JSON par carte** dans `data/corpus/cartes/`, nommé `<id>.json` (ex. `feu_as.json`).
- Le gabarit exact des clés : copie la structure de `data/corpus/cartes/feu_08.json` (champs dans le même ordre, clés SANS accent : `lecon`, jamais « leçon »).
- `source_referentielle` : cite tes angles (pollack/wen/greer + la source d'image du corpus).

## Les règles qui décident (résumé opérationnel — la charte fait foi)

**Voix.** Tutoiement. Un ami lucide qui te connaît bien — pas un oracle, pas un coach. Doux assumé. Ginette doit tout comprendre à la première lecture (âge de lecture ~13). Français standard québécois-compatible : pas de « du coup », « un truc », « bosser », « carrément ».

**Structure d'une phrase.** Une chute par entrée, pas par phrase. Le reste est plat, parlé, facile. Ouvrir par « Tu… » ou une image concrète — jamais par un concept abstrait (« Le passage… », « La profondeur… »), jamais par « Ce n'est pas… », jamais par le nom de la carte.

**Interdits durs.** « tu vas / vous allez / bientôt / destin / c'est écrit / il faut / tu dois / tu devras / prédire / le signe que ». Pas de métaphores économiques (« coûte », « payer », « le prix de »). Pas de « ton dedans », « ce qui se sent ». Pas d'« Éveil », pas de « Osho », pas de jargon du moteur (« en position de conseil », « la liaison feu-eau »). Gestes vagues interdits : « ouvre-toi », « lâche prise », « fais confiance à l'univers », « sois toi-même », « écoute ton cœur », « laisse-toi porter ».

**Remplacements qui marchent.** « tu vas » → « en ce moment, la situation penche vers ». « il faut » → « tu peux essayer ». « le signe que » → « un indice que ».

**Ombre.** Mode choisi parmi `amoindri / retourne / subi / differe` (définitions dans `tables.json → modes_ombre`). `texte` 50–85 mots OUVERT par « Tu… ». **`issue` OBLIGATOIRE** : toute ombre contient sa porte de sortie, en une phrase (la chaîne large).

**Longueurs.** `lumiere` et `ombre.texte` : 50–85 mots. Positions : 50–85 mots. `questions` : 2 à 4. `lecon` et `micro_geste` : une phrase.

**Banque de formes** (varier les ouvertures — jamais deux textes de la même forme d'affilée, ≤ 3 par famille) : Météo · Miroir · Offre · Question · Permission · Image · Geste déguisé. « Aujourd'hui » en ouverture ≤ 30 % de tes textes.

**Feu, la famille.** Élan, projet, désir, travail. Son problème : l'élan qui s'épuise ou se charge de trop. Sa voie : bouger pour la joie de bouger. Ton de famille : l'Offre et le Geste déguisé reviennent souvent au feu.

**Anti-tic entre agents.** Tes textes ne doivent partager AUCUNE suite de 8 mots avec les fiches déjà écrites (relis `feu_08.json` et `feu_reine.json` pour ne pas les imiter) et varier tes propres ouvertures. Inventorie tes 10 premières ouvertures dans ton rapport final.

## Les degrés (grille de lecture — `tables.json → degres`)

as = ouverture, don · 2 = mise en relation · 3 = premier fruit · 4 = cadre · 5 = secousse · 6 = circulation · 7 = évaluation · 8 = mouvement, maîtrise · 9 = bilan · 10 = achèvement ou saturation. Le nombre × la famille peut se renforcer OU se contredire — dit-le dans `note_grille` quand ça se contredit (ex. le 8 d'air : mouvement empêché).

## Les figures (jamais des personnes typées)

Une figure est **une manière d'être**, chez quelqu'un OU en toi (deux lectures simultanées, Greer). Page = exploration, message · Chevalier = élan vers un seul objectif · Reine = maîtrise intérieure, nourrir · Roi = maîtrise extérieure, cadre et responsabilité. Les figures n'ont ni âge, ni sexe, ni classe.

## Les douze cartes

Sources d'image : extraits du corpus OSHO de la famille (`ATRO_PLUS/_distillation/corpus_mineurs_feu.json` — lis ton entrée complète : `symboles` + `comprendre` décrivent NOTRE image). Angles concepts : Pollack (famille, nombres), Wen (degrés), Greer (rôles, questions).

### Groupe A — les ouvertures du feu

**`feu_as` · Source** (The Source) — degré as. Image : deux arbres moussus, une clairière, colonne de lumière sur une source, l'eau qui file vers les fougères. Concept : la qualité du feu à l'état pur, ce qui monte en toi avant d'avoir un nom. As = un don, une ouverture — la forme du banque : **Offre**.

**`feu_02` · Possibilités** (Possibilities) — degré 2. Image : pré de pissenlits, le vent arrache les graines en traînée dorée au-dessus des collines. Concept : les départs possibles, centaines de graines, nul ne sait où chacune retombe. 2 = mise en relation, polarité. Forme suggérée : **Image** ou **Offre**.

**`feu_03` · Expérience** (Experiencing) — degré 3. Image : petite fille, paume à plat contre le tronc immense, les yeux fermés, elle écoute dessous. Concept : l'expérience directe, éprouver plutôt que comprendre. 3 = premier fruit. Forme : **Miroir** ou **Question**.

**`feu_04` · Participation** (Participation) — degré 4. Image : nuit sur la rivière, lucioles par centaines montent vers les étoiles comme un fleuve, l'eau reflète. Concept : se joindre au mouvement, faire partie de la lumière plutôt que la regarder. 4 = cadre — ici le cadre est la rivière elle-même. Forme : **Offre** ou **Météo**.

### Groupe B — le cœur du feu

**`feu_05` · Totalité** (Totality) — degré 5. Image : prairie fleurie au soleil couchant, grand ballon à bandes rouges et crème, quatre personnes tiennent les cordes (un enfant, un vieil homme, une femme, un homme barbu), aucun ne fait semblant de tirer. Concept : le ballon ne monte que de tout ce monde à la fois — l'engagement total, personne en spectateur. 5 = secousse, test. Forme : **Image** ou **Geste déguisé**.

**`feu_06` · Succès** (Success) — degré 6. Image : le village fête ce soir, grand feu dans son brasier de pierre, mât couvert de guirlandes, tout le monde danse, étoiles filantes comme si le ciel participait. Concept : la circulation, la joie partagée qui rayonne au-delà du cercle. 6 = réparation, circulation. Forme : **Météo** ou **Image**.

**`feu_07` · Stress** (Stress) — degré 7. Image : un homme avance sur un fil au-dessus d'un précipice, bras à l'horizontale, une pile instable de vieux livres et de paniers posés sur la tête, une goutte de sueur. En dessous, un pont de bois solide traverse le ruisseau, **vide**. Concept : l'élan qui se charge de trop — le 7 = évaluation : ce qui vaut, ce qui pèse. Forme : **Miroir** (la friction s'observe).

**`feu_10` · Refoulement** (Suppression) — degré 10. Image : au milieu d'un champ de blé, une femme ouvre les bras, une spirale de feu part de son cœur et se déploie vers le ciel en rubans. Le blé l'entoure sans prendre feu. Concept : le feu comprimé longtemps qui finit par monter — l'achèvement d'un refoulement. 10 = saturation, fin de cycle. Forme : **Image** ou **Geste déguisé**.

### Groupe C — les manières d'être du feu

**`feu_09` · Épuisement** (Exhaustion) — degré 9. Image : dans une pièce aux murs de bois, un homme se penche, dos rond, sur la manivelle d'une énorme machine de rouages et de sabliers. Il est seul à alimenter tout ce mécanisme. La porte, grande ouverte, donne sur la mer et le sable. Concept : l'élan épuisé, le mécanisme alimenté seul, le temps qui passe à côté. 9 = bilan. Forme : **Miroir**.

**`feu_page` · Jeu** (Playfulness) — figure page. Image : sur la plage, une petite fille rit à pleine bouche, le château de sable s'effrite sous la vague, elle rajoute une tour, papillons au-dessus des dunes. Concept : le jeu qui ne compte pas, construire en sachant que la vague revient. Page = exploration, début. Forme : **Permission** ou **Geste déguisé**.

**`feu_chevalier` · Intensité** (Intensity) — figure chevalier. Image : la lande sombre, sur un bloc de pierre une lumière blanche brûle, un homme en lunettes de soudeur et gants épais, la tige reliée à une petite machine de cuivre avec son manomètre. Concept : l'intensité tenue en main, la flamme dirigée. Chevalier = élan vers un seul objectif. Forme : **Miroir** ou **Question**.

**`feu_roi` · Le Créateur** (The Creator) — figure roi. Image : la nuit tombée dans la clairière, un homme frotte deux branches croisées sans se presser, neuf personnes de tous âges assises en cercle autour du grand feu cerné de pierres posées à la main. Concept : le feu qui se crée pour le cercle — la maîtrise extérieure au service de tous. Roi = maîtrise extérieure, cadre. Forme : **Geste déguisé** ou **Permission**.

## Checklist avant de livrer (chaque fiche)

1. JSON valide (`python3 -m json.tool`), clés exactes du gabarit, **`lecon` sans accent**.
2. Aucun mot des listes noires (interdits durs + gestes vagues).
3. Longueurs : lumiere/ombre.texte/positions 50–85 mots ; issue 1–4 phrases courtes ; questions 2–4 ; leçon et micro_geste une phrase.
4. Ombre : mode cohérent + **issue** qui ouvre (jamais un mur).
5. Aucune suite de 8 mots partagée avec les fiches existantes (relis feu_08, feu_reine, major_13) ni entre TES propres fiches.
6. Ouvertures variées (inventorie-les), aucune ouverture par concept abstrait, aucun « Ce n'est pas… » en tête, ≤ 1 tiret par texte.
7. `positions` : les quatre clés `jour / amene / se_joue / essayer`, chacune 50–85 mots, chacune une phrase différente de la même carte aux autres positions.
8. `lumiere` ne répète pas `positions.jour` — ce sont deux éclairages différents de la même qualité.
