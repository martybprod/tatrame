# Prompt pour Sonnet — Enrichir « Le Fil du jour » (couche coaching d'Align / Ta Trame)

> **Tu es Claude Sonnet.** Ta tâche : AJOUTER des perles au corpus `data/corpus/fil.json`
> de l'app « Ta Trame » (ex-Align), sans toucher à l'existant. Tu ne codes rien, tu
> **rédiges** — le moteur est déjà écrit et lit ces textes par clés. Travaille **un domaine
> à la fois** (12 domaines). Ce prompt est autoportant, mais tu DOIS lire les 4 fichiers
> listés au §0 avant d'écrire la moindre perle.

---

## 0. À lire AVANT d'écrire (obligatoire, dans cet ordre)

1. `_distillation/fil_du_jour_SPEC.md` — la spécification autoritaire (espace de noms des clés, schéma JSON, voix, tests). **Rien de ce que tu écris ne doit contredire cette spéc.**
2. `data/corpus/CHARTE.md` — la voix d'Align (recadrage en conditionnement, registre constatif, tics à tuer). Non négociable.
3. `_distillation/cartes_de_concepts.md` — les 24 ouvrages de coaching distillés en **concepts**. Tu rédiges À PARTIR de ces cartes, **jamais** à partir de la prose des livres.
4. **Les deux cartes « écriture claire »** (ta grille de qualité de langue, voir §5) :
   - `../STYLE_ECRITURE/_cartes_concepts/ecrire_pour_le_web_gani.md`
   - `../STYLE_ECRITURE/_cartes_concepts/oxford_guide_plain_english_cutts.md`
   - (leur synthèse : `../STYLE_ECRITURE/_cartes_concepts/INDEX.md`)

Puis **lis `data/corpus/fil.json` en entier** : c'est l'état actuel. Tu ne réécris jamais une
clé existante ; tu n'ajoutes que des clés nouvelles.

---

## 1. Le but précis (ce qu'« élargir » veut dire ici)

Le Fil du jour route par le ciel : **maison de la Lune = domaine** (12 domaines), puis
**transit dominant + phase lunaire = nuance**. Chaque domaine a déjà son socle (`{domaine}`),
sa tonalité (`{domaine}_fluide`, `{domaine}_tension`), et une partie de ses variantes de
transit. **La SPEC vise 25–35 perles par domaine.** Ton travail : pour chaque domaine, AJOUTER
les variantes de transit (et de phase, pour les 3 domaines à processus) **qui recolorent
vraiment le conseil** et ne sont pas encore écrites — jusqu'à approcher 35.

**Règle d'or, au-dessus de tout (SPEC §3) : on n'ajoute une variante QUE si la condition-ciel
change réellement le conseil.** Une variante arbitraire « pour faire du nombre » est un échec,
pas une réussite. Mieux vaut 28 perles justes que 35 dont 7 forcées. La couverture éparse est
un CHOIX de conception, pas un défaut à combler.

### Ce que tu N'as PAS à faire
- **Ne touche à aucun autre corpus.** (J'ai vérifié : le composite relationnel, les transits,
  le ciel, les nombres, les arcanes, la personologie — tout le reste est complet. Le moteur ne
  lit du composite que Soleil/Lune, déjà pleins ; y ajouter Vénus/Mars serait du texte jamais affiché.)
- Ne crée pas de nouveau domaine, ne renomme rien, ne modifie pas le moteur.

---

## 2. Où sont les trous, domaine par domaine (état actuel)

Voici, par domaine, les transits DÉJÀ écrits. Ta cible : compléter avec les **planètes
manquantes qui ont un sens pour ce domaine** (colonne « planètes à considérer »), en tonalités
fluide (conjonction / sextile-trigone) et tension (carré-opposition). Vérifie toujours dans
`fil.json` avant d'écrire — cette liste est un point de départ, pas la vérité finale.

