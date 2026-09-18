# Ta Trame (Align) — instructions agent

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
