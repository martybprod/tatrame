# -*- coding: utf-8 -*-
"""La fréquence RÉELLE des transits précis — le guide des lots de rédaction.

Pour chaque profil réel (hors profils de test) et chaque jour d'une année
pleine, on repasse par le MÊME calcul que la production (`_jour_pour`) et on
compte la clé qui porte le titre du jour :

- `precis`    : la clé existe dans `transits_precis` → l'amorce est à écrire ;
- `generique` : pas d'entrée précise → repli sur le générique (déjà amorcé) ;
- `aucune`    : pas de dominante ce jour-là (rare).

Le classement `precis` (jours cumulés, puis profils distincts) donne l'ordre
des batchs ChatGPT : on écrit d'abord ce que les gens verront le plus.
"""
import collections
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import app as application

RACINE = pathlib.Path(__file__).resolve().parents[1]
DEBUT = dt.date(2026, 10, 16)
JOURS = 365
EXCLURE = ("jean-test", "test")


def profils_reels():
    out = []
    for p in sorted((RACINE / "data" / "profils").glob("*.json")):
        if any(x in p.stem for x in EXCLURE):
            continue
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def main():
    precis = collections.Counter()
    phases_par_cle = collections.defaultdict(collections.Counter)
    profils_par_cle = collections.defaultdict(set)
    generiques = collections.Counter()
    aucune = 0
    total = 0

    for profil in profils_reels():
        pid = profil["id"]
        for i in range(JOURS):
            d = DEBUT + dt.timedelta(days=i)
            j = application._jour_pour(profil, d)
            if not j.get("complet"):
                continue          # profil sans heure/lieu : rien de calculable
            total += 1
            dom = j["jour"]["dominante"]
            if not dom:
                aucune += 1
                continue
            phase = j["jour"]["phase"]["phase"]
            if dom["cle"] in application.corpus.lire("transits", "transits_precis") or True:
                # la clé précise ne se sert que si l'entrée existe (repli
                # générique sinon) — on regarde ce que le corpus renvoie.
                entree = application.corpus.lire(
                    "transits", "transits_precis", dom["cle"])
                if entree:
                    precis[dom["cle"]] += 1
                    phases_par_cle[dom["cle"]][phase] += 1
                    profils_par_cle[dom["cle"]].add(pid)
                    continue
            generiques[f"{dom['transit']}_{dom['classe']}"] += 1

    rapport = {
        "fenetre": f"{DEBUT.isoformat()} + {JOURS} jours",
        "profils": len(profils_reels()),
        "total_jours_profil": total,
        "sans_dominante": aucune,
        "precis": [
            {
                "cle": cle,
                "jours": n,
                "profils": len(profils_par_cle[cle]),
                "phases": dict(phases_par_cle[cle]),
            }
            for cle, n in precis.most_common()
        ],
        "generique_fallback": [
            {"cle": cle, "jours": n} for cle, n in generiques.most_common()
        ],
    }
    sortie = RACINE / "scripts" / "frequence_precis.json"
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2),
                      encoding="utf-8")

    print(f"fenêtre {rapport['fenetre']} — {rapport['profils']} profils, "
          f"{total} jours-profil, {aucune} sans dominante")
    print("\n— TOP PRÉCIS (jours cumulés | profils | phases) —")
    for ligne in rapport["precis"][:40]:
        print(f"{ligne['jours']:4d}  {ligne['profils']:2d}p  "
              f"{json.dumps(ligne['phases'], ensure_ascii=False)}  {ligne['cle']}")
    print("\n— REPLIS GÉNÉRIQUES (déjà amorcés) —")
    for ligne in rapport["generique_fallback"][:10]:
        print(f"{ligne['jours']:4d}  {ligne['cle']}")
    print(f"\n→ {sortie}")


if __name__ == "__main__":
    main()
