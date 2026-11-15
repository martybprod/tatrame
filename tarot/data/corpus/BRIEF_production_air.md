# Brief de production — famille Air (12 fiches restantes)

> **Pour les agents-rédacteurs.** Tu produis des fiches JSON du corpus tarot, prêtes pour la reformulation de Martin. Le produit est bilingue : concepts justes, langue simple, voix d'un ami lucide. Lis ce brief EN ENTIER, puis `data/corpus/CHARTE.md` (la charte complète), puis deux fiches voix de référence : `data/corpus/cartes/air_08.json` (Culpabilité — même famille, reformulée par Martin) et `data/corpus/cartes/air_roi.json` (Contrôle — même famille, une figure, voix de Martin).

## Sorties

- Écris **un fichier JSON par carte** dans `data/corpus/cartes/`, nommé `<id>.json` (ex. `air_as.json`).
- Le gabarit exact des clés : copie la structure de `data/corpus/cartes/air_08.json` (champs dans le même ordre, clés SANS accent : `lecon`, jamais « leçon »).
- `source_referentielle` : cite tes angles (pollack/wen/greer + la source d'image du corpus) dans le champ **`production`** uniquement.

## RÈGLE ABSOLUE — le champ `reprise`

**N'écris JAMAIS dans `source_referentielle.reprise`.** Ce champ est réservé à la note d'intégration posée par l'orchestrateur quand Martin a reformulé. Laisser la clé **absente** de ton JSON. Une fiche livrée avec un `reprise` = fausse attribution de la voix de Martin = rejet.

## Les règles qui décident (résumé opérationnel — la charte fait foi)

**Voix.** Tutoiement. Un ami lucide qui te connaît bien — pas un oracle, pas un coach. Doux assumé. Ginette doit tout comprendre à la première lecture (âge de lecture ~13). Français standard québécois-compatible : pas de « du coup », « un truc », « bosser », « carrément ».

**Structure d'une phrase.** Une chute par entrée, pas par phrase. Le reste est plat, parlé, facile. Ouvrir par « Tu… » ou une image concrète — jamais par un concept abstrait (« Le mental… », « L'isolement… »), jamais par « Ce n'est pas… », jamais par le nom de la carte.

**Interdits durs.** « tu vas / vous allez / bientôt / destin / c'est écrit / il faut / tu dois / tu devras / prédire / le signe que ». Exception documentée : les « tu dois » / « il faut » dans des croyances rapportées (« Tu crois que tu dois… », « tu as l'impression qu'il faut… ») sont permis — le conditionnement nommé, pas la prescription. Pas de métaphores économiques (« coûte », « payer », « le prix de »). Pas de « ton dedans », « ce qui se sent ». Pas d'« Éveil », pas de « Osho », pas de jargon du moteur (« en position de conseil », « la liaison feu-eau »). Gestes vagues interdits : « ouvre-toi », « lâche prise », « fais confiance à l'univers », « sois toi-même », « écoute ton cœur », « laisse-toi porter ».

**Remplacements qui marchent.** « tu vas » → « en ce moment, la situation penche vers ». « il faut » → « tu peux essayer ». « le signe que » → « un indice que ».

**Ombre.** Mode choisi parmi `amoindri / retourne / subi / differe` (définitions dans `tables.json → modes_ombre`). `texte` 50–85 mots OUVERT par « Tu… ». **`issue` OBLIGATOIRE** : toute ombre contient sa porte de sortie, en une phrase (la chaîne large).

**Longueurs.** `lumiere` et `ombre.texte` : 50–90 mots. Positions : 50–95 mots. `questions` : 2 à 4. `lecon` et `micro_geste` : une phrase.

