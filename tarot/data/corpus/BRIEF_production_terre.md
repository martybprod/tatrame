# Brief de production — famille Terre (13 fiches restantes)

> **Pour les agents-rédacteurs.** Tu produis des fiches JSON du corpus tarot, prêtes pour la reformulation de Martin. Le produit est bilingue : concepts justes, langue simple, voix d'un ami lucide. Lis ce brief EN ENTIER, puis `data/corpus/CHARTE.md` (la charte complète), puis deux fiches voix de référence : `data/corpus/cartes/terre_08.json` (Simplicité — même famille, reformulée par Martin) et `data/corpus/cartes/air_08.json` (Culpabilité — voix de Martin, autre famille).

## Sorties

- Écris **un fichier JSON par carte** dans `data/corpus/cartes/`, nommé `<id>.json` (ex. `terre_as.json`).
- Le gabarit exact des clés : copie la structure de `data/corpus/cartes/terre_08.json` (champs dans le même ordre, clés SANS accent : `lecon`, jamais « leçon »).
- `source_referentielle` : cite tes angles (pollack/wen/greer + la source de l'image) dans le champ **`production`** uniquement.

## RÈGLE ABSOLUE — le champ `reprise`

**N'écris JAMAIS dans `source_referentielle.reprise`.** Ce champ est réservé à la note d'intégration posée par l'orchestrateur quand Martin a reformulé. Laisser la clé **absente** de ton JSON. Une fiche livrée avec un `reprise` = fausse attribution de la voix de Martin = rejet.

## Les règles qui décident (résumé opérationnel — la charte fait foi)

**Voix.** Tutoiement. Un ami lucide qui te connaît bien — pas un oracle, pas un coach. Doux assumé. Ginette doit tout comprendre à la première lecture (âge de lecture ~13). Français standard québécois-compatible : pas de « du coup », « un truc », « bosser », « carrément ».

**Structure d'une phrase.** Une chute par entrée, pas par phrase. Le reste est plat, parlé, facile. Ouvrir par « Tu… » ou une image concrète — jamais par un concept abstrait (« La matière… », « La patience… »), jamais par « Ce n'est pas… », jamais par le nom de la carte. Pas de verdict nié en tête (« Ce n'est pas X, c'est Y »).

**Interdits durs.** « tu vas / vous allez / bientôt / destin / c'est écrit / il faut / tu dois / tu devras / prédire / le signe que ». Exception documentée : les « tu dois » / « il faut » dans des croyances rapportées (« Tu crois que tu dois… », « tu as l'impression qu'il faut… ») sont permis — le conditionnement nommé, pas la prescription. Pas de métaphores économiques (« coûte », « payer », « le prix de ») — attention particulier sur cette famille (accumulation, avarice, abondance) : parler de richesse sans langage monétaire. Pas de « ton dedans », « ce qui se sent ». Pas d'« Éveil », pas de « Osho », pas de jargon du moteur. Gestes vagues interdits : « ouvre-toi », « lâche prise », « fais confiance à l'univers », « sois toi-même », « écoute ton cœur », « laisse-toi porter ».

**Remplacements qui marchent.** « tu vas » → « en ce moment, la situation penche vers ». « il faut » → « tu peux essayer ». « le signe que » → « un indice que ».

**Ombre.** Mode choisi parmi `amoindri / retourne / subi / differe` (définitions dans `tables.json → modes_ombre`). `texte` 50–85 mots OUVERT par « Tu… ». **`issue` OBLIGATOIRE** : toute ombre contient sa porte de sortie, en une phrase (la chaîne large).

**Longueurs.** `lumiere` et `ombre.texte` : 50–90 mots. Positions : 50–95 mots. `questions` : 2 à 4. `lecon` et `micro_geste` : une phrase.

**Banque de formes** (varier les ouvertures — jamais deux textes de la même forme d'affilée, ≤ 3 par forme dans ton lot) : Météo · Miroir · Offre · Question · Permission · Image · Geste déguisé. « Aujourd'hui » en ouverture ≤ 30 % de tes textes.

**Terre, la famille.** Le physique, le corps, la matière, la lenteur, la nourriture, la maison. Son problème : l'immobilisme, l'accumulation, la lourdeur — ce qu'on entasse et ce qui s'entarte. Sa voie : faire, durer, laisser mûrir. Ton de famille : **la Terre garde le geste concret** — chaque invitation se fait avec les mains (un objet, un pas, une récolte, une table).

**Anti-tic — les formules déjà usées ailleurs (interdites dans ton lot)** : « ce qui se joue, c'est ta capacité à… » (Eau ×3) · « Tu arrives avec le réflexe de… » (Feu) · « la carte te rappelle que tu possèdes déjà cette capacité » (Feu/Eau) · « tu n'as pas besoin d'attendre d'être… » (Feu/Eau) · « On t'a appris à… » (Feu) · « Tu as pris l'habitude de… » (Feu/Eau) · « Un choix t'attend peut-être entre… » (Air) · « La force y est toujours, mais… » (Air). Tes textes ne doivent partager AUCUNE suite de 8 mots avec les 47 fiches déjà écrites ni entre tes propres fiches. Inventorie tes ouvertures dans ton rapport final.

## Les degrés (grille de lecture — `tables.json → degres`)

as = la source, le potentiel pur · 2 = mise en relation · 3 = premier fruit · 4 = cadre · 5 = secousse · 6 = circulation · 7 = évaluation · 8 = mouvement, maîtrise · 9 = bilan · 10 = achèvement ou saturation. Le nombre × la famille peut se renforcer OU se contredire — dit-le dans `note_grille` quand ça se contredit.

## Les figures (jamais des personnes typées)

Une figure est **une manière d'être**, chez quelqu'un OU en toi (deux lectures simultanées, Greer). Page = exploration, message · Chevalier = élan vers un seul objectif · Reine = maîtrise intérieure, nourrir · Roi = maîtrise extérieure, cadre et responsabilité. Les figures n'ont ni âge, ni sexe, ni classe — les personnes des images restent des manières d'être.

## Les treize cartes

Sources : `ATRO_PLUS/_distillation/passation/` (concept + lecture) et `ATRO_PLUS/_distillation/symboles/` (grille de l'image validée) — **noms de fichiers avec zéro** (`terre_02_Presence.md`). Angles concepts : Pollack (famille Deniers, nombres), Wen (degrés), Greer (rôles, questions).

### Groupe A — la source et les fondamentaux

**`terre_as` · Maturité** (Maturity) — degré as = la source pure de la couleur. Lis `symboles/terre_as_maturite.md` (pas de passation pour l'as). Concept : la maturité comme racine — ce qui est déjà là, prêt à servir, sans effort encore. Tension : la figure seule, silencieuse et alerte. Forme : **Offre** ou **Image**.

**`terre_02` · Présence** (Moment to Moment) — degré 2. La carte dit : *un pas posé — et rien dans les mains*. Image : un mur de pierre sèche étroit sur la crête d'un plateau italien ; un homme pieds nus y marche vu de dos, un pied devant l'autre ; d'un côté la prairie (ombelles, olivier, deux cyprès), de l'autre le terrain tombe vers la vallée dans la brume ; lumière basse et chaude. Osho : l'équilibre en marche — dans le marché et hors de lui ; si tu trébuches, relève-toi. 2 = mise en relation — ici, le pas et la terre. Forme : **Image** ou **Miroir**.

**`terre_03` · Guidance** — degré 3. La carte dit : *la main qui ne parle pas*. Image : atelier de potier ; un tour à pied de bois (volant au ras des dalles, axe vertical, tête large) ; un jeune potier pieds nus fait monter un vase mouillé ; derrière lui, le maître penché — une main sur son épaule, l'autre au vase. Concept : la transmission par le geste, pas par la parole. 3 = premier fruit — le vase qui monte sous deux mains. Forme : **Image** ou **Miroir**.

**`terre_04` · Avarice** (Avarice) — degré 4. La carte dit : *ce qu'on ferme ne sert plus à personne*. Image : cour de ferme au soleil bas ; un vieux puits de pierres, margelle usée, coulures vertes ; poteau, poulie, crochet, corde retombante ; une dalle de pierre encastrée à ras ferme l'ouverture du puits. Concept : le cadre qui garde peut fermer — l'eau existe, personne n'y puise. 4 = cadre — ici, la dalle qui scelle. Forme : **Image** ou **Miroir**.

### Groupe B — les secousses et les temps longs

**`terre_05` · Marginalité** — degré 5. La carte dit : *le chemin est à gauche, il est à droite*. Image : un large chemin de terre monte vers la crête ; une file de gens y marche, tous de dos, ballot sur l'épaule, de plus en plus petits ; à droite, une bande d'herbe haute et de chardons sépare le chemin d'un pré non fauché où un homme marche dans l'autre sens, vers nous, pieds nus. Concept : l'écart choisi — être de la file ou être du pré, aucun des deux n'est une faute. 5 = secousse — l'écart qui secoue la file. Forme : **Miroir** ou **Question**.

**`terre_06` · Compromis** — degré 6. La carte dit : *pour entrer ici, il faut prendre la couleur de la pièce*. Image : dehors un mur ochre, terre sèche, lumière chaude ; une porte de bois sombre entrouverte ; dedans tout est gris et immobile ; dans l'embrasure, un vieil homme gris de la tête aux pieds, la main ouverte tendue ; devant lui, un jeune homme pieds nus. Concept : ce qu'on échange contre l'entrée — la couleur qu'on prend, la teinte qu'on laisse dehors. 6 = circulation — le prix du passage est un accord, pas une insulte. Forme : **Image** ou **Miroir**.

**`terre_07` · Patience** (Patience) — degré 7. La carte dit : *le travail est fait, et rien n'est encore obtenu*. Image : un potager en terrasses sur une pente douce ; quatre planches du même légume — la fève — à quatre âges : terre fraîchement semée (raies visibles, graines pâles en surface), semis, plants dressés, et la quatrième. Concept : les quatre âges d'une même chose — le temps n'est pas un adversaire. 7 = évaluation — mesurer sans arracher. Forme : **Image** ou **Météo**.

**`terre_09` · Plénitude** (Plénitude?) — degré 9. La carte dit : *la réserve est pleine, et le contentement est passé à l'intérieur*. Image : une resserre voûtée en pierre à la fin de l'été ; trois étagères pleines (bocaux fermés, sacs de grain, herbes sèches, chapelets d'ail et d'oignons) ; au sol une jarre de grès, des paniers, deux courges, une caisse de haricots ; une seule lumière. Concept : le bilan qui suffit — assez, sans plus. 9 = bilan — la réserve pleine, l'appétit apaisé. Forme : **Image** ou **Permission**.

### Groupe C — la table commune et les manières d'être

**`terre_10` · Communauté** (We Are the World) — degré 10. La carte dit : *ce qu'on a amassé devient bon quand il est posé entre plusieurs — et où personne n'est assis au bout*. Image : une longue table de planches sur tréteaux, dehors, sur la terre battue, sous un vieil arbre, à la fin du jour de moisson ; trois figures lisibles : le vieil homme à barbe grise qui rit la tête renversée, la femme au fichu rouge qui pose un plat, la petite assise au bout. Concept : la réserve partagée — ce qui se garde seul tourne, ce qui se pose nourrit. 10 = achèvement — la moisson finie qui devient repas. Forme : **Météo** ou **Image**.

**`terre_page` · Aventure** (Adventure) — figure page. La carte dit : *un enfant qui met le pied dans le noir — sans lampe, sans carte, et sans avoir peur*. Image : une pente sèche et minérale à la lumière basse du soir ; dans la roche, une ouverture naturelle plus haute qu'un homme dont on ne voit pas le fond — le dedans brun, chaud, tiède, jamais noir d'encre ; un enfant d'une dizaine d'années, de profil, tourné vers le noir. Concept : l'exploration au corps — le premier pas dans l'inconnu concret. Page = exploration, message. Forme : **Question** ou **Image**.

**`terre_chevalier` · Ralentir** (Slowing Down) — figure chevalier. La carte dit : *porter deux seaux pleins — et comprendre que la vitesse, c'est eux qui la donnent*. Image : un chemin de terre et de cailloux entre de gros rochers, fin du jour, dans une gorge de montagne ; un homme d'une quarantaine, pieds nus, une longue perche de bois posée sur ses deux épaules (linge plié dessous, la perche fléchit), deux seaux pleins. Osho : comme la tortue, nous portons notre maison. Concept : la vitesse juste — le pas qui tient la charge. Chevalier = élan vers un seul objectif ; ici, l'élan ralenti qui n'échappe rien. Forme : **Geste déguisé** ou **Image**.

**`terre_reine` · Épanouissement** (Flowering) — figure reine. La carte dit : *être arrivée à son point de fleur — et tenir dans ses mains de quoi recommencer ailleurs*. Image : un sentier de terre le long d'un mur de rose-trémières plus hautes que la figure, fleuries jusqu'au sommet, une couleur nette par plante (rose pâle, lie-de-vin, abricot, doré, mauve, bleu-violet, crème) ; massif à gauche, proche et dense ; le côté droit reste ouvert. Concept : la floraison aboutie — et les graines de la suivante. Reine = maîtrise intérieure, nourrir. Forme : **Offre** ou **Permission**.

**`terre_roi` · Abondance** (Abundance) — figure roi. La carte dit : *ce qui est là, en tas, prêt à être donné — et personne n'a encore rien demandé*. Image : un marché à l'aube ; une longue table de planches brutes sur tréteaux dont le bois fléchit ; sur le bois, à même, des montagnes de fruits (abricots, citrons, tomates, aubergines, figues) ; caisses ouvertes, sacs de grain et d'amandes avec leur pelle, bassines d'olives aux deux bouts. Concept : la maîtrise qui donne — l'abondance qui ne compte pas. Roi = maîtrise extérieure. Forme : **Offre** ou **Permission**.

## Checklist avant de livrer (chaque fiche)

1. JSON valide (`python3 -m json.tool`), clés exactes du gabarit, **`lecon` sans accent**, **aucun champ `reprise`**.
2. Aucun mot des listes noires (interdits durs + gestes vagues) — hors croyances rapportées exemptées. Aucun verdict nié en tête de phrase.
3. Longueurs : lumiere/ombre.texte 50–90 mots ; positions 50–95 mots ; issue 1–4 phrases courtes ; questions 2–4 ; leçon et micro_geste une phrase.
4. Ombre : mode cohérent + **issue** qui ouvre (jamais un mur).
5. Aucune suite de 8 mots partagée avec les fiches existantes (relis terre_08, air_08, major_13) ni entre TES propres fiches.
6. Ouvertures variées (inventorie-les), aucune ouverture par concept abstrait, aucun « Ce n'est pas… » en tête, ≤ 1 tiret par texte.
7. `positions` : les quatre clés `jour / amene / se_joue / essayer`, chacune 50–95 mots, chacune différente des autres.
8. `lumiere` ne répète pas `positions.jour` — ce sont deux éclairages différents de la même qualité.
9. `micro_geste` : un geste avec les mains (Terre), faisable aujourd'hui, en une phrase.
