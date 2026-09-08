import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_21_Accomplissement_v5_motif_echeveaux"
SEED = 777051

# XXI · ACCOMPLISSEMENT — v5 : (a) robe = motif tres leger/discret (pas de tie-dye) ; (b) visage
# naturel sans maquillage, signes d'age discrets, sourire doux ; (c) franges = echeveaux UNIS
# (une couleur pure par paquet), un paquet par couleur de base (7 arc-en-ciel + noir + blanc + or).
positive = ("A single serene mature woman in her forties, natural and dignified, no makeup, bare "
"natural skin with subtle natural signs of aging, beautiful with a soft gentle smile, alone, "
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
"threads at her feet, is a pale neutral fabric adorned with a very light, delicate, discreet "
"woven pattern — the harmony of colors expressed subtly through the fine pattern itself, "
"never as a bold tie-dye wash or large blocks of saturated color. The wooden loom frame "
"carries the same discreet, tasteful touches of color in its grain and carved details, and "
"the soft misty background likewise holds a gentle, understated balance of every hue — the "
"whole composition remains harmonious and uncluttered, never overloaded. Along both sides of "
"the loom hang several small skeins of thread, each one a single pure solid color, never "
"striped or multicolored — together forming a weaver's palette of every base color used in "
"the tapestry: red, orange, yellow, green, blue, indigo, violet, black, white, and gold. The "
"loom's carved wooden frame, ornamented in flowing Art Nouveau curves, encircles the entire "
"composition like a natural frame. She wears no trousers, no boots, no shoes visible. Her "
"expression is quiet gratitude and fulfillment, an ending that is also a beginning. The "
"figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, stylized idealized mature features, flowing ornamental hair, flat areas of soft "
"watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across every part of the scene, muted jewel tones, subtle gold "
"linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

# Exceptions legitimes (rainbow, magic circles/esoteric patterns) toujours retirees du negatif.
# Ajout v5 : bannir maquillage/aristocratique, tie-dye, et franges multicolores/degradees.
negative = ("makeup, lipstick, eyeshadow, glamorous, aristocratic, elaborate jewelry, bejeweled, "
"tie-dye, tie dye pattern, rainbow dyed fabric, ombre fabric, large blocks of saturated "
"color on dress, multicolored tassel, rainbow-striped tassel, ombre thread bundle, "
"variegated yarn, young woman, teenage girl, child, girl, elderly, hunched, frail, puzzle "
"piece, jigsaw puzzle, mosaic tile, interlocking tiles, laurel wreath, garland, crown of "
"leaves, wreath frame, four animals, lion, bull, ox, eagle, winged angel in corner, zodiac "
"creatures, corner creatures, visible third eye mark, eye symbol on forehead, painted eye on "
"forehead, bindi, dot on forehead, landscape scenery, mountains, painted sky background, "
"extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing "
"limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, "
"malformed hands, fused fingers, extra finger, malformed anatomy, bad anatomy, disfigured, "
"mutated, two people, twins, duplicate person, multiple figures, text, watermark, "
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
