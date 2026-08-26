import py_compile
for m in ("moteur/jour.py", "app.py"):
    py_compile.compile(m, doraise=True)
print("compile OK: jour.py, app.py")

from moteur.corpus import Corpus
from moteur import jour as J
c = Corpus()
assert "fil" in c.tables, "table fil absente"
inv = c.inventaire()
nfil = sum(v for k, v in inv.items() if k.startswith("fil."))
print("fil chargé:", nfil, "entrées")
assert "creativite" not in c.tables, "creativite encore chargé"
print("creativite retiré du corpus: OK")

DOMAINES = ["soi","ressources","echanges","racines","creation","quotidien",
            "autre","traversee","sens","metier","communaute","retrait"]
manque = [d for d in DOMAINES if not c.lire("fil", d)]
assert not manque, f"génériques manquants: {manque}"
print("12 socles génériques résolvent: OK")

ph = {"phase":"pleine"}
print("cles_fil creation(M5)+venus/conj:", J._cles_fil({"transit":"venus","classe":"conjonction"}, ph, {"maison":5}))
print("cles_fil autre(M7)+mars/carré :", J._cles_fil({"transit":"mars","classe":"carre-opposition"}, ph, {"maison":7}))
print("cles_fil sens(M9) sans dominante:", J._cles_fil(None, ph, {"maison":9}))

for cle in J._cles_fil({"transit":"venus","classe":"conjonction"}, ph, {"maison":7}):
    t = c.lire("fil", cle)
    if t:
        print("autre+venus/conj -> clé servie:", cle, "| miroir:", t["miroir"][:55], "...")
        break
print("VALIDATION OK")
