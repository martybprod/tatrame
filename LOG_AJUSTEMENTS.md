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