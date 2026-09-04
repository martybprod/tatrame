import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_01_Existence"

positive = ("A serene young woman reclining peacefully on a bed of soft moss and intertwining roots beneath "
"a vast starry night sky, one arm trailing gently in a still clear pool of water, small fish swimming near "
"her hand, birds resting nearby in flowering branches, a sense of deep belonging and kinship with every "
"creature around her, her expression calm and fully at home. Overhead, the star-threads and hanging vines "
"seem to softly interweave above her like a delicate natural canopy. The figure drawn in the flat "
"decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, "
"flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted "
"watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike "
"mood, a rich complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, "
"disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic "
"streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical glyphs, "
"decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, "
"circular emblems, two people, twins, duplicate person, multiple figures, text, watermark, "
"photorealistic, 3d render")

SEED = -1  # aleatoire, on garde celui qui sortira
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
    path = OUTDIR + f"CARTE_{NAME}.png"
    with open(path, "wb") as f:
        f.write(raw)
    print(f"OK -> {path}  ({round(time.time()-t0,1)}s)")
else:
    print("ECHEC: pas d'image")
