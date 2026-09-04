import json, urllib.request, base64, time
from PIL import Image
import io

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective_v16"
SEED = 777030

positive = ("A young man swimming forward through open air in a graceful breaststroke-like motion, both "
"arms extended forward and slightly downward together as if parting the air ahead of him — not raised "
"overhead, not looking skyward, no gesture of worship or adoration. His gaze is directed forward "
"toward the unknown horizon ahead of him, not upward. His torso leans forward in the direction of this "
"swimming motion, emerging close to a small rectangular frame shaped like a miniature version of a "
"tarot card (proportioned tall like 2 by 3), right side up, richly decorated with ornate flowing Art "
"Nouveau border details — gold linework, elegant curling flourishes — containing a small ordinary "
"landscape of gentle hills and a single tree. This small ornamental frame is centered in the middle of "
"the image, modestly sized, roughly one quarter of the composition. His torso, both arms and head "
"extend just beyond the frame's edge, still close to it, into the open space right around the frame. "
"One of his feet has just stepped across the frame's lower edge, planted right at the boundary, "
"clearly crossing the frame's border line but staying close to the frame itself — not flying away into "
"the distance, simply the single clear action of a foot stepping out — while his other leg remains "
"inside the frame, planted on the small landscape within it — the unmistakable moment of climbing out, "
"one foot in each world, right at the threshold. He wears a knitted vest and 1920s-1930s style "
"plus-four knickerbocker trousers — loose knee-length trousers gathered just below the knee — with his "
"calves and feet completely bare, no socks, no shoes. There is absolutely no other frame, border, or "
"edge decoration anywhere else in the entire image — everywhere outside this one small ornate frame is "
"a gorgeous, brilliant, luminous blue sky, radiant and beautiful, completely borderless. Exactly three "
"small glowing geometric shapes float nearby: one square (soft green), one circle (soft blue), one "
"triangle (soft gold) — these three only. High on his upper back, precisely at the shoulder blades, "
"two minuscule wing-buds are attached — each no bigger than a thumb, just a few small downy feathers, "
"barely noticeable, symmetrically placed one on each shoulder blade. His expression is serene, "
"focused, quietly determined, swimming forward with calm purpose into the unknown. The figure drawn in "
"the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized "
"features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, "
"mystical dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel "
"tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("flying far from frame, floating away from frame, distant from frame, leg far from frame, "
"leg detached from frame, socks, shoes, boots, dark sky, dull sky, grey sky, muted sky outside frame, "
"leg barely visible outside frame, leg mostly inside frame, arms raised overhead, arms straight up, "
"looking upward, looking skyward, worship pose, adoration pose, religious ecstasy, both legs inside "
"frame, both legs fully inside, figure entirely inside frame, outer border, image border, full-image "
"card frame, border around entire image, second frame, double frame, plain frame, undecorated frame, "
"large wings, big wings, medium wings, wings at armpits, asymmetric wings, feathered wings, angel "
"wings, diamond shape, rhombus, two triangles, multiple triangles, two squares, two circles, four "
"shapes, extra geometric shapes, jeans, modern clothing, jacket, blazer, sneakers, extra leg, third "
"leg, two left legs, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, deformed "
"wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, "
"rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, two people, twins, duplicate person, multiple figures, text, "
"watermark, photorealistic, 3d render")

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
