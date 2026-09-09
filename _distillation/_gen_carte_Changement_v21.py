import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v21_couleurs_anneau_serre"
SEED = 777097

# X · CHANGEMENT — v20 : encore des tranches dupliquees (une section verte en trop) et
# l'ouroboros ne formait pas un anneau ferme (il se promenait en arriere-plan). v21 : (a)
# CHAQUE tranche s'ouvre desormais par sa couleur dominante explicite en PREMIER (avant le
# motif) — les couleurs sont plus fiables que l'identite d'objet pour la distinction
# spatiale chez le modele ; aucune tranche n'est "verte" par defaut. (b) ouroboros ancre
# physiquement CONTRE la jante en bois (comme une bague/bracelet serre), pas flottant dans
# les etoiles en arriere-plan.
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
"exactly eight equal slices radiating from the hub to the rim, clean and evenly spaced, "
"like an artist's color wheel cut into eight equal slices — EIGHT, never four, never "
"twelve, and above all never a simple four-quarter division. Moving clockwise from the "
"top of the wheel, each slice has its own single dominant color, no two slices sharing "
"the same dominant color, and each stage of the year appears exactly once in this "
"order: slice one is VIOLET — very early spring, violet and white crocuses piercing "
"the last melting snow; slice two is PINK — late spring, pink apple blossom in full "
"flower; slice three is BLUE — early summer, tall blue lupins; slice four is a "
"MULTICOLOR RAINBOW MIX with RED roses standing out — high summer, a many-colored "
"profusion of different flowers; slice five is ORANGE — early autumn, orange pumpkins; "
"slice six is GOLD AND CRIMSON — late autumn, red and gold leaves blowing from bare "
"branches; slice seven is PALE GREY — early winter, sparse white snowflakes on dark "
"bare earth; slice eight is DEEP BLUE-WHITE — deep winter, thick snow and long hanging "
"icicles, closing the wheel back into slice one's violet crocuses. No slice is plain "
"green: violet, pink, blue, rainbow-with-red, orange, gold-crimson, pale grey, "
"deep blue-white — eight distinct dominant colors, no slice repeated, none missing, "
"none out of order, none appearing twice, always eight separate visible slices, never "
"merging into four larger quarters. The weaving is rich, intricate and fully "
"accomplished, "
"a magnificent progression of cloth. A single slender elegant serpent forms a tight "
"perfect ring pressed directly against the wheel's outer wooden rim, touching the wood "
"all the way around like a ring worn snug on a finger or a bracelet clasped tight — an "
"ouroboros, gently biting its own tail exactly where the ring closes, the eternal cycle "
"of time made visible — its body thin and graceful, uniformly rounded, muted "
"silver-gold in tone, running in one unbroken circle immediately around the rim, never "
"drifting away into the starry background, with no knots, no coils, no extra loops, its "
"head meeting its tail cleanly; it is calm and beautiful, never threatening, clearly "
"separate from the sphinx. "
"At a respectful distance from the loom, seated "
"calmly on a low "
"outcrop of rock, a sphinx in slight three-quarter profile with a single tail curving "
"naturally behind it watches the great round loom turn, the silent riddle observing time "
"pass without touching it. No human weaver, no second serpent, no snake attacking, no "
"written words, no "
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

negative = ("four sections, four quarters, divided in four, quartered wheel, "
"two-season wheel, only four slices, "
"dharma wheel, Buddhist wheel of dharma, "
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
"twelve wedges, ten spokes, six spokes, sixteen spokes, "
"uneven sections, patchwork wheel, mosaic wheel, "
"mirrored "
"seasons, symmetrical seasons, symmetric wheel, same season twice, repeated season, "
"autumn facing autumn, spring facing spring, "
"seasons out of "
"order, seasons mixed up, winter next to summer, autumn next to spring, spring next to "
"autumn, summer next to winter, alternating "
"seasons, spring opposite spring, "
"abstract wheel, plain wheel without loom structure, cartwheel, ferris wheel, "
"steering wheel, coiled serpent, tangled serpent, knotted serpent, two serpents, "
"second serpent, multiple serpents, serpent near the sphinx, "
"serpent floating away from the rim, serpent in the background stars, serpent not "
"touching the wheel, loose wandering serpent, serpent far from the loom, "
"green slice, plain green section, two green slices, "
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
