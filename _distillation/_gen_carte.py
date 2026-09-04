import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_06_Union_v4"
SEED = 777007

positive = ("A circle of several people — men and women of different ages — standing in a ring, each "
"firmly clasping the forearm of the person beside them, rising together off the ground in joyful unity, "
"a grounded sense of shared connection and belonging rather than romance. All wear flowing ancient-style "
"robes, their feet bare, no modern clothing. Surrounded by a soft gradient of light that shifts from "
"warm earthen tones below to luminous pale sky tones above. On either side of the circle stand two "
"trees — one heavy with ripe fruit, the other bare and graceful — with a small serpent coiled peacefully "
"near the roots of one, a symbol of wisdom rather than danger. A radiant sun glows softly in the "
"background sky above the circle. Delicate wings of light unfold from each person's back as they rise "
"together. The figures drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of "
"warm and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("two people only, couple, romantic pose, embracing, hugging, kissing, wedding pose, trousers, "
"pants, boots, shoes, modern clothing, jeans, extra leg, third leg, two left legs, duplicated limb, "
"missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra "
"hand, floating hand, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed "
"wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, "
"rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, circular emblems, text, watermark, photorealistic, 3d render")

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
with urllib.request.urlopen(req, timeout=500) as resp:
    out = json.loads(resp.read())
imgs = out.get("images", [])
if imgs:
    raw = base64.b64decode(imgs[0])
    path = OUTDIR + f"CARTE_{NAME}_seed{SEED}.png"
    with open(path, "wb") as f:
        f.write(raw)
    print(f"OK -> {path}  seed={SEED}  ({round(time.time()-t0,1)}s)")
else:
    print("ECHEC: pas d'image")
