import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v17_12_quadrants_topright"
SEED = 777093

# X · CHANGEMENT — v16 (8 parts) : presque, mais saisons encore mal placees. Retour a 12
# parts demande par Martin. Nouvelle approche anti-symetrie : au lieu de numeroter des
# wedges abstraits (que le modele rearrange en miroir), on ancre CHAQUE saison sur un
# QUADRANT SPATIAL ABSOLU du cercle (printemps = quart SUPERIEUR-DROIT, ete = inferieur-
# droit, automne = inferieur-gauche, hiver = superieur-gauche) et on commence l'annee au
# haut-droite (1 heure, a cote du sommet) comme le demande Martin — progression circulaire
# claire, chaque saison n'apparait que dans son quadrant.
positive = ("A circular tapestry loom perfectly round — as perfectly round as a full moon "
"seen dead-on, as round as a coin lying flat face-up, as round as a cathedral rose window "
"seen straight-on — a true circle whose width and height are exactly identical, never "
"oval, never elongated vertically, never stretched, "
"never elliptical, never tilted, seen perfectly frontal and centered — a small loom "
"floating at the center of a tall portrait card, clearly smaller than the frame, "
"suspended in the endless depth of open cosmic space, deep indigo starfields and faint "
"drifting nebula clouds stretching away in every direction around it, no room, no "
"interior, no walls, no floor, no furniture anywhere — only stars and open sky above, "
"below, and on every side — much more empty starry space around the loom than loom "
"itself, a broad margin of breathing room between the rim and the edges of the image on "
"all four sides. It is unmistakably a real weaver's loom built in the shape "
"of a great round wheel: a carved wooden outer rim, a solid wooden hub at the center, and "
"pale warp threads strung taut "
"from the hub out to the rim, and colored weft threads woven across them "
"by a wooden shuttle resting visibly against the cloth partway around, the weave in active "
"progress. At the still wooden hub sits a small yin-yang symbol, perfectly motionless "
"while the great round loom slowly turns. The woven cloth of the wheel is divided into "
"exactly twelve equal wedges radiating from the hub to the rim, like a pizza cut into "
"twelve equal slices, like the twelve hours of a clock — twelve wedges, never eight, "
"never six, never sixteen. The four seasons flow around the wheel in one single "
"continuous clockwise order, and each season is anchored to its own fixed quarter of the "
"circle so they can never be confused or mirrored. SPRING is only ever in the upper-right "
"quarter of the wheel, the quarter from twelve o'clock down to three o'clock, and the "
"year begins there: the very first wedge of spring sits right beside the top of the "
"wheel at one o'clock, in the upper right, and is earliest spring, white snowdrops and "
"pale crocuses on half-frozen ground; the next spring wedge at two o'clock is full "
"spring, pink and white cherry blossoms on fresh green branches; the last spring wedge at "
"three o'clock is late spring, coral tulips with deep meadow green. SUMMER is only ever "
"in the lower-right quarter, from three o'clock down to six o'clock: its first wedge at "
"four o'clock is early summer, wild roses and red poppies among fresh green; its second "
"wedge at five o'clock is high summer's richest abundance, deep green foliage with blue "
"cornflowers, purple lupins and white daisies blooming together; its third wedge at six "
"o'clock, at the very bottom of the wheel, is late summer, heavy ripe sunflowers bowing "
"over golden wheat. AUTUMN is only ever in the lower-left quarter, from six o'clock up "
"to nine o'clock: its first wedge at seven o'clock is early autumn, heavy purple harvest "
"grapes with golden wheat; its second wedge at eight o'clock is full autumn, amber and "
"russet falling leaves; its third wedge at nine o'clock is late autumn, nearly bare dark "
"branches with a few last brown leaves in thin mist. WINTER is only ever in the upper-"
"left quarter, from nine o'clock up to twelve o'clock, closing the year: its first wedge "
"at ten o'clock is early winter, the first snowflakes falling on frozen dark earth; its "
"second wedge at eleven o'clock is deep winter, white and silver-blue cloth with woven "
"snowflake and ice-crystal motifs; its third wedge at twelve o'clock, at the very top of "
"the wheel right beside spring's first wedge, is the end of winter, quiet white cloth "
"with two tiny snowdrop buds announcing the new spring. The four quarters are all "
"different — spring upper right, summer lower right, autumn lower left, winter upper "
"left — a flowing clockwise progression, never a symmetric mirror design. Every flower "
"lives only in its own wedge: sunflowers appear nowhere except six o'clock, cherry "
"blossoms nowhere except two o'clock, grapes nowhere except seven o'clock — the seasons "
"never repeat, never mirror, never mix. The weaving is rich, intricate and fully "
"accomplished, "
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

negative = ("dharma wheel, Buddhist wheel of dharma, eight-spoked wheel, "
"room, interior room, indoor scene, walls, floor, ceiling, "
"furniture, hall, chamber, "
"written words on the wheel, letters on the wheel, inscriptions, engraved "
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
"eight wedges, eight spokes, eight sections, ten spokes, six spokes, sixteen spokes, "
"uneven wedges, mirrored "
"seasons, symmetrical seasons, symmetric wheel, same season twice, repeated season, "
"autumn facing autumn, spring facing spring, "
"seasons out of "
"order, seasons mixed up, winter next to summer, autumn next to spring, spring next to "
"autumn, summer next to winter, alternating "
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
