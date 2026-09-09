import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v18_8_quarters_spring_start"
SEED = 777094

# X · CHANGEMENT — v17 (12 parts) "plutot tres bien" mais repartition inegale (1 hiver, 3 ete).
# Decision finale Martin : 8 parts (12 jamais fiable), 2 par saison, et l'annee COMMENCE AU
# PRINTEMPS (haut-droite, comme v17 qui marchait) puis ete -> automne -> hiver dans le sens
# horaire. Contenu des 8 parts valide par Martin (crocus, pommiers, lupins, profusion+roses,
# courges, feuilles qui s'envolent, flocons sur sol nu, coeur d'hiver avec glaçons). Ancrage
# quadrants spatiaux conserve (anti-miroir).
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
"exactly eight equal wedges radiating from the hub to the rim, like a pizza cut into "
"eight equal slices — eight wedges, never twelve, never six, never sixteen. The four "
"seasons flow around the wheel in one single continuous clockwise order, two wedges per "
"season, and each season is anchored to its own fixed quarter of the circle so they can "
"never be confused or mirrored. SPRING is only ever in the upper-right quarter of the "
"wheel, the quarter from twelve o'clock down to three o'clock, and the year begins "
"there: its first wedge, right beside the top of the wheel in the upper right, is very "
"early spring, purple and white crocuses blooming through melting snow; its second "
"wedge, reaching three o'clock, is late spring, apple trees in full white-and-pink "
"blossom. SUMMER is only ever in the lower-right quarter, from three o'clock down to six "
"o'clock: its first wedge is early summer, tall blue and purple lupins rising among "
"fresh meadow flowers; its second wedge is high summer's full abundance, a rich "
"profusion of different flowers all blooming together — roses, daisies, poppies, "
"cornflowers, cosmos. AUTUMN is only ever in the lower-left quarter, from six o'clock up "
"to nine o'clock: its first wedge is early autumn, harvest squashes and pumpkins among "
"browning leaves; its second wedge is late autumn, gusts of wind sweeping golden and red "
"leaves up into the air from nearly bare branches. WINTER is only ever in the upper-left "
"quarter, from nine o'clock up to twelve o'clock, closing the year back into spring: its "
"first wedge is early winter, a few sparse snowflakes falling onto dark bare earth, the "
"snow not yet covering the ground; its second wedge, finishing at the very top of the "
"wheel right beside spring's first wedge, is deep mid-winter, thick snow covering "
"everything, snowdrifts and long hanging icicles, which closes the cycle back into the "
"melting-snow crocuses of spring. The four quarters are all different — spring upper "
"right, summer lower right, autumn lower left, winter upper left — a flowing clockwise "
"progression of a single unbroken year, never a symmetric mirror design. Every motif "
"lives only in its own wedge: crocuses and apple blossoms nowhere except spring, lupins "
"and the flower profusion nowhere except summer, squashes and windblown leaves nowhere "
"except autumn, snow and icicles nowhere except winter — the seasons never repeat, "
"never mirror, never mix. The weaving is rich, intricate and fully accomplished, "
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
"twelve wedges, twelve spokes, ten spokes, six spokes, sixteen spokes, "
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
