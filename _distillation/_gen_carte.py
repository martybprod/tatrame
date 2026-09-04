import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_03_Creativite_v3"
SEED = 777002

positive = ("A woman actively weaving with vivid multicolored threads of light stretched between her two "
"hands, visibly shaping and guiding them into an emerging pattern — a blossoming mandala-like form of "
"color taking shape in the air in front of her, still incomplete, threads crossing and curving with "
"dynamic motion. Her eyes are open, alive with focus, joy and creative energy; her body leans into the "
"act of creation, one arm raised higher than the other, her hair and the fabric of her dress caught "
"mid-movement as if stirred by a gust of creative energy. Below and around her feet, in a decorative "
"stylized ornamental spiral entirely separate from her body and clothing — like a painted mandala on the "
"ground, never touching or rising up her dress — swirling shapes of fire and water interweave together. "
"The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, "
"stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art "
"Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm and cool "
"hues, harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel "
"tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, flames touching body, flames "
"on dress, figure standing in fire, figure engulfed in flames, burning at the stake, witch burning, pyre, "
"fire licking clothing, random occult symbols, magic circles, alchemical sigils, mystical glyphs, "
"decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, "
"circular emblems, two people, twins, duplicate person, multiple figures, text, watermark, "
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