**Banque de formes** (varier les ouvertures — jamais deux textes de la même forme d'affilée, ≤ 3 par famille) : Météo · Miroir · Offre · Question · Permission · Image · Geste déguisé. « Aujourd'hui » en ouverture ≤ 30 % de tes textes. L'Air est la famille qui pose des questions — mais garde le plafond : pas plus de 3 ouvertures-questions par lot.

**Air, la famille.** Le mental, la clarté, la communication, le souffle, le conflit. Son problème : la dispersion et les paroles vides, le mental qui tourne en rond. Sa voie : voir clair et dire vrai. Ton de famille : l'Air pose des questions, coupe net, nomme les choses ; la parole y est un outil, pas un décor.

**Anti-tic — les formules déjà usées ailleurs (interdites dans ton lot)** : « ce qui se joue, c'est ta capacité à… » (Eau, 3×) · « Tu arrives avec le réflexe de… » (Feu) · « la carte te rappelle que tu possèdes déjà cette capacité » (Feu/Eau) · « tu n'as pas besoin d'attendre d'être… » (Feu/Eau) · « On t'a appris à… » (Feu) · « Tu as pris l'habitude de… » (Feu). Tes textes ne doivent partager AUCUNE suite de 8 mots avec les 35 fiches déjà écrites ni entre tes propres fiches. Inventorie tes 12 premières ouvertures dans ton rapport final.

## Les degrés (grille de lecture — `tables.json → degres`)

as = ouverture, don · 2 = mise en relation · 3 = premier fruit · 4 = cadre · 5 = secousse · 6 = circulation · 7 = évaluation · 8 = mouvement, maîtrise · 9 = bilan · 10 = achèvement ou saturation. Le nombre × la famille peut se renforcer OU se contredire — dit-le dans `note_grille` quand ça se contredit.

## Les figures (jamais des personnes typées)

Une figure est **une manière d'être**, chez quelqu'un OU en toi (deux lectures simultanées, Greer). Page = exploration, message · Chevalier = élan vers un seul objectif · Reine = maîtrise intérieure, nourrir · Roi = maîtrise extérieure, cadre et responsabilité. Les figures n'ont ni âge, ni sexe, ni classe.

## Les douze cartes

Sources d'image : extraits du corpus OSHO de la famille (`ATRO_PLUS/_distillation/corpus_mineurs_air.json` — lis ton entrée complète : `symboles` + `comprendre` décrivent NOTRE image). Angles concepts : Pollack (famille, nombres), Wen (degrés), Greer (rôles, questions).

### Groupe A — les ouvertures

**`air_as` · Conscience** (Consciousness) — degré as. Image : ciel immense blanc pâle vu de très haut, sans un nuage, une lumière qui rend visible la profondeur de l'air ; un lit de nuages doux tout au fond, un petit nuage unique immobile. Concept : la clarté qui voit loin, l'esprit limpide. As = un don, une ouverture. Forme : **Image** ou **Offre**.

**`air_02` · Dualité** (Schizophrenia) — degré 2. Image : deux mains ouvertes paume contre paume, une large et une fine, l'une dans l'or du jour, l'autre dans le lilas du soir, contact posé sans serrer. Concept : les deux côtés de toi qui se touchent sans fusionner — tenir les deux sans choisir à la légère. 2 = mise en relation. Forme : **Miroir** ou **Question**.

**`air_03` · Isolement** (Ice-olation) — degré 3. Image : vitre couverte de givre, femme assise derrière, paume posée à plat — le givre retiré là où la main appuie, une fine fêlure qui monte en biais. Concept : la vitre qu'on colle soi-même, et la main qui la réchauffe déjà. Isolement choisi = repos ; vitre givrée = coupure. 3 = premier fruit — ici, le premier geste de dégel. Forme : **Image** ou **Miroir**.

**`air_04` · Procrastination** (Postponement) — degré 4. Image : porte ouverte sur un jardin, personne de dos dans l'encadrement, une main sur le cadre ; pièce grise et nue derrière, herbe et rosiers devant ; les couleurs déjà montées sur son manteau gris. Concept : le seuil où on reste — la porte est déjà ouverte. 4 = cadre — ici, l'encadrement de la porte. Forme : **Image** ou **Geste déguisé**.

### Groupe B — les secousses

**`air_05` · Comparaison** (Comparison) — degré 5. Image : bouleau clair et fin, pin énorme et sombre, chacun entier de la racine à la cime, même terre, même lumière, ciel qui a la place pour les deux. Concept : comparer deux formes qui n'ont rien à se dire. 5 = secousse — la comparaison qui secoue la confiance. Forme : **Image** ou **Miroir**.

**`air_06` · Fardeau** (The Burden) — degré 6. Image : escalier de pierre dans la brume, tas de six pièces de voyage laissées en un seul tas (sac, couverture, gamelle, corde, outre, sacoche), voyageuse de dos plusieurs marches plus haut, allégée. Concept : on peut déposer le chargement en un seul geste et continuer plus léger. 6 = circulation — ce qu'on porte vs ce qui circule. Forme : **Image** ou **Permission**.

**`air_07` · Manipulation** (Politics) — degré 7. Image : figure debout, un masque riant dans une main, un masque sévère dans l'autre, aucun porté ; cinq autres masques suspendus à des fils fins ; le visage nu et calme tourné vers la lumière. Concept : les rôles qu'on tient à distance du visage. 7 = évaluation, discernement. Forme : **Image** ou **Question**.

**`air_09` · Tristesse** (Sorrow) — degré 9. Image : grand paysage pâle, femme assise droite sur une pierre basse, mains vides dans le giron, tête un peu penchée, yeux ouverts, châle bleu profond sur robe crème, herbe couchée par le vent. Concept : la tristesse qui se tient droite — être présent à une perte, sans se cacher. 9 = bilan. Forme : **Météo** ou **Image**.

### Groupe C — le renouveau et les manières d'être

**`air_10` · Renaissance** (Rebirth) — degré 10. Image : paysage sous la neige, un seul crocus sorti droit de la neige, trois pétales violet pâle et cœur doré ; ciel de nuit qui se déchire, plaques de lumière, dont une sur la fleur. Concept : ce qui pousse après la longue attente. 10 = achèvement — un cycle se ferme, un autre commence. Forme : **Météo** ou **Image**.

**`air_page` · Dispersion** (Mind) — figure page. Image : jeune homme nu-pieds qui marche vite, cape qui gonfle, fumée claire au-dessus de la tête où flottent les objets : cadran de montre, enveloppe au sceau rouge, sablier, ruban, médaille. Concept : mille pensées qui courent avec toi — le mental qui s'éparpille et les objets qu'il soulève. Page = exploration, message. Forme : **Image** ou **Miroir**.

**`air_chevalier` · Lutte** (Fighting) — figure chevalier. Image : cheval blanc cabré, poitrail haut, jeune homme assis en arrière, deux mains sur les rênes tendues, bras raides — il tire de tout son poids contre le départ. Concept : se battre contre ce qui avance — l'élan retenu de force. Chevalier = élan vers un seul objectif ; ici, l'élan contré. Forme : **Miroir** ou **Question**.

**`air_reine` · Morale** (Morality) — figure reine. Image : jardin anglais, pelouse tondue ras, deux haies de buis taillées droit, femme debout au milieu, très droite, mains croisées, regard calme et sûr ; à ses pieds, une mauvaise herbe : tige grêle, trois feuilles poussiéreuses. Concept : le cadre qui garde — et ce qu'il écrase sans le voir. Reine = maîtrise intérieure, nourrir. Forme : **Question** ou **Miroir**.

## Checklist avant de livrer (chaque fiche)

1. JSON valide (`python3 -m json.tool`), clés exactes du gabarit, **`lecon` sans accent**, **aucun champ `reprise`**.
2. Aucun mot des listes noires (interdits durs + gestes vagues) — hors croyances rapportées exemptées.
3. Longueurs : lumiere/ombre.texte 50–90 mots ; positions 50–95 mots ; issue 1–4 phrases courtes ; questions 2–4 ; leçon et micro_geste une phrase.
4. Ombre : mode cohérent + **issue** qui ouvre (jamais un mur).
5. Aucune suite de 8 mots partagée avec les fiches existantes (relis air_08, air_roi, major_13) ni entre TES propres fiches.
6. Ouvertures variées (inventorie-les), aucune ouverture par concept abstrait, aucun « Ce n'est pas… » en tête, ≤ 1 tiret par texte.
7. `positions` : les quatre clés `jour / amene / se_joue / essayer`, chacune 50–95 mots, chacune différente des autres.
8. `lumiere` ne répète pas `positions.jour` — ce sont deux éclairages différents de la même qualité.
