import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v10"
SEED = 777026

positive = ("A young man captured in mid-leap, dynamic and joyful, knees bent, one leg pushing off "
"behind him and the other extended forward, his whole body launching diagonally upward and outward in "
"an energetic jumping motion — like diving through a window into a new perspective, not hanging, not "
"dangling, a clear athletic leap. He is leaping out of a small rectangular frame shaped like a "
"miniature version of a tarot card (proportioned tall like 2 by 3), right side up, richly decorated "
"with ornate flowing Art Nouveau border details — gold linework, elegant curling flourishes — matching "
"the decorative style of a fine tarot card, containing a small ordinary landscape of gentle hills and a "
"single tree. This small ornamental frame is centered in the middle of the image, modestly sized, "
"roughly one quarter of the composition. There is absolutely no other frame, border, or edge decoration "
"anywhere else in the entire image — everywhere outside this one small ornate frame is open luminous "
"sky with soft radiant light, completely borderless with no edge decoration around the image itself. "
"Exactly three small glowing geometric shapes float near him in the open sky: one square (soft green), "
"one circle (soft blue), one triangle (soft gold) — these three only. High on his upper back, precisely "
"at the shoulder blades, two minuscule wing-buds are attached — each no bigger than a thumb, just a few "
"small downy feathers, barely noticeable. He wears simple timeless clothing, a loose shirt, no jacket, "
"no modern clothing. His expression is bright, excited, alive with the thrill of the leap. The figure "
"drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized "
"idealized features, flowing ornamental hair caught in the motion, flat areas of soft watercolor "
"pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full "
"range of warm and cool hues, harmoniously balanced and distributed naturally across the scene "
"according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("hanging, hanged man, dangling, limp legs, rope, suspended by foot, outer border, image "
"border, full-image card frame, border around entire image, second frame, double frame, inverted "
"frame, upside down frame, plain frame, undecorated frame, large wings, big wings, medium wings, wings "
"at armpits, feathered wings, angel wings, diamond shape, rhombus, two triangles, multiple triangles, "
"two squares, two circles, four shapes, extra geometric shapes, jeans, modern clothing, jacket, "
"blazer, sneakers, boots, extra leg, third leg, two left legs, missing foot, missing leg, missing "
"limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed "
"hands, fused fingers, extra finger, deformed wing, malformed anatomy, bad anatomy, disfigured, "
"mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, "
"spectrum band, random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative "
"rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, two "
"people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render")

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
