import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

STYLE = ("The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, Art Nouveau, mystical dreamlike nocturnal mood, muted jewel-tone palette with the full rainbow "
"spectrum woven softly throughout in varying proportions, subtle gold linework, soft misty atmosphere, "
"not photorealistic, not 3d, not airbrushed.")

positive = ("A single serene young woman seated at the center of the scene, alone, the only person, her "
"face calm, alert and watchful, gazing softly forward like an inner oracle. She holds a clear luminous "
"crystal cupped between her two hands — her left hand in shadow, her right hand in light — expressing "
"acceptance of both dark and light. She wears a flowing kimono-like robe adorned with green leaves, and a "
"delicate crescent-moon crown rests on her brow. Behind her rises a deep starry night cosmos; below her, "
"two dolphins dance and dive through luminous rippling water. She is framed by two slender pillars, one "
"dark and one pale. " + STYLE)

neg_base = "two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render"
neg_anat = ("extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, "
"malformed anatomy, bad anatomy, disfigured, mutated, " + neg_base)

SEED = 404
payload = {
    "prompt": positive, "negative_prompt": neg_anat,
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
    path = OUTDIR + f"exp_02_voix_interieure_V2_seed{SEED}.png"
    with open(path, "wb") as f:
        f.write(raw)
    print(f"OK -> {path}  ({round(time.time()-t0,1)}s)")
else:
    print("ECHEC: pas d'image")
