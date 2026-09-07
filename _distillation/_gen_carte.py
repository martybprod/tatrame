import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_16_Rupture_v2"
SEED = 777041

positive = ("A vast woven tapestry stretched on a tall wooden loom, filling the scene. The image woven "
"inside the tapestry: a proud, majestic stone tower rising to a great height, rendered as true woven "
"textile art — a clearly visible interlaced warp-and-weft thread texture, simplified flat stylized "
"shapes built from coarse colored threads, like a medieval tapestry, visibly distinct from the smooth "
"watercolor rendering of the rest of the scene. At this exact moment, a single vertical line of "
"white-golden light has torn the fabric from top to bottom, splitting the woven tower in two — the "
"tear is the lightning, the rupture itself is made of light, and true radiant light floods into the "
"scene through the opening. Along the tear, the weave is coming undone: loose threads free themselves "
"from the fabric and drift through the air, some floating gently toward the ground. A golden woven "
"crown at the tower's summit unravels and falls, its gold thread trailing behind it like a comet "
"tail. The edges of the tear glow softly with small orange embers — a quiet fire of purification, "
"subtle and contained. Two tiny woven figures from the tapestry tumble freely through the open air "
"beneath the torn fabric, falling straight down head over heels, thrown off as the weave unravels — "
"not sliding along the tear, but plummeting through the gap. Before the loom stands a real woman, "
"calm and still, bathed in the true light streaming through the tear, watching the weaving come "
"undone without fear. The woman and loom drawn in the flat decorative style of Alphonse Mucha — bold "
"elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color "
"palette spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold linework, soft "
"misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, "
"spectrum band, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, "
"missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, "
"malformed hands, fused fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, "
"two women, couple, romantic pair, lovers embracing, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, circular emblems, real people inside the tapestry, "
"photorealistic, 3d render, text, watermark")

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
