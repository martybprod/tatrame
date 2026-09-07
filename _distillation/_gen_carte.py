import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_18_Invisible_v2_arbre"
SEED = 777044

# XVIII · L'INVISIBLE — concept v2 "L'ARBRE ET SES RACINES" (remplace le portail+lézards)
positive = ("A single great tree at night under a crescent moon, its dark slender crown rising into "
"a starry twilight sky. The image shows the earth in cross-section: below the ground line, the "
"tree's vast root network spreads much wider and deeper than the crown above, glowing softly "
"with subdued golden light like a luminous underground web, far larger than the visible part of "
"the tree. Nestled here and there within the glowing roots, the earth holds small distinct "
"objects from lives long past: a ring, an old key, a tiny crown, a small hourglass — each one "
"separate and clearly different, held gently in the root network like keepsakes. In the far "
"distance on the horizon, two standing stones rise side by side, silent and discreet. No human "
"figure anywhere in the scene. The visible world above ground is quiet, dim and small; the "
"hidden world below is vast, radiant and alive. The whole image is framed by an ornate Art "
"Nouveau golden border with flowing organic whiplash lines and delicate ornamental corners, "
"enclosing the entire card. Flat decorative Art Nouveau illustration style, bold elegant clean "
"contour lines, stylized idealized forms, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, mystical dreamlike mood, a rich complete color palette spanning the full range of warm "
"and cool hues, harmoniously balanced and distributed naturally across the scene according to "
"its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, "
"not 3d, not airbrushed.")

# Retour au négatif standard (plus d'exception arc-en-ciel : les lézards ont disparu avec le concept v1)
negative = ("angels, cherubs, putti, angelots, winged figures in corners, corner figures, decorative "
"figures in upper corners, clouds with figures, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom hand, "
"disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra finger, "
"malformed anatomy, bad anatomy, disfigured, mutated, human figure, person, face in the roots, "
"faces in the ground, skulls, bones, two trees, several trees, forest, random occult symbols, "
"magic circles, alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, "
"esoteric patterns, embroidered symbols, medallion patterns, circular emblems, photorealistic, "
"3d render, text, watermark")

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
