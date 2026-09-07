import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_17_Silence_v1"
SEED = 777042

positive = ("A vast, silent night sky filled with stars and a full moon surrounded by seven smaller "
"twinkling stars, a serene feminine face gently visible within the clouds and moonlight, deep in "
"meditation, like a goddess of the night watching over everything. A single bird rests silently on "
"a branch at the water's edge, watching. Below, a still misty lake perfectly mirrors the starlit "
"sky and her tranquil face. Nothing moves; total stillness and peace. No other figure. The whole "
"image is framed by an ornate Art Nouveau golden border with flowing organic whiplash lines and "
"delicate ornamental corners, enclosing the entire card. Flat decorative Art Nouveau illustration "
"style, bold elegant clean contour lines, stylized idealized features, flat areas of soft "
"watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible "
"paper grain and pigment bleeds, mystical dreamlike mood, a rich complete color palette spanning "
"the full range of warm and cool hues, harmoniously balanced and distributed naturally across the "
"scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("angels, cherubs, putti, angelots, winged figures in corners, corner figures, decorative "
"figures in upper corners, clouds with figures, more than one bird, flock of birds, rainbow, "
"rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, "
"extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed "
"hands, fused fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, "
"multiple faces in the sky, more than one face in the clouds, random occult symbols, magic "
"circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, "
"esoteric patterns, embroidered symbols, medallion patterns, circular emblems, photorealistic, "
"3d render, text, watermark")

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
