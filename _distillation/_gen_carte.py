import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_14_Equilibre_v4"
SEED = 777037

positive = ("A magical, impossible pond lies below, its still surface reflecting a riddle: exactly "
"where the eagle stands above, the water below reflects a swan — a complete, separate, whole swan "
"shape, not a blend, not a hybrid, not merged with the eagle in any way. And exactly where the swan "
"stands above, the water below reflects a complete, separate, whole eagle shape, not a blend, not "
"merged with the swan. The two birds above remain entirely themselves, distinct and unmixed, each "
"with its own unmistakable head and body; only their reflections in the water are swapped. An eagle "
"and a swan intertwined mid-flight over this calm water, at the exact threshold where night meets day "
"— one half of the sky still deep indigo with stars, the other half warming into golden dawn. The "
"eagle dips one talon lightly into the water, while the swan rests one foot on the grassy shore — "
"each briefly touching the other's element. The eagle's powerful wings and the swan's graceful curve "
"merge into a single balanced, flowing shape. In the distance, a luminous path winds toward far "
"mountains crowned by a radiant rising sun. No human figure. Flat decorative Art Nouveau illustration "
"style, bold elegant clean contour lines, flat areas of soft watercolor pigment, minimal shading. "
"Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, mystical "
"dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel "
"tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("hybrid creature, chimera, mixed animal, swan head on eagle body, eagle head on swan "
"body, merged animal, fused creature, eagle reflected under eagle, swan reflected under swan, normal "
"reflection, self reflection, human figure, person, people, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, extra "
"wing, three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, "
"rainbow arc, rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random "
"occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, circular emblems, "
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
