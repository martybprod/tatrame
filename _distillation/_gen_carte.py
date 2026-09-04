import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_12_Perspective"
SEED = 777020

positive = ("A man depicted upside down yet at peace, wearing simple timeless clothing with a loose "
"shirt and simple trousers, no modern clothing, no jacket, suspended gently by one bare foot from the "
"branch of a great tree, arms elegantly crossed behind his back, a faint halo of soft light glowing "
"around his head. His roots still connect him to the earth below while wings begin to grow from his "
"shoulders, reaching toward the boundless sky above. Around his body float three glowing geometric "
"shapes — a square (the physical, the known), a circle (the unmanifest, pure spirit), and a triangle "
"(the threefold nature of existence) — each casting soft colored light. His expression is calm, "
"curious, seeing everything from a completely new angle. The figure drawn in the flat decorative style "
"of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental "
"hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on "
"textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced and "
"distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("jeans, modern clothing, jacket, blazer, sneakers, boots, extra leg, third leg, two left "
"legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, extra wing, "
"three wings, deformed wing, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, "
"rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, "
"magic circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
"patterns, embroidered symbols, medallion patterns, circular emblems, two people, twins, duplicate "
"person, multiple figures, text, watermark, photorealistic, 3d render")

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
