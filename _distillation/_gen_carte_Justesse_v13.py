import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v13_paysage_riche_balance"
SEED = 777119

# XI · JUSTESSE — v9 "pire" : empiler des consignes de precision (alignement arc/fleche,
# fil continu en 3 segments) a degrade le resultat — meme pattern que la carte Changement,
# lecon deja documentee : une architecture simple plutot que l'accumulation. v10 : TOUTE
# la composition est reorganisee autour d'UN SEUL principe fondateur, la LIGNE VERTICALE
# ROUGE — v11 : l'archer pointait TOUJOURS vers la droite (prior massif du modele). Pivot
# propose par Martin : au lieu de combattre ce prior, on s'aligne avec lui — la cible est
# placee A DROITE dans la direction ou l'archer veut naturellement tirer, et le fil rouge
# suit la trajectoire de la fleche parfaitement. La ligne n'est plus verticale : c'est une
# trajectoire qui monte en diagonale de la main gauche vers la cible en haut a droite du
# tableau tisse. Ciseaux toujours ouverts sur le fil, fil continu, fin au centre du mille.
positive = ("A wide shot with the figure at medium scale, set comfortably back from the "
"camera so the rich surroundings are clearly visible around her, composed with careful "
"visual balance: the weaver and her loom anchoring the left side of the frame, the "
"workroom breathing on the right, the whole scene arranged on a gentle rising diagonal "
"that carries the eye naturally from the lower left to the upper right, with generous "
"breathing room and no element crowding another. The entire image is "
"built around one single continuous crimson-red line — the flight path of an arrow — "
"running without any interruption from the lower left of the frame to the upper right "
"of the frame. Reading the image from lower left to upper right: at the lower left, "
"the hands of a calm, precise woman hold the lower end of this red thread; a short "
"distance along the thread, it passes between the wide-"
"open blades of the image's only pair of scissors — a single pair of fine weaver's "
"scissors held in her other hand, the blades clearly separated in a "
"V around the thread, not yet closing; the thread continues, enters the woven "
"tapestry stretched on a grand wooden loom — the largest object in the scene — and "
"inside the tapestry this same red line is exactly the trajectory of an arrow that has "
"just been shot. The woven scene itself is a rich, fully detailed pastoral landscape, "
"nothing empty in it: rolling green meadows scattered with tiny woven wildflowers, a "
"few leafy woven trees, a small winding stream glinting through the grass, soft "
"distant woven mountains on the horizon, and a warm woven sky with a low golden sun "
"and a few drifting clouds. In the meadow at the left edge of the tapestry stands a "
"small woven archer, bow drawn, aiming to the "
"right toward a large woven archery target on a wooden stand at the right side of the "
"tapestry, directly in his line of fire, the meadow stretching between them. The red "
"line travels from the archer's bow in "
"a perfectly straight rising line across the whole woven landscape, over the meadow "
"and the stream, and arrives at "
"the exact center of that target, the bullseye — and there it stops, absolutely: no "
"red thread extends past the target, nothing red continues above or beyond the "
"bullseye, the line ends at that single point. One "
"line, from her hands, through the scissors, across the tapestry, along the arrow's "
"trajectory, ending at the bullseye — "
"nothing breaks it, nothing branches off it, it never curves and never stops. The "
"woman's eyes are on the point where the scissors meet the thread, clear-eyed and "
"quietly certain, her posture composed and deliberate. In the foreground, on the "
"floor at the lower right of the scene, close to the viewer and fully within the "
"frame, rests an old "
"brass balance scale with its two hanging pans clearly visible, one pan on each side "
"of the central beam, a complete classic two-pan balance, set down and gently "
"released, still intact but simply no longer needed, quietly abandoned — the old way "
"of judging, laid aside. Around the loom the workroom is soft and characterful: "
"shelves with neatly wound yarn baskets, a potted plant on the sill, warm morning "
"light through a window falling on her hands "
"and the red line, nothing glowing on her body itself. She wears a beautiful flowing "
"artisan's gown with careful details — embroidered bodice, full sleeves gathered at "
"the forearm, layered skirts in warm muted teal, rust and cream, a woven sash at the "
"waist, bare feet, no modern clothing. The whole image framed by an ornate Art "
"Nouveau golden "
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
"foreground, large archer, archer facing away from the target, archer aiming left, "
"archer aiming up, archer aiming down, target on the left, target at the top, "
"red thread past the target, red thread above the target, red thread continuing "
"beyond the bullseye, thread going past the target, "
"vertical red line, plumb line, "
"empty tapestry, bare tapestry, plain empty woven background, blank sky in the "
"tapestry, no scale, missing balance scale, scale cut off by the edge, scale outside "
"the frame, tiny distant scale, "
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
