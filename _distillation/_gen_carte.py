import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v4"
SEED = 777021

positive = ("A young man, large in scale, straddling the edge of a small ornamental Art Nouveau frame — "
"the frame is small and tightly centered in the middle of the image, only about one third of the "
"composition, so the man's body is clearly larger than the frame itself. One of his legs is planted "
"inside the frame, standing on the tiny ordered miniature world of earth, roots and familiar landscape "
"within it, while his other leg has stepped fully outside the frame into the open luminous space "
"around it — caught mid-stride, genuinely crossing the boundary, one foot in each world. His body is "
"tilted sideways and upside down at an unusual angle, head hanging toward one side, so his whole "
"orientation defies ordinary perspective — the world itself seems to rotate around him. All around the "
"frame, filling the rest of the image: boundless luminous freedom, soft radiant light, open sky in "
"every direction. Small wings are just beginning to sprout from his shoulders, still unfurling. Around "
"him float three glowing geometric shapes — a square (the physical, the known), a circle (the "
"unmanifest, pure spirit), and a triangle (the threefold nature of existence) — each casting soft "
"colored light. His expression is calm, curious, exhilarated by the completely new angle from which he "
"now sees everything. He wears simple timeless clothing, a loose shirt, no jacket, no modern clothing. "
"The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, "
"stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("both legs inside frame, both legs outside frame, standing upright normally, full-edge "
"border, frame at image edge, large frame, hanging by foot, hanged man, rope around ankle, jeans, "
"modern clothing, jacket, blazer, sneakers, boots, extra leg, third leg, two left legs, duplicated "
"limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, "
"extra hand, floating hand, malformed hands, fused fingers, extra finger, extra wing, three wings, "
"deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow "
"gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic "
"circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
"patterns, embroidered symbols, medallion patterns, two people, twins, duplicate person, multiple "
"figures, text, watermark, photorealistic, 3d render")

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
