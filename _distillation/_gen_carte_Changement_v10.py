import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v10_ete_riche_cercle"
SEED = 777086

# X · CHANGEMENT — v9 : ordre des saisons reussi ("ca s'en vient tres bien"). v10 : (a)
# enrichir les couleurs du printemps et SURTOUT de l'ete — l'ete doit montrer toute sa
# richesse, fleurs de toutes les couleurs tissees ; (b) roue encore legerement ovale
# (allongee verticalement) -> consigne de rondeur absolue renforcee en tete de prompt ;
# (c) roue trop pres des bords -> marge d'air explicite tout autour.
positive = ("A circular tapestry loom of absolute perfect roundness — drawn with a "
"compass, a mathematically true circle whose width and height are exactly identical, never "
"oval, never elongated vertically, never stretched, never elliptical, never tilted, seen "
"perfectly frontal and centered — surrounded by a generous margin of open sky all around "
"its rim, breathing space between the loom and the edges of the image on every side, the "
"loom never touching the border. A real weaver's "
"loom built in the shape of a great round wheel, its carved wooden rim, exactly twelve "
"wooden spokes evenly spaced like a clock face, and its wooden hub clearly the frame of an "
"actual round loom, with warp threads strung taut from hub to rim and weft being woven "
"across them. At the still wooden hub sits a small yin-yang symbol, perfectly motionless "
"while the great round loom slowly turns. Reading the loom like a clock face, the four "
"seasons are woven as four continuous blocks of three hours each, progressing clockwise in "
"one single unbroken cycle: spring occupies the top-right quarter of the circle, from noon "
"to three o'clock — fresh varied greens with blossom threads in soft pink, white and coral "
"woven among them; summer occupies the right-to-bottom quarter, from three to six o'clock — "
"the richest quarter of the whole wheel, deep green foliage alive with woven flowers of "
"every color, red poppies, blue cornflowers, yellow sunflowers, purple lupins, orange "
"butterflies' flowers, white daisies, the full abundance and richness of high summer "
"blooming all together under bright sun-gold threads; autumn occupies the bottom-left quarter, "
"from six to nine o'clock — amber, russet and copper threads with falling leaves woven in; "
"winter occupies the left-to-top quarter, from nine to noon — white and silver-blue threads "
"with delicate snowflake patterns, closing the cycle back into spring at the top. Each "
"season is one single continuous block of cloth — never repeated, never mirrored, never "
"alternated: spring appears exactly once, summer exactly once, autumn exactly once, winter "
"exactly once, each season's three sectors always adjacent to each other in the order "
"spring then summer then autumn then winter, going clockwise around the wheel. The weaving "
"is rich, intricate and fully accomplished, "
"a magnificent progression of cloth. Galaxies and stars swirl faintly around the loom's "
"outer wooden rim, the twelve zodiac signs etched discreetly along the rim's circumference, "
"one aligned with each spoke, faint I Ching trigrams nested just inside them. At a "
"respectful distance from the loom, seated calmly on a low outcrop of rock, a sphinx in "
"slight three-quarter profile with a single tail curving naturally behind it watches the "
"great round loom turn, the silent riddle observing time pass without touching it. No "
"human figure, no serpent, no snake anywhere — the circular loom itself is "
"the subject, vast, turning, weaving the seasons. The whole image framed by an ornate Art "
"Nouveau golden border with flowing organic whiplash lines and delicate openwork corners — "
"the scene's own sky and stars show through the corner ornaments, no white or solid fill "
"anywhere in the border. Flat decorative Art Nouveau illustration style, bold elegant clean "
"contour lines, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according "
"to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("oval wheel, vertically elongated wheel, wheel taller than wide, wheel "
"stretched vertically, elliptical wheel, tilted wheel, wheel seen at an angle, "
"perspective view of wheel, distorted circle, squashed circle, wheel touching the border, "
"wheel cropped by the edge, wheel too close to the edges, no margin around the wheel, "
"eight spokes, eight sections, six spokes, sixteen spokes, uneven spokes, mirrored "
"seasons, symmetrical seasons, same season twice, repeated season, autumn facing autumn, "
"seasons out of "
"order, seasons mixed up, winter next to summer, autumn next to spring, alternating "
"seasons, spring opposite spring, "
"abstract wheel, plain wheel without loom structure, cartwheel, ferris wheel, "
"steering wheel, serpent, snake, two serpents, second serpent, multiple serpents, "
"snake attacking, "
"threatening serpent, prominent large serpent, sphinx on top of the loom, sphinx touching "
"the loom, sphinx perfectly symmetrical, two tails, doubled sphinx, lightning bolts, zigzag "
"marks, static loom, loom not weaving, human figure, person at the loom, weaver, hands, "
"random occult symbols, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, solid beige circle in border, miniature scene inside border circle, "
"white solid border, plain white frame, solid filled border, no border, text, watermark, "
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
