import json, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
FIL = json.loads((R/"data"/"corpus"/"fil.json").read_text(encoding="utf-8"))
for k in ["echanges_transit_mars_conjonction","racines_transit_mars_conjonction",
          "sens_tension","sens_transit_jupiter_sextile-trigone",
          "metier_transit_venus_conjonction","ressources_transit_venus_conjonction"]:
    e=FIL[k]
    print(f"### {k}")
    print("miroir:", e["miroir"])
    print("geste :", e["geste"])
    print()
