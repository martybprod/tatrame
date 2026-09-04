import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_06_Union_v12"
SEED = 777014

positive = ("Wide establishing shot, the two figures smaller within the frame, seen from a greater "
"distance so that much more of the sweeping landscape, sky, and cliff top is visible around them. Two "
"young male friends, both clearly youthful, clean-shaven, in their twenties — clearly two different "
"people, not twins, not matching outfits. The first is taller and broader-built, with short dark curly "
"hair, wearing a plain rolled-sleeve linen shirt and simple straight trousers. The second is shorter and "
"slimmer, with light wavy hair, wearing a knitted vest over his shirt and 1920s-1930s style plus-four "
"knickerbocker trousers — loose knee-length trousers gathered just below the knee, paired with tall "
"ribbed socks and two-tone brogue shoes typical of that era. Both are caught in the middle of joyful, "
"energetic motion, running side by side along the grassy top of a sunlit cliff, both laughing with wide "
"genuine smiles, arms thrown up in the air in playful triumph, captured mid-stride, dynamic and full of "
"life — no physical contact between them, no romantic mood, pure shared fun and exhilaration. As they "
"run, they pass between two trees — one heavy with ripe fruit, the other bare and graceful — with a "
"small serpent coiled peacefully near the roots of one, glimpsed briefly in their path, a symbol of "
"wisdom rather than danger. A radiant sun glows low on the horizon ahead of them, casting long joyful "
"shadows. The figures drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, dynamic flowing motion, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, lively "
"energetic mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted jewel "
"tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("close-up, figures filling the frame, mustache, facial hair, beard, older man, middle-aged, "
"twins, identical faces, identical clothing, matching outfits, same height, holding hands, touching, "
"embracing, hugging, kissing, romantic pose, romantic couple, wedding pose, gazing into each others "
"eyes, still pose, static pose, contemplative, dreamy stillness, wings, ancient robes, toga, tunic, long "
"coat, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, "
"extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, "
"rainbow gradient, rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, "
"magic circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
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
