import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v11_fil_a_plomb"
SEED = 777117

# XI · JUSTESSE — v9 "pire" : empiler des consignes de precision (alignement arc/fleche,
# fil continu en 3 segments) a degrade le resultat — meme pattern que la carte Changement,
# lecon deja documentee : une architecture simple plutot que l'accumulation. v10 : TOUTE
# la composition est reorganisee autour d'UN SEUL principe fondateur, la LIGNE VERTICALE
# ROUGE — elle traverse l'image entiere du bas (mains de la femme) au haut (centre de la
# cible), en passant par les ciseaux, le bord bas de la tapisserie et l'archer, tous
# POSes sur cette meme ligne. Description econome et directe, moins de mots par element.
positive = ("A wide shot with the figure at medium scale, set comfortably back from the "
"camera so the rich surroundings are clearly visible around her. The entire image is "
"built around one single straight vertical red line — a plumb line, hanging perfectly "
"vertical, exactly parallel to the left and right edges of the frame, running from "
"the very bottom of the frame to the very top of the frame, never interrupted at any "
"point along its length. Reading the image from bottom to "
"top: at the bottom, the hands of a calm, precise woman hold the lower end of this "
"red thread; a short distance above her hands, the thread passes between the wide-"
"open blades of the image's only pair of scissors — a single pair of fine weaver's "
"scissors held in her other hand, the blades clearly separated in a "
"V around the thread, not yet closing; the thread continues upward, enters the woven "
"tapestry stretched on a grand wooden loom — the largest object in the scene — and "
"inside the tapestry this same red plumb line becomes the flight path of an arrow: a "
"tiny "
"woven archer stands on the line at the bottom of the woven scene, bow drawn and "
"aiming straight up toward the very top of the image, and at the top of the woven "
"scene the red line ends at "
"the exact center of a woven archery target of concentric rings, the bullseye. One "
"line, bottom to top, through hands, scissors, tapestry, archer, and bullseye — "
"nothing breaks it, nothing branches off it, it never curves and never stops. The "
"woman's eyes are on the point where the scissors meet the thread, clear-eyed and "
"quietly certain, her posture composed and deliberate. The scene is set in a quiet "
"softly-lit weaver's workroom at morning: shelves with neatly wound yarn baskets, a "
"potted plant on the sill, warm morning light through a window falling on her hands "
"and the red line, nothing glowing on her body itself. She wears a beautiful flowing "
"artisan's gown with careful details — embroidered bodice, full sleeves gathered at "
"the forearm, layered skirts in warm muted teal, rust and cream, a woven sash at the "
"waist, bare feet, no modern clothing. On the floor beside the loom rests an old "
"brass balance scale with its two hanging pans clearly visible, one pan on each side "
"of the central beam, a complete classic two-pan balance, set down and gently "
"released, still intact but simply no longer needed, quietly abandoned — the old way "
"of judging, laid aside. The whole image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners — the "
"scene's own soft room light shows through the corner ornaments, no white or solid "
"fill anywhere in the border. The figure drawn in the flat decorative style of "
"Alphonse Mucha — bold elegant clean contour lines, stylized idealized mature "
"features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold "
"linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("single-pan scale, one pan only, missing pan, incomplete scale, "
"red thread floating over the landscape, red line added on top of the tapestry, red "
"string crossing the woven scene without being part of it, "
"broken scale, shattered scale, damaged balance scale, destruction, "
"explosion, debris, shattering, falling masonry, sword, blade, weapon, glowing body, "
"glowing plexus, glowing chest, red light on skin, fiery aura, "
"modern clothing, contemporary clothing, trousers, jeans, shoes, boots, sneakers, "
"wristwatch, jewelry, second person, man, crowd, child, "
"cut thread, severed thread, thread already cut, two threads, two separate red "
"threads, thread gap, thread interrupted, broken thread, thread ending at the "
"scissors, thread not passing through the scissors, bow not aligned with the arrow, "
"bow aimed sideways, mismatched trajectory, tangled threads, knots, "
"closed scissors, scissors mid-cut, scissors already cutting, blades touching, closed "
"blades, two pairs of scissors, second pair of scissors, duplicate scissors, scissors "
"in close-up, giant scissors in the foreground, oversized scissors, scissors at the "
"bottom of the frame, scissors lying on the floor, "
"arrow visible in the tapestry, drawn bowstring about to shoot, archer in the "
"foreground, large archer, archer aiming sideways, archer facing away from the target, "
"archer pointing right, horizontal trajectory, diagonal sideway arrow, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative "
"rune circles, meaningless icons, esoteric patterns, extra leg, third leg, two left "
"legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, "
"phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, white "
"solid border, plain white frame, solid filled border, no border, text, watermark, "
"photorealistic, 3d render")

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
