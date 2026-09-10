import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v24_boussole_ouroboros"
SEED = 777103

# X · CHANGEMENT — v23 (deux couches) : "vraiment tres tres bien parti" — plus de
# doublons/comptage rate, mais (a) saisons pas dans l'ordre malgre "clockwise from the
# top", (b) l'ouroboros n'est carrement pas apparu (probablement dilue par la longueur de
# la description du tableau saisonnier). v24 : (a) chaque saison ancree a une position de
# BOUSSOLE absolue (printemps=haut, ete=droite, automne=bas, hiver=gauche) en plus du
# degrade continu — combine l'ancrage spatial qui marchait pour l'ordre (v17) avec le
# degrade continu qui marche pour l'absence de doublons (v23). (b) ouroboros deplace plus
# tot dans le prompt et reformule plus court pour eviter d'etre noye. (c) retour a 20
# steps (Martin).
positive = ("A single continuous circular painting, perfectly round — as round as a full "
"moon seen dead-on, as round as a coin lying flat face-up — a true circle whose width "
"and height are exactly identical, never oval, never elongated vertically, never "
"tilted, seen perfectly frontal and centered, small and floating at the center of a "
"tall portrait card with wide open cosmic space all around it: deep indigo starfields "
"and faint drifting nebula clouds stretching away on every side, no room, no interior, "
"no walls, no floor. A single slender elegant golden-silver serpent, an ouroboros, "
"forms a tight perfect ring pressed directly against the circle's outer edge, biting "
"its own tail, thin and graceful, no knots, no coils, running the whole way around. "
"Inside this circle is a single unbroken landscape painting of "
"a full year, wrapped seamlessly around the ring like a Wheel of the Year illustration, "
"each season fixed to its own compass position: at the very TOP of the circle is "
"SPRING — violet crocuses and pink apple blossoms in fresh green; at the RIGHT side of "
"the circle is SUMMER — a rich profusion of blooming flowers, roses, lupins, poppies, "
"cornflowers, in lush deep green; at the very BOTTOM of the circle is AUTUMN — orange "
"pumpkins and golden-red leaves drifting from branches turning bare; at the LEFT side "
"of the circle is WINTER — sparse snowflakes deepening into thick snow, frost and "
"hanging icicles. Between top-spring and right-summer, right-summer and bottom-autumn, "
"bottom-autumn and left-winter, left-winter and top-spring, the painting blends "
"gradually with no hard seam or dividing line, one single continuous flowing gradient "
"going clockwise top-right-bottom-left-top, with no separate slices, no repeated "
"season, no missing season — the whole year in one unbroken circular canvas. "
"Overlaid directly on top of this painted seasonal circle, like a real physical object "
"placed in front of it, is the visible structure of a great round weaver's loom: a "
"carved wooden outer rim running exactly along the edge of the circle, a solid wooden "
"hub at the very center, and a few plain straight wooden spokes of warp thread "
"stretching from the hub out to the rim like the spokes of a wheel, laid on top of the "
"painted scene beneath them — the seasonal painting is the woven fabric itself, seen "
"through the loom's plain structural framework. A wooden shuttle rests against the "
"cloth partway around, mid-weave. At the still wooden hub sits a small yin-yang "
"symbol, perfectly motionless while the great circle slowly turns beneath it. At a "
"respectful distance from the loom, seated calmly on a low outcrop "
"of rock, a sphinx in slight three-quarter profile with a single tail curving "
"naturally behind it watches the great circle turn, the silent riddle observing time "
"pass without touching it. No human weaver, no second serpent, no written words, no "
"letters, no inscriptions, no engraved symbols anywhere on the loom or its rim — the "
"seasons speak through the painted imagery alone. The whole image framed by an ornate "
"Art Nouveau golden border with flowing organic whiplash lines and delicate openwork "
"corners — the scene's own sky and stars show through the corner ornaments, no white "
"or solid fill anywhere in the border. Flat decorative Art Nouveau illustration style, "
"bold elegant clean contour lines, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, mystical dreamlike mood, a rich complete color palette spanning the "
"full range of warm and cool hues, harmoniously balanced and distributed naturally "
"across the scene according to its mood, muted jewel tones, subtle gold linework, soft "
"misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("no ouroboros, missing ouroboros, no ring around the rim, ouroboros absent, "
"visible pie slices, segmented wheel, eight slices, twelve slices, wedge "
"dividers, hard seams between seasons, sharp border between seasons, repeated season, "
"missing season, two winters, two summers, seasons out of order, spring not at top, "
"summer not on the right, autumn not at bottom, winter not on the left, "
"dharma wheel, Buddhist wheel of dharma, "
"room, interior room, indoor scene, walls, floor, ceiling, furniture, hall, chamber, "
"written words on the wheel, letters on the wheel, inscriptions, engraved text, "
"calligraphy on the loom, fake lettering, pseudo-alphabet, gibberish writing, "
"zodiac lettering, engraved symbols on the rim, zodiac signs, I Ching trigrams, runes, "
"oval wheel, vertically elongated wheel, wheel taller than wide, wheel stretched "
"vertically, elliptical wheel, tilted wheel, wheel seen at an angle, perspective view "
"of wheel, distorted circle, squashed circle, wheel filling the frame, wheel touching "
"the border, wheel cropped by the edge, wheel too close to the edges, no margin "
"around the wheel, large dominant wheel, oversized wheel, "
"many spokes, dense spokes, spokes obscuring the painting, thick spokes, "
"abstract wheel, plain wheel without loom structure, cartwheel, ferris wheel, "
"steering wheel, coiled serpent, tangled serpent, knotted serpent, two serpents, "
"second serpent, multiple serpents, serpent near the sphinx, serpent floating away "
"from the rim, serpent in the background stars, serpent not touching the wheel, loose "
"wandering serpent, serpent far from the loom, snake attacking, threatening serpent, "
"prominent large serpent, sphinx on top of the loom, sphinx touching the loom, sphinx "
"perfectly symmetrical, two tails, doubled sphinx, lightning bolts, zigzag marks, "
"static loom, human figure, person at the loom, weaver, hands, "
"random occult symbols, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, solid beige circle in border, miniature scene inside border "
"circle, white solid border, plain white frame, solid filled border, no border, text, "
"watermark, photorealistic, 3d render")

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
