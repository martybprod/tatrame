import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v13_douze_rayons_verrouilles"
SEED = 777089

# X · CHANGEMENT — v12 : rondeur/marge reussies MAIS la roue retombe a 8 sections au lieu
# de 12. Le decoupage par "SECTORS" numerotes n'a pas suffit. v13 : on passe par une
# STRUCTURE connue du modele — la roue decrite comme un cadran d'horloge complet avec SES
# DOUZE POSITIONS DE CHIFFRES (chaque rayon tombe sur une heure), et les 4 saisons posees
# comme les 4 QUARTS d'horloge (12-3, 3-6, 6-9, 9-12), chaque heure recevant son motif
# propre. Un cadran a 8 chiffres n'existe pas dans les priors du modele — une horloge, si.
# Le prompt reste identique par ailleurs (v12 validee sur la rondeur).
positive = ("A circular tapestry loom of absolute perfect roundness — a wide, low "
"horizontal circle, drawn with a compass, a mathematically true circle whose width and "
"height are exactly identical, never oval, never elongated vertically, never stretched, "
"never elliptical, never tilted, seen perfectly frontal and centered, occupying a compact "
"central area of the composition sized to the image width with wide open sky on every "
"side — much more empty space around the loom than loom itself, a broad margin of "
"breathing room between the rim and the edges of the image on all four sides, the sky "
"clearly visible above and below the circle. It is unmistakably a real weaver's loom built in the shape "
"of a great round wheel: a carved wooden outer rim, a solid wooden hub at the center, and "
"exactly twelve wooden spokes evenly spaced between them like the twelve hours of a clock "
"face — count them, twelve, never eight, never six — with pale warp threads strung taut "
"from the hub out to the rim along every spoke, and colored weft threads woven across them "
"by a wooden shuttle resting visibly against the cloth partway around, the weave in active "
"progress. At the still wooden hub sits a small yin-yang symbol, perfectly motionless "
"while the great round loom slowly turns. The structure of the cloth is the structure of "
"a full clock face: the wheel is divided into exactly twelve wedges like the twelve "
"hour-markers of a clock — one wedge per hour, a complete twelve-hour dial, the same "
"division as every ordinary clock — and the four seasons are woven into the four quarters "
"of that dial, three hour-wedges per season, going clockwise: SPRING fills the quarter "
"from twelve to three o'clock — at one o'clock white snowdrops and pale crocuses on "
"half-frozen ground, at two o'clock pink and white cherry blossoms on fresh green "
"branches, at three o'clock coral tulips and deep meadow green. SUMMER fills the quarter "
"from three to six o'clock — at four o'clock wild roses and red poppies among fresh "
"green, at five o'clock high summer's richest abundance, deep green foliage with blue "
"cornflowers, purple lupins and white daisies blooming together, at six o'clock heavy "
"ripe sunflowers bowing over golden wheat. AUTUMN fills the quarter from six to nine "
"o'clock — at seven o'clock heavy purple harvest grapes with golden wheat, at eight "
"o'clock amber and russet falling leaves, at nine o'clock nearly bare dark branches with "
"a few last brown leaves in thin mist. WINTER fills the quarter from nine to twelve "
"o'clock — at ten o'clock the first snowflakes falling on frozen dark earth, at eleven "
"o'clock deep winter, white and silver-blue cloth with woven snowflake and ice-crystal "
"motifs, at twelve o'clock quiet white cloth with two tiny snowdrop buds, closing the "
"cycle back into spring. Twelve hour-wedges, no fewer: every hour of the dial has its "
"own wedge, exactly like a real clock. Every flower motif lives only in its "
"own wedge: sunflowers appear nowhere except the six o'clock wedge, cherry blossoms "
"nowhere except two o'clock, grapes nowhere except seven o'clock — the seasons never "
"repeat, never mirror, never mix. The weaving is rich, intricate and fully accomplished, "
"a magnificent progression of cloth. At a respectful distance from the loom, seated "
"calmly on a low "
"outcrop of rock, a sphinx in slight three-quarter profile with a single tail curving "
"naturally behind it watches the great round loom turn, the silent riddle observing time "
"pass without touching it. No human weaver, no serpent, no snake, no written words, no "
"letters, no inscriptions, no engraved symbols anywhere on the loom or its rim — the "
"seasons speak through woven imagery alone. The whole image framed by an ornate Art "
"Nouveau golden border with flowing organic whiplash lines and delicate openwork corners — "
"the scene's own sky and stars show through the corner ornaments, no white or solid fill "
"anywhere in the border. Flat decorative Art Nouveau illustration style, bold elegant clean "
"contour lines, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according "
"to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("written words on the wheel, letters on the wheel, inscriptions, engraved "
"text, calligraphy on the loom, fake lettering, pseudo-alphabet, gibberish writing, "
"zodiac lettering, engraved symbols on the rim, zodiac signs, I Ching trigrams, "
"runes on the wheel, "
"sunflowers in spring, sunflowers outside summer, cherry blossoms in summer, "
"cherries in winter, grapes in spring, flowers of the wrong season, "
"oval wheel, vertically elongated wheel, wheel taller than wide, wheel "
"stretched vertically, elliptical wheel, tilted wheel, wheel seen at an angle, "
"perspective view of wheel, distorted circle, squashed circle, wheel filling the frame, "
"wheel touching the border, "
"wheel cropped by the edge, wheel too close to the edges, no margin around the wheel, "
"large dominant wheel, oversized wheel, "
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
