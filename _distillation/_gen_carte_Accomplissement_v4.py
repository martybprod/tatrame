import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_21_Accomplissement_v4_femme_mature"
SEED = 777050

# XXI · ACCOMPLISSEMENT — v4 : (a) tisserande mature (40aine), pas jeune femme ni vieillarde ;
# (b) abandon du pastel : equilibre du spectre complet PARTOUT dans le decor, mais discret/subtil,
# jamais aussi affirme que le mandala qui reste le point focal.
positive = ("A single serene mature woman in her forties, dignified and graceful, not elderly, alone, "
"the only person in the scene, seated at an antique wooden weaving loom, her hands placing "
"the very final touch — the last stitch of luminous golden thread — to complete a "
"magnificent radially symmetric mandala tapestry, perfectly balanced, filling the entire "
"loom before her. The mandala is woven from all seven colors of the rainbow in harmonious "
"balance, together with deep black and pure white, an intricate geometric sacred-geometry "
"pattern of interlocking triangles and stars radiating outward from a glowing golden point "
"exactly at the position of her own third eye. Within the black sections of the mandala, a "
"cosmic starfield and soft nebula glow subtly through the weave, as if the night sky itself "
"were woven into the cloth. Fine golden linework traces the geometric pattern throughout. "
"Loose unwoven golden warp threads stream down from the top of the loom into the finished "
"mandala below. Her long flowing robe, reaching the floor with its hem lost among the woven "
"threads at her feet, carries a harmonious balance of every color of the spectrum, rendered "
"more discreetly and subtly than the mandala's vivid palette — present throughout the fabric "
"but never competing with it. The wooden loom frame itself carries the same discreet "
"full-spectrum balance in its wood grain and carved details, and from both sides of the loom "
"hang small fringes of thread spanning the full spectrum in a quieter, more subdued presence "
"than the mandala, echoing the four elements (fire, water, air, earth). Even the soft misty "
"background atmosphere holds a discreet, even balance of every hue, always subordinate to "
"the mandala's vivid centerpiece. The loom's carved wooden frame, ornamented in flowing Art "
"Nouveau curves, encircles the entire composition like a natural frame. She wears no "
"trousers, no boots, no shoes visible. Her expression is quiet gratitude and fulfillment, an "
"ending that is also a beginning. The figure drawn in the flat decorative style of Alphonse "
"Mucha — bold elegant clean contour lines, stylized idealized mature features, flowing "
"ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art "
"Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of "
"warm and cool hues, harmoniously balanced and distributed naturally across every part of "
"the scene, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

# Memes exceptions legitimes que v2/v3 (rainbow + magic circles/esoteric patterns/mystical glyphs
# retires du negatif). Ajout : bannir jeune femme ET vieillarde pour cibler l'age mature demande.
negative = ("young woman, teenage girl, child, girl, elderly woman, old woman, wrinkled skin, hunched, "
"frail, puzzle piece, jigsaw puzzle, mosaic tile, interlocking tiles, laurel wreath, garland, "
"crown of leaves, wreath frame, four animals, lion, bull, ox, eagle, winged angel in corner, "
"zodiac creatures, corner creatures, visible third eye mark, eye symbol on forehead, painted "
"eye on forehead, bindi, dot on forehead, landscape scenery, mountains, painted sky "
"background, extra leg, third leg, two left legs, duplicated limb, missing foot, missing "
"leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, malformed anatomy, bad "
"anatomy, disfigured, mutated, two people, twins, duplicate person, multiple figures, text, "
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
