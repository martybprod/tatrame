#!/usr/bin/env python3
"""Génère maquettes/fiches_pilotes.html — les fiches du corpus en page lisible.

Lit data/corpus/cartes/*.json (corpus rédigé) avec repli sur
data/grammaire/exemples/*.json (moules de phase 0). Images réduites en
vignettes base64 : la page est autonome, ouvrable hors app.

Usage : ./venv/bin/python outils/generer_maquette_fiches.py
"""
import base64
import io
import json
import pathlib

from PIL import Image

RACINE = pathlib.Path(__file__).resolve().parent.parent
IMG = RACINE / "static" / "img" / "cartes"
SOURCES = [RACINE / "data" / "corpus" / "cartes", RACINE / "data" / "grammaire" / "exemples"]
SORTIE = RACINE / "maquettes" / "fiches_pilotes.html"


def vignette(id_carte, largeur=190):
    p = IMG / f"{id_carte}.jpg"
    if not p.exists():
        return ""
    im = Image.open(p).convert("RGB")
    r = im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    r.save(buf, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def charger_fiches():
    fiches, vus = {}, set()
    for dossier in SOURCES:
        if not dossier.is_dir():
            continue
        for p in sorted(dossier.glob("*.json")):
            f = json.loads(p.read_text(encoding="utf-8"))
            if f["id"] not in vus:
                vus.add(f["id"])
                fiches[f["id"]] = f
    return [fiches[k] for k in sorted(fiches)]


def bloc_fiche(f, img64):
    meta = []
    if f.get("registre") and f["registre"] != "hors_cycle":
        meta.append(f["registre"])
    if f.get("element"):
        meta.append(f["element"])
    if f.get("famille"):
        meta.append(f["famille"])
    if f.get("degre") is not None:
        meta.append(f"degré {f['degre']}")
    if f.get("rang"):
        meta.append(f["rang"])
    pos = f.get("positions")
    questions = "".join(f"<li>{esc(q)}</li>" for q in f["questions"])
    img = f["image"]
    reprise = (f.get("source_referentielle") or {}).get("reprise")
    badge = f'<p class="reprise">{esc(reprise)}</p>' if reprise else ""

    def posb(titre, txt):
        return f'<div class="pos"><div class="pos-titre">{titre}</div><p>{esc(txt)}</p></div>'

    section_regard = ""
    if not pos:
        regard = "<ul>" + "".join(f"<li>{esc(r)}</li>" for r in f.get("le_regard", [])) + "</ul>"
        section_regard = f'<section class="positions"><h3>Le regard — variantes de la phrase d\'exception</h3>{regard}</section>'

    section_positions = ""
    if pos:
        section_positions = f'''<section class="positions"><h3>Positions (table A)</h3>
    {posb("Aujourd'hui — tirage du jour", pos["jour"])}
    {posb("Ce que j'amène", pos["amene"])}
    {posb("Ce qui se joue", pos["se_joue"])}
    {posb("Ce que je peux essayer", pos["essayer"])}
  </section>'''

    return f'''
<article class="fiche">
  <header>
    <img src="{img64}" alt="{esc(f["nom"])}">
    <div>
      <h2>{esc(f["nom"])}</h2>
      <p class="meta">{esc(f["id"])} · {" · ".join(esc(m) for m in meta)}</p>
      <p class="mots">{" · ".join(esc(m) for m in f["mots_cles"])}</p>
      <p class="tension"><span>pousse&nbsp;: {esc(f["tension"]["pousse"])}</span><span>retient&nbsp;: {esc(f["tension"]["retient"])}</span></p>
    </div>
  </header>
  {badge}
  <section><h3>Lumière — la qualité qui circule</h3><p>{esc(f["lumiere"])}</p></section>
  <section><h3>Ombre — mode « {esc(f["ombre"]["mode"])} »</h3><p>{esc(f["ombre"]["texte"])}</p>
    <div class="issue"><b>Issue (la chaîne large)</b><p>{esc(f["ombre"]["issue"])}</p></div></section>
  <section><h3>Questions (Greer)</h3><ul>{questions}</ul></section>
  <section><h3>Leçon</h3><p class="lecon"><i>{esc(f["lecon"])}</i></p></section>
  <section><h3>L'image (Pollack — décrire avant d'interpréter)</h3>
    <p class="imgligne"><b>geste</b> — {esc(img["geste"])}</p>
    <p class="imgligne"><b>seuil</b> — {esc(img["seuil"])}</p>
    <p class="imgligne"><b>détail</b> — {esc(img["detail"])}</p></section>
  <section><h3>Micro-geste (24 h)</h3><p>{esc(f["micro_geste"])}</p></section>
  {section_positions}
  {section_regard}
</article>'''


def main():
    fiches = charger_fiches()
    cartes = "".join(bloc_fiche(f, vignette(f["id"])) for f in fiches)
    n = len(fiches)
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fiches pilotes — le corpus</title>
<style>
  body {{ margin:0; background:#131019; color:#ece7dc; font-family:Georgia,"Iowan Old Style",serif; line-height:1.6; }}
  .page {{ max-width: 1180px; margin:0 auto; padding: 34px 26px 60px; }}
  h1 {{ font-size: 30px; font-weight:400; text-align:center; margin: 0 0 6px; }}
  .sur {{ text-align:center; font-family:-apple-system,sans-serif; font-size:10px; letter-spacing:.4em; text-transform:uppercase; color:#c9a55c; }}
  .intro {{ text-align:center; color:#9a92a6; font-size:14.5px; max-width:760px; margin: 10px auto 34px; }}
  .grille {{ display:grid; grid-template-columns:1fr 1fr; gap:26px; }}
  @media (max-width: 980px) {{ .grille {{ grid-template-columns:1fr; }} }}
  .fiche {{ background:#1a1524; border:1px solid rgba(201,165,92,.18); border-radius:14px; padding:26px 26px 30px; }}
  .fiche header {{ display:flex; gap:20px; align-items:flex-start; border-bottom:1px solid rgba(201,165,92,.14); padding-bottom:18px; margin-bottom:14px; }}
  .fiche header img {{ width:120px; border-radius:8px; border:1px solid rgba(201,165,92,.3); }}
  .fiche h2 {{ margin:0; font-size:26px; font-weight:400; color:#c9a55c; }}
  .meta {{ font-family:-apple-system,sans-serif; font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:#9a92a6; margin:6px 0 10px; }}
  .mots {{ font-style:italic; color:#b9b0c6; font-size:14px; margin:0 0 12px; }}
  .tension {{ display:flex; gap:16px; font-family:-apple-system,sans-serif; font-size:12px; margin:0; }}
  .tension span {{ background:rgba(201,165,92,.1); border-radius:99px; padding:4px 12px; }}
  .reprise {{ font-family:-apple-system,sans-serif; font-size:11.5px; color:#9a92a6; background:rgba(154,146,166,.08); border-radius:8px; padding:8px 12px; margin:0 0 14px; }}
  h3 {{ font-family:-apple-system,sans-serif; font-size:10.5px; letter-spacing:.2em; text-transform:uppercase; color:#c9a55c; margin:20px 0 8px; }}
  section p {{ margin:0; font-size:15px; }}
  ul {{ margin:0; padding-left:18px; }}
  li {{ margin-bottom:5px; }}
  .issue {{ border-left:3px solid #c9a55c; background:rgba(201,165,92,.07); padding:10px 14px; border-radius:0 8px 8px 0; margin-top:12px; }}
  .issue b {{ font-family:-apple-system,sans-serif; font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color:#c9a55c; }}
  .issue p {{ margin:4px 0 0; font-size:14px; }}
  .lecon {{ font-size:16px; }}
  .imgligne {{ margin-bottom:8px; font-size:14px; color:#d5cfc2; }}
  .imgligne b {{ font-family:-apple-system,sans-serif; font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:#9a92a6; margin-right:6px; }}
  .pos {{ background:rgba(255,255,255,.03); border:1px solid rgba(201,165,92,.12); border-radius:10px; padding:12px 16px; margin-top:10px; }}
  .pos-titre {{ font-family:-apple-system,sans-serif; font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:#c9a55c; margin-bottom:6px; }}
  .pos p {{ font-size:14.5px; }}
  .note {{ text-align:center; color:#9a92a6; font-size:13px; margin-top:36px; font-style:italic; }}
  .statut {{ display:inline-block; background:rgba(201,165,92,.12); color:#c9a55c; border-radius:99px; padding:4px 16px; font-family:-apple-system,sans-serif; font-size:11.5px; letter-spacing:.1em; margin-top:12px; }}
</style></head><body><div class="page">
  <p class="sur">Le corpus pilote</p>
  <h1>Les fiches pilotes</h1>
  <p class="intro">Chaque fiche suit le schéma <b>carte.schema.json</b> et la chaîne complète : production sous charte → reformulation par Martin → révision → validation. Les positions sont celles du tirage à trois et de la carte du jour.</p>
  <div class="grille">{cartes}</div>
  <p class="statut">{n} / 10 fiches du pilote</p>
  <p class="note">Toute ombre contient son issue (la chaîne large) ; aucune carte renversée ; la nuance tient dans les quatre modes d'ombre.<br>
  Les fiches sans badge « reformulée » attendent la passe de Martin.</p>
</div></body></html>''', encoding="utf-8")
    print(f"{n} fiches -> {SORTIE}")


if __name__ == "__main__":
    main()
