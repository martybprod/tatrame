import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_09_Solitude"
SEED = 777017

positive = ("A humble solitary man walking alone along a dark, snow-dusted mountain path at night, "
"wearing a long hooded grey cloak over simple timeless robes, no modern clothing, and leaning gently on "
"a gnarled wooden walking staff. No lantern in his hand — instead, a soft warm light glows gently from "
"within his own chest and skin, lighting his way from the inside, its glow faintly forming the shape of "
"a six-pointed star. The surrounding darkness is vast and quiet, snowy peaks faintly visible, stars "
"faint overhead, no other path or companion in sight. His expression is calm, self-sufficient, unafraid "
"of the dark. The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean "
"contour lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor "
"pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full "
"range of warm and cool hues, harmoniously balanced and distributed naturally across the scene according "
"to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, "
"not airbrushed.")

negative = ("trousers, pants, jeans, boots, shoes, sneakers, modern clothing, jacket, blazer, other "
"people, companion, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, "
"missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, "
"malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed "
"anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, "
"rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, "
"mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, "
"medallion patterns, circular emblems, two people, text, watermark, photorealistic, 3d render")

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
