import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v11_12_rayons_ultra_precis"
SEED = 777087

# X · CHANGEMENT — v10 : "s'en vient vraiment bien", mais (a) la roue n'a montre que 8
# sections au lieu de 12 ; (b) saisons melangees (tournesols au printemps) ; (c) aspect
# metier a tisser perdu ; (d) des MOTS ecrits sur la roue (jamais voulu). v11 : reecriture
# de la description des secteurs en NUMEROTATION PAR RAYON ultra-explicite (rayon 1 =
# minuit-1h, rayon 2 = 1h-2h... comme les 12 heures d'une horloge), chaque rayon nommant
# SON unique contenu floral — plus de listes "flowers of every color" qui laissent le modele
# semer des fleurs de la mauvaise saison partout. Structure de metier reaffirmee en tete
# (navette visible, tissage en cours). Zodiac/trigrammes RETIRES de la jante : source
# probable des faux glyphes/mots — seuls les motifs tisses restent, aucun symbole grave.
# Sphinx garde, serpent toujours banni.
positive = ("A circular tapestry loom of absolute perfect roundness — drawn with a "
"compass, a mathematically true circle whose width and height are exactly identical, never "
"oval, never elongated vertically, never stretched, never elliptical, never tilted, seen "
"perfectly frontal and centered — surrounded by a generous margin of open sky all around "
"its rim, breathing space between the loom and the edges of the image on every side, the "
"loom never touching the border. It is unmistakably a real weaver's loom built in the shape "
"of a great round wheel: a carved wooden outer rim, a solid wooden hub at the center, and "
"exactly twelve wooden spokes evenly spaced between them like the twelve hours of a clock "
"face — count them, twelve, never eight, never six — with pale warp threads strung taut "
"from the hub out to the rim along every spoke, and colored weft threads woven across them "
"by a wooden shuttle resting visibly against the cloth partway around, the weave in active "
"progress. At the still wooden hub sits a small yin-yang symbol, perfectly motionless "
"while the great round loom slowly turns. The cloth between the twelve spokes is woven "
"with the four seasons, one season per quarter, three spokes per season, each single "
"sector holding exactly one kind of imagery, going clockwise starting at the top: SECTOR "
"ONE, just right of the twelve o'clock spoke, early spring — white snowdrops and pale "
"purple crocuses emerging from half-frozen pale ground. SECTOR TWO, one to two o'clock, "
"full spring — pink and white cherry blossoms on fresh light-green branches. SECTOR THREE, "
"two to three o'clock, late spring — coral tulips and lush deepening meadow green. SECTOR "
"FOUR, three to four o'clock, early summer — wild roses and red poppies among fresh "
"green. SECTOR FIVE, four to five o'clock, high summer, the richest sector of the whole "
"wheel — deep green foliage with blue cornflowers, purple lupins, white daisies and "
"orange flowers blooming together. SECTOR SIX, five to six o'clock, late summer — heavy "
"ripe sunflower heads bowing over golden wheat, no other flower. SECTOR SEVEN, six to "
"seven o'clock, early autumn — heavy clusters of purple harvest grapes with golden wheat. "
"SECTOR EIGHT, seven to eight o'clock, full autumn — amber, russet and copper falling "
"leaves. SECTOR NINE, eight to nine o'clock, late autumn — nearly bare dark branches with "
"a few last muted-brown leaves in thin mist. SECTOR TEN, nine to ten o'clock, early "
"winter — first small snowflakes falling on frozen dark earth. SECTOR ELEVEN, ten to "
"eleven o'clock, deep winter — white and silver-blue cloth with woven snowflake and "
"ice-crystal motifs. SECTOR TWELVE, eleven to twelve o'clock, late winter — quiet white "
"cloth with two tiny snowdrop buds, the first hint of returning light, closing the cycle "
"back into the snowdrops of sector one at the top. Every flower motif lives only in its "
"own sector: sunflowers appear nowhere except sector six, cherry blossoms nowhere except "
"sector two, grapes nowhere except sector seven — the seasons never repeat, never mirror, "
"never mix. The weaving is rich, intricate and fully accomplished, a magnificent "
"progression of cloth. At a respectful distance from the loom, seated calmly on a low "
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
