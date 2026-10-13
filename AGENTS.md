# Ta Trame (Align) — instructions agent

## ⚠️ MONTRER UNE IMAGE : jamais l'Aperçu macOS, TOUJOURS OpenChamber

Ne jamais lancer `open` / `open -a Preview` pour montrer une carte ou un comparatif.
Utiliser l'outil OpenChamber **`file.open`** avec le chemin du fichier (règle globale).

## ⚠️ RÈGLE PRIORITAIRE — UNE IMAGE À LA FOIS (Martin, 2026-10-03)

**NE JAMAIS produire trois tirages — ni trois propositions, ni trois graines — d'un
seul coup.** Une itération = **UNE image**. On en produit **une**, on la montre à
Martin, et on attend son retour avant la suivante.

Trois tirages en parallèle ne sont permis que sur **consigne expresse et explicite**
de Martin (« fais-moi trois propositions »). En l'absence de cette phrase, c'est UN.

*(Motif : trois images d'un coup diluent le jugement, font brûler du temps de calcul et
masquent la direction — la production se reprend une carte à la fois, un tirage à la fois.)*

Coach de vie quotidien **100 % DÉTERMINISTE** : **zéro LLM et zéro réseau au runtime** (le LLM ne sert qu'à la fabrication du corpus, hors app). Flask + vanilla, Skyfield (pas pyswisseph). Interface en français.
Port : **5073** (inscrite dans `services.json`).

## Lancement

```bash
./run.sh
```

→ http://127.0.0.1:5073

## Validation

- Suite de tests pytest (obligatoire verte avant de conclure) :

```bash
./venv/bin/python -m pytest
```

- **Contrainte produit centrale : ne JAMAIS introduire d'appel LLM ni d'appel réseau dans le runtime de l'app.** La variété vient du ciel réel (calcul), pas d'un modèle.

## Déploiement

- Plateforme : **Coolify**, site **tatrame.ca** (voir `DEPLOIEMENT.md`).
- ⚠️ **Ne jamais déployer sans demande explicite de Martin.**

## Modèle

- Rédaction/distillation du corpus (hors app) : modèles cloud frontière (Claude/Opus) — cf. principe « l'app tourne en local, elle est construite avec le meilleur outil ».
