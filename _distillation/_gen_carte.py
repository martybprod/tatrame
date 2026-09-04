import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v5"
SEED = 777018

positive = ("A vast cosmic wheel filling the composition, its spokes woven like threads on a great loom "
"radiating out from a still center marked by a yin-yang symbol. A still sphinx sits perched at the very "
"top of the wheel, seen in a slight three-quarter profile, its body naturally proportioned with a "
"single tail curving gracefully behind it — not perfectly symmetrical, not doubled, silent guardian of "
"destiny's riddle. A single small and discreet serpent, only one serpent, winds elegantly around the "
"outer ring of the wheel itself, coiled within the wheel's outer circumference, its body following the "
"circular rim in smooth, sinuous curves, small in scale and subdued in color so it blends into the "
"wheel rather than standing out. Galaxies and stars spin around the wheel's outer rim, the twelve "
"zodiac signs etched along its circumference, faint I Ching trigrams nested just inside them, and four "
"soft glowing compass-point markers indicating the cardinal directions closer to the center — small, "
"elegant, diamond-like points of light, not lightning bolts, not zigzag shapes. An upward-pointing "
"triangle glows faintly at the hub. No human figure — the wheel itself is the subject, vast and "
"turning. Flat decorative Art Nouveau illustration style, bold elegant clean contour lines, flat areas "
"of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed naturally across "
"the scene according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("lightning, thunderbolt, lightning bolt, zigzag bolt, zigzag shape, lightning rod, two "
"serpents, two snakes, multiple snakes, serpents on spokes, serpent on spoke, large serpent, prominent "
"snake, oversized snake, bold serpent, two tails, double tail, symmetrical sphinx, perfectly mirrored "
"sphinx, duplicated body, human figure, person, people, extra leg, third leg, two left legs, duplicated "
"limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, "
"extra hand, floating hand, malformed hands, fused fingers, extra finger, extra wing, three wings, "
"deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow "
"gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic "
"circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
"patterns, embroidered symbols, medallion patterns, circular emblems, text, watermark, photorealistic, "
"3d render")

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
