# Brief de production — famille Eau (13 fiches restantes)

> **Pour les agents-rédacteurs.** Tu produis des fiches JSON du corpus tarot, prêtes pour la reformulation de Martin. Le produit est bilingue : concepts justes, langue simple, voix d'un ami lucide. Lis ce brief EN ENTIER, puis `data/corpus/CHARTE.md` (la charte complète), puis deux fiches voix de référence : `data/corpus/cartes/eau_08.json` (Lâcher-prise — même famille, reformulée par Martin) et `data/corpus/cartes/major_13.json` (Transformation).

## Sorties

- Écris **un fichier JSON par carte** dans `data/corpus/cartes/`, nommé `<id>.json` (ex. `eau_as.json`).
- Le gabarit exact des clés : copie la structure de `data/corpus/cartes/eau_08.json` (champs dans le même ordre, clés SANS accent : `lecon`, jamais « leçon »).
- `source_referentielle` : cite tes angles (pollack/wen/greer + la source d'image du corpus).

## Les règles qui décident (résumé opérationnel — la charte fait foi)

**Voix.** Tutoiement. Un ami lucide qui te connaît bien — pas un oracle, pas un coach. Doux assumé. Ginette doit tout comprendre à la première lecture (âge de lecture ~13). Français standard québécois-compatible : pas de « du coup », « un truc », « bosser », « carrément ».

**Structure d'une phrase.** Une chute par entrée, pas par phrase. Le reste est plat, parlé, facile. Ouvrir par « Tu… » ou une image concrète — jamais par un concept abstrait (« Le lien… », « La culpabilité… »), jamais par « Ce n'est pas… », jamais par le nom de la carte.

**Interdits durs.** « tu vas / vous allez / bientôt / destin / c'est écrit / il faut / tu dois / tu devras / prédire / le signe que ». Pas de métaphores économiques (« coûte », « payer », « le prix de »). Pas de « ton dedans », « ce qui se sent ». Pas d'« Éveil », pas de « Osho », pas de jargon du moteur (« en position de conseil », « la liaison feu-eau »). Gestes vagues interdits : « ouvre-toi », « lâche prise », « fais confiance à l'univers », « sois toi-même », « écoute ton cœur », « laisse-toi porter ».

**Remplacements qui marchent.** « tu vas » → « en ce moment, la situation penche vers ». « il faut » → « tu peux essayer ». « le signe que » → « un indice que ».

**Ombre.** Mode choisi parmi `amoindri / retourne / subi / differe` (définitions dans `tables.json → modes_ombre`). `texte` 50–85 mots OUVERT par « Tu… ». **`issue` OBLIGATOIRE** : toute ombre contient sa porte de sortie, en une phrase (la chaîne large).

**Longueurs.** `lumiere` et `ombre.texte` : 50–90 mots. Positions : 50–95 mots. `questions` : 2 à 4. `lecon` et `micro_geste` : une phrase.

**Banque de formes** (varier les ouvertures — jamais deux textes de la même forme d'affilée, ≤ 3 par famille) : Météo · Miroir · Offre · Question · Permission · Image · Geste déguisé. « Aujourd'hui » en ouverture ≤ 30 % de tes textes.

**Eau, la famille.** Lien, émotion, intériorité, imaginaire. Son problème : la passivité et le rêve vide. Sa voie : accueillir et aimer. Ton de famille : l'Eau donne des permissions et des images d'eau ; la parole coule, l'écoute d'abord.

**Anti-tic entre agents.** Tes textes ne doivent partager AUCUNE suite de 8 mots avec les fiches déjà écrites (relis `eau_08.json` et `major_17.json` pour ne pas les imiter) et varier tes propres ouvertures. Inventorie tes 10 premières ouvertures dans ton rapport final.

## Les degrés (grille de lecture — `tables.json → degres`)

as = ouverture, don · 2 = mise en relation · 3 = premier fruit · 4 = cadre · 5 = secousse · 6 = circulation · 7 = évaluation · 8 = mouvement, maîtrise · 9 = bilan · 10 = achèvement ou saturation. Le nombre × la famille peut se renforcer OU se contredire — dit-le dans `note_grille` quand ça se contredit.

## Les figures (jamais des personnes typées)

Une figure est **une manière d'être**, chez quelqu'un OU en toi (deux lectures simultanées, Greer). Page = exploration, message · Chevalier = élan vers un seul objectif · Reine = maîtrise intérieure, nourrir · Roi = maîtrise extérieure, cadre et responsabilité. Les figures n'ont ni âge, ni sexe, ni classe.

## Les treize cartes

Sources d'image : extraits du corpus OSHO de la famille (`ATRO_PLUS/_distillation/corpus_mineurs_eau.json` — lis ton entrée complète : `symboles` + `comprendre` décrivent NOTRE image). Angles concepts : Pollack (famille, nombres), Wen (degrés), Greer (rôles, questions).

### Groupe A — les sources et les premières eaux

**`eau_as` · Suivre le mouvement** (The Source) — degré as. Image : feuille dorée au centre d'une eau calme, cercles réguliers, iris ouverts, roseaux, saule. Concept : ce qui monte en toi avant d'avoir un nom — suivre le mouvement naturel. As = un don, une ouverture. Forme : **Offre**.

**`eau_02` · Amitié** (Friendliness) — degré 2. Image : deux adolescents sur un chemin d'herbe, l'un raconte avec de grands gestes, l'autre éclate de rire ; deux arbres en fleurs, arche de branches. Concept : l'amitié sans effort, la relation qui n'exige rien. 2 = mise en relation. Forme : **Permission** ou **Image**.

**`eau_03` · Célébration** (Celebration) — degré 3. Image : trois générations de femmes rient sous la pluie dans une vigne d'automne, paniers de vendange débordants. Concept : la joie partagée entre générations, célébrer sous la pluie. 3 = premier fruit. Forme : **Météo** ou **Image**.

**`eau_04` · Recueillement** (Turning In) — degré 4. Image : forêt immense au soir, arche de pierre entre deux troncs, femme assise au bord d'un cours d'eau très calme. Concept : se tourner vers l'intérieur, la grotte sèche au bord de l'eau. 4 = cadre — ici le cadre est intérieur. Forme : **Permission** ou **Météo**.

### Groupe B — les nuances de l'eau

**`eau_05` · Attachement** (Clinging to the Past) — degré 5. Image : homme au bord de la mer, pieds nus, tunique de lin, il avance sans se retourner, ses pas en une seule ligne sur le sable mouillé. Concept : le passé qui suit, les pas qui restent — avancer sans se retourner. 5 = secousse, test. Forme : **Image** ou **Miroir**.

**`eau_06` · Illusion** (The Dream) — degré 6. Image : homme dans le sable mouillé soulève une toile immense ; sur la toile, tout un été peint. Concept : le rêve qu'on soulève, la frontière entre l'imaginaire et le réel. 6 = circulation — ici, entre les deux mondes. Forme : **Image** ou **Question**.

**`eau_07` · Projections** (Projections) — degré 7. Image : scène de théâtre la nuit, deux toiles peintes — derrière l'homme une fête peinte, derrière la femme un jardin sauvage — cordes et poulies visibles. Concept : ce qu'on projette sur l'autre, la fête imaginaire contre le jardin réel. 7 = évaluation, discernement. Forme : **Miroir** ou **Question**.

**`eau_09` · Paresse** (Laziness) — degré 9. Image : midi sur une rivière immobile, homme adossé au tronc d'un grand arbre ancien, racines dans l'eau, chapeau de paille. Concept : le repos profond qui n'est pas de la paresse, l'arbre qui porte. 9 = bilan. Forme : **Permission** ou **Image**.

### Groupe C — l'harmonie et les manières d'être

**`eau_10` · Harmonie** (Harmony) — degré 10. Image : petite chutes d'eau en forêt, chaque chute sa cuvette de pierre mousseuse, toutes les eaux réunies dans une nappe tranquille. Concept : chaque eau trouve son niveau, l'harmonie qui n'exige pas l'uniformité. 10 = achèvement, plénitude. Forme : **Météo** ou **Image**.

**`eau_page` · Compréhension** (Understanding) — figure page. Image : rivière claire à l'aube, pierres plates du fond visibles, herbe fine qui bouge, rive verte et proche. Concept : voir clair dans l'eau peu profonde — la compréhension qui vient en regardant le fond. Page = exploration, message. Forme : **Offre** ou **Question**.

**`eau_chevalier` · Confiance** (Trust) — figure chevalier. Image : homme en plein saut très haut dans un ciel sans fin, ni sol ni mer, nuages blancs en bas, corps lancé penché en avant. Concept : le saut dans le vide tenu par la confiance seule. Chevalier = élan vers un seul objectif. Forme : **Question** ou **Geste déguisé**.

**`eau_reine` · Réceptivité** (Receptivity) — figure reine. Image : grand lac limpide en plein jour, femme debout l'eau à la taille, le fond visible, aucune trace de reflet sur la surface. Concept : recevoir sans faire miroir — être là, transparente. Reine = maîtrise intérieure, nourrir. Forme : **Permission**.

**`eau_roi` · Guérison** (Healing) — figure roi. Image : lac immense vu de très haut, fond visible, bandes d'or du soleil, homme flottant sur le dos au milieu, visage vers le ciel. Concept : l'eau qui porte sans effort — la guérison par la confiance. Roi = maîtrise extérieure. Forme : **Permission** ou **Geste déguisé**.

## Checklist avant de livrer (chaque fiche)

1. JSON valide (`python3 -m json.tool`), clés exactes du gabarit, **`lecon` sans accent**.
2. Aucun mot des listes noires (interdits durs + gestes vagues).
3. Longueurs : lumiere/ombre.texte/positions 50–90 mots ; issue 1–4 phrases courtes ; questions 2–4 ; leçon et micro_geste une phrase.
4. Ombre : mode cohérent + **issue** qui ouvre (jamais un mur).
5. Aucune suite de 8 mots partagée avec les fiches existantes (relis eau_08, major_17, feu_08, feu_reine) ni entre TES propres fiches.
6. Ouvertures variées (inventorie-les), aucune ouverture par concept abstrait, aucun « Ce n'est pas… » en tête, ≤ 1 tiret par texte.
7. `positions` : les quatre clés `jour / amene / se_joue / essayer`, chacune 50–90 mots, chacune une phrase différente de la même carte aux autres positions.
8. `lumiere` ne répète pas `positions.jour` — ce sont deux éclairages différents de la même qualité.
