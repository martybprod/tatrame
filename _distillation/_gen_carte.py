import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v9"
SEED = 777025

positive = ("Exactly three geometric shapes appear in this image, no more: one square, one circle, one "
"triangle. The composition is dominated by a large figure: a young man, filling most of the frame, "
"climbing head-first down out of a small ornamental Art Nouveau frame that hangs inverted (rotated 180 "
"degrees) in the upper middle of the composition — the frame's miniature landscape of earth and roots "
"literally hangs upside down inside it, ground pointing up. One of his legs remains inside the small "
"inverted frame while his head, both arms and most of his body fill the lower two thirds of the image, "
"climbing down and out into open luminous space, both arms reaching forward and down like a careful "
"explorer feeling his way into the unknown. High on his upper back, just below the shoulder blades and "
"far from his armpits, grow two tiny nascent wings — each merely two or three small downy feathers, "
"like the first sprouting plumage of a fledgling bird, minuscule against his body. Floating near him: "
"exactly one glowing square (soft green), exactly one glowing circle (soft blue), exactly one glowing "
"triangle (soft gold) — these three only, no other geometric forms anywhere. Around everything, open "
"luminous sky with soft radiant light, no outer border. His expression is calm and curious. He wears "
"simple timeless clothing, a loose shirt, no jacket, no modern clothing. The figure drawn in the flat "
"decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, "
"flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted "
"watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike "
"mood, a rich complete color palette spanning the full range of warm and cool hues, harmoniously "
"balanced and distributed naturally across the scene according to its mood, muted jewel tones, subtle "
"gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("wings at armpits, wings on arms, large wings, big wings, medium wings, wings spread, "
"feathered wings, angel wings, diamond shape, rhombus, two triangles, multiple triangles, two squares, "
"two circles, four shapes, extra geometric shapes, hexagon, octagon, star shape, double frame, second "
"frame, outer border, image border, right side up frame, upright frame, upright landscape, limp arms, "
"arms hanging down, invisible leg, hidden leg, missing leg, extra limbs, duplicated limbs, hanged man, "
"rope around ankle, jeans, modern clothing, jacket, blazer, sneakers, boots, extra leg, third leg, two "
"left legs, missing foot, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra "
"hand, floating hand, malformed hands, fused fingers, extra finger, deformed wing, malformed anatomy, "
"bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, "
"prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical "
"glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d "
"render, too much empty space")

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
