"""Vérif en-process (test client Flask) : le Fil du jour sort bien par HTTP.
N'ouvre aucun port, ne démarre pas le scheduler, ne touche pas la flotte."""
import pathlib
from app import app  # import seul : pas de scheduler (voir _demarrer_scheduler)

PROFILS = pathlib.Path("data/profils")
pid = sorted(p.stem for p in PROFILS.glob("*.json"))[0]
c = app.test_client()

# /api/conventions : la règle fil_du_jour est-elle publiée ?
conv = c.get("/api/conventions").get_json()
assert "fil_du_jour" in conv, "convention fil_du_jour absente"
print("conventions: fil_du_jour publié — source:", conv["fil_du_jour"]["source"])

# /api/jour : le bloc fil sort-il ? Sur 6 dates espacées, pour voir tourner le domaine.
print(f"\nprofil test: {pid}")
for d in ["2026-08-09", "2026-08-12", "2026-08-15", "2026-08-18", "2026-08-22", "2026-08-26"]:
    j = c.get(f"/api/jour/{pid}?date={d}").get_json()
    fil = j.get("textes", {}).get("fil")
    trace = dict(j["jour"]["cles"]).get("fil")  # le domaine du jour (traçabilité)
    lune_m = j["jour"]["lune"]["maison"]
    if fil and fil.get("miroir"):
        print(f"  {d} | Lune maison {lune_m:>2} → domaine '{trace}' | « {fil['miroir'][:60]}… »")
    else:
        print(f"  {d} | Lune maison {lune_m:>2} → domaine '{trace}' | !!! fil ABSENT")
print("\nVERIF HTTP OK")
