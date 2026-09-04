import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v5"
SEED = 777022

positive = ("The entire composition is upside down. A small ornamental Art Nouveau frame sits centered "
"in the middle of the image, about one third of the composition, itself inverted upside down — inside "
"it, a tiny miniature world of earth, roots and familiar landscape, hanging inverted. A young man hangs "
"head-down out of this small frame, like stepping out of a window into open space: one leg still inside "
"the frame while his head and both arms have emerged below it into the open luminous space, caught in "
"the simple single clear action of crawling out. He has exactly two arms, two hands and two legs, "
"anatomically correct and simple. Around him float three glowing geometric shapes — a square, a "
"circle, and a triangle — each casting soft colored light. All around, filling the rest of the image: "
"boundless luminous freedom, soft radiant light, open sky. Small wings are just beginning to sprout "
"from his shoulders, still unfurling. His expression is calm and curious, seeing everything from a "
"completely new angle. He wears simple timeless clothing, a loose shirt, no jacket, no modern clothing. "
"The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, "
"stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("extra limbs, duplicated limbs, doubled arms, doubled legs, complex twisted pose, "
"contorted pose, upright composition, right side up, full-edge border, frame at image edge, hanging by "
"foot, hanged man, rope around ankle, jeans, modern clothing, jacket, blazer, sneakers, boots, extra "
"leg, third leg, two left legs, missing foot, missing leg, missing limb, extra arm, third arm, phantom "
"hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, "
"extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, "
"rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random "
"occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, two people, twins, "
"duplicate person, multiple figures, text, watermark, photorealistic, 3d render")

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
