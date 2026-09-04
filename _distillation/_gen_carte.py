import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_07_Volonte"
SEED = 777015

positive = ("A young man with delicate, almost childlike serene features, his face emerging as a "
"translucent veil in front of him burns slowly away in cool blue-white flames — not the heat of passion "
"but the quiet fire of awareness. Behind the dissolving veil, his expression is peaceful, detached, "
"witnessing. Wisps of the burning veil drift upward and transform into stardust, forming a faint canopy "
"of stars above his head. In the soft background, two still sphinx-like guardian silhouettes, one pale "
"and one dark, flank him in perfect stillness — opposing forces now mastered. Small crescent moon "
"motifs rest on each of his shoulders. The figure drawn in the flat decorative style of Alphonse Mucha "
"— bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas "
"of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color "
"palette spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally "
"across the scene according to its mood, muted jewel tones, subtle gold linework, soft misty "
"atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("trousers, pants, boots, shoes, modern clothing, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, extra wing, "
"three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, "
"rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, "
"magic circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
"patterns, embroidered symbols, medallion patterns, circular emblems, two people, twins, duplicate "
"person, multiple figures, text, watermark, photorealistic, 3d render")

payload = {
    "prompt": positive, "negative_prompt": negative,
    "seed": SEED, "steps": 20, "cfg_scale": 3.0,
    "width": 1024, "height": 1536,
    "sampler_name": "Euler A Trailing",
    "guidance_embed": 3.5, "shift": 3, "batch_size": 1,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=500) as resp:
        body = resp.read()
    out = json.loads(body)
    imgs = out.get("images", [])
    if imgs:
        raw = base64.b64decode(imgs[0])
        path = OUTDIR + f"CARTE_{NAME}_seed{SEED}.png"
        with open(path, "wb") as f:
            f.write(raw)
        print(f"OK -> {path}  seed={SEED}  ({round(time.time()-t0,1)}s)")
    else:
        print("ECHEC: pas d'image. contenu:", str(out)[:300])
except Exception as e:
    print("ERREUR:", repr(e))
