import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "master_Eveil_v1_maitre_fil"
SEED = 777064

# ÉVEIL (hors cycle) — concept "Ta Trame" retravaille : LE MAITRE-FIL. Il ne tisse plus, sa
# trame (carte XXI) est achevee derriere lui. Les fils des autres tisserands, au loin, passent
# pres de lui et s'embrasent d'or un instant a son contact, puis repartent inchanges vers leur
# propre metier — il ne les capte pas, ne les redirige pas. La lumiere doree n'est pas la
# sienne, elle appartient aux fils qui la lui empruntent en passant.
positive = ("A serene older man sitting cross-legged in quiet stillness in a wide, harmonious "
"natural landscape at golden hour, his hands empty and resting on his knees, no loom in front "
"of him. Behind him stands a tall wooden frame bearing his own completed tapestry — a "
"finished, radiant, radially symmetric mandala woven in every color, fully achieved, catching "
"the light like a quiet accomplishment already behind him rather than a task ahead. Scattered "
"far across the landscape, several small distant looms each stand attended by a different "
"tiny weaver figure, each working a single thread of a single pure color, distinctly "
"different from the others. From each of these distant looms, a thin luminous thread rises "
"into the air, drifts across the sky, and passes close beside the seated man — brightening "
"briefly into pure gold light exactly as it nears him — then continues on unchanged in its "
"own original color, carrying onward uninterrupted to complete its own distant weaving; the "
"threads are never caught, never redirected, never cut by him. Soft golden light appears only "
"at the points where a passing thread grazes his chest or brow, a brief glow that is not his "
"own but borrowed for an instant by the thread itself; he does not radiate light on his own. "
"His expression is deeply calm, eyes open, gaze low and unfocused, entirely at peace, "
"offering nothing and asking nothing of anyone. The whole image framed by an ornate Art "
"Nouveau golden border with flowing organic whiplash lines and delicate openwork corners — "
"the scene's own landscape and sky show through the corner ornaments, no white or solid fill "
"anywhere in the border. The figure drawn in the flat decorative style of Alphonse Mucha — "
"bold elegant clean contour lines, stylized idealized mature features, flowing hair and "
"beard, flat areas of soft watercolor pigment, minimal shading. Entirely hand-painted "
"watercolor on textured paper, visible paper grain and pigment bleeds, Art Nouveau, mystical "
"dreamlike mood, a rich complete color palette spanning the full range of warm and cool hues, "
"harmoniously balanced and distributed naturally across the scene, muted jewel tones, subtle "
"gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("lotus flower, concentric rings of light, halo, aura rings, permanent glowing aura, "
"chrysalis, cocoon, butterfly, disciples gathered around him, followers, hierarchy, throne, "
"crown, staff, scepter, third eye mark, bindi, painted eye on forehead, loom in front of him, "
"weaving tool in his hands, shuttle, beater, active weaving, working a loom, second man, "
"another man in foreground, multiple men, woman, female figure, young man, child, old "
"decrepit man, hunched, frail, rainbow arc in sky, literal rainbow across the sky, "
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
