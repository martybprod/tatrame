import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_08_Courage"
SEED = 777016

positive = ("A single small wildflower growing directly out of a crack between harsh grey stones, its "
"petals fully open toward the light, surrounded by a bright golden halo of glow as if it shone as "
"brightly as the sun itself. A small wildcat lies peacefully asleep right beside the flower, utterly "
"calm, not tamed by force but gentled by presence. A delicate ribbon of light curls into an infinity "
"shape floating just above the halo. The rocks around it are rugged and unforgiving, but the flower "
"stands unashamed and luminous. No human figure, close-up nature composition. Flat decorative Art "
"Nouveau illustration style, bold elegant clean contour lines, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, mystical dreamlike mood, a rich complete color palette spanning the full range of warm and cool "
"hues, harmoniously balanced and distributed naturally across the scene according to its mood, muted "
"jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("human figure, person, people, extra leg, third leg, two left legs, duplicated limb, missing "
"foot, missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, "
"malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, alchemical "
"sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered "
"symbols, medallion patterns, circular emblems, text, watermark, photorealistic, 3d render")

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
