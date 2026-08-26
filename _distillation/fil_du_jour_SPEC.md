# SPÉC — « Le Fil du jour » : couche coaching complète d'Align

> **Auteur de la spéc** : Opus (architecture). **Rédaction des perles** : Sonnet.
> Ce document est AUTORITAIRE : les clés écrites dans `fil.json` DOIVENT matcher
> exactement l'espace de noms défini ici, sinon le moteur ne les lira pas.
> Rien ici ne se code sans avoir lu aussi `data/corpus/CHARTE.md`.

---

## 0. Le principe (à ne jamais perdre de vue)

- Le moteur **calcule et classe**, il ne rédige rien. Il émet des **clés** ; le corpus est lu par ces clés. Zéro LLM au runtime.
- La variété vient du **ciel qui bouge**, pas d'un dé. On n'invente **jamais** de « jour personnel ».
- Tables **additives**, jamais N×M. On écrit une perle par (domaine × condition-ciel **qui a un sens**), pas toutes les combinaisons.
- **Une** voix coaching par jour (« un conseil, pas dix »). Le Fil du jour est le domaine de vie du jour — il complète le transit principal (miroir/pas), il ne le double pas.
- **Droit d'auteur** : prose 100 % originale, aucune citation, aucun nom de méthode/marque des livres. Test anti-plagiat obligatoire (commercialisation).

---

## 1. L'ancre : la Lune en maison → le domaine de vie

La Lune change de maison ~tous les 2,5 jours. Les 12 maisons sont la carte classique des domaines de vie (astrologie **imprimée**, publiable dans « Les Règles »). Le domaine du jour = maison de la Lune aujourd'hui (`j["lune"]["maison"]`, déjà calculé).

| Maison | Slug domaine | Domaine | Livres sources (n° dans `cartes_de_concepts.md`) |
|---|---|---|---|
| I | `soi` | identité, mentalité, valeur de soi | Mindset (19), Gifts of Imperfection (20), Daring Greatly (12), Atomic Habits §C identité (1) |
| II | `ressources` | argent, valeurs, rapport à l'avoir | Psychology of Money (21) |
| III | `echanges` | mental, communication, focus | Deep Work (13), How to Talk (17), Essentialism (14) §non/clarté, Accords toltèques (10) §parole |
| IV | `racines` | foyer, famille, présence au quotidien | Whole-Brain Child (22), How to Talk (17), Tolle (3) §présence |
| V | `creation` | créativité, jeu, expression | Big Magic (2), Creative Act (6), Creative Habit (7), War of Art (8) **+ migration de `creativite.json`** |
| VI | `quotidien` | habitudes, santé, sommeil, routine | Atomic Habits (1), Why We Sleep (23), Why Zebras (24) §santé |
| VII | `autre` | couple, amour, lien | 5 langages (18), Hold Me Tight (15), Attached (11) |
| VIII | `traversee` | intimité, crise, transformation, deuil, honte | When Things Fall Apart (9), Daring Greatly (12) §honte, Frankl (5) §souffrance, Accords toltèques (10) §émotions |
| IX | `sens` | quête de sens, croyances, croissance | Frankl (5), Mindset (19) §croissance, Tolle (3), Chödrön (9) §chemin |
| X | `metier` | vocation, visibilité, essentiel | Essentialism (14), 7 Habitudes (4), War of Art (8) §pro/territoire, Deep Work (13) |
| XI | `communaute` | amitiés, appartenance, coopération | Gifts of Imperfection (20) §appartenance, 7 Habitudes (4) §coopération/synergie |
| XII | `retrait` | solitude, intérieur, lâcher-prise, anxiété | Tolle (3), Chödrön (9), Hope and Help (16), Why Zebras (24) §stress |

> Les slugs sont ASCII, sans accent, définitifs (ils sont dans les clés). Les
> **libellés affichés** pourront différer (comme « miroir/pas ») — à décider plus tard.
> Aucun slug n'entre en collision avec le vocabulaire numérologique d'Align
> (Cap, Voix, Foyer, Reflet, Geste, Source, Trace, Élan, Héritages, Frictions, Appuis, Chantiers).

---

## 2. Le raffinement : transit dominant + phase → la condition-ciel

Dans un domaine, la perle du jour se précise selon le ciel. Deux dimensions :

