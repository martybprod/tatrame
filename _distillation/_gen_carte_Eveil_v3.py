import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "master_Eveil_v3_rayons_vallee"
SEED = 777066

# ÉVEIL (hors cycle) — v3. Retour terrain sur v2 : (a) pas clair que le maitre illumine les
# autres -> abandon du "fil qui emprunte sa lumiere en passant" (trop subtil), remplace par un
# principe direct : plusieurs rayons dores partent visiblement de LUI et descendent jusqu'a
# chaque tisserand distant (sens de lecture LUI -> EUX sans ambiguite) ; (b) le rayon sortant
# de son coeur avait un contour noir en v2 -> explicitement banni, la lumiere n'a pas de trait.
positive = ("A serene older man with a flowing beard, standing calmly on a high rocky outcrop "
"overlooking a wide valley below, seen from a slightly lower angle so the sky and valley "
"both read clearly around him. He wears a simple flowing tunic of undyed natural linen with "
"a loosely draped shawl over one shoulder, timeless and plain, bare feet, no modern clothing "
"of any kind. His hands rest open at his sides, no loom in front of him. Behind him, a tall "
"wooden frame holds his own completed tapestry — a finished, radiant, radially symmetric "
"mandala woven in every color. From his chest, several distinct golden rays of pure soft "
"light fan outward and downward across the sky like spokes, each ray a smooth glowing line "
"entirely without outline or contour — pure luminous gold with soft feathered edges, never a "
"hard black border around the light itself, unlike the clean flat outlines used for the rest "
"of the illustration. Each golden ray travels down into the valley below and arrives at a "
"different small distant loom, gently illuminating the tiny weaver working there — visibly "
"brightening that loom and the single pure-colored thread in the weaver's hands — before the "
"weaver's own color reasserts itself past the point of contact; his light touches and warms "
"each distant weaving without ever changing its color or taking hold of it. The visual "
"connection between him and each illuminated weaver below is unmistakable and clearly "
"readable at a glance. His expression is deeply calm, eyes open, gaze lowered toward the "
"valley with quiet warmth. The whole image framed by an ornate Art Nouveau golden border "
"with flowing organic whiplash lines and delicate openwork corners echoing the fan of rays "
"— the scene's own landscape and sky show through the corner ornaments, no white or solid "
"fill anywhere in the border. The figure drawn in the flat decorative style of Alphonse "
"Mucha — bold elegant clean contour lines on the figure and landscape only, stylized "
"idealized mature features, flowing hair and beard, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain "
"and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene, muted jewel tones, subtle gold linework, soft misty atmosphere, "
"not photorealistic, not 3d, not airbrushed.")

negative = ("black outline around light ray, black contour on glow, outlined beam of light, "
"hard edge on light ray, dark border around golden light, comic-book style light beam, "
"ambiguous illumination, disconnected rays, rays not reaching the valley, "
"modern clothing, contemporary clothing, shirt, dress shirt, collared shirt, "
"trousers, pants, jeans, suit, jacket, blazer, robe with modern cut, shoes, boots, sneakers, "
"sandals, wristwatch, "
"lotus flower, concentric rings of light, halo, aura rings, permanent glowing aura, "
"chrysalis, cocoon, butterfly, disciples gathered around him, followers, hierarchy, throne, "
"crown, staff, scepter, third eye mark, bindi, painted eye on forehead, loom in front of him, "
"weaving tool in his hands, shuttle, beater, active weaving, working a loom, second man, "
"another man in foreground, multiple men, woman, female figure, young man, child, old "
"decrepit man, hunched, frail, rainbow arc in sky, literal rainbow across the sky, "
"flat frontal portrait, centered symmetrical composition, static pose, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune "
"circles, meaningless icons, esoteric patterns, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom "
"hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra "
"finger, malformed anatomy, bad anatomy, disfigured, mutated, white solid border, plain "
"white frame, solid filled border, no border, text, watermark, photorealistic, 3d render")

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
