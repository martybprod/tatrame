import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "master_Eveil_v5_bordure_transparente"
SEED = 777068

# ÉVEIL (hors cycle) — v4 validee dans l'esprit ("magnifique"). v5 : seule correction, les
# cercles du cadre Art Nouveau (surtout inferieurs) montraient un remplissage plein beige au
# lieu de la transparence habituelle du deck -> consigne renforcee + interdits explicites.
positive = ("A vast, sweeping mountain landscape seen from a great distance, an immense sense "
"of scale — jagged peaks, deep valleys, winding rivers, and forests spread far below. At the "
"very summit of the highest peak, a single tiny human figure stands motionless, barely "
"visible against the vastness, facing outward toward the view, wearing a simple timeless "
"tunic. Around this one still point, the whole world is in visible motion: long ribbons of "
"cloud streaming and curling past the peak in graceful sweeping Art Nouveau curves, birds "
"circling in wide arcs far below, wind bending the grasses and treetops on the lower slopes "
"into flowing waves, a river winding and glinting through the valley floor. Everything moves "
"— except the tiny figure at the summit and the peak beneath his feet, both perfectly still, "
"an unmoving axis around which the entire landscape seems to turn. Soft golden light breaks "
"through the clouds and falls gently on the summit alone, the only place in the whole scene "
"untouched by any shadow or motion. The whole image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners, echoing the "
"curling clouds and wind — every circular medallion and roundel in the border, especially "
"the ones in the lower corners, is open and transparent, showing the scene's own sky and "
"mountains directly through it, with absolutely no solid color fill of any kind — not white, "
"not beige, not any flat color — inside any circle or roundel anywhere in the border. The "
"scene rendered in the flat "
"decorative style of Alphonse Mucha — bold elegant clean contour lines, flowing organic "
"curves throughout the clouds, wind, and water, flat areas of soft watercolor pigment, "
"minimal shading. Entirely hand-painted watercolor on textured paper, visible paper grain "
"and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene, muted jewel tones, subtle gold linework, soft misty atmosphere, "
"not photorealistic, not 3d, not airbrushed.")

negative = ("beige fill in border circles, solid beige medallion, solid colored roundel, "
"filled corner circle, opaque corner medallion, flat color inside border circle, solid disk "
"in border, solid fill in lower corner circles, "
"close-up, prominent figure, large figure, figure filling the frame, detailed "
"face, portrait, foreground figure, second figure, multiple people, crowd, animals in "
"foreground, modern clothing, contemporary clothing, shirt, trousers, jeans, suit, jacket, "
"shoes, boots, sneakers, loom, weaving, tapestry, thread, shuttle, mandala, "
"static clouds, still clouds, calm weather everywhere, no motion, uniform stillness, flat "
"empty sky, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune "
"circles, meaningless icons, esoteric patterns, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom "
"hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra "
"finger, malformed anatomy, bad anatomy, disfigured, mutated, white solid border, plain "
"white frame, solid filled border, no border, text, watermark, photorealistic, 3d render")

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
