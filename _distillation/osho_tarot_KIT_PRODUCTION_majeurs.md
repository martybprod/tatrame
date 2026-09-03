# KIT DE PRODUCTION — Arcanes majeurs (tarot personnel, base Osho + Rider)

> **But** : tout ce qu'il faut pour écrire les 23 prompts Draw Things des arcanes majeurs, sans rien réinventer. Rédigé le 2026-09-03.
> **Compagnons** : `osho_zen_tarot_carte_de_concepts.md` (l'OS du jeu) · source des symboles = EPUB `TAROT/OSHO/osho-zen-tarot_BOOK.epub`.
> **Modèle d'image** : **Flux.2 Klein 9B** dans Draw Things.

---

## 1. RECETTE FIGÉE (réglages Draw Things)

| Réglage | Valeur |
|---|---|
| Résolution | **1024 × 1536** (2:3) |
| Modèle | **Flux.2 Klein 9B** (`flux_2_klein_9b_q8p.ckpt`) |
| LoRA | **Mucha** (`mucha_style_f29b_...`) poids **0.55** |
| Échantillonneur | **Euler A Trailing** |
| Étapes | **20** (indispensable pour l'anatomie — 8 steps = pieds/mains/ailes ratés) |
| Guidage du texte (CFG) | **3.0** (choix de Martin pour la qualité ; à CFG 3 le négatif REDEVIENT actif → garde-fous anatomie utiles) |
| Négatif anatomie | **actif** : `extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render` |
| Guidage Flux (guidance_embed) | **3.5** |
| Décalage (Shift) | **3** |
| Graine | **explicite et notée par carte** (l'API ne renvoie pas le seed aléatoire) |

**Pilotage** : via l'API HTTP Draw Things (`http://127.0.0.1:7860/sdapi/v1/txt2img`), script `_distillation/_gen_carte.py`. **~325 s/carte** à 20 steps + CFG 3 (le CFG>1 double le temps, assumé pour la qualité). Validée sur 2 cartes (0 Confiance, II Voix intérieure).
**Workflow anti-raté** : générer 1 image/carte, vérifier l'anatomie de PRÈS (pieds, mains, ailes, doublons), régénérer avec un autre seed uniquement les cartes défaillantes.

⚠️ **CFG à 1.0 = prompt négatif ignoré.** → **Tout se pilote dans le prompt POSITIF.** On ne décrit JAMAIS ce qui ne doit pas être là (pas de « no luggage » → dessine une valise).

---

## 2. RÈGLES D'ÉCRITURE D'UN PROMPT (à appliquer à CHAQUE carte)

1. **Langue du prompt** : anglais (Flux suit mieux).
2. **Un seul sujet** : commencer par « *A single …, alone, the only person in the scene* » pour éviter les dédoublements.
3. **Genre explicite** selon la carte (indiqué dans l'inventaire §5). Pas de figures non binaires.
4. **Pose / action-clé d'abord** : c'est le cœur de la carte (ex. Le Fou EST EN TRAIN de faire le pas dans le vide).
5. **Symboles** : fusionner Osho (prioritaire) + Rider (en appoint), tous listés dans le positif.
6. **Fond signifiant** (pas décoratif) : y placer les éléments symboliques de fond.
7. **Palette complète, PAS d'arc-en-ciel objet par défaut** : toutes les teintes (chaudes + froides) présentes dans la carte, mais **réparties naturellement et équilibrées selon la scène** — pas d'arc-en-ciel littéral (ni rivière/ciel arc-en-ciel) SAUF si la carte l'exige vraiment. **Exception** : pour une carte qui veut réellement un arc-en-ciel (ex. certaines majeures, future famille Arc-en-ciel), le nommer dans le positif ET **retirer les termes `rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band` du négatif** pour cette carte.

10. **Couleurs des 4 éléments** (quand une carte représente les éléments — veste du Fou, alchimie feu/eau, etc.) : 🔥 Feu = **red (or orange)** · 💧 Eau = **blue** · 🌬️ Air = **white (or yellow)** · ⛰️ Terre = **brown (or black)**. Employer ces couleurs traditionnelles, pas des couleurs arbitraires.
8. **Terminer par l'ANCRE DE STYLE** (ci-dessous, copiée telle quelle).
9. Pas de texte/chiffres dans l'image (ne PAS l'écrire dans le positif ; c'est géré par le style « hand-painted »).

### ANCRE DE STYLE (à coller en fin de chaque prompt positif)
> *The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.*

### NÉGATIF STANDARD (ACTIF à CFG 3 — à utiliser tel quel)
> *extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render*

---

## 3. GABARIT PAR CARTE (structure de livraison)

```
### N · NOM-ÉTAT (équivalent traditionnel)
Genre : …
Pose / action-clé : …
Symboles Osho : …
Symboles Rider (appoint) : …
Fond : …
PROMPT (positif EN) : … + [ANCRE DE STYLE]
Texte de lecture (FR, app) : …
Seed : (à remplir après génération)
```

---

## 4. EXEMPLE VALIDÉ (le « gold standard » à imiter) — 0 · CONFIANCE

**PROMPT positif :**
> *A single solitary young man captured mid-stride, in the very act of stepping his leading foot off the edge of a high cliff into empty air, one leg extended forward over the abyss with no ground beneath it, body leaning into the open void, his face refined and serene, gently holding one white rose. He wears a long flowing coat softly patterned with the four traditional elemental colors — red for fire, blue for water, white for air, brown for earth. A single small white dog stands alert at the cliff edge behind him. Below, a luminous winding river flows through misty valleys, a pale dawn sun glows through haze, a single white bird drifts across the sky, distant mountains fade into mist. The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.*

**Texte de lecture :** *Fais confiance à ton intuition, à ton sens du « juste ». Ton geste peut sembler fou à la raison — mais c'est là, au point zéro, que la confiance guide mieux que l'expérience passée.*

---

## 5. INVENTAIRE DES SYMBOLES — 23 ARCANES MAJEURS
*(fidèle au texte « This Card » du livre ; Osho prioritaire, Rider en appoint)*

### 0 · CONFIANCE (Le Fou) — ✅ déjà écrit (voir §4)
Genre : homme. Pose : le pas dans le vide.

### I · EXISTENCE (Le Magicien)
Genre : femme (nu pudique, à la Mucha). Pose : assise sur une feuille de lotus, contemplant le ciel nocturne, détendue et « chez elle ».
Osho : feuille de lotus de la perfection · nudité = innocence/être chez soi · ciel étoilé · étoiles, rochers, arbres, fleurs, poissons, oiseaux (tous « frères et sœurs » dans la danse de la vie).
Rider (appoint) : sentiment d'unité, énergie une reliant tout.
Fond : nuit étoilée, éléments de nature autour d'elle (eau avec poissons, arbres, fleurs, oiseaux).

### II · VOIX INTÉRIEURE (La Grande Prêtresse) — ✅ déjà écrit (test #2)
Genre : femme. Pose : assise au centre, sereine et veilleuse, tenant le cristal à deux mains.
Osho : visage central alerte · deux mains tenant un cristal (une dans l'ombre, une dans la lumière) · cristal = clarté au-delà des dualités · deux dauphins dansant dans l'eau · couronne de croissant de lune · feuilles vertes sur le kimono.
Rider (appoint) : deux piliers (un sombre, un clair) · croissant de lune · voile du savoir caché.
Fond : cosmos étoilé en haut, eau ondoyante en bas.

### III · CRÉATIVITÉ (L'Impératrice)
Genre : figure (au choix, plutôt féminine/maternelle possible). Pose : « possédée par » la force créatrice, abandon, bras ouverts.
Osho : alchimie du feu et de l'eau en bas · lumière divine descendant d'en haut · énergie sans forme d'où naissent toutes les formes.
Rider (appoint) : abondance, fertilité, floraison.
Fond : feu + eau se mêlant en bas, faisceau de lumière divine en haut, énergie créatrice tourbillonnante, formes naissantes.

### IV · LE REBELLE (L'Empereur)
Genre : homme. Pose : debout, puissant, maître de son destin.
Osho : emblème du soleil sur l'épaule · torche dans la main droite (lumière de sa vérité durement acquise) · chaînes brisées du conditionnement · toutes les couleurs de l'arc-en-ciel embrassées · ailes déployées pour voler · émergeant de racines sombres et informes.
Rider (appoint) : posture d'autorité (trône/empereur).
Fond : ciel ouvert, racines sombres en bas, aigle (animal-esprit, messager terre-ciel) dans le ciel.

### V · NÉANT (Le Pape)
Genre : figure/silhouette (ou abstrait). Pose : « dans l'intervalle », suspendue dans le vide, sans repère.
Osho : le vide (« the gap ») · potentiel pur d'avant la création de l'univers · silence entre les mots · intervalle entre deux souffles · quelque chose de sacré sur le point de naître.
Rider (appoint) : quasi rien (Osho diverge fortement) — garder l'épure.
Fond : vide sombre et informe, un germe de lumière sacrée émergeant, minimalisme.

### VI · LES AMANTS (Les Amoureux)
Genre : un homme et une femme. Pose : union qui s'élève, de la terre vers le ciel.
Osho : spectre de l'amour, de la terre (attirance) au ciel (amour universel) · le partenaire comme miroir · ailes qui portent plus haut vers l'amour-un.
Rider (appoint) : couple, figure/ange lumineux au-dessus, soleil.
Fond : dégradé terre→ciel, ailes, lumière universelle enveloppante.

### VII · CONSCIENCE (Le Chariot)
Genre : visage de bouddha (androgyne, délicat) + un témoin. Pose : voile qui se consume, visage émergeant.
Osho : voile de l'illusion (maya) qui brûle · flamme FROIDE de la conscience (pas la chaleur de la passion) · visage de bouddha délicat et enfantin qui apparaît · le témoin silencieux au centre.
Rider (appoint) : idée de maîtrise/direction intérieure.
Fond : voile en train de se consumer, flamme froide (bleutée), lumière du centre-témoin.

### VIII · COURAGE (La Force)
Genre : PAS de personnage central — une petite fleur sauvage. Pose : la fleur perce les rochers et s'ouvre à la lumière.
Osho : petite fleur sauvage émergeant d'entre les rochers et les pierres · auréole de lumière dorée · égale au soleil le plus brillant, sans honte.
Rider (appoint) : facultatif — un lion doux/apprivoisé en arrière-plan (force douce).
Fond : rochers/pierres, percée de lumière dorée, soleil.

### IX · SOLITUDE (L'Ermite)
Genre : figure humble (au choix). Pose : marche seule dans l'obscurité, rayonnant d'une lumière intérieure.
Osho : figure humble qui brille d'une lumière venant de l'intérieur · « sois une lumière pour toi-même » · traverser l'obscurité sans compagnon, carte ni guide.
Rider (appoint) : lanterne/bâton/cape d'ermite — MAIS remplacer la lanterne par la lumière qui émane du corps.
Fond : nuit/obscurité, sentier solitaire, halo intérieur.

### X · CHANGEMENT (La Roue de Fortune)
Genre : (optionnel) une figure relâchée au centre. Pose : au centre calme d'une roue qui tourne.
Osho : roue immense = temps/destin/karma · galaxies tournoyant autour · les 12 signes du zodiaque sur la circonférence · les 8 trigrammes du Yi King · les 4 directions illuminées par la foudre · triangle tournant pointé vers le haut (le divin) · yin/yang au centre.
Rider (appoint) : la grande roue.
Fond : roue cosmique, galaxies, bord tourbillonnant vs centre immobile.

### XI · PERCÉE (La Justice)
Genre : figure (au choix). Pose : jaillissement, posture d'exubérance et de détermination, brise ses entraves.
Osho : dominance du ROUGE · énergie/puissance/force · éclat rayonnant du plexus solaire · éclatement des vieux schémas et limitations.
Rider (appoint) : idée de décision tranchée/libératrice.
Fond : énergie rouge, barreaux/murs qui volent en éclats, explosion de vitalité.

### XII · NOUVELLE VISION (Le Pendu)
Genre : figure (source : « him », plutôt masculin). Pose : naît à nouveau, s'élève de ses racines terrestres, ailes déployées vers l'illimité.
Osho : figure renaissant de racines terrestres · ailes vers l'illimité · formes géométriques autour du corps : carré (physique/connu), cercle (non-manifesté/esprit), triangle (triple nature de l'univers) · toutes les couleurs de la vie qui pénètrent.
Rider (appoint) : renversement de perspective (le Pendu).
Fond : racines en bas, ciel ouvert en haut, formes géométriques flottantes, ailes.

### XIII · TRANSFORMATION (La Mort)
Genre : figure androgyne (« its »). Pose : assise au sommet de la fleur du vide, une main ouverte sur les genoux, l'autre descend toucher la bouche d'un visage endormi.
Osho : fleur immense du vide · épée (tranche l'illusion) · serpent (mue/renouvellement) · chaîne brisée (limitations) · symbole yin/yang (dépasser la dualité) · main réceptive ouverte · visage endormi en bas (le silence du repos).
Rider (appoint) : mort/renaissance (sans macabre).
Fond : grande fleur du vide, visage endormi en contrebas, ambiance de lâcher-prise.

### XIV · INTÉGRATION (Tempérance)
Genre : union (androgyne, ou aigle + cygne). Pose : fusion des opposés, alchimie.
Osho : union mystica, fusion des contraires · nuit et jour qui coopèrent, chacun portant le germe de l'autre · l'AIGLE (puissance, solitude) et le CYGNE (espace, pureté, flottant sur l'eau des émotions) · masculin/féminin, feu/eau, vie/mort · alchimie.
Rider (appoint) : ange versant/mêlant deux coupes.
Fond : jour et nuit se rejoignant, eau, aigle et cygne.

### XV · CONDITIONNEMENT (Le Diable)
Genre : animaux (un lion + des moutons). Pose : un lion qui se croit mouton, découvrant son reflet dans l'étang.
Osho : conte zen — un lion élevé parmi les moutons se prend pour un mouton · le troupeau · l'étang où il voit enfin son vrai reflet (un lion).
Rider (appoint) : idée de chaînes/servitude (conditionnement imposé de l'extérieur).
Fond : troupeau de moutons, un lion, un étang-miroir révélant le vrai soi.

### XVI · COUP DE FOUDRE (La Maison-Dieu)
Genre : un homme et une femme + une figure-témoin. Pose : ils sautent d'une tour en flammes (sans choix), une silhouette transparente médite en fond.
Osho : tour en train de brûler, détruite, soufflée · un homme et une femme s'en échappent en sautant · figure transparente et méditative en arrière-plan (conscience-témoin) · foudre.
Rider (appoint) : tour foudroyée, figures qui chutent.
Fond : tour en flammes, éclair, figures sautant, témoin serein en retrait.

### XVII · SILENCE (L'Étoile)
Genre : visage féminin dans le ciel (déesse de la nuit). Pose : méditation profonde, réceptivité miroir.
Osho : nuit étoilée avec pleine lune reflétée dans un lac brumeux · visage dans le ciel en méditation, déesse de la nuit (profondeur, paix).
Rider (appoint) : étoiles, eau, sérénité (femme/eau versée — optionnel).
Fond : ciel étoilé, pleine lune, lac brumeux miroir.

### XVIII · VIES ANTÉRIEURES (La Lune)
Genre : pas de personnage unique — des mains + des visages + deux lézards. Pose : les mains de l'existence forment un portail/matrice cosmique révélant des visages d'autres temps.
Osho : les mains de l'existence formant l'ouverture de la mère cosmique (à rendre en **portail/matrice symbolique et pudique**) · à l'intérieur, de nombreux visages d'autres époques · deux lézards arc-en-ciel de part et d'autre (savoir et non-savoir, gardiens de l'inconscient).
Rider (appoint) : la lune, cycles, motifs répétitifs.
Fond : portail cosmique de visages, deux lézards arc-en-ciel, lune.
Note : traiter l'ouverture « mère cosmique » de façon symbolique et non explicite.

### XIX · INNOCENCE (Le Soleil)
Genre : un vieil homme. Pose : rayonne une joie enfantine, communique avec une mante religieuse sur son doigt.
Osho : vieil homme au bonheur enfantin, plein de grâce · mante religieuse sur son doigt (grands amis) · fleurs roses cascadant autour de lui (lâcher-prise, douceur) · innocence enfantine mais SAGE (pas puérile).
Rider (appoint) : soleil chaud, lumière joyeuse (l'enfant du Soleil → ici transposé au vieillard sage).
Fond : cascade de fleurs roses, lumière solaire douce et chaude.

### XX · AU-DELÀ DE L'ILLUSION (Le Jugement)
Genre : un visage de conscience (androgyne) + un papillon. Pose : le papillon devant, le visage regardant vers l'intérieur, le troisième œil s'ouvre.
Osho : papillon = l'extérieur, le mouvant, l'illusion · derrière, le visage de la conscience tourné vers l'intérieur · l'espace entre les deux yeux s'ouvre, révélant le lotus de l'épanouissement spirituel et le soleil levant de la conscience (troisième œil).
Rider (appoint) : appel/réveil, résurrection intérieure.
Fond : papillon, grand visage serein, troisième œil = lotus + soleil levant.

### XXI · ACCOMPLISSEMENT (Le Monde)
Genre : pas indispensable — des mains plaçant la dernière pièce (ou un visage). Pose : la dernière pièce d'un puzzle se pose à l'emplacement du troisième œil.
Osho : dernière pièce d'un puzzle mise en place · position du troisième œil (perception intérieure) · l'image entière enfin révélée · fins et recommencements.
Rider (appoint) : couronne/guirlande, totalité, danse d'achèvement.
Fond : puzzle complété formant une image entière/mandala, emplacement du troisième œil lumineux.

### XXII · LE MAÎTRE (hors cycle, sans numéro)
Genre : un sage serein (à la présence lumineuse). Pose : présence rayonnante ; des disciples autour non pour le suivre mais pour s'imprégner de sa présence.
Osho : maître de LUI-MÊME (pas des autres) · chaque geste reflète l'éveil · dans ses yeux les autres trouvent leur propre vérité reflétée · silence · champ d'énergie · métaphore chenille→papillon (commentaire).
Rider (appoint) : aucun — carte propre à Osho ; carte-miroir de l'éveil.
Fond : aura lumineuse, quelques disciples/silhouettes en cercle, papillon(s) évoquant la métamorphose.

---

## 6. CE QU'IL RESTE À FAIRE (pour l'exécutant en Sonnet)
Pour chaque carte de §5 : rédiger le **PROMPT positif EN** en suivant §2 + §4 (gold standard), en terminant par l'ANCRE DE STYLE, et le **texte de lecture FR** (esprit Align : clair, non-fataliste, tutoiement). Livrer dans un fichier `_distillation/osho_tarot_PROMPTS_majeurs.md`. Ne PAS écrire les 4 familles tant que les majeurs ne sont pas validés visuellement.
