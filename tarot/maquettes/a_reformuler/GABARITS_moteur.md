# Les gabarits du moteur — réécriture pour la clarté

> Chaque phrase de la section de lecture est un **fait calculé** (une liaison
> d'éléments, un comptage contre un seuil) exprimé avec un **gabarit fixe** de
> `tables.json`. Cette passe ne touche que les gabarits : les faits restent,
> les phrases deviennent limpides. Le vocabulaire du jeu (feu, eau, air, terre,
> majeures, figures, colonnes) est expliqué **dans la phrase** au lieu d'être
> supposé connu.
>
> Pour chaque gabarit : **quand il sort** (le déclencheur), l'**ancien texte**,
> et ma **proposition** à reformuler. Reformule librement — les faits calculés
> doivent rester les mêmes, le reste est à ta voix.
>
> ⚠️ Deux changements mécaniques accompagneront l'intégration (côté moteur,
> invisible ici) : les liaisons seront choisies par paire exacte (6 gabarits au
> lieu de 3, pour pouvoir nommer les deux éléments), et deux espaces
> (« {famille} », « {glose} ») seront remplis par le moteur avec le nom et la
> traduction de la famille.

## 1. Phrase de seuil — tirage avec deux majeures ou plus

**Quand** : 2 majeures ou plus dans les trois cartes.
**Ancien** : « Deux majeures dans le tirage. Ce qui se joue là touche un passage de ta vie, pas un détail d'agenda. »
**Proposition** : « Ce tirage contient au moins deux cartes majeures. Les majeures sont les grandes cartes du jeu : elles parlent de passages, de décisions qui marquent une vie, pas de détails d'agenda. Quand elles arrivent en nombre, c'est que le moment compte. »

## 2. Phrase de seuil — une famille domine (feu)

**Quand** : au seuil, deux cartes ou plus de la même famille.
**Ancien (feu)** : « Le feu domine ce tirage — l'élan, le projet, le désir de bouger. »
**Proposition (feu)** : « Le feu domine ce tirage. Le feu, dans ce jeu, c'est l'élan : l'envie de faire, de commencer, de bouger. Ce dont il est question ici, c'est d'énergie et de projet. »

## 3. Phrase de seuil — famille eau

**Ancien** : « L'eau traverse ce tirage — le lien, ce qui se sent, ce qui s'imagine. »
**Proposition** : « L'eau domine ce tirage. L'eau, c'est le lien : les émotions, les relations, ce qui se sent plus que ce qui se dit. Ici, c'est le cœur de la situation. »

## 4. Phrase de seuil — famille air

**Ancien** : « L'air domine ce tirage — les idées, les mots, ce qui se comprend. »
**Proposition** : « L'air domine ce tirage. L'air, ce sont les idées : ce qu'on se dit, ce qu'on comprend, la clarté ou le doute. Ici, tout passe par la tête. »

## 5. Phrase de seuil — famille terre

**Ancien** : « La terre tient ce tirage — le concret, le corps, ce qui se construit. »
**Proposition** : « La terre domine ce tirage. La terre, c'est le concret : le corps, la maison, l'argent, ce qui se construit à la main. Ici, c'est du solide, du lent, du réel. »

## 6. Phrase de seuil — tirage sans trait dominant

**Ancien** : « Trois cartes posées, et un fil entre elles. »
**Proposition** : « Trois cartes posées côte à côte, sans qu'une seule matière domine. Chacune a son mot à dire, et ensemble elles forment un seul récit. »

## 7. Liaison « renforce » — feu et air côte à côte

**Quand** : deux cartes adjacentes, l'une de feu et l'autre d'air (dans n'importe quel ordre).
**Ancien** : « Ces deux cartes se soutiennent : la première donne de l'air à la seconde, et l'ensemble prend de l'ampleur. »
**Proposition** : « L'une de ces deux cartes est de feu — l'élan, l'envie de faire. L'autre est d'air — les idées, les mots. Ensemble, elles vont dans le même sens : quand l'élan rencontre les mots justes, le mouvement prend de l'ampleur. »

## 8. Liaison « renforce » — eau et terre côte à côte

**Ancien** : « Ces deux cartes se soutiennent : la première donne de l'air à la seconde, et l'ensemble prend de l'ampleur. »
**Proposition** : « L'une de ces deux cartes est d'eau — le lien, les émotions. L'autre est de terre — le concret, ce qui dure. Elles se portent l'une l'autre : le sentiment trouve un appui solide, et le réel devient plus doux. »

