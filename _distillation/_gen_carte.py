import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_06_Union_v3"
SEED = 777006

positive = ("A man and a woman standing at arm's length facing each other, each firmly clasping the "
"other's forearm in a gesture of solidarity and trust — like two allies or old friends sealing a bond, "
"not a romantic embrace. Both stand upright and confident, slowly rising off the ground together. Both "
"wearing flowing ancient-style robes, their feet bare, no modern clothing. Surrounded by a soft gradient "
"of light that shifts from warm earthen tones at their feet to luminous pale sky tones above their "
"heads. Behind them stand two trees — one heavy with ripe fruit, the other bare and graceful — with a "
"small serpent coiled peacefully at the base of one, a symbol of wisdom rather than danger. A radiant "
"sun glows softly off to one side in the background sky, not centered between them. Delicate wings of "
"light unfold from their backs as they lift higher. The figures drawn in the flat decorative style of "
"Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental "
"hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on "
"textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced and "
"distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("embracing, hugging, foreheads touching, romantic couple pose, wedding pose, kissing, holding "
"hands, sun centered between faces, trousers, pants, boots, shoes, modern clothing, jeans, extra leg, "
"third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, third "
"arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra "
"finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, "
"rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, circular emblems, text, "
"watermark, photorealistic, 3d render")

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
