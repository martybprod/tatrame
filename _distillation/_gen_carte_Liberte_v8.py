import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_04_Liberte_v8_gauche_droite"
SEED = 777073

# IV · LIBERTÉ — v6 ET v7 interrompues par Martin : des fleurs continuaient d'apparaitre DEVANT
# le personnage malgre la consigne "ahead/behind", trop abstraite pour le modele. v8 : ancrage
# concret sur la gauche/droite de l'image plutot que sur une notion de "devant/derriere"
# relative a sa pose — il marche en direction du bord GAUCHE du cadre, le monolithe reste a
# DROITE en arriere-plan, les fleurs sont explicitement limitees au cote DROIT (entre lui et
# le monolithe) et bannies du cote GAUCHE (son sens de marche).
positive = ("A powerful young man seen in clear left-facing profile, walking steadily toward "
"the left edge of the frame, away from an ancient stone monolith carved with ram-head motifs "
"at its base, weathered and deeply cracked, overtaken by climbing green vines, standing in "
"the right background behind him. He wears a flowing knee-length tunic with a sash, his legs "
"and feet completely bare, no trousers, no boots, no shoes. A small sun emblem is embroidered "
"discreetly on his shoulder. He holds a lit torch low at his side, close to his body, its "
"flame small and warm, lighting his own next step rather than raised overhead in triumph. He "
"walks along a clear bare rocky path, solid ground stretching visibly across the whole scene. "
"On the right side of the path, in the whole stretch of ground between his trailing back "
"foot and the monolith behind him, a trail of individual footprints is each marked by its "
"own small burst of wildflowers of every color, blooming exactly within the footprint's "
"shape, rooted directly in the solid rock, never floating above it — most vivid right behind "
"his trailing foot, gradually thinning back toward the monolith. On the left side of the "
"path, from directly beneath his leading front foot all the way to the left edge of the "
"frame, the ground is completely bare plain rock with absolutely no flowers anywhere in that "
"direction — the side he is walking toward is untouched and flowerless. Far above, "
"high in the open sky, an eagle circles at a distance, a silent "
"messenger between earth and heaven. His posture is calm and forward-moving, walking "
"purposefully rather than defiantly, self-possessed. The whole image framed by "
"an ornate Art Nouveau golden border with flowing organic whiplash lines and delicate "
"openwork corners — the scene's own sky and mountains show through the corner ornaments, no "
"white or solid fill anywhere in the border. The figure drawn in the flat decorative style of "
"Alphonse Mucha — bold elegant clean contour lines, stylized idealized features, flowing "
"ornamental hair, flat areas of soft watercolor pigment, minimal shading. Entirely "
"hand-painted watercolor on textured paper, visible paper grain and pigment bleeds, Art "
"Nouveau, mystical dreamlike mood, a rich complete color palette spanning the full range of "
"warm and cool hues, harmoniously balanced and distributed naturally across the scene "
"according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("flowers on the left side of the path, flowers to the left of the man, flowers "
"near the left edge of the frame, flowers ahead of him, flowers in his path forward, "
"flowers in front of the walking man, flowers on the untouched path, flowers where he has "
"not yet stepped, flowers under his leading foot, flowers past his leading foot, "
"flowers floating in mid-air, flowers disconnected from the ground, hovering "
"flowers, flowers in empty space, scattered flowers with no visible path, flower trail not "
"grounded, path disappearing into void, ungrounded background, "
"broken chain, chain at his feet, chains, raised torch, torch held overhead, "
"triumphant pose, Statue of Liberty pose, arm raised straight up, wings on his own body, "
"organic wings, feathered wings on the man, modern clothing, trousers, pants, jeans, shoes, "
"boots, sneakers, sandals, second man, another man, woman, child, "
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
