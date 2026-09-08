import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_21_Accomplissement_v9_bordure_regard"
SEED = 777055

# XXI · ACCOMPLISSEMENT — v9 : (a) ajout de la bordure Art Nouveau doree ajouree (norme du deck
# depuis XVI, manquante jusqu'ici) ; (b) regard de la tisserande tourne vers le mandala, pas la camera.
positive = ("A single serene mature woman in her forties, natural and dignified, no makeup, bare "
"natural skin with subtle natural signs of aging, beautiful with a soft gentle smile, alone, "
"the only person in the scene, seen from a slightly wider view with room around her, seated "
"upright properly behind a tall vertical tapestry loom (a high-warp loom), its wooden frame "
"standing upright, placed outdoors in a magnificent natural landscape — a sunlit meadow "
"bordered by flowering shrubs, soft distant mountains, and a gentle stream, evoking a deep "
"sense of completion and harmony. Her gaze is turned toward the mandala tapestry on the loom "
"before her, watching her completed work with quiet focus and gratitude. Her body is clearly "
"separate from the tapestry, never seated on or wrapped within the weave itself, never "
"resting flat across her lap or knees — the finished mandala tapestry is woven flat against "
"the loom's vertical frame, standing upright before her like a piece of standing artwork, "
"its warp threads strung vertically from the top beam to the bottom beam. Both her hands are "
"actively at work on the loom's mechanism, one hand guiding the wooden shuttle through the "
"vertical threads, the other pressing home the very last golden thread with the weaver's "
"beater, completing a magnificent radially symmetric mandala tapestry, perfectly balanced. "
"The mandala is woven from all seven colors of the rainbow in harmonious balance, together "
"with deep black and pure white, an intricate geometric sacred-geometry pattern of "
"interlocking triangles and stars radiating outward from a glowing golden point exactly at "
"the position of her own third eye. Within the black sections of the mandala, a cosmic "
"starfield and soft nebula glow subtly through the weave, as if the night sky itself were "
"woven into the cloth. Fine golden linework traces the geometric pattern throughout. The "
"active threads strung on the loom — its vertical warp and the weft crossing through it — "
"clearly display all nine base colors of the weaver's palette (red, orange, yellow, green, "
"blue, indigo, violet, black, white) plus a tenth thread of pure gold, each clearly "
"distinguishable and woven into the mandala's pattern. Radiant colored threads visibly rise "
"up from the natural surroundings to reach the loom — one emerging from the damp earth, "
"another unfurling from the center of a blooming flower, another lifting glistening from the "
"surface of the stream — while more luminous threads of pure light descend from the open sky "
"itself, streaming down from sunlight and drifting starlight alike, all converging and "
"joining the working threads on the loom, as if the entire living world, earth and sky "
"together, were spinning material into her weaving. Her long flowing robe, reaching the "
"floor with its hem lost among the woven threads at her feet, is a pale neutral fabric "
"adorned with a very light, delicate, discreet woven pattern carrying subtle variations of "
"color running through it, quietly echoing the full spectrum without ever becoming a bold or "
"saturated wash. The wooden loom frame carries the same discreet, tasteful touches of color "
"in its grain and carved details, and the sunlit meadow around her holds its own gentle, "
"natural balance of every hue across its flowers and foliage — the whole composition remains "
"harmonious and uncluttered, never overloaded. Along both sides of the loom hang exactly "
"nine small skeins of thread, each one a single pure solid color, no color repeated — red, "
"orange, yellow, green, blue, indigo, violet, black, and white. The loom's carved wooden "
"frame is ornamented in flowing Art Nouveau curves. The whole image is framed by an ornate "
"Art Nouveau golden border with flowing organic whiplash lines and delicate openwork "
"corners — the scene's own meadow and sky show through the corner ornaments, no white or "
"solid fill anywhere in the border. She wears no trousers, no boots, no shoes visible. Her "
"expression is quiet gratitude and fulfillment, an ending that is also a beginning. The "
"figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean contour "
"lines, stylized idealized mature features, flowing ornamental hair, flat areas of soft "
"watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously "
"balanced and distributed naturally across every part of the scene, muted jewel tones, "
"subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

# Exceptions legitimes (rainbow, magic circles/esoteric patterns) toujours retirees du negatif.
# Ajout v9 : bannir regard camera (le regard doit rester sur le mandala) et bordure blanche/pleine
# (on veut l'ajouree, coherente avec les cartes XVI-XX).
negative = ("looking at viewer, looking at camera, eye contact with viewer, white solid border, "
"plain white frame, solid filled border, no border, mandala resting on her lap, tapestry "
"lying flat on her knees, horizontal loom, tapestry draped across her legs, weaving in her "
"lap, tapestry flat on the ground, woman sitting inside the fabric, woman embedded in "
"tapestry, woman wrapped in cloth, tapestry covering her body, sitting on top of the weave, "
"merged with the fabric, woman seated within the mandala, rainbow arc in sky, rainbow arch, "
"literal rainbow across the sky, monochrome dress pattern, single color dress pattern, "
"extreme close-up, tight close-up, makeup, lipstick, eyeshadow, glamorous, aristocratic, "
"elaborate jewelry, bejeweled, tie-dye, tie dye pattern, rainbow dyed fabric, ombre fabric, "
"large blocks of saturated color on dress, multicolored tassel, rainbow-striped tassel, "
"ombre thread bundle, variegated yarn, repeated color skein, duplicate colored skein, young "
"woman, teenage girl, child, girl, elderly, hunched, frail, puzzle piece, jigsaw puzzle, "
"mosaic tile, interlocking tiles, laurel wreath, garland, crown of leaves, wreath frame, "
"four animals, lion, bull, ox, eagle, winged angel in corner, zodiac creatures, corner "
"creatures, visible third eye mark, eye symbol on forehead, painted eye on forehead, bindi, "
"dot on forehead, extra leg, third leg, two left legs, duplicated limb, missing foot, "
"missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra "
"hand, floating hand, malformed hands, fused fingers, extra finger, malformed anatomy, bad "
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
