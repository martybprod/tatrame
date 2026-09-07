import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_18_Invisible_v3_arbre"
SEED = 777044

# v3 : grâce — racines fluides danses, objets suspendus comme des joyaux, transition sol soyeuse
positive = ("A single graceful tree at night under a slender crescent moon, its elegant crown rising "
"into a starry twilight sky with flowing Art Nouveau curves. The ground line is drawn as one "
"soft, undulating silky line crossing the card — not a hard straight cut — and the tree's "
"delicate trunk passes through it seamlessly, its bark gently dissolving into roots. Below this "
"gentle line, the tree's root network unfolds like a living lace: fine, curving, sinuous roots "
"that dance and swirl downward with the same flowing elegance as the branches above, glowing "
"with a subdued golden light like filigree jewelry, spreading much wider and deeper than the "
"crown. Suspended within this luminous filigree, like precious gems set in a necklace, hang a "
"few small treasures from lives long past — a ring, an old key, a tiny crown — each one "
"separate and distinct, cradled and encircled by the curved roots themselves, perfectly "
"composed like jewels in a display, never scattered or buried. The roots and the ground fade "
"into one another in soft watercolor gradients. In the far distance on the horizon, two "
"standing stones rise side by side, silent and discreet. No human figure anywhere in the "
"scene. The visible world above ground is quiet, dim and small; the hidden world below is "
"vast, radiant and alive. The whole image is framed by an ornate Art Nouveau golden border "
"with flowing organic whiplash lines and delicate ornamental corners, enclosing the entire "
"card. Flat decorative Art Nouveau illustration style, bold elegant clean contour lines, "
"stylized idealized forms, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, mystical "
"dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene according to its mood, muted "
"jewel tones, subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not "
"airbrushed.")

negative = ("angels, cherubs, putti, angelots, winged figures in corners, corner figures, decorative "
"figures in upper corners, clouds with figures, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, hard straight ground line, sharp cut "
"between ground and underground, objects scattered on the ground, objects buried in dirt, "
"cluttered objects, extra leg, third leg, two left legs, duplicated limb, missing foot, "
"missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, malformed anatomy, bad anatomy, "
"disfigured, mutated, human figure, person, face in the roots, faces in the ground, skulls, "
"bones, two trees, several trees, forest, random occult symbols, magic circles, alchemical "
"sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, circular emblems, photorealistic, 3d render, text, "
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
