import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v8_12_rayons_serpent_discret"
SEED = 777084

# X · CHANGEMENT — v7 : "direction bonne", quatre corrections. (a) Roue ovale -> cercle
# PARFAIT explicite (frontal, pas de perspective inclinee, parfaitement circulaire). (b) 8
# sections -> 12 rayons, chaque saison = 3 sections (printemps 1-2-3, ete 4-5-6, automne
# 7-8-9, hiver 10-11-12), ordre absolu. (c) Tissage encore plus abouti (progression tres
# belle a conserver/rehausser). (d) Serpent plus discret encore.
positive = ("A vast circular tapestry loom seen perfectly frontal and perfectly circular — "
"a flawless geometric circle, never oval, never elliptical, never tilted — a real weaver's "
"loom built in the shape of a great round wheel, its carved wooden rim, exactly twelve "
"wooden spokes evenly spaced like a clock face, and its wooden hub clearly the frame of an "
"actual round loom, with warp threads strung taut from hub to rim and weft being woven "
"across them. At the still wooden hub sits a small yin-yang symbol, perfectly motionless "
"while the great round loom slowly turns. The twelve sectors of the loom weave the four "
"seasons in strict unbroken order, three sectors per season, going around the circle: "
"sectors one to three are spring — pale green shoots, pink blossom threads, fresh light "
"greens growing richer; sectors four to six are summer — deep green foliage, bright warm "
"sun-gold threads at their fullest; sectors seven to nine are autumn — amber, russet and "
"copper threads with falling leaves woven in, gradually fading; sectors ten to twelve are "
"winter — white and silver-blue threads with delicate snowflake patterns, the circle then "
"returning to spring as it closes. The weaving is rich, intricate and fully accomplished, "
"a magnificent progression of cloth. Galaxies and stars swirl faintly around the loom's "
"outer wooden rim, the twelve zodiac signs etched discreetly along the rim's circumference, "
"one aligned with each spoke, faint I Ching trigrams nested just inside them. At a "
"respectful distance from the loom, seated calmly on a low outcrop of rock, a sphinx in "
"slight three-quarter profile with a single tail curving naturally behind it watches the "
"great round loom turn, the silent riddle observing time pass without touching it. A "
"single very small and subtle serpent of golden thread, barely noticeable, quietly slips "
"down along one spoke — letting go made visible as one thin golden strand working loose "
"from the pattern, discreet and understated. No human figure — the circular loom itself is "
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

negative = ("oval wheel, elliptical wheel, tilted wheel, wheel seen at an angle, "
"perspective view of wheel, distorted circle, squashed circle, "
"eight spokes, eight sections, six spokes, sixteen spokes, uneven spokes, seasons out of "
"order, seasons mixed up, winter next to summer, autumn next to spring, "
"abstract wheel, plain wheel without loom structure, cartwheel, ferris wheel, "
"steering wheel, two serpents, second serpent, multiple serpents, snake attacking, "
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
