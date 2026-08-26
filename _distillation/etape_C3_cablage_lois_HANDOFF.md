# Handoff pour Opus — C.3 : câbler lois.json (Cap → loi prioritaire)

> Reconnaissance faite par Sonnet (lecture seule, aucun code moteur touché). Ce document
> donne à Opus une carte précise et les options de point d'affichage, pour que Martin tranche.
> **La décision d'architecture (où afficher, une loi ou plusieurs) revient à Martin + Opus.**

## Ce qui est déjà en place (rien à recâbler côté données)
- `data/corpus/lois.json` : 17 lois (`nom` / `en_un_mot` / `le_principe` / `le_pas`) + `_routage`
  (base de Cap 1-9 → 2-3 slugs de loi). Validé (langage clair, anti-plagiat, intégrité routage).
- **Le corpus est déjà chargé** : `moteur/corpus.py::Corpus` fait un glob de tous les `*.json`.
  Donc `corpus.lire("lois", "flexibilite", "le_principe")` fonctionne déjà, sans modifier le
  chargeur. Le `_routage` se lit via `corpus.lire("lois", "_routage", "1")` → `["action", ...]`.
  ⚠️ vérifier : `Corpus.lire` s'arrête aux clés `_...` ? Non — `lire` descend par `noeud.get(str(cle))`,
  et `_routage` est une clé normale du dict `lois`. Seul le CHARGEMENT ignore les `_` (axes fusionnés).
  À confirmer par un test rapide au REPL avant de coder.
- Le Cap est déjà calculé partout : `from moteur.numerologie import cap as cap_de` (app.py:42),
  et `cap_de(jour, mois, annee)["base"]` donne la base 1-9 (voir app.py:946 `cap_de(...)["valeur"]`).
  ⚠️ Router sur `["base"]` (1-9), PAS sur `["valeur"]` (qui peut être un maître 11/22/33). Le
  `_note` de lois.json le dit : les maîtres héritent du routage de leur base réduite. Vérifier que
  `cap["base"]` est bien toujours dans 1-9 (c'est `reduire_total`, donc oui).

## La couture d'affichage — DEUX options, à trancher par Martin

### Option 1 (recommandée) — dans le PORTRAIT, sous le Cap
`app.py::api_portrait` (ligne 818) assemble déjà `textes.cap = _texte_nombre(nb, "cap")`.
Une loi (ou 2-3) est un **levier stable attaché au but de vie** — c'est conceptuellement une
extension du Cap, pas un contenu qui varie chaque jour. Insertion naturelle : ajouter dans le
dict `textes` une clé `lois` = la ou les lois routées par `nb["cap"]["base"]`.
- Pour : cohérent avec le sens (levier de fond), déterministe et stable, aucune logique de
  rotation à écrire, se pose à côté de cap/voix/foyer/elan.
- Contre : le portrait est déjà dense ; à voir si Martin veut 1 loi (la première du routage) ou
  les 2-3. Recommandation Sonnet : **la première loi seulement** dans le portrait (la plus
  prioritaire), avec les autres en réserve pour une V2.
- ⚠️ Ce chemin existe en DEUX branches : `complet: False` (ligne 841) et `complet: True`
  (ligne 892). Le Cap est calculé dans les deux (`nb`). La loi doit être servie dans les DEUX,
  sinon un profil sans heure de naissance n'a pas ses lois (or elles ne dépendent que de la date).

### Option 2 — comme « loi du jour » dans le FIL (`api_jour`, ligne 1716)
Une loi rotative, une par jour, servie avec le conseil du jour.
- Pour : renouvelle le contenu quotidien, colle à l'esprit « levier du jour » du brief.
- Contre : demande une règle de rotation DÉTERMINISTE (jamais de tirage — charte). Piste :
  indexer par le jour de l'année parmi les lois routées du Cap, ou parmi les 17. C'est une
  décision de conception (quelle rotation ?) qui mérite Opus + l'avis de Martin.
- ⚠️ Le fil a déjà sa mécanique de sélection (`routeur.router_du_jour`, `_titre_du_jour`). Ne
  pas la percuter : la loi du jour serait un bloc ADDITIF, pas un remplacement du conseil.

## Plomberie suggérée (à valider par Opus)
1. Une petite fonction, ex. `app.py::_lois_du_cap(base)` → lit `corpus.lire("lois", "_routage", str(base))`,
   puis résout chaque slug en `{slug, nom, en_un_mot, le_principe, le_pas}`. Trou de corpus =
   liste vide (jamais d'exception), comme partout ailleurs.
2. Brancher dans l'option retenue.
3. Front : `templates/index.html` — un bloc d'affichage (constantes de libellé, cf. LBL_MIROIR /
   LBL_PAS déjà en place pour le fil). Décider un libellé écran (« Ton levier » ? « Ta loi
   d'appui » ?) — dans le vocabulaire d'Align, à trancher avec Martin.
4. Test : `tests/test_lois_corpus.py` couvre déjà le corpus. Ajouter un test d'INTÉGRATION léger
   (le portrait/jour sert bien une loi cohérente avec la base du Cap) selon l'option retenue.

## Rappels de garde-fous
- Zéro LLM au runtime : on LIT lois.json, on ne génère rien.
- Additif, jamais multiplicatif : router sur le seul Cap (base 1-9). Pas de matrice.
- Langage clair déjà tenu dans le corpus ; le libellé écran doit l'être aussi.
- Ne pas décider seul du point d'affichage : c'est l'appel de Martin (le brief le réserve).
