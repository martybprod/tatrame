import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_14_Equilibre_v6"
SEED = 777038

positive = ("Exactly one eagle and exactly one swan stand together above still water, at the exact "
"threshold where night meets day — one half of the sky still deep indigo with stars, the other half "
"warming into golden dawn. There is only one eagle and only one swan in this image, never two of the "
"same bird. The eagle dips one talon lightly into the water, while the swan rests one foot on the "
"grassy shore — each briefly touching the other's element. The eagle's powerful wings and the swan's "
"graceful curve merge into a single balanced, flowing shape above the water. An invisible enchanted "
"mirror lies beneath the water's surface, tilted diagonally rather than straight down — because of "
"this diagonal orientation, each bird's reflection appears on the opposite diagonal side of the pond "
"rather than directly beneath itself. Following this diagonal mirror, the eagle's reflection appears "
"in the water on the swan's side, near where the swan stands above — a complete, whole eagle shape "
"reflected there. And the swan's reflection appears in the water on the eagle's side, near where the "
"eagle stands above — a complete, whole swan shape reflected there. The two birds above remain "
"entirely themselves, distinct and unmixed; the diagonal mirror simply redirects where each "
"reflection lands. In the distance, a luminous path winds toward far mountains crowned by a radiant "
"rising sun. No human figure. Flat decorative Art Nouveau illustration style, bold elegant clean "
"contour lines, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted "
"watercolor on textured paper, visible paper grain and pigment bleeds, mystical dreamlike mood, a "
"rich complete color palette spanning the full range of warm and cool hues, harmoniously balanced and "
"distributed naturally across the scene according to its mood, muted jewel tones, subtle gold "
"linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("reflection directly below itself, straight mirror, eagle reflected under eagle, swan "
"reflected under swan, normal reflection, self reflection, two swans, two eagles, twin swans, twin "
"eagles, duplicate swan, duplicate eagle, hybrid creature, chimera, mixed animal, swan head on eagle "
"body, eagle head on swan body, merged animal, fused creature, human figure, person, people, extra "
"leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, "
"third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad anatomy, "
"disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic "
"streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical glyphs, "
"decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion "
"patterns, circular emblems, text, watermark, photorealistic, 3d render")

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
