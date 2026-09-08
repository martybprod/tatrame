import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_21_Accomplissement_v1_trame"
SEED = 777047

# XXI · ACCOMPLISSEMENT — concept "LA TRAME ACHEVÉE" : le dernier fil noué soi-même, pas une pièce de casse-tête reçue
positive = ("A single serene woman, alone, the only person in the scene, seated at an ornate antique "
"wooden weaving loom, her hands tying the very last golden thread into place exactly at the "
"position of her own third eye. The tapestry she has woven fills the entire scene around her "
"— mountains, sky, and flowing water all rendered as woven threads and fabric, not painted "
"background, forming one complete harmonious picture. From the four corners of the loom's "
"frame hang four fringes of pure colored thread — red for fire, blue for water, white for "
"air, brown for earth — cascading down like tassels. The loom's carved wooden frame, "
"ornamented in flowing Art Nouveau curves, encircles the entire composition like a natural "
"frame. She wears a long flowing robe reaching the floor, its hem lost among the woven "
"threads at her feet, no trousers, no boots, no shoes visible. Her expression is quiet "
"gratitude and fulfillment, an ending that is also a beginning. The figure drawn in the flat "
"decorative style of Alphonse Mucha — bold elegant clean contour lines, stylized idealized "
"features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal shading. "
"Entirely hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, "
"Art Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range "
"of warm and cool hues, harmoniously balanced and distributed naturally across the scene "
"according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("puzzle piece, jigsaw puzzle, mosaic tile, interlocking tiles, laurel wreath, garland, "
"crown of leaves, wreath frame, four animals, lion, bull, ox, eagle, winged angel in corner, "
"zodiac creatures, corner creatures, visible third eye mark, eye symbol on forehead, painted "
"eye on forehead, bindi, dot on forehead, extra leg, third leg, two left legs, duplicated "
"limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, "
"malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, "
"rainbow river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic "
"circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, "
"esoteric patterns, embroidered symbols, medallion patterns, circular emblems, two people, "
"twins, duplicate person, multiple figures, text, watermark, photorealistic, 3d render")

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
