# Brief de production — les 18 majeurs restants

> **Pour les agents-rédacteurs.** Tu produis des fiches JSON du corpus tarot, prêtes pour la reformulation de Martin. Le produit est bilingue : concepts justes, langue simple, voix d'un ami lucide. Lis ce brief EN ENTIER, puis `data/corpus/CHARTE.md` (la charte complète), puis deux fiches voix de référence : `data/corpus/cartes/major_00.json` (Foi — majeur reformulé par Martin) et `data/corpus/cartes/major_13.json` (Transformation — majeur reformulé par Martin).

## Sorties

- Écris **un fichier JSON par carte** dans `data/corpus/cartes/`, nommé `<id>.json` (ex. `major_01.json`).
- Le gabarit exact des clés : copie la structure de `data/corpus/cartes/major_00.json` — **pas de `famille` ni de `degre` ni de `rang`** : le majeur porte `type: "majeur"`, un `registre` et un `element` (table Wen, déjà posés dans `jeu.json` — recopie-les tels quels).
- `source_referentielle` : cite tes angles (pollack §3 / wen §3 / greer §6.2 + la source de l'image) dans le champ **`production`** uniquement.

## RÈGLE ABSOLUE — le champ `reprise`

**N'écris JAMAIS dans `source_referentielle.reprise`.** Ce champ est réservé à la note d'intégration posée par l'orchestrateur quand Martin a reformulé. Laisser la clé **absente** de ton JSON. Une fiche livrée avec un `reprise` = fausse attribution de la voix de Martin = rejet.

## Les règles qui décident (résumé opérationnel — la charte fait foi)

**Voix.** Tutoiement. Un ami lucide qui te connaît bien — pas un oracle, pas un coach. Doux assumé. Ginette doit tout comprendre à la première lecture (âge de lecture ~13). Français standard québécois-compatible : pas de « du coup », « un truc », « bosser », « carrément ».

**Structure d'une phrase.** Une chute par entrée, pas par phrase. **Aucun deux-points dans les textes** (la chute est une phrase courte ou un fragment). Le reste est plat, parlé, facile. Ouvrir par « Tu… » ou une image concrète — jamais par un concept abstrait (« La liberté… », « Le vide… »), jamais par « Ce n'est pas… », jamais par le nom de la carte, jamais de verdict nié en tête.

**Interdits durs.** « tu vas / vous allez / bientôt / destin / c'est écrit / il faut / tu dois / tu devras / prédire / le signe que ». Exception documentée : les « tu dois » / « il faut » dans des croyances rapportées (« Tu crois que tu dois… », « tu finis par croire que tu dois… ») sont permis — le conditionnement nommé, pas la prescription. Pas de métaphores économiques (« coûte », « payer », « le prix de »). Pas de « ton dedans », « ce qui se sent ». Pas d'« Éveil », pas de « Osho », pas de jargon du moteur. Gestes vagues interdits : « ouvre-toi », « lâche prise », « fais confiance à l'univers », « sois toi-même », « écoute ton cœur », « laisse-toi porter ».

**Remplacements qui marchent.** « tu vas » → « en ce moment, la situation penche vers ». « il faut » → « tu peux essayer ». « le signe que » → « un indice que ».

**Ombre.** Mode choisi parmi `amoindri / retourne / subi / differe` (définitions dans `tables.json → modes_ombre`). `texte` 50–85 mots OUVERT par « Tu… ». **`issue` OBLIGATOIRE** : toute ombre contient sa porte de sortie, en une phrase (la chaîne large).

**Longueurs.** `lumiere` et `ombre.texte` : 50–90 mots. Positions : 50–95 mots. `questions` : 2 à 4. `lecon` et `micro_geste` : une phrase.

**Banque de formes** (varier les ouvertures — jamais deux textes de la même forme d'affilée, ≤ 3 par forme dans ton lot) : Météo · Miroir · Offre · Question · Permission · Image · Geste déguisé. « Aujourd'hui » en ouverture ≤ 30 % de tes textes.

**Les majeurs, la famille.** Pas de famille : un **registre** dit où se joue la carte, un **élément** (table Wen) teint la manière.
- `exterieur` : ça se joue dans le monde — avec les autres, dans le concret.
- `interieur` : ça se joue dans ton dedans — la croissance, la mesure, l'accord.
- `transpersonnel` : plus grand que toi — ce qui te traverse, t'hérite, te dépasse.
- Éléments : feu = l'élan, eau = le flux, air = la clarté, terre = le concret.
Dit dans `note_grille` quand le nombre du majeur contredit son registre ou son élément (la tension assumée de la carte).

**Anti-tic — les formules déjà usées ailleurs (interdites dans ton lot)** : « ce qui se joue, c'est ta capacité à… » (Eau) · « Tu arrives avec le réflexe de… » (Feu) · « la carte te rappelle que tu possèdes déjà cette capacité » · « tu n'as pas besoin d'attendre d'être… » · « On t'a appris à… » · « Tu as pris l'habitude de… » · « Un choix t'attend peut-être entre… » (Air) · « La force y est toujours, mais… » (Air). Tes textes ne doivent partager AUCUNE suite de 8 mots avec les 60 fiches déjà écrites ni entre tes propres fiches. Inventorie tes ouvertures dans ton rapport final.

## Les 18 cartes

Sources de concept : `TAROT_APP/_distillation/cartes_concepts/` (Pollack §3, Greer §6.2, Wen §3) et le nom Osho de chaque carte dans `ATRO_PLUS/_distillation/noms_cartes.json`. Sources d'image : les descriptions ci-dessous (visages validés par Martin).

### Groupe A — les fondations (extérieur)

**`major_01` · Existence** (Existence) — exterieur/terre. Image : une femme de dos, assise au bord d'un lac immense, la nuit sous la Voie lactée ; la coupe de gazon de la berge montre ses racines d'arbre ; des étoiles sont suspendues au-dessus de l'eau par de fins fils d'or ; branches fleuries et oiseaux dans le cadre ; un nénuphar, le reflet calme. Concept : tu es porté — la terre, le lac et le ciel te soutiennent déjà ; l'appartenance n'a pas de conditions. Forme : **Image** ou **Offre**.

**`major_02` · Intuition** (Inner Voice) — exterieur/eau. Image : une jeune femme assise au bord d'un bassin de pierre, jambes dans l'eau (l'eau se ferme en anneaux lents), le regard baissé vers l'eau ; un cristal lumineux au creux de ses deux mains, à hauteur de cœur ; deux têtes de dauphins émergent à gauche et à droite de ses pieds ; fond nocturne de colonnes. Concept : la voix intérieure — le savoir doux qui monte de toi, entendu sans être prouvé. Forme : **Miroir** ou **Question**.

**`major_03` · Créativité** (Creativity) — exterieur/terre. Image : une danseuse au sourire franc, cheveux au vent, robe longue à panneaux de couleurs différentes ; des rubans multicolores partent d'elle et rayonnent en arcs jusqu'au haut du cadre ; elle danse pieds nus sur un disque-mandala au centre d'un bassin où tournent des flammes en anneau. Concept : l'énergie qui crée en dansant — les couleurs partent d'un centre, le feu et l'eau réunis sous les pieds. Forme : **Image** ou **Météo**.

**`major_04` · Liberté** (The Rebel) — exterieur/feu. Image : paysage immense vu de très haut : falaises et ruines d'un temple à colonnes sur une paroi ; une rivière sinueuse descend vers la vallée verte ; un aigle, vu de dos, plein ciel au centre, vers le lointain ; lumière dorée pâle. Concept : l'envol au-dessus des ruines — la liberté décolle de ce qui fut construit, sans détruire. Forme : **Image** ou **Miroir**.

**`major_05` · Vide** (No-Thingness) — exterieur/terre. Image : un noir d'encre lisse et velouté, sans horizon, sans paysage ; un seul œuf de lumière crème flotte un peu au-dessus du centre, petit, qui brille de l'intérieur, discret halo. Concept : le vide d'avant la première forme — rien n'est encore dit, tout est encore possible. Forme : **Image** ou **Permission**.

### Groupe B — l'art de marcher (extérieur et intérieur)

**`major_07` · Volonté** (Awareness) — exterieur/eau. Image : un jeune homme marche tranquille vers nous, chemise claire manches retroussées ; des flammes blanches, froides, montent autour de lui comme une aura ; à sa gauche un sphinx crème, à sa droite un sphinx gris foncé, marchent avec lui (colliers croissant et disque) ; ciel étoilé. Concept : la maîtrise tranquille — les deux instincts opposés marchent avec toi ; le feu blanc qui n'épuise pas. Forme : **Image** ou **Miroir**.

**`major_08` · Courage** (Courage) — interieur/feu. Image : un œuf éclos sur un promontoire au bord d'un canyon dans la brume ; l'oisillon émerge encore de la moitié de coquille ; un oiseau adulte en plein vol traverse le vide au premier plan ; un grand vautour plane loin dans le ciel ; un épi de graminée à côté. Concept : le premier vol au-dessus du vide — le courage naît dans l'œuf encore tiède, il ne se prépare pas debout. Forme : **Image** ou **Geste déguisé**.

**`major_09` · Solitude** (Aloneness) — interieur/terre. Image : un homme encapuchonné marche seul dans une vallée de montagnes enneigées, la nuit ; bâton à la main ; une étoile blanche à six branches brille sur sa poitrine comme une lanterne intérieure ; il regarde calmement. Concept : être seul sans être coupé — la lumière qu'on porte dans l'immense froid. Forme : **Image** ou **Météo**.

**`major_10` · Changement** (Change) — interieur/feu. Image : dans un cosmos d'indigo (étoiles, nébuleuses légères), une roue-peinture parfaitement ronde, entourée d'un ouroboros doré collé au bord ; à l'intérieur, une seule peinture continue de l'année fondue avec les heures du jour — printemps à l'aube en haut, été en plein jour à droite, automne au crépuscule en bas, hiver de nuit à gauche, chacune avec ses plantes. Concept : tout tourne — les saisons et les heures ne sont qu'une seule moûture ; ce qui change n'abîme pas ce qui reste. Forme : **Image** ou **Météo**.

### Groupe C — la mesure et l'accord (intérieur)

**`major_11` · Justesse** (Breakthrough) — interieur/air. Image : un atelier de tissage ; une femme pieds nus tient des ciseaux le long d'un fil rouge tendu, qui traverse l'atelier et le tissu monté sur le métier ; derrière le tissu, en trompe-l'œil, un archer tire vers une cible — la flèche au centre exact ; une balance de laiton au premier plan. Concept : la juste mesure — tout est aligné, le moment de couper est net, ni tôt ni tard. Forme : **Image** ou **Question**.

**`major_12` · Perspective** (New Vision) — interieur/eau. Image : un jeune homme ailé est suspendu la tête en bas, tenu par les pieds au cadre même de la carte ; petites ailes blanches le long du corps ; ciel d'aquarelle rose et bleue, cercle doré et triangle géométriques ; dans la partie haute de la carte, un petit paysage au dôme. Concept : voir à l'envers — le monde suspendu change de sens quand tu changes d'angle ; la patience qui voit. Forme : **Miroir** ou **Question**.

**`major_14` · Équilibre** (Integration) — interieur/feu. Image : la carte coupée en deux moitiés verticales — nuit étoilée et jour doré ; un aigle et un cygne se tiennent ensemble au bord d'une eau calme, ailes déployées qui se touchent presque, leurs reflets inversés dans l'eau. Concept : deux natures opposées partagent le même bord — l'accord sans fusion. Forme : **Image** ou **Miroir**.

**`major_15` · Emprise** (Conditioning) — transpersonnel/terre. Image : une femme emmaillotée de bandages serrés, debout sur un socle noir (une chaîne rouillée posée à côté) ; des fils de marionnette montent vers une main venue du haut du cadre, et elle tient elle-même l'un des fils ; une flamme de lampe pend à un fil ; son cœur brille à travers les bandages ; en bas, un bassin reflète sa silhouette libre et lumineuse. Concept : le conditionnement — les fils qu'on finit par tenir soi-même ; la forme vivante attend sous les bandages, le reflet libre est déjà là. Forme : **Image** ou **Miroir**.

### Groupe D — plus grand que toi (transpersonnel)

**`major_16` · Rupture** (Thunderbolt) — transpersonnel/feu. Image : une grande tapisserie sur son métier de bois montre une tour couronnée en spirale ; la toile se déchire du haut en bas — une déchirure verticale lumineuse, incandescente, avec des étincelles ; deux petites figures tombent la tête en bas de chaque côté, dans le tissage ; une femme de profil regarde calmement, les fils dorés de sa robe tissés dans la toile. Concept : la rupture qui révèle — le construit se fend, la lumière passe par la fente ; on peut regarder sans fuir. Forme : **Image** ou **Météo**.

**`major_18` · L'Invisible** (Past Lives) — transpersonnel/eau. Image : un grand arbre la nuit, croissant de lune et étoiles, menhirs au loin ; sous la ligne de sol, les racines dorées descendent dans une caverne lumineuse où pendent, suspendues à des chaînes d'or fixées aux racines, trois objets : un anneau, une clé, une couronne. Concept : l'héritage invisible — ce qui te soutient dort sous le visible ; lumineux, accessible par ce qui te relie. Forme : **Image** ou **Question**.

**`major_19` · Rayonnement** (Innocence) — transpersonnel/feu. Image : une grande serre victorienne baignée de matin chaud ; banc de petits pots en rangs, agrumes chargés, suspensions, fougères, petit palmier, dallage de pierre ; de larges rais dorés entrent par les vitres, épais de poussière lumineuse, et dorent tout ce qu'ils touchent ; un petit enfant de dos, pieds nus, s'occupe d'un carreau ; un chat dort. Concept : le rayonnement de l'innocence — la lumière entre sans effort et fait de l'or de tout ce qu'elle touche. Forme : **Météo** ou **Image**.

**`major_20` · Vérité** (Beyond Illusion) — transpersonnel/eau. Image : un colossal visage de pierre balinais, les yeux clos et un sourire doux, à moitié enfoui dans la terre ; un monticule d'herbe au premier plan cache le bas du visage ; trois petites fleurs blanches posées en offrande ; pierre gris-vert patinée de mousse. Concept : la vérité sous les apparences — le visage qui reste quand les modes passent ; enfoui, serein, reconnaissable. Forme : **Image** ou **Question**.

**`major_21` · Accomplissement** (Completion) — transpersonnel/terre. Image : une femme d'âge mûr, digne et souriante, assise devant un grand métier de haute-lice ; les fils verticaux portent chacun une couleur d'une même palette (bobines suspendues) ; elle noue à mains nues les derniers fils au centre du motif. Concept : l'accomplissement — les derniers nœuds du motif, posés sans hâte ; la pièce n'est pas finie qui n'a pas été habitée. Forme : **Image** ou **Offre**.

## Checklist avant de livrer (chaque fiche)

1. JSON valide (`python3 -m json.tool`), clés exactes du gabarit majeur (`registre` + `element`, sans famille/degré/rang), **`lecon` sans accent**, **aucun champ `reprise`**.
2. Aucun mot des listes noires — hors croyances rapportées exemptées. **Aucun deux-points dans les textes.** Aucun verdict nié en tête.
3. Longueurs : lumiere/ombre.texte 50–90 mots ; positions 50–95 mots ; issue 1–4 phrases courtes ; questions 2–4 ; leçon et micro_geste une phrase.
4. Ombre : mode cohérent + **issue** qui ouvre (jamais un mur).
5. Aucune suite de 8 mots partagée avec les 60 fiches existantes (relis major_00, major_13) ni entre TES propres fiches.
6. Ouvertures variées (inventorie-les), aucune ouverture par concept abstrait, ≤ 1 tiret par texte.
7. `positions` : les quatre clés `jour / amene / se_joue / essayer`, chacune 50–95 mots, chacune différente des autres.
8. `lumiere` ne répète pas `positions.jour`. `note_grille` pose la tension nombre × registre × élément quand elle se contredit.
