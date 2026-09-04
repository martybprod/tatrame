import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_13_Transformation_v3"
SEED = 777033

positive = ("An immense chrysalis hangs suspended above a vast flower of the void, softly glowing, its "
"surface translucent but thick and indistinct — inside it only a diffuse, featureless warm light "
"suggesting life taking form, no discernible anatomy, no limbs, no face visible at all. A single "
"elegant double-edged sword with a long clean blade and no pommel, one sword only, rests on the "
"flower at a clear distance from everything else, its blade catching soft light. Near the base, a "
"snake is caught mid-shedding, its old skin peeling away to reveal fresh scales — the sword and the "
"snake are clearly separated, the sword never touching or piercing the snake. A broken chain lies "
"loosely draped below the chrysalis, no longer binding anything, finally released. A small yin-yang "
"symbol glows softly exactly where the chrysalis touches the flower. A single white rose blooms "
"beside it on the same stem. Centered in the background behind the chrysalis, larger and clearly "
"visible, a pale white horse stands quietly in soft mist — not in a corner, not tiny, an important "
"presence centered on the horizon. No human figure anywhere in the composition. Flat decorative Art "
"Nouveau illustration style, bold elegant clean contour lines, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, mystical dreamlike mood, a rich complete color palette spanning the full range of warm and "
"cool hues, harmoniously balanced and distributed naturally across the scene according to its mood, "
"muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("human figure, person, people, visible anatomy, arms in chrysalis, body in chrysalis, "
"face in chrysalis, two swords, multiple swords, sword piercing snake, sword through snake, sword "
"impaling, skeleton, skull, grim reaper, dead body, corpse, macabre, scary, horse in corner, tiny "
"horse, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing "
"limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed "
"hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad "
"anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, "
"prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical "
"glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, text, watermark, photorealistic, 3d render")

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
