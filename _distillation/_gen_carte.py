import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_20_Verite_v1_lampe"
SEED = 777046

# XX · VÉRITÉ — concept "LA LAMPE ALLUMÉE" : l'appel vient de soi, il se propage par contagion
positive = ("A woman standing at the top of an old stone staircase at nightfall, holding a small lit "
"oil lamp whose living golden flame lights the whole scene. Her face is serene, eyes open, "
"gazing calmly toward the village below — lucid and awake, not ecstatic. In the lamplight, "
"her own clothes are revealed in their true richness: what looked dark is showing woven gold "
"threads and deep colors, revealed only by her own light. Descending the staircase, a village "
"lies below, and in answer to her lamp, other small lamps are lighting up by themselves in "
"windows and doorways, one after another, windows glowing warm one by one — no one carried "
"the flame to them, each window awakening in response. Behind her, on the upper steps, the "
"darkness remains thick and unlit — what is not yet illuminated simply waits. A single moth "
"circles her lamp, drawn to the flame — the beginning of the path, not a mistake. The whole "
"image is framed by an ornate Art Nouveau golden border with flowing organic whiplash lines "
"and delicate openwork corners — the scene's own night sky and village show through the "
"corner ornaments, no white or solid fill anywhere in the border. The woman drawn in the "
"flat decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized "
"idealized features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("angel, trumpeting angel, trumpet, horn, rising dead, open graves, coffins, skeletons, "
"cross in the sky, religious iconography, butterfly, large butterfly in foreground, closed "
"eyes, third eye, lotus on forehead, old man, child, sun, sun in the sky, daylight scene, "
"angels, cherubs, putti, winged figures in corners, corner figures, decorative figures in "
"upper corners, clouds with figures, rainbow, rainbow arc, rainbow gradient, rainbow river, "
"rainbow sky, prismatic streak, spectrum band, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom "
"hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra "
"finger, malformed anatomy, bad anatomy, disfigured, mutated, two women, couple, random "
"occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, esoteric patterns, embroidered symbols, medallion patterns, circular "
"emblems, white corners, white medallions in the corners, solid filled corners, "
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
