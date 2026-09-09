import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v15_pizza_cosmos"
SEED = 777091

# X · CHANGEMENT — v14 interrompue : (a) toujours 8 sections au lieu de 12 malgre la
# reference horloge — hypothese : "spokes" tire trop fort vers l'attracteur de la roue du
# dharma bouddhiste (8 rayons, tres present dans l'entrainement) ; remplace par la
# reference "coupe comme une pizza en douze parts" + enumeration explicite 1-12, et
# interdit nomme contre la roue du dharma. (b) plus de "salle" en arriere-plan -> l'espace
# cosmique etoile explicitement redonne (perdu par erreur en v11 lors d'une reecriture).
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
"while the great round loom slowly turns. The woven cloth of the wheel is cut, like a "
"pizza sliced into twelve equal pieces, into exactly twelve equal pie-shaped wedges "
"radiating from the hub to the rim — count the wedges one by one going clockwise from the "
"top: wedge 1, wedge 2, wedge 3, wedge 4, wedge 5, wedge 6, wedge 7, wedge 8, wedge 9, "
"wedge 10, wedge 11, wedge 12, twelve wedges total, the same twelve-fold division as the "
"twelve numbers on a clock face, NOT the eight-spoked Buddhist dharma wheel, NOT any "
"eight-fold division — and the four seasons are woven into these twelve wedges, three "
"consecutive wedges per season, going clockwise starting at the top: SPRING fills wedges "
"1, 2 and 3 — wedge 1 is white snowdrops and pale crocuses on half-frozen ground, wedge 2 "
"is pink and white cherry blossoms on fresh green branches, wedge 3 is coral tulips and "
"deep meadow green. SUMMER fills wedges 4, 5 and 6 — wedge 4 is wild roses and red "
"poppies among fresh green, wedge 5 is high summer's richest abundance, deep green "
"foliage with blue cornflowers, purple lupins and white daisies blooming together, wedge "
"6 is heavy ripe sunflowers bowing over golden wheat. AUTUMN fills wedges 7, 8 and 9 — "
"wedge 7 is heavy purple harvest grapes with golden wheat, wedge 8 is amber and russet "
"falling leaves, wedge 9 is nearly bare dark branches with a few last brown leaves in "
"thin mist. WINTER fills wedges 10, 11 and 12 — wedge 10 is the first snowflakes falling "
"on frozen dark earth, wedge 11 is deep winter, white and silver-blue cloth with woven "
"snowflake and ice-crystal motifs, wedge 12 is quiet white cloth with two tiny snowdrop "
"buds, closing the cycle back into wedge 1's spring. Twelve wedges, no fewer, no eight: "
"every one of the twelve wedges is distinct and present. Every flower motif lives only "
"in its own wedge: sunflowers appear nowhere except wedge 6, cherry blossoms "
"nowhere except wedge 2, grapes nowhere except wedge 7 — the seasons never "
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

negative = ("dharma wheel, Buddhist wheel of dharma, eight-spoked wheel, wagon wheel, "
"cartwheel with eight spokes, room, interior room, indoor scene, walls, floor, ceiling, "
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
