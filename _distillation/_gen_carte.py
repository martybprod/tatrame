import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v7"
SEED = 777024

positive = ("A single small ornamental Art Nouveau frame, rotated a full 180 degrees upside down "
"together with everything it contains — its miniature landscape of earth, roots and gentle hills "
"literally hangs inverted, its ground pointing toward the top of the image and its sky toward the "
"bottom. The frame floats centered in the middle of the composition, about one third of its size. "
"There is no other frame or border anywhere — the space outside this one small frame is completely "
"open. A young man climbs head-first down out of this inverted frame, like stepping out of a window "
"into open space: his left leg remains clearly visible inside the frame, planted on the inverted "
"ground, while his right leg has stepped fully outside below it — both legs entirely visible and "
"distinct, one in each world. His head, shoulders and both arms have emerged into the open luminous "
"space, arms stretched forward and downward, reaching out tentatively, feeling his way into the "
"unknown like a careful explorer. Exactly three glowing geometric shapes float around him, one of each "
"only: a single square (the physical, the known, soft green light), a single circle (the unmanifest, "
"pure spirit, soft blue light), and a single upward-pointing triangle (the threefold nature of "
"existence, soft golden light) — no other geometric shapes of any kind anywhere. Tiny, barely visible "
"miniature wings, no larger than a small bird's, sprout from his shoulders. All around, filling the "
"rest of the image to its very edges with no border: boundless luminous freedom, soft radiant light, "
"open sky. His expression is calm and curious. He wears simple timeless clothing, a loose shirt, no "
"jacket, no modern clothing. The figure drawn in the flat decorative style of Alphonse Mucha — bold "
"elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of soft "
"watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible "
"paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally across "
"the scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("diamond shape, rhombus, two triangles, two squares, two circles, four shapes, extra "
"geometric shapes, double frame, second frame, outer border, image border, right side up frame, upright "
"frame, upright landscape, large wings, big wings, limp arms, arms hanging down, dangling arms, "
"invisible leg, hidden leg, missing leg, extra limbs, duplicated limbs, hanged man, rope around ankle, "
"jeans, modern clothing, jacket, blazer, sneakers, boots, extra leg, third leg, two left legs, missing "
"foot, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, "
"malformed hands, fused fingers, extra finger, deformed wing, malformed anatomy, bad anatomy, "
"disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic "
"streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical glyphs, "
"decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d "
"render")

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
