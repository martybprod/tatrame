import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v7_metier_circulaire_saisons"
SEED = 777083

# X · CHANGEMENT — v6 : direction gardee ("c'est bien comme direction"), deux corrections.
# (a) La roue doit etre un VRAI metier a tisser, mais de forme CIRCULAIRE — un metier rond,
# avec sa structure en bois visible (jante, rayons, moyeu, peigne), pas une roue abstraite.
# (b) Les 4 saisons ne sont plus dans la moitie descendante : chacune occupe un QUART des
# rayons (nord = printemps, est = ete, sud = automne, ouest = hiver, sens de rotation).
positive = ("A vast circular tapestry loom filling the composition — a real weaver's loom "
"built in the shape of a great wheel, its carved wooden rim, wooden spokes, and wooden hub "
"clearly the frame of an actual round loom, with warp threads strung taut from hub to rim "
"and weft being woven across them. At the still wooden hub sits a small yin-yang symbol, "
"perfectly motionless while the great round loom slowly turns. The four quarters of the "
"loom's spokes each weave one season: the first quarter of the woven cloth is spring, pale "
"green shoots and pink blossom threads; the second quarter is summer, deep green foliage "
"and bright warm threads; the third quarter is autumn, amber gold and russet threads with "
"falling leaves woven in; the fourth quarter is winter, white and silver-blue threads with "
"delicate snowflake patterns — the four seasons each occupying exactly one quarter of the "
"circle, in sequence, the cloth rotating from raw unwoven warp on one side into finished "
"seasonal fabric as it comes around. Galaxies and stars swirl faintly around the loom's "
"outer wooden rim, the twelve zodiac signs etched discreetly along the rim's circumference, "
"faint I Ching trigrams nested just inside them, and four small soft glowing diamond-like "
"points of light marking the cardinal directions between the seasonal quarters — never "
"lightning bolts, never zigzags. At a respectful distance from the loom, seated calmly on a "
"low outcrop of rock, a sphinx in slight three-quarter profile with a single tail curving "
"naturally behind it watches the great round loom turn, the silent riddle observing time "
"pass without touching it. A single small serpent of golden thread slides down along one "
"spoke, unravelling itself from the weave as it descends — letting go made visible, one "
"smooth sinuous golden thread working loose from the pattern and slipping free toward the "
"ground. No human figure — the circular loom itself is the subject, vast, turning, weaving "
"the seasons. The whole image framed by an ornate Art Nouveau golden border with flowing "
"organic whiplash lines and delicate openwork corners — the scene's own sky and stars show "
"through the corner ornaments, no white or solid fill anywhere in the border. Flat "
"decorative Art Nouveau illustration style, bold elegant clean contour lines, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured "
"paper, visible paper grain and pigment bleeds, mystical dreamlike mood, a rich complete "
"color palette spanning the full range of warm and cool hues, harmoniously balanced and "
"distributed naturally across the scene according to its mood, muted jewel tones, subtle "
"gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("abstract wheel, plain wheel without loom structure, cartwheel, ferris wheel, "
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
