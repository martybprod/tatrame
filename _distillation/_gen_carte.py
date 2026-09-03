import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

positive = ("A single solitary young man captured mid-stride, in the very act of stepping his leading foot "
"off the edge of a high cliff into empty air, one leg extended forward over the abyss with no ground "
"beneath it, body leaning into the open void, his face refined and serene, gently holding one white rose. "
"He wears a long flowing coat softly patterned with the four elemental colors — red, blue, grey, green. "
"A single small white dog stands alert at the cliff edge behind him. Below, a luminous winding rainbow "
"river flows through misty valleys, a pale dawn sun glows through haze, a single white bird drifts across "
"the sky, distant mountains fade into mist. The figure drawn in the flat decorative style of Alphonse "
"Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat "
"areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, muted jewel-tone palette "
"with the full rainbow spectrum woven softly throughout in varying proportions, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

neg_base = ("two people, twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render")
neg_anat = ("extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, "
"malformed anatomy, bad anatomy, disfigured, mutated, " + neg_base)

SEED = 202  # seed connu pour son defaut (pied manquant a 8 steps)

variants = [
    {"tag": "V1_st20_cfg1", "steps": 20, "cfg": 1,   "neg": neg_base},
    {"tag": "V2_st20_cfg3", "steps": 20, "cfg": 3.0, "neg": neg_anat},
]

def gen(v):
    payload = {
        "prompt": positive, "negative_prompt": v["neg"],
        "seed": SEED, "steps": v["steps"], "cfg_scale": v["cfg"],
        "width": 1024, "height": 1536,
        "sampler_name": "Euler A Trailing",
        "guidance_embed": 3.5, "shift": 3, "batch_size": 1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=400) as resp:
        out = json.loads(resp.read())
    imgs = out.get("images", [])
    if not imgs:
        return None
    raw = base64.b64decode(imgs[0])
    path = OUTDIR + f"exp_00_confiance_seed{SEED}_{v['tag']}.png"
    with open(path, "wb") as f:
        f.write(raw)
    return path, round(time.time()-t0,1)

for v in variants:
    try:
        r = gen(v)
        print(f"{v['tag']} -> {r[0]}  ({r[1]}s)" if r else f"{v['tag']} -> ECHEC")
    except Exception as e:
        print(f"{v['tag']} -> ERREUR {repr(e)}")