**Tonalité** (dérivée de la classe du transit dominant, `j["dominante"]["classe"]`) :
- `fluide` = conjonction OU sextile-trigone (l'énergie coule)
- `tension` = carre-opposition (ça résiste, ça demande un arbitrage)

**Nuance planétaire** (planète du transit dominant, `j["dominante"]["transit"]`) — à écrire seulement là où elle recolore VRAIMENT le domaine :
- `venus` → douceur, lien, valeurs · `mars` → élan, conflit, action · `mercure` → mental, mots · `lune` → émotion, sensibilité · `soleil` → visibilité, affirmation · `saturne`/`jupiter` quand ils dominent → limite/expansion.

**Phase lunaire** (`j["phase"]["phase"]`) — pour les domaines à **processus** seulement (creation, quotidien, metier) : commencer, tenir, montrer, se reposer, etc. Interdit ailleurs (une phase de lune plaquée sur « argent » serait arbitraire).

---

## 3. Espace de noms des clés (AUTORITAIRE)

Le moteur (`_cles_fil`) émettra des clés candidates, **de la plus précise à la plus générale**. Le corpus lit la **première qui existe** (même logique que `transits_precis` → `transits_generiques`, et que `_cles_creativite`). Format des clés dans `fil.json` :

```
{domaine}_transit_{planete}_{classe}     ← le plus précis (ex. autre_transit_venus_carre-opposition)
{domaine}_{tonalite}                      ← ex. autre_tension        (tonalite ∈ fluide|tension)
{domaine}_phase_{phase}                   ← domaines à processus SEULEMENT (ex. creation_phase_pleine)
{domaine}                                 ← générique, socle (ex. autre)  ← OBLIGATOIRE pour chaque domaine
```

- `{planete}` ∈ soleil, lune, mercure, venus, mars, jupiter, saturne, uranus, neptune, pluton
- `{classe}` ∈ conjonction, carre-opposition, sextile-trigone
- `{phase}` ∈ nouvelle, croissante, premier_quartier, gibbeuse, pleine, diffusante, dernier_quartier, balsamique

**Règle d'or de volume** : chaque domaine a AU MINIMUM sa clé générique (socle qui résout toujours). On ajoute une variante **uniquement si la condition-ciel change réellement le conseil**. On n'écrit jamais une variante arbitraire pour « faire du nombre ».

**Cible** : ~25-35 perles par domaine, meaning-gated → **~300-400 au total**. Volume qui flexe selon la richesse de la source (ex. `autre` en aura beaucoup, `ressources` moins — c'est honnête).

---

## 4. Schéma de `data/corpus/fil.json`

Un seul fichier, dict à plat keyé par les clés du §3. Mêmes conventions que `creativite.json`.

```json
{
  "_charte": "data/corpus/CHARTE.md",
  "_note": "Le Fil du jour — couche coaching, distillée des 24 ouvrages (voir _distillation/cartes_de_concepts.md). CONCEPTS repris, JAMAIS la prose des livres. Routé par le ciel (maison de la Lune = domaine, transit + phase = nuance), jamais par un dé. Additif : une perle par (domaine × condition-ciel qui a un sens).",

  "autre": {
    "source_livre": "d'après les concepts de Chapman, Johnson, Levine & Heller",
    "themes": ["amour", "lien", "presence"],
    "miroir": "…",  // 1 phrase, présent, observable, non moral
    "geste": "…"    // 1 action concrète, faisable aujourd'hui, petite
  },
  "autre_tension": {
    "source_livre": "d'après les concepts de Levine & Heller — l'attachement",
    "themes": ["amour", "conflit"],
    "miroir": "…",
    "geste": "…"
  },
  "autre_transit_venus_conjonction": { "...": "..." }
}
```

Champs par entrée :
- `source_livre` (string) : attribution honnête « d'après les concepts de … » — jamais un titre présenté comme officiel.
- `themes` (array de tags) : crochets pour les tests de variété (ex. `["amour","conflit"]`).
- `miroir` (string) : **le miroir** — 1 phrase, ce qui se joue au présent.
- `geste` (string) : **le pas** — 1 action concrète, petite, faisable aujourd'hui.

Longueur cible **miroir + geste = 30-85 mots** (registre « jour » de la charte).

---

## 5. La voix (rappel condensé de CHARTE.md — non négociable)

1. **Recadrer en conditionnement, jamais en faute** : constat → normalisation → déculpabilisation.
2. **Désigner le système, pas l'individu**.
3. **Registre CONSTATIF** : « Tu es en train de… » ✅ · « Tu es… » ❌ · « Tu vas… » ❌ (jamais de prédiction).
4. **Tutoiement**, chaleureux, ami lucide — pas oracle, pas coach de performance.
5. **UNE chute par entrée, pas par phrase.** Le reste est plat, parlé, facile.
6. **Tics à tuer** : concept abstrait en sujet · chute au tiret cadratin · deux-points aphoristique · « Ce n'est pas… » en ouverture.
7. Test à voix haute : ça doit sonner comme quelqu'un qui te parle, pas qui écrit.

---

## 6. Discipline droit d'auteur (commercialisation)

- On reprend les **idées/concepts**, jamais la prose. Zéro citation, même courte.
- Rédiger **à partir des cartes de concepts** (`_distillation/cartes_de_concepts.md`), pas des textes sources. Les `.txt` sources ne servent qu'au **test anti-plagiat**.
- Aucun **nom de méthode/marque** des livres (« Atomic Habits », « 5 langages », « règle des 2 minutes » comme label…). Exprimer en langage courant, vocabulaire d'Align.

---

## 7. Tests obligatoires — `tests/test_fil.py`

1. **Anti-plagiat** : aucun 7-gramme d'une perle n'apparaît dans un fichier de `_distillation/sources/*.txt` (normalisé : minuscules, sans accents, ponctuation retirée). Aucune suite de 5 mots ne différant que par des mots-outils. → garantie contractuelle.
2. **Style** (mêmes seuils que `tests/test_style.py`) : tirets cadratins < 8 / 100 phrases, deux-points < 10 / 100, ouverture sur concept abstrait < 3 / 100, « Ce n'est pas… » en ouverture < 2 / 100.
3. **Variété** : aucune ouverture (5 premiers mots) ne domine ; aucune suite de 8 mots partagée entre deux perles ; distribution des `themes` pas trop concentrée.
4. **Structure** : chaque entrée a `miroir` + `geste` non vides ; 30-85 mots ; la clé matche le motif du §3 (domaine connu, classe/phase/planète valides).
5. **Couverture** : chaque domaine des 12 a au moins sa clé générique (le fil résout toujours).

---

## 8. Changements moteur (petits, dans la lignée de l'existant)

> Cette partie est du **code**, pas de la rédaction. Peut être faite par Opus
> ou Sonnet. À faire APRÈS ou EN PARALLÈLE de la rédaction (les clés sont figées ici).

**`moteur/jour.py`** :
- Ajouter `MAISON_DOMAINE = {1:"soi", 2:"ressources", 3:"echanges", 4:"racines", 5:"creation", 6:"quotidien", 7:"autre", 8:"traversee", 9:"sens", 10:"metier", 11:"communaute", 12:"retrait"}`.
- Ajouter `DOMAINES_A_PHASE = frozenset({"creation", "quotidien", "metier"})`.
- Ajouter `_cles_fil(dominante, phase, lune)` : calque de `_cles_creativite`, renvoie les candidates du §3 dans l'ordre précis→générique. `tonalite = "tension" if classe == "carre-opposition" else "fluide"`.
- Dans `_cles(...)` : remplacer la ligne `cles.append(("creativite", f"phase_{phase['phase']}"))` par `cles.append(("fil", <clé de traçabilité>))` (la vraie résolution se fait dans app.py, comme aujourd'hui pour creativite).

**`app.py` `_jour_pour`** : remplacer le bloc `elif genre == "creativite":` par `elif genre == "fil":` qui boucle sur `J._cles_fil(j["dominante"], j["phase"], j["lune"])` et prend la première clé que `corpus.lire("fil", ccle)` résout.

**Décision à confirmer avec l'utilisateur** : le nouveau `fil` **remplace** l'ancien « fil créatif » (la créativité devient le domaine `creation`, montré quand la Lune est en maison V → **une** voix coaching/jour). Le contenu de `creativite.json` est **migré** dans `fil.json` sous les clés `creation_*`. Recommandé pour tenir « un conseil, pas dix ».

**`data/corpus/CHARTE.md` + écran « Les Règles »** : documenter le mapping maison→domaine (imprimé) ; marquer « tranché par Align » la tonalité fluide/tension et le choix des domaines à phase.

---

## 9. Découpage du travail pour Sonnet (1 domaine = 1 lot)

Chaque lot est autonome : Sonnet lit (a) cette spéc, (b) les sections des livres sources du domaine dans `cartes_de_concepts.md`, (c) `CHARTE.md`, puis rédige les entrées du domaine dans `fil.json` (ou un fragment par domaine, à fusionner).

Ordre suggéré (du plus riche au plus lean) : `autre`, `quotidien`, `retrait`, `soi`, `traversee`, `sens`, `metier`, `echanges`, `racines`, `creation` (migration + enrichissement), `communaute`, `ressources`.

Par lot, Sonnet produit : la clé générique + les variantes tonalité/phase/transit **meaningful** (viser 25-35, qualité d'abord), au format §4, voix §5, discipline §6.
