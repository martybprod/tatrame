import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_19_Rayonnement_v1_jardin"
SEED = 777045

# XIX · RAYONNEMENT — concept "LE JARDINIER DE LUMIÈRE" : le soleil pousse, il ne se lève pas
positive = ("A kneeling woman gardener in her garden at early morning, sleeves rolled up, wearing a "
"simple apron, her face lit with a quiet, simple joy. In the center of the garden, on a tall "
"green stem growing from the earth, blooms a small living sun — a radiant sun-flower whose "
"warm rays illuminate the entire scene, all the light of the card coming from this cultivated "
"blossom; the sky above remains a pale dawn, still faint. The sun-flower has a soft gentle "
"face, alive and benevolent, glowing gold. A watering can rests against the stem, drops of "
"water catching the light like sparks. At the foot of the stem, a few tight closed buds wait "
"— future suns not yet open. A few bees circle the sun-flower, drawn to its light like "
"nectar. The garden flowers all around lean gently toward the sun-flower rather than toward "
"the sky, their faces turned to the cultivated light. The whole image is framed by an ornate "
"Art Nouveau golden border with flowing organic whiplash lines and delicate openwork corners "
"— the scene's own garden and sky show through the corner ornaments, no white or solid fill "
"anywhere in the border. The woman drawn in the flat decorative style of Alphonse Mucha — "
"bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat "
"areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on "
"textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike "
"mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, "
"muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, "
"not airbrushed.")

negative = ("sun in the sky, sun rising on the horizon, sunlight from above, sky brighter than the "
"garden, old man, elderly face, child, naked child, horse, praying mantis, cascade of flowers "
"falling from the sky, angels, cherubs, putti, winged figures in corners, corner figures, "
"decorative figures in upper corners, clouds with figures, rainbow, rainbow arc, rainbow "
"gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, extra leg, third leg, "
"two left legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, third "
"arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, two women, "
"couple, random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative "
"rune circles, meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, "
"circular emblems, white corners, white medallions in the corners, solid filled corners, "
"photorealistic, 3d render, text, watermark")

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
