"""Un thème réel, de bout en bout, à l'écran.

Le filet golden prouve que chaque pièce est juste ; ce script prouve que la
CHAÎNE tourne : nom de ville -> SQLite -> fuseau -> UTC -> éphémérides ->
maisons -> thème lisible.

    python outils/demo.py "Trois-Pistoles" 1975-07-16 14:30
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from moteur.geo import ATTRIBUTION, Lieux  # noqa: E402
from moteur.theme import Moteur  # noqa: E402

GLYPHES = {
    "soleil": "☉", "lune": "☽", "mercure": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturne": "♄", "uranus": "♅", "neptune": "♆",
    "pluton": "♇", "noeud_moyen": "☊",
}


def main():
    ville = sys.argv[1] if len(sys.argv) > 1 else "Trois-Pistoles"
    date = sys.argv[2] if len(sys.argv) > 2 else "1975-07-16"
    heure = sys.argv[3] if len(sys.argv) > 3 else "14:30"
    an, mo, jo = map(int, date.split("-"))
    hh, mi = map(int, heure.split(":"))

    lieux = Lieux()
    candidats = lieux.chercher(ville)
    if not candidats:
        sys.exit(f"✗ lieu introuvable : {ville}")
    if len(candidats) > 1:
        print(f"⚠️  {len(candidats)} lieux portent ce nom — l'app devra faire choisir :")
        for c in candidats[:4]:
            print(f"     {c['nom']} ({c['pays']}/{c['admin1']}, {c['code']}) "
                  f"{c['lat']:.4f},{c['lon']:.4f} · {c['fuseau']}")
        print()
    lieu = candidats[0]

    m = Moteur()
    t = m.theme_natal(an, mo, jo, hh, mi, lieu["lat"], lieu["lon"], lieu["fuseau"])

    n = t["naissance"]
    print("═" * 66)
    print(f"  {lieu['nom']} ({lieu['pays']})  ·  {n['locale']}  ·  {n['fuseau']}")
    print(f"  {lieu['lat']:.4f}, {lieu['lon']:.4f}  ·  UTC {n['utc']}")
    print("═" * 66)

    a = t["angles"]
    print(f"\n  Ascendant  {a['asc']['degre']:>2}° {a['asc']['signe']:<11} {a['asc']['minute']:>2}'")
    print(f"  Milieu du Ciel {a['mc']['degre']:>2}° {a['mc']['signe']:<11} {a['mc']['minute']:>2}'")

    print(f"\n  {'':<12} {'position':<22} {'maison':>7}")
    print("  " + "─" * 44)
    for nom, c in t["corps"].items():
        retro = " ℞" if c["retrograde"] else "  "
        pos = f"{c['degre']:>2}° {c['signe']:<11} {c['minute']:>2}'{retro}"
        print(f"  {GLYPHES[nom]} {nom:<10} {pos:<22} {c['maison']:>5}")

    mz = t["maisons"]
    print(f"\n  Maisons ({mz['systeme']})")
    if mz["repli"]:
        print(f"  ⚠️  repli : {mz['repli']}")
    for i in range(0, 12, 4):
        ligne = "   ".join(
            f"{j+1:>2}: {mz['cuspides_signe'][j]['degre']:>2}° "
            f"{mz['cuspides_signe'][j]['signe'][:4]:<4}"
            for j in range(i, i + 4)
        )
        print("   " + ligne)

    if t["avis"]:
        print("\n  ⚠️  À trancher par l'utilisateur")
        for av in t["avis"]:
            print(f"     {av['message']}")
    if t["limites"]:
        print("\n  ℹ️  Réserves historiques (affichées, jamais tues)")
        for l in t["limites"]:
            print(f"     · {l}")

    print(f"\n  {ATTRIBUTION}")


if __name__ == "__main__":
    main()
