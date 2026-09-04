import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_06_Union_v6"
SEED = 777009

positive = ("Two men who are close friends, clearly different from each other in appearance — one with "
"short dark curly hair and a short beard, sturdy build; the other with longer light wavy hair, "
"clean-shaven, leaner build — not look-alikes, not twins. They stand together firmly clasping each "
"other's forearm in a warrior's grip of trust and loyalty, each resting their other hand on the other's "
"shoulder, looking at each other with mutual respect and quiet confidence rather than romantic longing. "
"Both wearing flowing ancient-style robes, their feet bare, no modern clothing. Rising slightly off the "
"ground together. Surrounded by a soft gradient of light that shifts from warm earthen tones below to "
"luminous pale sky tones above. Behind them stand two trees — one heavy with ripe fruit, the other bare "
"and graceful — with a small serpent coiled peacefully at the base of one, a symbol of wisdom rather "
"than danger. A radiant sun glows softly off to one side in the background sky. Delicate wings of light "
"unfold from each of their backs as they rise together. The figures drawn in the flat decorative style "
"of Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental "
"hair, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on "
"textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced and "
"distributed naturally across the scene according to its mood, muted jewel tones, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("twins, identical faces, identical appearance, look-alike, same face, clones, romantic "
"couple, embracing, hugging, kissing, wedding pose, gazing longingly, trousers, pants, boots, shoes, "
"modern clothing, jeans, extra leg, third leg, two left legs, duplicated limb, missing foot, missing "
"leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, "
"malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed "
"anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, "
"rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, "
"mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, "
"medallion patterns, circular emblems, text, watermark, photorealistic, 3d render")

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
        print("ECHEC: pas d'image. Cles reponse:", list(out.keys()), "contenu:", str(out)[:500])
except Exception as e:
    print("ERREUR:", repr(e))
