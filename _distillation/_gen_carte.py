import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_16_Rupture_v6"
SEED = 777041

positive = ("A huge medieval woven tapestry on a tall wooden loom dominates the scene, and its surface "
"is unmistakably textile: thick coarse interlaced threads in a clearly visible warp-and-weft grid, "
"like the Bayeux Tapestry — every shape inside the tapestry built from visible individual stitches "
"and threads, simplified flat stylized medieval forms, nothing smooth or painted about it. Woven "
"into this coarse fabric: a monumental spiral tower like the Tower of Babel, rising in many winding "
"superimposed tiers and encircling ramparts, ziggurat-like, reminiscent of Brueghel's Tower of "
"Babel, with a woven golden crown sitting at its very summit, the crown woven into the fabric as "
"part of the tapestry itself. At this exact moment, a single vertical line of white-golden light "
"has torn the fabric from top to bottom, passing straight through both the woven crown and the "
"woven tower — the tear is the lightning, the rupture itself is made of pure light, splitting "
"crown and tower in two, and the band of light contains nothing solid at all, only radiant "
"brightness through which true light floods into the scene. Along the tear, the weave is coming "
"undone: loose threads free themselves from the fabric and drift through the air, some floating "
"gently toward the ground, and the edges of the tear glow softly with small orange embers — a "
"quiet fire of purification, subtle and contained. Two small woven figures have come loose from "
"the unravelling weave and fall upside down through the open air beside the tear — head first, "
"heads pointing straight toward the ground, legs up, clearly outside the band of light, at a "
"distance from it, two separate falling figures not one, tumbling freely like discarded puppets. "
"The scene contains only these elements: the tapestry, the loom, the falling woven figures, and "
"one real woman standing before the loom — nothing in the upper corners, no angels, no cherubs, "
"no decorative figures anywhere else. The woman wears a long robe woven of the same coarse grey "
"threads as the tapestry, but her robe is coming undone from its lower hem upward: the grey weave "
"loosens, frees itself and dissolves into flowing threads of luminous gold and soft warm light "
"that drift gently around her legs like released ribbons — she is dressed in the rupture itself, "
"the old weaving unraveling into light. She stands calm and still, rendered in smooth watercolor "
"in deliberate contrast with the coarse threaded tapestry, bathed in the true light streaming "
"through the tear, watching the weaving come undone without fear. The whole image is framed by "
"an ornate Art Nouveau golden border with flowing organic whiplash lines and delicate ornamental "
"corners, enclosing the entire card. The woman drawn in the flat decorative style of Alphonse "
"Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, "
"flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on "
"textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a "
"rich complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across the scene according to its mood, muted jewel tones, subtle gold "
"linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("angels, cherubs, putti, angelots, winged figures in corners, corner figures, decorative "
"figures in upper corners, clouds with figures, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, smooth tapestry, printed fabric, painted "
"banner, glossy fabric, extra leg, third leg, two left legs, duplicated limb, missing foot, "
"missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, malformed anatomy, bad anatomy, "
"disfigured, mutated, two women, couple, romantic pair, lovers embracing, figures inside the "
"light beam, single falling figure, figures falling feet first, figures upright, crown outside "
"the tapestry, crown falling, crown unravelling, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric "
"patterns, embroidered symbols, medallion patterns, circular emblems, real people inside the "
"tapestry, photorealistic, 3d render, text, watermark")

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