## 9. Liaison « neutralise » — feu et terre côte à côte

**Ancien** : « Ces deux cartes se tiennent en équilibre : l'une retient l'autre, sans victoire ni défaite. »
**Proposition** : « L'une de ces deux cartes est de feu — l'élan. L'autre est de terre — la lenteur, le concret. Elles ne se battent pas : l'une veut bouger, l'autre veut durer. Ensemble, elles imposent un rythme ni trop rapide ni trop lent. »

## 10. Liaison « neutralise » — air et eau côte à côte

**Ancien** : « Ces deux cartes se tiennent en équilibre : l'une retient l'autre, sans victoire ni défaite. »
**Proposition** : « L'une de ces deux cartes est d'air — les idées. L'autre est d'eau — les émotions. Trop réfléchir noie le sentiment, trop sentir brouille l'idée. L'équilibre entre les deux est le vrai sujet du moment. »

## 11. Liaison « tension » — feu et eau côte à côte

**Ancien** : « Ces deux cartes se contrarient : ce que l'une demande, l'autre éteint ou l'alourdit. La tension est le sujet, pas un accident. »
**Proposition** : « L'une de ces deux cartes est de feu — l'élan. L'autre est d'eau — les émotions. L'eau éteint le feu, le feu fait bouillir l'eau. Cette friction n'est pas un accident : c'est exactement ce qui se joue ici. »

## 12. Liaison « tension » — air et terre côte à côte

**Ancien** : « Ces deux cartes se contrarient : ce que l'une demande, l'autre éteint ou l'alourdit. La tension est le sujet, pas un accident. »
**Proposition** : « L'une de ces deux cartes est d'air — les idées qui tournent. L'autre est de terre — le concret, qui va lentement. Les idées tournent, le réel ne suit pas. Cette friction dit où se trouve le travail à faire. »

## 13. Écho de famille — deux cartes de la même famille côte à côte

**Quand** : deux cartes adjacentes de la même famille. Le moteur remplit « {famille} » et « {glose} ».
**Ancien (feu)** : « Deux cartes de feu côte à côte — la même matière, deux fois. »
**Proposition (gabarit)** : « Deux cartes de {famille} côte à côte. {glose}. La même matière, deux fois de suite : quand une même famille revient, elle parle plus fort. »
**Exemple rendu (feu)** : « Deux cartes de feu côte à côte. Le feu, c'est l'élan : l'envie de faire, de commencer, de bouger. La même matière, deux fois de suite : quand une même famille revient, elle parle plus fort. »

## 14. Écho de majeures — deux majeures du même élément

**Ancien** : « Deux majeures du même élément — la même force qui traverse, à deux étages. »
**Proposition** : « Deux cartes majeures portent le même élément. Les majeures parlent des grands mouvements d'une vie. Quand deux d'entre elles portent la même force, cette force est au centre du passage. »

## 15. Écho mixte — une majeure et une mineure du même élément

**Ancien** : « Une majeure et une mineure du même élément — la même force, à deux échelles de ta vie. »
**Proposition** : « Une carte majeure et une carte mineure partagent le même élément. La majeure parle du grand passage, la mineure du quotidien. Même force, deux échelles : la grande histoire et la journée ordinaire disent la même chose. »

## 16. Deux majeures de la même colonne

**Quand** : deux majeures qui appartiennent au même groupe de sens (les colonnes de la grammaire).
**Ancien** : « Deux majeures de la même colonne — le même motif à deux étages. »
**Proposition** : « Deux cartes majeures appartiennent au même groupe de sens dans le jeu. Elles racontent, de deux places différentes, la même leçon. C'est un écho qu'il vaut la peine d'écouter. »

## 17. Motif — deux majeures ou plus

**Ancien** : « Deux majeures ou plus dans ce tirage. Ce qui se joue là touche un passage de ta vie. »
**Proposition** : « Ce tirage contient plusieurs cartes majeures. Les majeures parlent de passages et de décisions qui marquent une vie. Leur nombre ici n'est pas un hasard : le moment compte. »

## 18. Motif — aucune majeure

**Ancien** : « Aucune majeure dans le tirage. Une affaire courante, malléable, qui se laisse travailler. »
**Proposition** : « Aucune grande carte dans ce tirage, seulement des cartes du quotidien. C'est plutôt une bonne nouvelle : la situation est courante et malléable. Elle se laisse travailler sans drame. »

