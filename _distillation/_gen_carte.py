import json, urllib.request, base64, time
from PIL import Image
import io

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v13"
SEED = 777029

positive = ("A young man emerging upward and outward from a small rectangular frame shaped like a "
"miniature version of a tarot card (proportioned tall like 2 by 3), right side up, richly decorated "
"with ornate flowing Art Nouveau border details — gold linework, elegant curling flourishes — "
"containing a small ordinary landscape of gentle hills and a single tree. This small ornamental frame "
"is centered in the middle of the image, modestly sized, roughly one quarter of the composition. The "
"man's body is clearly and fully emerging well beyond the frame's upper edge — his entire torso, both "
"arms, and head extend far above and outside the frame, unmistakably breaking free of its boundary — "
"only his hips and legs remain inside or just behind the frame. He reaches upward and outward with "
"both arms in a slow, gentle, wonder-filled ascension, not an athletic leap, not a triumphant pose. "
"There is absolutely no other frame, border, or edge decoration anywhere else in the entire image — "
"everywhere outside this one small ornate frame is open luminous sky with soft radiant light, "
"completely borderless. Exactly three small glowing geometric shapes float nearby: one square (soft "
"green), one circle (soft blue), one triangle (soft gold) — these three only. High on his upper back, "
"precisely at the shoulder blades, two minuscule wing-buds are attached — each no bigger than a "
"thumb, just a few small downy feathers, barely noticeable, symmetrically placed one on each shoulder "
"blade. He wears simple timeless clothing, a loose shirt, no jacket, no modern clothing. His "
"expression is serene, quietly awed, absorbed in wonder — not smiling triumphantly, not heroic. The "
"figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, "
"stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("superhero pose, heroic pose, triumphant pose, action pose, diving pose, athletic leap, "
"cape, figure still fully inside frame, small figure, outer border, image border, full-image card "
"frame, border around entire image, second frame, double frame, plain frame, undecorated frame, large "
"wings, big wings, medium wings, wings at armpits, asymmetric wings, feathered wings, angel wings, "
"diamond shape, rhombus, two triangles, multiple triangles, two squares, two circles, four shapes, "
"extra geometric shapes, jeans, modern clothing, jacket, blazer, sneakers, boots, extra leg, third "
"leg, two left legs, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, deformed "
"wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, "
"rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, two people, twins, duplicate person, multiple figures, "
"text, watermark, photorealistic, 3d render")

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
        upright_path = OUTDIR + f"CARTE_{NAME}_UPRIGHT_seed{SEED}.png"
        with open(upright_path, "wb") as f:
            f.write(raw)
        # pivoter 180 degres pour obtenir la version finale tete en bas
        im = Image.open(io.BytesIO(raw))
        im_flipped = im.rotate(180)
        final_path = OUTDIR + f"CARTE_{NAME}_seed{SEED}.png"
        im_flipped.save(final_path)
        print(f"OK -> endroit: {upright_path}")
        print(f"OK -> pivote 180 (FINAL): {final_path}  seed={SEED}  ({round(time.time()-t0,1)}s)")
    else:
        print("ECHEC: pas d'image. contenu:", str(out)[:300])
except Exception as e:
    print("ERREUR:", repr(e))
