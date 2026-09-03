import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

# Ancre de style CORRIGEE : palette complete equilibree, PAS d'arc-en-ciel objet
STYLE = ("The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of "
"warm and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

# Prompt du Fou : "rainbow river" -> "river" (plus d'arc-en-ciel objet)
positive = ("A single solitary young man captured mid-stride, in the very act of stepping his leading foot "
"off the edge of a high cliff into empty air, one leg extended forward over the abyss with no ground "
"beneath it, body leaning into the open void, his face refined and serene, gently holding one white rose. "
"He wears a long flowing coat softly patterned with the four elemental colors — red, blue, grey, green. "
"A single small white dog stands alert at the cliff edge behind him. Below, a luminous winding river "
"flows through misty valleys, a pale dawn sun glows through haze, a single white bird drifts across the "
"sky, distant mountains fade into mist. " + STYLE)

neg_base = "two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render"
neg_rainbow = "rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band"
neg_anat = ("extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, "
"malformed anatomy, bad anatomy, disfigured, mutated, " + neg_rainbow + ", " + neg_base)

SEED = 202
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
    path = OUTDIR + f"exp_00_confiance_PALETTE_seed{SEED}.png"
    with open(path, "wb") as f:
        f.write(raw)
    print(f"OK -> {path}  ({round(time.time()-t0,1)}s)")
else:
    print("ECHEC: pas d'image")
