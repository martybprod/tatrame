import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_04_Liberte_v3"
SEED = 777004

positive = ("A powerful young man standing atop a wind-swept mountain peak at the break of dawn, wearing "
"a flowing knee-length tunic with a sash, his legs and feet completely bare — no trousers, no boots, no "
"shoes — one bare foot resting on a broken chain lying shattered on the rock, a sun emblem embroidered on "
"his shoulder, holding a lit torch out to his side at chest height rather than raised overhead, its flame "
"streaming sideways in the wind, a golden signet ring visible on his other hand. Behind him stands a "
"weathered stone monolith carved with ram-head motifs, now cracked and overtaken by climbing green vines "
"— the old authority reclaimed by nature. Two large feathered wings spread open symmetrically behind him, "
"both clearly visible. Far off to the side, high in the open sky, an eagle circles at a distance, clearly "
"separate from his wings, a bridge between earth and heaven. His posture is proud, three-quarter view, "
"self-possessed rather than defiant. The figure drawn in the flat decorative style of Alphonse Mucha — "
"bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, visible "
"paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally across "
"the scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("trousers, pants, boots, shoes, modern clothing, one wing, single wing, missing wing, "
"asymmetric wings, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, "
"missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed "
"hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad "
"anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, "
"prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical "
"glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, circular emblems, two people, twins, duplicate person, multiple figures, text, watermark, "
"photorealistic, 3d render")

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
with urllib.request.urlopen(req, timeout=500) as resp:
    out = json.loads(resp.read())
imgs = out.get("images", [])
if imgs:
    raw = base64.b64decode(imgs[0])
    path = OUTDIR + f"CARTE_{NAME}_seed{SEED}.png"
    with open(path, "wb") as f:
        f.write(raw)
    print(f"OK -> {path}  seed={SEED}  ({round(time.time()-t0,1)}s)")
else:
    print("ECHEC: pas d'image")