## 19. Motif — famille feu absente

**Quand** : au moins deux mineurs, et aucune carte de feu.
**Ancien** : « Aucun feu dans le tirage. Et si l'élan absent était justement le sujet ? »
**Proposition** : « Aucune carte de feu dans ce tirage. Le feu, c'est l'élan : l'envie de faire, de commencer, de bouger. Son absence se lit de deux façons : l'élan est déjà là sans avoir besoin d'être dit, ou il manque. La question du jour est de savoir laquelle. »

## 20. Motif — famille eau absente

**Ancien** : « Aucune eau dans le tirage. Et si ce qui manque était ce qu'il faut regarder ? »
**Proposition** : « Aucune carte d'eau dans ce tirage. L'eau, c'est le lien : les émotions, les relations, ce qui se sent. Son absence peut dire que tout est calme sur ce plan, ou que le lien est passé sous silence. À toi de voir laquelle. »

## 21. Motif — famille air absente

**Ancien** : « Aucun air dans le tirage. Et si l'idée manquante était le nœud ? »
**Proposition** : « Aucune carte d'air dans ce tirage. L'air, ce sont les idées, les mots, la clarté. Son absence peut vouloir dire que tout est déjà clair, ou que ce qui manque, c'est justement une conversation. Le tirage ouvre les deux portes. »

## 22. Motif — famille terre absente

**Ancien** : « Aucune terre dans le tirage. Et si le concret absent était la question ? »
**Proposition** : « Aucune carte de terre dans ce tirage. La terre, c'est le concret : le corps, la maison, ce qui se construit. Son absence peut dire que le concret va de soi, ou qu'il est oublié. Les deux portes sont ouvertes. »

## 23. Motif — famille dominante

**Quand** : deux cartes ou plus de la même famille (hors seuil). Le moteur remplit « {famille} » et « {glose} ».
**Ancien (feu)** : « Deux cartes de feu traversent ce tirage — une saison, pas un verdict. »
**Proposition (gabarit)** : « Deux cartes de {famille} traversent ce tirage. {glose}. Une famille dominante n'est pas un verdict : c'est une saison. Elle colore tout le tirage, et elle passe. »
**Exemple rendu (feu)** : « Deux cartes de feu traversent ce tirage. Le feu, c'est l'élan : l'envie de faire, de commencer, de bouger. Une famille dominante n'est pas un verdict : c'est une saison. Elle colore tout le tirage, et elle passe. »

## 24. Motif — figures en nombre

**Quand** : au moins deux figures (Page, Chevalier, Reine, Roi).
**Ancien** : « Les figures occupent le terrain. Des manières d'être demandent la scène, chez toi comme autour de toi. »
**Proposition** : « Ce tirage contient au moins deux figures : les personnages du jeu — le Page, le Chevalier, la Reine, le Roi. Les figures ne parlent pas d'événements, elles parlent de manières d'être. La question devient : qui se comporte comment, chez toi comme autour de toi ? »

## 25. Motif — un degré répété

**Quand** : le même degré (le nombre de la carte mineure) apparaît au moins deux fois. Le moteur remplit « {texte} » par le sens du degré.
**Ancien** : « Le {degre} se répète dans le tirage — {texte}. »
**Proposition (gabarit)** : « Le même degré revient au moins deux fois dans ce tirage. Son thème : {texte}. Quand un nombre se répète, c'est qu'il insiste. Son thème mérite un temps d'arrêt. »
**Exemple rendu (degré 5)** : « Le même degré revient au moins deux fois dans ce tirage. Son thème : la crise, la fêlure, le test. Quand un nombre se répète, c'est qu'il insiste. Son thème mérite un temps d'arrêt. »

## 26. Motif — Éveil dans le tirage

**Quand** : Éveil (la 79ᵉ carte) est sortie.
**Ancien** : « Éveil, la carte hors cycle, s'est glissée dans le tirage. Une visite rare, qui ne demande rien. »
**Proposition** : « Éveil, la 79ᵉ carte du jeu, s'est glissée dans le tirage. C'est une visite rare. Elle ne demande rien : elle regarde. »
**Note** : avec la nouvelle forme d'Éveil (le libellé « le regard » et sa phrase d'exception à sa place dans le tirage), ce motif pourrait devenir redondant. À trancher pendant l'intégration : garder (il nomme la rareté dans le fil de la lecture) ou retirer (la phrase d'exception suffit).
