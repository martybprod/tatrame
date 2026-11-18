# Journal des ajustements — Ta Trame (Align)

> Référentiel durable des **demandes d'ajustement**, tous domaines confondus.
> Créé le 2026-09-20 (proposé par Martin, validé en session) : avant, les ajustements
> partaient dans la mémoire de session, le CHANGELOG ou les commits git — et se perdaient
> (ex. la mémoire `ginette-lectrice-cible.md` d'origine, évanouie).
>
> **Workflow (à suivre à chaque demande — sinon elle se reperd) :**
> 1. Toute demande d'ajustement (langage clair, image locale, autre) est **consignée
>    ici le jour même** : date, domaine, demande, décision, statut.
> 2. Si elle change la façon de faire, elle est **remontée dans le guide** (CHARTE.md /
>    RELECTURE.md / skill concerné).
> 3. Entrée **résumée dans CHANGELOG.md** (racine PROJETS_IA) à la fin de la session.
> 4. Si le projet est sous git (cas d'un agent autonome), un **commit** référence l'entrée.
>
> Domaine **image locale (Draw Things)** : journal seul tant que la difficulté actuelle
> n'est pas résolue — pas de skill dédié avant stabilisation (décision 2026-09-20).

## 2026-09-20 — Langage clair : consolidation de la passe Ginette

- **Demande** : consolider les ajustements « langage clair » / « Pense à Ginette »
  accumulés depuis août dans un guide durable + recréer la mémoire de lectrice-cible perdue.
- **Décision** : audit des commits git (mineurs + transits, 31/08 → 01/09) ; consolidation
  dans CHARTE.md (§ les leçons de la passe), RELECTURE.md (§3), recréation de
  `ginette-lectrice-cible.md`, création du skill `langage-clair` (méthode + filet, multi-projets).
- **Sources** : commits `b8785b8` → `d40e906` (passe Ginette), `1379fc7` (abus
  « on t'a appris à… »), briefs RETONE_*, CHANGELOG 2026-08-27…30.
- **Statut** : livré le jour même.

## 2026-09-20 — Image locale (Draw Things) : consignation seule

- **Demande** (Martin) : les difficultés actuelles en création d'image avec un modèle
  local — « consigner, c'est tout, d'accord de ne pas faire un skill tant que ce n'est pas résolu ».
- **Décision** : journal seul. Piste B différée jusqu'à résolution de la difficulté courante.
- **Contexte** : module Atelier visuel (Assistant Roman, porté dans Élisabeth, CHANGELOG 286),
  Draw Things port auto-détecté 7860, presets + file FIFO + ControlNet ; génération des cartes
  tarot par modèle local (seeds 777142-144 dans `_distillation/`, modèles Mucha/Art Nouveau/
  flux-dev dans `PROJETS_IA/DrawThings/`, packs `PACKS/`).
- **Statut** : ouvert — à compléter à chaque demande.

## 2026-09-23 — UX Le Jour : sortie du message plein écran + mémoire des cartes retournées

- **Demande** (Martin, retours de testeuses) : (1) à l'ouverture de l'app, le message du
  jour en plein écran se fermait au premier toucher — celles qui scrollaient pour voir si
  le message avait une suite perdaient la vue du message ; (2) les cartes du jour
  retournées reprenaient leur dos à chaque redémarrage de l'app dans la même journée.
- **Décision** : (1) sortie du plein écran accueil par le **✕ en haut à droite, un clic
  dans le fond (hors panneau) ou Échap** — le même mode que carte-plein/angle-plein ;
  plus aucun fermeture au clic/touchend sur le panneau, qui est devenu scrollable
  (`max-height` + `overflow-y`) ; l'indice « touche pour continuer » retiré. (2) état
  `.revelee` des trois cartes du jour **mémorisé pour la journée** (localStorage
  `trame.cartes.revelees`, clé = date SERVEUR `j.date` posée en `data-jour`) et
  réappliqué au rendu — un redémarrage le même jour garde les faces visibles, un
  nouveau jour rend les dos. (3) le mode test `ACCUEIL_TEST_TOUJOURS` (accueil montré
  à CHAQUE chargement, 2026-08-22) est **repassé à `false` le jour même, décision de
  Martin** : le message revient une fois par moment (jour OU soir — `cleAccueil`).
- **Vérifié** : suite pytest verte (759) + parcours navigateur complet (ouverture, clic
  panneau ne ferme plus, ✕ ferme, fond ferme, carte retournée → rechargement → face
  conservée ; accueil montré une seule fois, plus au rechargement du même moment,
  « À méditer » restant un moment distinct le soir).
- **Statut** : livré le jour même.

## 2026-09-23 — Couleur du cartouche tarot : or éclairci d'un cran

- **Demande** (Martin) : le cartouche (le médaillon doré qui entoure le disque des numéros)
  est « parfait, mais très légèrement trop foncé ».
- **Décision** : l'or des lignes `ORN_LINE` passe de `(200,162,78)` à **`(219,181,101)`** —
  même teinte jaune brun, ~+6 % de luminosité (nuance « B » choisie sur un aperçu de
  3 candidats). Corrigé dans `_distillation/_composer_cartouches.py` (+ `_tint_ornements.py`
  pour les maquettes HTML). Le disque, le cerne foncé et le nom ne changent pas.
- **Déployé** : 37 cartes recomposées dans les 2 thèmes ; les 22 majeurs du thème **clair**
  repassés en `static/cartes/NN.jpg` (800×1388, BICUBIC, q82 — la recette documentée) +
  miniatures WebP régénérées. **Art intact** : l'écart avec les cartes précédentes est
  confiné aux lignes d'or (0,03-0,18 % des pixels), le reste est identique.
- **Notes** : `_distillation/` (composeur + images sources) n'est PAS versionné (hors
  dépôt de l'app) ; seul le jpg déployé l'est. « L'Éveil » (major_22) n'est pas servi par
  l'app (arcanes 0-21) — non déployé. Les mineures de l'app restent les cartes classiques
  (sans cartouche de ce jeu).
- **Statut** : livré le jour même.

## 2026-09-23 — Le Jour : aperçu de la première phrase sous le titre « Aujourd'hui »

- **Demande** (Martin) : la carte-entrée « Aujourd'hui » ne montre que le titre ; ajouter
  en dessous la **première phrase du message**, pour donner un avant-goût avant d'appuyer.
- **Décision** : la carte affiche désormais un aperçu (`premierePhrase(titre.miroir)`),
  sous le titre et, s'il y en a un, sous le sous-titre de la voix. Nouvelle fonction
  `premierePhrase` (découpe au premier `. ! ? …` suivi d'une espace ou de la fin) et
  classe CSS `.carte-jour-hero--entree .apercu-message` (serif 16,5 px, encre2).
- **⚠️ Étape suivante (à faire)** : **vérifier que la première phrase de CHAQUE message
  est autonome et appropriée** — elle est maintenant lue **seule, hors contexte**, en
  aperçu (elle doit se tenir sans la suite du miroir). Passe à planifier sur l'ensemble
  du corpus des titres (ciel / chinois / numéro / lune).
- **Statut** : livré le jour même ; la vérification des premières phrases reste ouverte.

## 2026-09-29 — Plein écran carte du jour : le calcul passe en tiroir replié

- **Demande** (Martin) : (1) ne plus afficher directement l'explication du calcul des
  cartes du jour — un tiroir replié « Le calcul » à la place ; (2) la phrase du
  « pouls du monde » (« Le même calcul que ta carte de naissance, appliqué à la date
  du jour… ») n'était pas claire : on croyait qu'elle parlait de la carte de
  naissance, pas de la carte du jour.
- **Décision** : (1) dans la vue plein écran, la ligne `.carte-plein-cause` devient un
  `<details class="aide carte-plein-calcul">` replié « Le calcul » — remis fermé à
  chaque ouverture (même geste que la lecture). Seules les trois cartes du jour
  portaient une `cause` (carte de l'année et arcane de naissance n'en passent pas),
  donc les autres ouvertures plein écran ne changent pas. (2) La phrase devient :
  « Calculée sur la date du jour seule — comme une carte de naissance se calcule sur
  une date de naissance. Le monde entier la partage. » (le parallèle date → carte est
  explicite, le sujet reste la carte du jour).
- **Statut** : livré le jour même.

## 2026-09-27 — Carte IV · Liberté : texte recollé sur la nouvelle image validée (v33)

- **Demande** (Martin) : après refonte de l'image de la carte **IV · Liberté** (« le grand
  ciel à vol d'oiseau », validée v33), « regarde en profondeur les ajustements qu'il faut
  faire au message de la carte », puis « applique les ajustements ».
- **Décision** : passe de relecture (`RELECTURE.md` — le texte suit la carte). Corrections
  dans `data/corpus/arcanes.json` (entrée « 4 »), toutes tirées de l'image validée :
  - `lecture` : temple désormais **gréco-romain, au flanc d'une montagne, très lointain**,
    vu **de très haut** ; l'eau le **traverse** puis **s'élargit et prend toute la place
    en bas** ; **plaines** autour ; l'**aigle** s'en va **vu de dos** au centre du ciel.
    Retirés : les **têtes de bélier** et les **fleurs sauvages** (absentes de l'image),
    « éperon de roche », « frontons », « plusieurs cascades ».
  - `contrarie` : « **les colonnes tombées** de la carte » (au lieu des béliers de pierre),
    « figée en ruine », « attend **de l'espace** ».
  - `en_resonance` : « la brèche / le mur » supprimés → « Une seule sortie ouverte suffit ».
  - `invitation` : « le vieux **temple** se laisse traverser, et **la campagne** s'ouvre
    derrière » (les murs disparaissent).
  - `conditionnement` : « **Ce que tu maintiens** a été utile » (le « mur » retiré).
  - Filet : `tests/test_lectures.py` → `SYMBOLES_REQUIS[4]` = temple, colonnes, aigle,
    rivière, eau, montagnes, plaines, ciel (retirés : bélier, fleurs, lierre, soleil,
    cascades).
- **Sources** : `cartes_validees/CARTE_major_04_Liberte_validee.png` (v33) ;
  `_distillation/_gen_carte_Liberte_v33_validee.py` ; fiche image
  `osho_tarot_PROMPTS_majeurs.md` §IV.
- **Régénéré** : `TEXTES_22_ARCANES_MAJEURS.html` (`gen_fiches_cartes.py`) ; miroir
  `TEXTES_22_ARCANES_MAJEURS.md`. Suite pytest **verte** (764 passed, 11 skipped).
- **Statut** : livré le jour même.

## 2026-10-01 — Cartes « mod Martin » : maj 21 et eau 03 remises en app + textes recollés

- **Demande** (Martin) : deux cartes retouchées à la main à mettre en app — **maj 21 ·
  Accomplissement** et **eau 03 · Célébration** ; pour eau 03, « la modification a changé
  la saturation », à « remettre au même niveau qu'elle était précédemment » ; puis
  « réécris le texte correctement et pousse ».
- **Diagnostic** : les deux dépôts Draw Things portaient une **aberration** que Martin avait
  retirée sur ses photos — maj 21 : **deux papillons** (un de trop, à gauche) ; eau 03 :
  **un verre en trop**. Le texte de maj 21 dit « **un** papillon monarque… en haut du
  métier ».
- **Décision / travail** (reconstruit sans filigrane à partir des dépôts propres + régions
  corrigées des photos) :
  - **maj 21** : papillon en trop retiré + raccord de la robe. Master
    `cartes_validees/CARTE_major_21_Accomplissement_validee.png`.
  - **eau 03** : verre en trop retiré + **saturation au niveau précédent** (38,0 → 34,0 %,
    lum 139 → 140 ; cible v10 = 34,5/141). Master
    `cartes_validees/CARTE_eau_03_Celebration_validee.png`.
  - Anciennes validées archivées : `archives/…_AVANT_MOD_MARTIN_2026-10-01.png`.
  - **Textes recollés** : `arcanes.json` « 21 » (« Au centre du mandala s'allume une
    lumière dorée, juste là où elle travaille » au lieu du « rayon de soleil descend droit
    du ciel ») + filet `SYMBOLES_REQUIS[21]` (« rayon de soleil » → « lumière ») ;
    `corpus_mineurs_eau.json` eau_3 réécrit pour la version **statique** (plus de « pied
    levé » ; paniers portés ; celui du milieu lève son verre).
- **Déployé** : `static/cartes/21.jpg` et `static/cartes/mineurs/eau_3.jpg` (800×1388
  BICUBIC, q82) + miniatures WebP ; cartouches recomposés (41 cartes).
- **Outil** : `gen_fiches_cartes.py` rendu tolérant aux arcanes **sans `correspondance`**
  (l'arcane **22** ajouté par une autre session cassait la génération du HTML).
- **Sources image** : `IMG_20261001_194756(1).png` (maj 21) et
  `IMG_20261001_201037(1).png` (eau 03) = versions corrigées (photos).
- **Vérifs** : suite pytest **verte** (771 passed, 11 skipped) ; texte maj 21 recollé dans
  le HTML régénéré.
- **Statut** : livré et poussé le jour même.

## 2026-10-03 — RÈGLE : une seule image à la fois (et non trois)

- **Demande** (Martin) : « il faut vraiment que tu notes quelque part en gros et
  prioritaire que tu ne fais jamais trois cartes si je ne t'en donne pas expressément
  et explicitement la consigne. Ce que je voudrais, c'est que le personnage sur la
  nouvelle carte [saisisse] un coin en haut pour voir derrière. »
- **Contexte** : sur le 6 d'Eau · Illusion, trois tirages ont été produits à chaque
  itération (v1 « la toile », puis v2 « le coin tiré ») ; Martin n'en a retenu aucun
  et a arrêté la série.
- **Décision** : la règle est inscrite **en tête de `ASTRO_PLUS_APP/AGENTS.md`**
  (section « RÈGLE PRIORITAIRE — UNE IMAGE À LA FOIS »), donc chargée à chaque
  session. Une itération = une image ; trois seulement sur consigne expresse.
  La production des mineures reprend **une carte à la fois, un tirage à la fois**.
- **Statut** : règle inscrite le jour même.

## 2026-10-03 — 5 d'Eau · Attachement livrée · style d'origine rétabli · HTTP/LoRA

- **Demande** (Martin) : revenir au **style des premières cartes majeures**, « par
  souci de cohérence », puis « certains pas effacés par les vagues ».
- **Style** : le bloc des premières cartes est celui de `_gen_carte_Existence_v9_validee.py`
  (« large flat areas », « no realistic shading, no modelling of light and shadow »,
  « not a comic ») ; le bloc des cartes Eau en était une **version tronquée**.
  Rétabli, il ramène le trait et l'aplat. La variante faible (`_gen_carte.py`) ne suffit pas.
- **Découverte** : l'API HTTP **accepte et applique** la clé `loras` et remplace la pile
  de l'app (vérifié dans les métadonnées XMP du PNG). Le postulat « le HTTP subit les
  LoRA de l'app » était **faux** — une recette JSON est reproductible de bout en bout.
- **Master 5 d'Eau** : retouche haute résolution de Martin (6932×10399, graine d'origine
  779068, v15-C), réduite en 1024×1536 ; export et ancien master archivés ; fiche
  `_gen_carte_Attachement_v15C_validee.py`.
- **Organisation** : ancre `style_deck_origine` dans `_ancres.json` (le bloc ne se recopie
  plus), contrôle pré-vol `_verifier_recette.py`, LoRA déclarés, section 0 dans
  `ETAT_PRODUCTION_MINEURS.md`.
- **Textes** : les 5 textes Eau (as, 2, 3, 4, 5) sont conformes à la charte ; celui de la 2
  (Amitié) réécrit (il ne nommait qu'un symbole). Livraison des 14 Eau en bloc décidée.
- **Statut** : livré le jour même ; **non poussé**.
## 2026-11-17 — Le fil de lecture (repère « déjà lu » sur Tout / Le Portrait / Le Ciel)

- **Demande** (Martin) : « dans les sections tout, le portrait et le ciel, il y a
  beaucoup d'informations à lire… elle ne lira pas ça d'un coup. Il serait intéressant
  d'ajouter un repère visuel qui permet de savoir si l'utilisateur a déjà lu la
  section. Regarde les meilleures pratiques et fais-moi une proposition. »
- **Proposition** : maquette validée `maquettes/fil_de_lecture.html` (démo vivante,
  meilleures pratiques citées : défiler ≠ lire, reprise de lecture, progression à
  l'entrée, un indicateur par tâche, pas de gamification). « Le fil de lecture » :
  ① un **point de trame** par bloc (pointillé → plein, forme jamais couleur seule,
  bascule manuelle au doigt) ; ② une **ligne de reprise** en tête de section
  (« X fils sur Y · il reste ≈ N min · Reprendre à « … » » qui dépose au premier
  bloc non lu) ; ③ un **fil de 2 px** sous les onglets Tout / Le Portrait / Le Ciel.
- **Implémentation** : `templates/index.html` seulement — bloc CSS après les styles
  de nav, module JS `fil*` (~140 lignes vanilla, zéro réseau), `data-lu` stables sur
  les .carte des trois vues, appel `filInstaller()` à la fin des trois chargeurs.
  Marquage auto honnête : fin de bloc franchie (ou vu entier) + présence ≥ 2,5 s ;
  défiler en diagonale ne compte pas ; quitter l'onglet ne juge pas. Détissage
  manuel efface les preuves accumulées (sinon l'auto retisse aussitôt — bug vu
  en test, corrigé le jour même). Persistance : `localStorage` clé `trame.fil.<profil>`,
  versionnée par VSTAT (corpus qui change → fils remis en attente, même mécanique
  que le cache statique). Accessibilité : `aria-pressed` + libellés sur les points,
  fils `aria-hidden`, comptes en texte, `prefers-reduced-motion` respecté.
- **Le Jour exclu** : neuf chaque matin, rien à « reprendre ».
- **Validation** : pytest verte (840 passés) ; testé au navigateur sur profil
  d'essai `jeanne-fil` (tissage au scroll, ligne de reprise, reprise → dépôt au
  bloc, bascule manuelle dans les deux sens, persistance au rechargement).
- **Statut** : livré et **poussé** le jour même (`cf1a3b4`) — Coolify redéploie tatrame.ca.

## 2026-11-17 — Annonce « nouveau » sur l'onglet Tarot (10 jours)

- **Demande** (Martin) : « l'onglet tarot dans ta trame est un nouvel élément. Il est
  quand même discret donc j'aimerais que pour les 10 prochains jours, à l'ouverture
  de l'application quand on arrive au menu principal après avoir vu le message
  d'accueil s'il y a lieu, le bouton tarot soit mis en surbrillance avec affiché
  discrètement le mot "nouveau". Pendant quelques secondes. Regarde les meilleures
  pratiques avant de coder. »
- **Pratiques suivies** : étiquette d'UN mot (« nouveau ») — un badge bavard n'est
  plus un badge ; signal d'arrivée TRANSITOIRE (un « nouveau » permanent devient du
  bruit, donc quelques secondes puis tout s'efface, DOM nettoyé) ; jamais la couleur
  seule (le mot est le signal) ; contraste fort (or #d9b95c sur encre #141110, ~10:1) ;
  pulsation coupée en `prefers-reduced-motion` ; l'étiquette disparaît dès qu'on
  choisit l'onglet (une fois sélectionné, le « nouveau » n'a plus de sens) ; jamais
  de vol de focus ni d'annonce qui interrompt.
- **Implémentation** (`templates/index.html` seulement) : constantes
  `NOUVEAU_TAROT_DEBUT = '2026-11-17'` / `NOUVEAU_TAROT_JOURS = 10` (fenêtre locale :
  du 17 au 26 novembre inclus) ; `annoncerTarot()` gardé une fois par ouverture ;
  déclenché à DEUX moments — `demarrer()` quand aucun accueil n'a à montrer
  (`montrerAccueilJour()` renvoie false) et la fermeture de l'accueil du jour
  (`fermerAccueilJour` → `fini`) ; apparition en fondu (0,45 s), deux pulsations
  discrètes de l'anneau doré, pose ~4 s, fondu de sortie (0,9 s), puis retrait du
  DOM ; clic sur l'onglet = retrait immédiat.
- **Validation** : testé au navigateur sur les DEUX chemins (sans accueil : état
  `annonce-surbrillance` + nom accessible « Tarot NOUVEAU » vérifié ; avec accueil :
  l'annonce ne part qu'à la fermeture) ; disparition propre vérifiée (étiquette
  retirée, classes nettoyées). Suite pytest relancée.
- **Statut** : livré et **poussé** le jour même (`2056808`) — Coolify redéploie tatrame.ca.

## 2026-11-17 — Ops : le compte admin « martin-boucher » impossible à utiliser sur tatrame.ca

- **Demande** : « Le compte administrateur est Martin Boucher. Je devrais pouvoir m'y
  connecter depuis tatrame.ca, mais ce n'est pas possible — je dois à chaque fois me créer
  un nouveau compte et je n'ai pas mes accès administrateur. » (mot de passe voulu : « Merci »)
- **Diagnostic** : le profil `martin-boucher` existait en prod mais en **thème secondaire**
  du compte d'Arianne (créé sur un appareil où sa session était ouverte), avec deux doublons
  secondaires (`-14ebda`, dont le propriétaire n'existe plus ; `-b9dba1`, chez Arianne aussi).
  Aucun compte racine connectable au slug → `/api/connexion` 401 systématique,
  `COMPTE_ADMIN` indéverrouillable. Le CODE était correct — c'était l'état des données.
- **Correction** (données prod, accord explicite de Martin, backup préalable) : copie dans
  `data/profils/_sauvegarde-2026-11-17/` (sur le volume), `proprietaire` retiré de
  `martin-boucher.json` (redevient un compte racine, vraies données 6/4/1980 5 h), mot de
  passe « Merci » posé (PBKDF2 généré avec le Werkzeug du conteneur — même méthode épinglée
  que `auth.py`), doublons supprimés. Vérifié depuis l'extérieur : connexion OK + jeton admin
  (`/api/admin/jeton`) OK. Sans redémarrage (les profils sont relus du disque à chaque requête).
  Rappel du repli documenté : `/admin/commentaires` + `ADMIN_PASSWORD` (Coolify) depuis un
  appareil non connecté.
- **Statut** : résolu le jour même.

## 2026-11-17 — Créer un profil pendant qu'un compte est ouvert : confirmation avant le rattachement

- **Demande** (sur proposition de l'agent après le diagnostic ops, accord de Martin :
  « point 2, oui go ») : le rattachement silencieux en thème secondaire (décision assumée
  « le thème de ma fille ») a enfermé trois fois « martin-boucher » chez d'autres comptes —
  ne plus jamais le faire en silence.
- **Décision** (`templates/index.html`, aucun changement d'API) : note dès l'ouverture du
  formulaire quand un compte est actif (« Tu es connecté à « X » : le profil créé ici
  deviendra un thème de ce compte, pas un nouveau compte… ») + confirmation en DEUX temps
  avant le POST (premier clic arme « Confirmer — créer le thème » + message « Petit moment
  important… », deuxième crée). Commentaire synchronisé côté serveur (`api_creer_profil`).
- **Validation** : suite pytest verte (840) ; parcours réel au navigateur (premier clic
  sans création, deuxième avec rattachement, profils de test supprimés ensuite).
- **Statut** : livré et poussé le jour même (`9b54477`).

## 2026-11-17 — Tableau de bord : ajouter le Tarot aux données d'utilisation

- **Demande** : « dans le tableau de bord, je ne vois pas la section tarot dans les données
  d'utilisation, il faut l'ajouter ».
- **Diagnostic** : plus large que le Tarot — AUCUN clic d'onglet n'était journalisé : le
  handler `#nav` appelait `montrer()` sans passer par `montrerVue()` (seul à envoyer
  l'événement `nav` à `/api/activite`). En prod : `nav:jour` 1239 (gonflé par les
  démarrages), `nav:tarot`/`nav:apercu`/`nav:relations` 0 — « Sections les plus visitées »
  ne comptait que les sauts programmatiques (liens du fil, « À méditer ») et le jour de
  démarrage.
- **Décision** : le handler `#nav` passe par `montrerVue()` (même bascule d'état, un
  événement de plus) ; « tarot » rejoint `_LIBELLES_VUE` ; 3 tests
  (`tests/test_tableau_bord.py`) verrouillent les deux bouts (journal → synthèse → libellé).
- **Limites** : les comptages historiques restent biaisés (les événements manquants ne se
  rattrapent pas) ; la justesse repart du déploiement.
- **Pièges documentés au passage** : le service worker sert la racine en
  **stale-while-revalidate** — après un déploiement, le PREMIER chargement exécute encore
  l'ancien JS (le frais part en arrière-plan), le deuxième voit le nouveau : pour tester un
  changement local, recharger DEUX fois. Et l'app locale (`debug=False`) met les templates
  en cache : relancer l'app après chaque édition de `templates/`.
- **Statut** : livré et poussé le jour même (`72bfef3`) — 843 tests verts.

## 2026-11-17 — Le Jour : les pilules des cartes du jour ouvrent le sens de leur place

- **Demande** (Martin) : dans « Le Jour », cliquer sur les pilules « Le pouls du monde »,
  « Ton arcane du jour », « Ta couleur du jour » doit ouvrir une petite carte qui explique
  la signification de la place de cette carte dans le trio — « un peu comme dans la
  section Tarot » (le détail d'une position du tirage).
- **Décision** (`templates/index.html`) : la pilule devient cliquable (`.carte-jour-place`,
  role button + clavier Enter/Espace, `stopPropagation` — la pilule ne dévoile PAS la
  carte, le clic sur l'image ouvre toujours le plein écran) et ouvre `#angle-plein` via
  `ouvrirPlaceCarteJour()` — le même plein écran que les autres angles du jour, pas un
  nouveau mécanisme d'overlay. **Version courte (retour Martin dans la foulée) : UN seul
  texte par place** — ce qu'elle apporte aujourd'hui dans le trio, sans le calcul (ça
  reste dans le plein écran de la carte et l'aide « Trois cartes, pourquoi ? »), avec un
  mot sur les deux autres pour les situer. Textes dans `PLACES_CARTES_JOUR`.
- **Textes** : version courte d'abord rédigée par l'agent (27-37 mots, conformes), puis
  **reformulés par Martin le jour même et remplacés VERBATIM** (40-41 mots). Validation
  de sa version : aucun interdit, aucun chevauchement de 8 mots avec le corpus ; le
  validateur signale seulement les deux-points de « Ta couleur du jour » (1 sur 3
  phrases, cible < 10 pour 100) — gardés tels quels, décision Martin de garder sa
  formulation.
- **Piège au passage** : `pkill -f ASTRO_PLUS_APP/app.py` ne matche pas — le process
  s'appelle `…/Python app.py` (run.sh fait `exec ./venv/bin/python app.py`). Tuer via
  `lsof -nP -iTCP:5073 -sTCP:LISTEN` puis `kill <PID>`, sinon le vieux serveur garde le
  port et sert l'ancien template en cache.
- **Validation** : suite pytest verte (843) ; parcours réel au navigateur mobile — les
  trois pilules ouvrent leur carte, la pilule ne retourne pas le dos, le clic sur
  l'image ouvre toujours la visionneuse.
- **Statut** : version 3 blocs poussée le jour même (`b5e9212`, déployée) — remplacée le
  jour même par la version courte avec les textes reformulés par Martin, poussée en suite
  de session.

## 2026-11-18 — Le Jour : les chevrons d'ouverture reviennent, tournés à droite

- **Demande** (Martin) : réintégrer une indication visuelle sur les cartes qui offrent
  plus d'information (« Aujourd'hui », « La Lune aujourd'hui », les angles) — retirée
  avec les ⤢ le 2026-09-15 (`ee6dcaa`). Mais PAS le chevron ⌄ (déjà pris par les
  tiroirs « ça se déplie ici ») : le même chevron pointant vers la DROITE.
- **Décision** (`templates/index.html`) : nouvelle classe `.chev-plein` — le MÊME ⌄ que
  `.tiroir-chev`, `rotate(-90deg)`, même couleur/size (accent-doux, 18px). Deux sens
  fixes, un par geste : ⌄ = se déplie ici (tiroirs, Fil du jour, fond du temps),
  › = s'ouvre en grand (plein écran). Posé sur : les rangées d'angles (`angleCarte`),
  la carte « Aujourd'hui » (coin droit, absolu), l'en-tête date/Lune (quand la phase
  est ouvrable). PAS sur les tuiles du Fil du jour (grille dense, surcharge — décision
  2026-08-24 inchangée). Correctif au passage : `.rangee-angle .tete` passe à
  `flex:1;min-width:0` — sans quoi le chevron colle au texte quand le résumé est court
  (« À méditer »), au lieu d'être calé au bord droit.
- **Validation** : suite pytest verte (843) ; vérifié au navigateur mobile — les trois
  angles, « Aujourd'hui » et l'en-tête portent le ›, Fil du jour et fond du temps
  gardent leur ⌄, calage à droite OK même sur résumé court.
- **Piège du passage** : le service worker (stale-while-revalidate) a servi l'ancien
  document après DEUX rechargements — un `?v=…` frais dans l'URL contourne son cache
  pour tester un changement local.
- **Statut** : livré le jour même — en attente du feu de Martin pour commit/push.
