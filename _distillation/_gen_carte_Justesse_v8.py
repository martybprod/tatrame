import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v8_archer_vise_haut"
SEED = 777114

# XI · JUSTESSE — v6 "tres interessant", mais image tissee a retravailler + ciseaux non
# ouverts. v7 : image tissee = LA CIBLE ET LA FLECHEE (proposition retenue par Martin) —
# archer minuscule en bas de la tapisserie, cible aux anneaux concentriques en haut, le
# fil rouge EST la trajectoire de la fleche (entre en bas, file en diagonale, meurt pile
# au centre de la cible) et continue hors de la tapisserie jusqu'aux mains. Ciseaux
# EXPLICITEMENT OUVERTS, prets a couper, pas encore refermes (interdit ajoute).
positive = ("A wide shot with the figure at medium scale, set comfortably back from the "
"camera so the rich surroundings are clearly visible around her. A calm, precise woman "
"seated at a grand wooden tapestry loom — the loom is the largest object in the scene, "
"a tall imposing high-warp frame dominating the room — in a quiet softly-lit room at "
"morning, its plain bare wooden frame contrasting with what is woven on it: the upper "
"part of the loom carries a rich finished tapestry depicting an archery scene seen "
"from afar — in the lower third of the tapestry stands a tiny woven archer, barely "
"visible, aiming directly UPWARD at the target above him, his bow and his whole body "
"angled steeply skyward toward the top of the tapestry, facing the target squarely, "
"and in the upper third hangs a woven "
"archery target of concentric rings in muted tones, directly above the archer. The "
"vivid crimson-red thread is "
"the arrow's flight path itself: it enters the tapestry at the lower edge beside the "
"archer, shoots straight upward across the whole woven scene in one long taut line "
"rising vertically toward the top — the arrow's trajectory, woven in the same red, "
"perfectly aligned between the archer and the target above him — and lands exactly at the "
"precise center of the target, the exact bullseye, not a ring beside it, not off-"
"center, but the very middle point. From that exact center of the target the very "
"same red thread continues out of the tapestry, hanging down loose in front of the "
"loom, the loose continuation she is now working with. Stretched "
"taut between her "
"two hands runs that single vivid crimson-red thread, and with her other hand she holds "
"a pair of fine weaver's scissors held wide open, blades clearly separated in a V, "
"poised around the thread exactly at the precise point where the cut must be made — "
"the open blades straddling the thread but not yet closing, the gesture suspended at "
"the exact instant before the decision is completed, neither "
"hesitation nor haste, simply absolute precision. Her eyes are on that exact point, "
"clear-eyed and quietly certain, her whole posture composed and deliberate. On the "
"floor beside the loom rests an old brass balance scale with its two hanging pans "
"clearly visible, one pan on each side of the central beam, a complete classic "
"two-pan balance, set down and gently released, "
"still intact but simply no longer needed, quietly abandoned — the old way of judging, "
"laid aside. Around her the room is soft and characterful, a real weaver's workroom — "
"shelves with neatly wound yarn baskets, a potted plant on the sill, a finished folded "
"tapestry on a bench — warm morning "
"light falling gently through a window and illuminating her hands and the red thread, "
"nothing glowing on her body itself. She wears a beautiful flowing artisan's gown with "
"careful, considered details — an embroidered bodice, full sleeves gathered at the "
"forearm so they stay clear of her work, layered skirts in warm muted tones of deep "
"teal, rust and cream that harmonize with the crimson thread, a woven sash at the "
"waist, bare feet, "
"no modern clothing, and a loose strand of her hair has escaped as she leans slightly "
"forward in concentration. The whole image framed by an ornate Art Nouveau golden "
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
"cut thread, severed thread, thread already cut, two threads, tangled threads, knots, "
"closed scissors, scissors mid-cut, scissors already cutting, blades touching, closed "
"blades, "
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
