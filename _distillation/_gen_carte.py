import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_18_Invisible_v6_arbre"
SEED = 777044

# v4 : racines BOTANIQUEMENT RÉALISTES — système ramifié complexe, densément détaillé (garde la grâce v3)
positive = ("A single graceful tree at night under a slender crescent moon, its elegant crown rising "
"into a starry twilight sky with flowing Art Nouveau curves. The ground line is drawn as one "
"soft, undulating silky line crossing the card — not a hard straight cut — and the tree's "
"delicate trunk passes through it seamlessly, its bark gently dissolving into roots. Below this "
"gentle line, the tree's root system unfolds in breathtaking botanical complexity, painted "
"with the accuracy of a naturalist's study: a mighty taproot diving straight down, from which "
"countless lateral roots branch and divide again and again into ever finer rootlets, a dense "
"ramified tree of roots mirroring the branching of the crown above but far more intricate — "
"every root tapering naturally, forking at true angles, twisting around stones, overlapping "
"and weaving between each other in a richly detailed, dense, believable network, rendered with "
"fine precise linework, glowing with a subdued golden light from within, spreading much wider "
"and deeper than the crown. Suspended within this intricate luminous rootwork, like precious "
"gems set in a necklace, hang a "
"few small treasures from lives long past — one single ring, one old key, one tiny crown, each "
"appearing exactly once — each one "
"separate and distinct, cradled and encircled by the curved roots themselves, perfectly "
"composed like jewels in a display, never scattered or buried. The roots and the ground fade "
"into one another in soft watercolor gradients. In the far distance on the horizon, two "
"standing stones rise side by side, silent and discreet. No human figure anywhere in the "
"scene. The visible world above ground is quiet, dim and small; the hidden world below is "
"vast, radiant and alive. The whole image is framed by an ornate Art Nouveau golden border "
"with flowing organic whiplash lines and delicate ornamental corners — the corner ornaments "
"are openwork: the scene's own sky, stars and landscape show through them, no white or solid "
"fill inside the border or corners, the artwork continues seamlessly behind the golden "
"linework everywhere. Flat decorative Art Nouveau illustration style, bold elegant clean "
"contour lines, "
"stylized idealized forms, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, mystical "
"dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted "
"jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("angels, cherubs, putti, angelots, winged figures in corners, corner figures, decorative "
"figures in upper corners, clouds with figures, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, hard straight ground line, sharp cut "
"between ground and underground, sparse simple roots, few roots, schematic roots, symmetrical "
"root pattern, two rings, multiple rings, several rings, duplicated objects, objects scattered "
"on the ground, objects buried in dirt, "
"cluttered objects, extra leg, third leg, two left legs, duplicated limb, missing foot, "
"missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, malformed anatomy, bad anatomy, "
"disfigured, mutated, human figure, person, face in the roots, faces in the ground, skulls, "
"bones, two trees, several trees, forest, random occult symbols, magic circles, alchemical "
"sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, circular emblems, white corners, white medallions "
"in the corners, solid filled corners, blank corner roundels, white circles in corners, "
"photorealistic, 3d render, text, "
"watermark")

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
