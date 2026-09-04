import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_13_Transformation_v2"
SEED = 777032

positive = ("An immense, gently glowing translucent chrysalis hangs suspended above a vast flower of "
"the void, radiant with a soft inner light that hints at the being taking form within, not yet "
"emerged — the very moment of metamorphosis. Around the base of the chrysalis, a snake is caught "
"mid-shedding, its old translucent skin peeling away to reveal fresh scales beneath, a vivid image of "
"transformation itself. A sword that cuts through illusion rests nearby, its blade catching soft "
"light. A broken chain lies loosely draped below the chrysalis, no longer binding anything, finally "
"released. A small yin-yang symbol glows softly exactly where the chrysalis touches the flower. A "
"single white rose blooms beside it on the same stem. In the misty distance, the pale silhouette of a "
"white horse can just be glimpsed passing through the fog, a quiet passage rather than anything "
"macabre. No human figure anywhere in the composition. Flat decorative Art Nouveau illustration "
"style, bold elegant clean contour lines, flat areas of soft watercolor pigment, minimal shading. "
"Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, mystical "
"dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel "
"tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("human figure, person, people, skeleton, skull, grim reaper, dead body, corpse, macabre, "
"scary, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, "
"fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, "
"disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic "
"streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical glyphs, "
"decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, text, watermark, photorealistic, 3d render")

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
