import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v19_deux_mains_sans_interdits_archer"
SEED = 777125

# XI · JUSTESSE — v18 : archer TOUJOURS absent. Cause reelle identifiee : le modele ne
# traite pas les QUALIFICATIFS SPATIAUX dans les interdits — "archer outside the
# tapestry", "arrow outside the tapestry", "archer in the room" sont lus comme une simple
# negation du sujet, et l'archer est supprime PARTOUT (le fameux piege du negatif qui
# "appelle" le mot qu'il interdit). v19 : SUPPRESSION TOTALE de tout interdit lie a
# l'archerie (archer/arrow/bow/quiver). On ne garde que le positif. Risque de
# contamination assume et reduit autrement : le personnage ne tient PLUS D'OBJET DU TOUT
# (les deux mains tiennent le fil entre les doigts — plus de navette), donc il n'y a plus
# rien ou un arc pourrait se glisser. Balance decalee et ciseaux poses conserves.
positive = ("A wide shot with the figure at medium scale, set comfortably back from the "
"camera so the rich surroundings are clearly visible around her, composed with careful "
"visual balance: the weaver and her loom anchoring the left side of the frame, the "
"room breathing on the right, the whole scene arranged on a gentle rising diagonal "
"that carries the eye naturally from the lower left to the upper right, with generous "
"breathing room and no element crowding another. The entire image is "
"built around one single continuous crimson-red line — the flight path of an arrow — "
"running without any interruption from the lower left of the frame to the upper right "
"of the frame. Reading the image from lower left to upper right: at the lower left, "
"the two hands of a calm, precise woman hold the lower end of this red thread "
"delicately between her fingers, both hands lifting it gently, a soft careful hold on "
"the single strand — two open hands, fingers loosely curved around the thread, holding "
"nothing else at all, no tool, no instrument, no object of any kind except the thread "
"itself. "
"A short "
"distance along the thread, the "
"thread passes between the wide-open blades of a prominent pair of fine weaver's "
"scissors — the single most important symbolic object in the scene, standing out "
"clearly, resting open on the loom's wooden "
"beam right beside the taut thread, lying flat on the wood with nobody holding them, "
"the blades clearly separated in a V that straddles the thread at exactly the point "
"where the cut must be made, the two finger-rings of the handles lying flat and empty "
"on the wood, no hand near them; the thread continues, enters the woven "
"tapestry stretched on a grand wooden loom — the largest object in the scene — and "
"inside the tapestry this same red line is exactly the trajectory of an arrow that has "
"just been shot. The woven scene depicts a Japanese kyudo archery range at dawn: a "
"smooth field of fine pale sand raked into long straight parallel lines of perfect "
"regularity, a few weathered stones placed with deliberate care along its edge, a "
"light morning mist softening the far end of the range, and a single traditional "
"Japanese archery target, a circular kazaguruma-style target of concentric rings, "
"standing at the far right end of the field. At the left end of the sand range stands "
"a small woven kyudo archer in traditional robes, a woman standing in a formal shooting "
"stance, her bow raised and fully drawn, the arrow nocked and pointing steadily to the "
"right toward that target, directly in her line of fire — she is a real, clearly drawn "
"figure in the tapestry, one of the principal subjects of the woven picture, standing "
"plainly visible on the sand. The red "
"line travels from her drawn bow in "
"a perfectly straight rising line across the whole raked sand field and arrives at "
"the exact center of that target, the bullseye — the point where the thread begins "
"its run out of the tapestry is precisely the bullseye itself, the very middle of the "
"target, not the upper edge, not the rim, the exact center — and there the line "
"leaves the woven scene, absolutely: no "
"red thread extends past the target, nothing red continues above or beyond the "
"bullseye. One "
"line, from her hands, through the scissors, across the tapestry, along the arrow's "
"trajectory, ending at the bullseye — "
"nothing breaks it, nothing branches off it, it never curves and never stops. The "
"woman's eyes are on the point where the resting scissors meet the thread, clear-eyed "
"and "
"quietly certain, her posture composed and deliberate, both her hands holding only "
"the red thread between her fingers. In the foreground, on the "
"floor slightly left of the lower-right corner of the scene, set a little in from the "
"right edge toward the centre of the frame, close to the viewer and fully within the "
"frame, rests an old "
"brass balance scale with its two hanging pans clearly visible, one pan on each side "
"of the central beam, a complete classic two-pan balance, set down and gently "
"released, still intact but simply no longer needed, quietly abandoned — the old way "
"of judging, laid aside. Around the loom the workroom is soft and characterful, "
"entirely timeless and Western in feel, in clear contrast with the Japanese scene "
"woven inside the tapestry: shelves with neatly wound yarn baskets, a potted plant on "
"the sill, warm morning light through a window. She wears a "
"beautiful flowing artisan's gown with careful, considered details — an embroidered "
"bodice, full sleeves gathered at the forearm so they stay clear of her work, layered "
"skirts in warm muted tones of deep teal, rust and cream that harmonize with the "
"crimson thread, a woven sash at the waist, bare "
"feet, no modern clothing, no kimono, no Japanese dress on her. The whole image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners — the "
"scene's own soft room light shows through the corner ornaments, no white or solid "
"fill anywhere in the border. The figure drawn in the flat decorative style of "
"Alphonse Mucha — bold elegant clean "
"contour lines, stylized idealized mature features, flowing ornamental hair, flat "
"areas of soft watercolor pigment, "
"minimal shading; only the woven scene inside the tapestry itself borrows from "
"Japanese ukiyo-e woodblock printing style, the rest of the illustration staying pure "
"Mucha Art Nouveau. Entirely hand-painted watercolor on textured paper, visible paper "
"grain and pigment bleeds, Art Nouveau japonisme, mystical dreamlike mood, a rich "
"complete color palette of indigo, rust, cream and the single crimson thread, "
"harmoniously balanced and distributed naturally across the scene according to its "
"mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("single-pan scale, one pan only, missing pan, incomplete scale, "
"red thread floating over the landscape, red line added on top of the tapestry, red "
"string crossing the woven scene without being part of it, "
"broken scale, shattered scale, damaged balance scale, destruction, "
"explosion, debris, shattering, falling masonry, sword, blade, weapon, glowing body, "
"glowing plexus, glowing chest, red light on skin, fiery aura, "
"modern clothing, contemporary clothing, kimono on the weaver, kimono on her, obi "
"sash on her, tatami mats in the room, shoji screens in the room, Japanese dress on "
"the woman, Japanese room, "
"trousers, jeans, shoes, boots, sneakers, "
"wristwatch, jewelry, second person, second woman, man, crowd, child, "
"raked lines curved, wavy raked sand, chaotic sand pattern, "
"thread leaving from the top of the target, thread starting at the target rim, "
"cut thread, severed thread, thread already cut, two threads, two separate red "
"threads, thread gap, thread interrupted, broken thread, thread ending at the "
"scissors, thread not passing through the scissors, mismatched trajectory, tangled threads, knots, "
"closed scissors, scissors mid-cut, scissors already cutting, blades touching, closed "
"blades, scissors held in hand, scissors gripped by fingers, fingers through the "
"finger-rings, finger inside the scissor loop, hand holding the scissors, hands "
"holding scissors, scissors lifted off the loom, "
"two pairs of scissors, second pair of scissors, duplicate scissors, scissors "
"in close-up, giant scissors in the foreground, oversized scissors, scissors at the "
"bottom of the frame, scissors lying on the floor, "
"red thread past the target, red thread above the target, red thread continuing "
"beyond the bullseye, thread going past the target, "
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
