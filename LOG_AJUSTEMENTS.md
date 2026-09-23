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