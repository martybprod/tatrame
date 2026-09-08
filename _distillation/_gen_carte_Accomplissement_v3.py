import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_21_Accomplissement_v3_spectre_partout"
SEED = 777049

# XXI · ACCOMPLISSEMENT — v3 : l'equilibre du spectre complet (rainbow + noir + blanc) ne se limite
# plus au mandala, il infuse toute l'image (robe, metier, franges) en registre plus doux/pastel,
# pour que le mandala reste le point focal.
positive = ("A single serene woman, alone, the only person in the scene, seated at an antique wooden "
"weaving loom, her hands placing the very final touch — the last stitch of luminous golden "
"thread — to complete a magnificent radially symmetric mandala tapestry, perfectly balanced, "
"filling the entire loom before her. The mandala is woven from all seven colors of the "
"rainbow in harmonious balance, together with deep black and pure white, an intricate "
"geometric sacred-geometry pattern of interlocking triangles and stars radiating outward "
"from a glowing golden point exactly at the position of her own third eye. Within the black "
"sections of the mandala, a cosmic starfield and soft nebula glow subtly through the weave, "
"as if the night sky itself were woven into the cloth. Fine golden linework traces the "
"geometric pattern throughout. Loose unwoven golden warp threads stream down from the top of "
"the loom into the finished mandala below. Her long flowing robe, reaching the floor with "
"its hem lost among the woven threads at her feet, is dyed in soft pastel tones that echo "
"every hue of the mandala in a quieter register — pale rose, soft gold, dusty blue, muted "
"green, warm amber — harmoniously balanced across the fabric, no single hue dominating. The "
"wooden loom frame itself is subtly tinted with the same gentle rainbow balance in its wood "
"grain and carved details, and from both sides of the loom hang small fringes of thread in "
"soft muted pastel tones spanning the full spectrum, echoing the four elements (fire, water, "
"air, earth) without ever overpowering the mandala's vivid colors. Even the soft misty "
"background atmosphere holds a gentle, even balance of every hue. The loom's carved wooden "
"frame, ornamented in flowing Art Nouveau curves, encircles the entire composition like a "
"natural frame. She wears no trousers, no boots, no shoes visible. Her expression is quiet "
"gratitude and fulfillment, an ending that is also a beginning. The figure drawn in the flat "
"decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized "
"features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. "
"Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range "
"of warm and cool hues, harmoniously balanced and distributed naturally across every part of "
"the scene, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

# Memes exceptions legitimes qu'en v2 : rainbow + magic circles/esoteric patterns/mystical glyphs
# retires du negatif (mandala et palette generale explicitement multicolores, motif = signature de l'app)
negative = ("puzzle piece, jigsaw puzzle, mosaic tile, interlocking tiles, laurel wreath, garland, "
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