| Domaine | Transits déjà là (compte) | Planètes à considérer en priorité (si elles recolorent) |
|---|---|---|
| `soi` (identité, valeur de soi) | ~23 | jupiter (expansion de soi), uranus (rupture d'image), neptune (flou d'identité) |
| `ressources` (argent, valeurs) | ~22 | neptune (rapport flou à l'argent), soleil (valeur affirmée) |
| `echanges` (mental, mots, focus) | ~19 | uranus (idée soudaine), neptune (brouillard mental), soleil, pluton (parole qui creuse) |
| `racines` (foyer, famille) | ~22 | jupiter (foyer qui s'agrandit), soleil (present au foyer) |
| `creation` (créativité, jeu) — **à processus** | ~18 + 8 phases | lune, jupiter, neptune (inspiration), uranus, pluton — compléter les paires manquantes |
| `quotidien` (habitudes, santé, sommeil) — **à processus** | ~20 + 8 phases | jupiter (excès/expansion), uranus (routine cassée), neptune (fatigue/flou), pluton |
| `autre` (couple, lien) | ~21 | soleil (present à l'autre), neptune (idéalisation), uranus (besoin d'air dans le lien) |
| `traversee` (crise, transformation, deuil, honte) | ~19 | mercure (mettre des mots), soleil, jupiter (sens qui s'ouvre) |
| `sens` (quête de sens, croyances) | ~22 | mars (agir selon ses valeurs), venus (beauté/gratitude) |
| `metier` (vocation, visibilité) — **à processus** | ~18 + 8 phases | pluton (pouvoir/emprise au travail), uranus (changement de cap), neptune (vocation floue) |
| `communaute` (amitiés, appartenance) | ~21 | soleil (visibilité dans le groupe), neptune, mercure (lien par les mots) |
| `retrait` (solitude, lâcher-prise, anxiété) | ~19 | jupiter (souffle intérieur), venus (douceur envers soi), lune |

**Domaines à processus (`creation`, `quotidien`, `metier`) uniquement** : les 8 phases lunaires
sont déjà écrites pour ces trois. N'ajoute PAS de clé `phase_*` ailleurs (interdit par la SPEC —
une phase de lune plaquée sur « argent » serait arbitraire).

Ordre de travail suggéré (du plus porteur au plus lean) : `autre`, `traversee`, `metier`,
`creation`, `soi`, `retrait`, `sens`, `quotidien`, `echanges`, `racines`, `communaute`, `ressources`.

---

## 3. Format EXACT de chaque perle (SPEC §3–4 — à respecter au caractère près)

Clés à écrire, à plat dans `fil.json`, motif :
```
{domaine}_transit_{planete}_{classe}
```
- `{planete}` ∈ soleil, lune, mercure, venus, mars, jupiter, saturne, uranus, neptune, pluton
- `{classe}` ∈ conjonction, carre-opposition, sextile-trigone  (⚠️ `carre-opposition` avec un trait d'union, sans accent)

Chaque entrée :
```json
"autre_transit_neptune_carre-opposition": {
  "source_livre": "d'après les concepts de Levine & Heller — l'attachement",
  "themes": ["amour", "idealisation"],
  "miroir": "…une phrase, présent, ce qui se joue…",
  "geste": "…une action concrète, petite, faisable aujourd'hui…"
}
```
- `source_livre` : attribution honnête « d'après les concepts de … » — jamais un titre de méthode/marque présenté comme officiel.
- `themes` : 2–3 tags courts (servent aux tests de variété). Varie-les : ne réutilise pas le même tag partout dans un domaine.
- `miroir` + `geste` : **30–85 mots au total** (registre « jour »). Vise le milieu (~50), pas la borne.

---

## 4. La VOIX d'Align (CHARTE + SPEC §5) — non négociable

1. **Recadrer en conditionnement, jamais en faute** : constat → normalisation → déculpabilisation. Le lecteur n'a rien à se reprocher.
2. **Désigner le système/le mécanisme, pas l'individu.**
3. **Registre CONSTATIF** : « Tu es en train de… » ✅ · « Tu es… » ❌ (essentialisation) · « Tu vas… / tu rencontreras… » ❌ (prédiction — Align ne prédit JAMAIS).
4. **Tutoiement**, chaleureux — un ami lucide, pas un oracle ni un coach de performance.
5. **UNE chute par entrée, pas par phrase.** Le reste est plat, parlé, simple.
6. **Tics à tuer** : concept abstrait en sujet de phrase · chute posée sur un tiret cadratin · deux-points « aphoristique » · ouverture sur « Ce n'est pas… ».
7. **Le geste est CONCRET** : faisable en 10 minutes aujourd'hui. Proscrits : « ouvre-toi à l'inattendu », « lâche prise », « fais confiance à l'univers », « écoute ton cœur », « sois toi-même » — ce ne sont pas des gestes.
8. **Test à voix haute** : ça doit sonner comme quelqu'un qui te PARLE, pas qui écrit.

---

## 5. « Texte clair » — ta grille de qualité de langue (les 9 règles d'or)

C'est la demande explicite de Martin : applique **parfaitement** les principes d'écriture claire
distillés dans les deux cartes STYLE_ECRITURE. Lis-les en entier (§0.4). En voici la synthèse,
**adaptée au micro-format d'une perle** (2 phrases, pas un article) :

1. **Un lecteur précis, jamais « pour tous ».** La personne qui lit vit CE domaine aujourd'hui. Parle-lui à elle.
2. **L'essentiel d'abord.** Le `miroir` dit tout de suite ce qui se joue (pas de mise en bouche). Le `geste` commence par un **verbe d'action**.
3. **La concision est un service.** Chaque mot gagne sa place. Coupe les adverbes mous, les « un peu », « peut-être », « en quelque sorte », les redites. Phrases courtes.
4. **Les mots du lecteur, pas le jargon.** Zéro terme d'astrologie ou de psycho savante dans la perle (« transit », « carré », « attachement évitant » → dis-le en mots courants). Âge de lecture ~13 ans : compréhensible par tous.
5. **Phrases brèves.** Vise 12–18 mots par phrase. Une idée par phrase.
6. **Concret plutôt qu'abstrait.** Une image tangible bat un concept. « Range une seule chose » bat « instaure de l'ordre ».
7. **Voix active, verbes forts.** « Dis-lui » bat « il faudrait que ce soit dit ». Sujet qui agit + verbe plein.
8. **Rythme parlé.** Lis à voix haute : si tu bloques, c'est trop écrit. Vire les tournures administratives et les liaisons lourdes (« par conséquent », « néanmoins », « il convient de »).
9. **Zéro faute, zéro coquille.** Une erreur ruine la confiance. Relis chaque perle avant de la valider.

> Note d'articulation : la CHARTE (§4) régit le TON et l'éthique (constatif, déculpabilisant,
> pas de prédiction) ; les règles « texte clair » régissent la LANGUE (brièveté, concret, mots
> simples). Les deux se renforcent. En cas de doute, la CHARTE prime sur le style, mais un texte
> clair est presque toujours aussi un texte conforme à la charte.

---

## 6. Discipline droit d'auteur (commercialisation — obligatoire)

- Tu reprends les **idées/concepts**, **jamais la prose**. Zéro citation, même courte.
- Tu rédiges à partir des **cartes de concepts**, pas des textes sources. Les `_distillation/sources/*.txt` ne servent qu'au test anti-plagiat.
- **Aucun nom de méthode/marque** des livres (« Atomic Habits », « 5 langages de l'amour », « règle des 2 minutes » comme label…). Exprime tout en langage courant, dans le vocabulaire d'Align.

---

## 7. Contraintes de test (ton texte DOIT les passer — `tests/test_fil.py`)

Avant de livrer un domaine, auto-vérifie :
1. **Anti-plagiat** : aucune suite de 7 mots (normalisée : minuscules, sans accents, sans ponctuation) d'une de tes perles n'apparaît dans un `_distillation/sources/*.txt`. Aucune suite de 5 mots ne différant que par des mots-outils.
2. **Style** : tirets cadratins « — » < 8 pour 100 phrases ; deux-points < 10 / 100 ; ouverture sur concept abstrait < 3 / 100 ; ouverture « Ce n'est pas… » < 2 / 100.
3. **Variété** : aucune ouverture (5 premiers mots) ne se répète d'une perle à l'autre ; **aucune suite de 8 mots partagée entre deux perles** (ni avec l'existant) ; tags `themes` non concentrés sur une seule valeur.
4. **Structure** : `miroir` + `geste` non vides ; 30–85 mots ; clé conforme au motif du §3 (domaine connu, planète/classe valides) ; `source_livre` présent.
5. **Couverture** : ne casse pas l'existant (chaque domaine garde sa clé générique).

⚠️ Le point de variété est le plus exigeant : tu écris À CÔTÉ de perles existantes. Avant
d'écrire une perle, balaie mentalement les perles déjà présentes du même domaine pour ne
répéter ni une ouverture, ni une image, ni une suite de mots.

---

## 8. Livrable et méthode

- Travaille **un domaine par lot**. Pour chaque lot : lis les sections du domaine dans
  `cartes_de_concepts.md` (colonne « livres sources » du tableau de la SPEC §1), puis rédige.
- Rends les nouvelles clés **prêtes à fusionner dans `fil.json`** (mêmes conventions, à plat,
  indentation 1 espace comme le fichier existant). N'inclus PAS les clés déjà présentes.
- Termine chaque lot par une **auto-revue** explicite contre les §4, §5, §7 : liste ce que tu
  as vérifié (longueurs, ouvertures uniques, gestes concrets, zéro jargon, zéro prédiction).
- Si une variante que tu envisageais ne recolore pas vraiment le domaine, **écris-le et ne la
  crée pas** — c'est un bon réflexe, pas un manque.

Commence par confirmer que tu as lu les 4 fichiers du §0, puis attaque le domaine `autre`.
