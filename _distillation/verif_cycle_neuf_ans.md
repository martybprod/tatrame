# Vérification — le cycle de neuf ans (Livrable A, brief Millman étape B)

> Constat de départ confirmé : le cycle de neuf ans de Millman est déjà intégré dans
> `data/corpus/annees_detail.json` (`annee_perso.1` à `.9`, champ `la_place_dans_le_cycle` +
> `en_un_mot` + `resume` + `ce_qui_arrive_souvent`), déjà dans la voix d'Align (l'escalier à
> neuf marches : ouvrir, mûrir, montrer, construire, respirer, s'engager, regarder, récolter,
> finir). **Aucun nouveau champ ajouté.** Cette note vérifie l'exactitude et la distinction de
> chaque marche, sans y toucher — retouche uniquement si nécessaire.

> Mesure de style (contrôle direct, `test_style.mesures()`, sandbox pytest indisponible mais
> import direct du module) : 873 phrases, **0 tiret cadratin, 0 deux-points, 2,2 % de phrases
> longues** (cible < 12 %), 0,23 % d'abstrait en sujet (cible < 3 %), 0 % de « Ce n'est pas… ».
> Le fichier est déjà propre sur toute la ligne — confirmé, pas de retouche de style requise.

---

## Grille de lecture

Phase de Millman (carte, concept 59) comparée à l'entrée d'Align (`en_un_mot` + logique de
`resume`/`ce_qui_arrive_souvent`/`la_place_dans_le_cycle`).

| An | Millman | Align (`en_un_mot`) | Verdict |
|---|---|---|---|
| 1 | semer — nouveau départ, rien de visible | **le départ** — « ouvrir avant d'avoir la preuve » | **conforme**, correspondance directe |
| 2 | coopérer — la graine a besoin d'aide extérieure (soleil, terre, eau) | **l'attente à deux** — les autres deviennent centraux, on n'est pas aux commandes | **conforme**, même logique (dépendance à l'extérieur) exprimée en registre relationnel plutôt qu'agricole |
| 3 | croître — la pousse perce, vulnérabilité, doute, « en suis-je capable ? » | **être vu** — visibilité, éparpillement, écart entre l'image et le dedans (« on te trouve en forme pendant que tu te sens creux ») | **conforme**, la vulnérabilité de Millman survit sous une autre image (l'écart image/dedans) |
| 4 | s'enraciner — racines profondes, travail de fond, peu de croissance visible | **le travail** — factures, corps, papiers ; « la seule année du cycle qui n'offre rien à raconter » | **conforme**, correspondance forte et quasi littérale sur le fond (travail invisible) |
| 5 | fleurir — l'arbre attire la vie, opportunités, célébration | **le mouvement** — le cadre serre, envie de rupture, le corps parle | **à noter** (non bloquant) — voir ci-dessous |
| 6 | donner — partager la récolte, générosité, vue d'ensemble | **les liens** — choix de loyauté, engagements qui deviennent exigibles | **à noter** (non bloquant) — voir ci-dessous |
| 7 | gratitude — ralentir, regarder les six années passées, tirer les leçons | **le ralenti** — retrait, remise en question, besoin de comprendre | **conforme**, correspondance forte |
| 8 | récolter — récompenses proportionnées au travail des années précédentes | **les résultats** — « la 8 ne fait qu'additionner ce qui existe » | **conforme**, correspondance quasi littérale |
| 9 | achever — clore, retourner la terre, préparer le prochain cycle | **le dernier tour** — tri, départs discrets, libérer la place pour la 1 suivante | **conforme**, correspondance forte (« faire le tri » = « retourner la terre ») |

## Les deux « à noter »

**Année 5** — Millman filme un arbre en fleurs, une année de récolte précoce et de fête.
Align raconte l'inverse : un cadre qui devient trop étroit, une pulsion de rupture. Ce n'est
**pas une erreur** : Align a choisi d'accorder l'année-charnière du cycle à l'énergie de
**base** du chiffre 5 chez Millman lui-même (« Liberté et Discipline », voir carte section C) —
plutôt qu'à sa métaphore agricole du cycle. Le résultat reste cohérent avec la logique globale
(« la 5 est la charnière, l'étroitesse est le prix du travail de la 4 ») et distinct de ses
voisines. C'est une divergence assumée et réussie, pas un défaut — exactement ce que demande
la charte (« son vocabulaire, jamais ses textes »).

**Année 6** — Millman parle de partage généreux d'une abondance déjà là. Align parle
d'obligations relationnelles qui se resserrent (« on ne discute plus, on tient ou on ne tient
pas »). Angle différent (donner par abondance vs. décider à qui on reste loyal), mais les deux
restent dans le même territoire (les liens aux autres), et l'entrée d'Align est plus incarnée,
plus « à voix haute » que la version-source. Aucune correction nécessaire.

## Verdict global

**Les 9 années sont conformes.** Aucune modification apportée à `annees_detail.json`. Les
deux nuances relevées (5 et 6) sont des choix éditoriaux d'Align cohérents avec l'esprit du
système (potentiel + libre arbitre, non fataliste) et ne trahissent pas la structure de
Millman — elles l'habillent dans le vocabulaire propre d'Align, comme l'exige la charte.
Bonus : les 9 marches restent nettement distinctes les unes des autres (aucune paraphrase
détectée d'une année à l'autre).
