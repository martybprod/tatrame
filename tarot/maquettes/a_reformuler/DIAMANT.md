# Le Diamant — textes à reformuler

Le petit tirage en croix du Tarot Zen d'Osho (« The Diamond ») : cinq cartes, l'issue au centre, les deux influences à gauche et à droite, ce qu'il faut pour dénouer en bas, la résolution au sommet.

C'est déjà **câblé et jouable** (onglet « Le Diamant », `/api/tirage?mode=5`) : chaque position lit un champ qui existe dans les 79 fiches, il n'y a aucune ligne de corpus à écrire. Ce qui suit est le texte de la couche pédagogique — écrit par moi, à passer à ta voix. Rien ne presse : l'app tourne avec cette version en attendant.

Rappels : tutoiement, phrases courtes, concret, aucune promesse. Le résumé fait **45 mots maximum**.

---

## Résumé — cible : `diamant.pedagogie.resume`

Cinq cartes en croix pour éclaircir une question précise : l'issue, ce qui agit sans que tu le voies, ce qui vient de l'extérieur, ce qu'il faut pour dénouer, et la résolution.

## Pourquoi ce tirage — cible : `diamant.pedagogie.pourquoi`

Cette croix courte vient du Tarot Zen d'Osho, où elle s'appelle Le Diamant. Elle garde la forme de la grande croix, mais se contente de l'essentiel : cinq cartes suffisent quand la question est nette.

Elle convient quand tu veux y voir clair sur un point précis, sans dérouler tout un tableau. Si la situation est large, ou si plusieurs personnes s'y croisent, la croix à dix cartes laisse plus de place. Ici, chaque carte compte double : rien à contourner.

## Le sens général — cible : `diamant.pedagogie.le_tirage`

L'issue occupe le centre. À sa gauche, ce qui agit sans que tu le voies ; à sa droite, ce qui vient de l'extérieur et que tu reconnais déjà. Sous elle, ce qu'il faut pour dénouer. Au-dessus, la résolution : ce que la lecture te laisse à comprendre.

Les deux influences forment un couple. Souvent, l'une est nommée et l'autre pas : c'est ce déséquilibre qui retient l'issue en place. Regarde laquelle des deux oppose le plus de résistance.

## Les cinq positions

**Position 1 — l'issue**

- `diamant.positions.0.libelle` → l'issue
- `diamant.positions.0.question` → de quoi s'agit-il, au fond ?
- `diamant.positions.0.se_grade` → le sujet tel qu'il se présente, sans jugement

`diamant.pedagogie.positions_expliquees.issue`

La carte du centre nomme le sujet. Elle ne dit pas quoi faire ; elle dit de quoi il s'agit, avec le ton du moment. Si elle surprend, c'est souvent que la question posée n'était pas la vraie.

**Position 2 — ce qui agit sans que tu le voies**

- `diamant.positions.1.libelle` → ce qui agit sans que tu le voies
- `diamant.positions.1.question` → quelle influence intérieure échappe à ton regard ?
- `diamant.positions.1.se_grade` → la part cachée : ce que tu portes sans le nommer

`diamant.pedagogie.positions_expliquees.interieur`

Cette carte montre ce qui pèse ou soutient sans être reconnu : une habitude, une peur ancienne, un désir que tu n'as pas formulé. L'ombre de la carte et son mode précisent comment cette influence travaille.

**Position 3 — ce qui vient de l'extérieur**

- `diamant.positions.2.libelle` → ce qui vient de l'extérieur
- `diamant.positions.2.question` → quelle influence extérieure vois-tu déjà ?
- `diamant.positions.2.se_grade` → ce que les autres apportent, projettent ou renvoient

`diamant.pedagogie.positions_expliquees.exterieur`

Cette carte décrit ce qui vient des autres : ce qu'ils apportent, ce qu'ils projettent sur toi, ce que leurs réactions font revenir. Elle ne juge personne ; elle montre ce qui circule.

**Position 4 — ce qu'il faut pour dénouer**

- `diamant.positions.3.libelle` → ce qu'il faut pour dénouer
- `diamant.positions.3.question` → qu'est-ce qui manque, ou qu'est-ce qu'il faudrait lâcher ?
- `diamant.positions.3.se_grade` → le point de bascule : ce qui pourrait dénouer

`diamant.pedagogie.positions_expliquees.necessaire`

Cette carte dit ce qui pourrait dénouer l'issue : un renoncement, un pas de côté, une parole à dire. Elle nomme le point de bascule, pas la recette.

**Position 5 — la résolution**

- `diamant.positions.4.libelle` → la résolution
- `diamant.positions.4.question` → quelle idée retenir de cette lecture ?
- `diamant.positions.4.se_grade` → l'issue de la lecture, jamais un verdict

`diamant.pedagogie.positions_expliquees.resolution`

La carte du sommet est la résolution : l'idée à retenir, ce que la lecture a mis au jour. Elle ne prédit rien. Elle ferme la croix en donnant une phrase à garder.

## Comment lire — cible : `diamant.pedagogie.comment_lire`

Commence par le centre, puis les deux influences côte à côte.

1. **L'issue :** lis-la d'abord seule. C'est le sujet de la lecture.
2. **Les deux influences :** ce qui agit en toi sans que tu le voies, et ce qui vient de l'extérieur. Compare-les.
3. **Ce qu'il faut pour dénouer :** la carte du bas indique le point de bascule.
4. **La résolution :** termine par le sommet. C'est la phrase à retenir.

Les cinq cartes se lisent en un seul geste : la croix est courte, la lecture aussi.

## Après la lecture — cible : `diamant.pedagogie.apres`

Note l'issue en une phrase, puis le point de bascule. Relis ces deux lignes dans une semaine : c'est souvent là que le regard a bougé, plus que sur la résolution elle-même.

## Vocabulaire

`diamant.pedagogie.vocabulaire.0.titre` → **Le Diamant**

`diamant.pedagogie.vocabulaire.0.texte`

Le nom vient d'Osho. La forme est celle d'une croix, mais réduite à cinq cartes : assez pour voir le sujet, ses deux influences et ce qui le dénoue, sans dérouler un grand tableau.

`diamant.pedagogie.vocabulaire.1.titre` → **Les deux influences**

`diamant.pedagogie.vocabulaire.1.texte`

L'une est intérieure et cachée, l'autre extérieure et reconnue. Elles ne s'opposent pas forcément : une influence extérieure peut soutenir ce que l'intérieur retient. C'est leur écart qui éclaire.

---

## Annexe technique — les champs lus (ne pas reformuler)

| # | Position | Champ lu |
|---|---|---|
| 1 | l'issue | `lumiere` (+ détail d'image ou mots-clés) |
| 2 | ce qui agit sans que tu le voies | `ombre.texte` + mode |
| 3 | ce qui vient de l'extérieur | `croix.entourage` |
| 4 | ce qu'il faut pour dénouer | `ombre.issue` |
| 5 | la résolution | `lecon` |

Disposition : `col` 2 / `row` 2 pour l'issue, 1/2 à gauche, 3/2 à droite, 2/3 en bas, 2/1 en haut.
