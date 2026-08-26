import json, pathlib, re, unicodedata
from collections import defaultdict
R = pathlib.Path(__file__).resolve().parents[1]
FIL = json.loads((R/"data"/"corpus"/"fil.json").read_text(encoding="utf-8"))
E = {k:v for k,v in FIL.items() if not k.startswith("_")}
def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c)!="Mn")
    return re.sub(r"[^a-z0-9]+"," ",t).split()
vus={}; paires=defaultdict(list)
for k,e in E.items():
    m=norm(f"{e.get('miroir','')} {e.get('geste','')}")
    for i in range(len(m)-7):
        g=" ".join(m[i:i+8])
        if g in vus and vus[g]!=k:
            paires[tuple(sorted((vus[g],k)))].append(g)
        else:
            vus[g]=k
print(f"{len(paires)} paire(s) en collision :\n")
for (a,b),grams in paires.items():
    # reconstruit la plus longue suite partagée
    longest=max(grams,key=len) if grams else ""
    print(f"— {a}  <>  {b}")
    print(f"   suite : « … {longest} … »\n")
