import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v3"
SEED = 777019

positive = ("A wide shot with the figure at medium scale within the frame, ample room around her for a "
"rich setting. A calm, resolute woman stands at the center of a serene open colonnade at dawn, holding "
"a straight double-edged sword perfectly upright before her like a vertical axis of clarity — the "
"precise moment a true decision settles. Soft golden dawn light streams through the columns and gently "
"illuminates her from the side, nothing glowing on her body itself. Beside her feet, resting "
"peacefully on the ground, an old pair of balance scales lies gently set down — no longer needed, not "
"broken, simply released. A long flowing red cloth trails from her shoulder in the morning wind. Her "
"expression is clear-eyed, precise, quietly certain — discernment rather than fury, no destruction, "
"nothing shattering anywhere. She wears a flowing timeless robe with bare feet, no modern clothing. "
"The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour lines, "
"stylized idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("glowing chest, glowing heart, red glow on body, light from solar plexus, energy from "
"chest, destruction, explosion, shattering walls, debris, rubble, crumbling architecture, chaos, "
"broken scales, close-up, figure filling the frame, trousers, pants, jeans, boots, shoes, sneakers, "
"modern clothing, jacket, blazer, extra leg, third leg, two left legs, duplicated limb, missing foot, "
"missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating "
"hand, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed "
"anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, "
"rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, alchemical "
"sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered "
"symbols, medallion patterns, circular emblems, two people, twins, duplicate person, multiple figures, "
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
        path = OUTDIR + f"CARTE_{NAME}_seed{SEED}.png"
        with open(path, "wb") as f:
            f.write(raw)
        print(f"OK -> {path}  seed={SEED}  ({round(time.time()-t0,1)}s)")
    else:
        print("ECHEC: pas d'image. contenu:", str(out)[:300])
except Exception as e:
    print("ERREUR:", repr(e))
