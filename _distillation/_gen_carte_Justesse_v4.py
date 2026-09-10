import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_11_Justesse_v4_fil_qu_on_coupe"
SEED = 777110

# XI · JUSTESSE — concept retravaille "LE FIL QU'ON COUPE" (2026-09-10). v3 (femme + epee
# dans une colonnade) tres belle mais la plus "Rider orthodoxe" du deck. Dans Ta Trame, la
# justesse n'est pas trancher dans le vide : c'est trouver le point exact sur le fil et
# savoir qu'on va couper. Le rouge d'Osho = la couleur du fil ; l'epee de Rider = le geste
# de coupe suspendu ; la balance relachee conservee au sol (intacte, pas brisee — coherence
# retour terrain v2).
positive = ("A calm, precise woman seated at her wooden tapestry loom in a quiet "
"softly-lit room at morning, the loom mostly bare, its frame simple and unadorned so all "
"attention rests on the single thread she is working with. Stretched taut between her "
"two hands runs one single vivid crimson-red thread, and with her other hand she holds "
"a pair of fine weaver's scissors positioned exactly at the precise point on that "
"thread where the cut must be made — the scissors touching the thread but not yet "
"closing, the gesture suspended at the exact instant the decision is taken, neither "
"hesitation nor haste, simply absolute precision. Her eyes are on that exact point, "
"clear-eyed and quietly certain, her whole posture composed and deliberate. On the "
"floor beside the loom rests an old brass balance scale, set down and gently released, "
"still intact but simply no longer needed, quietly abandoned — the old way of judging, "
"laid aside. Nothing else clutters the scene: the room is spare and soft, warm morning "
"light falling gently through a window and illuminating her hands and the red thread, "
"nothing glowing on her body itself. She wears a flowing timeless robe with bare feet, "
"no modern clothing, and a loose strand of her hair has escaped as she leans slightly "
"forward in concentration. The whole image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners — the "
"scene's own soft room light shows through the corner ornaments, no white or solid "
"fill anywhere in the border. The figure drawn in the flat decorative style of "
"Alphonse Mucha — bold elegant clean contour lines, stylized idealized mature "
"features, flowing ornamental hair, flat areas of soft watercolor pigment, minimal "
"shading. Entirely hand-painted watercolor on textured paper, visible paper grain and "
"pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color palette "
"spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold "
"linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("broken scale, shattered scale, damaged balance scale, destruction, "
"explosion, debris, shattering, falling masonry, sword, blade, weapon, glowing body, "
"glowing plexus, glowing chest, red light on skin, fiery aura, "
"modern clothing, contemporary clothing, trousers, jeans, shoes, boots, sneakers, "
"wristwatch, jewelry, second person, man, crowd, child, "
"cut thread, severed thread, thread already cut, two threads, tangled threads, knots, "
"closed scissors, scissors mid-cut, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative "
"rune circles, meaningless icons, esoteric patterns, extra leg, third leg, two left "
"legs, duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, "
"phantom hand, disembodied hand, extra hand, floating hand, malformed hands, fused "
"fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, white "
"solid border, plain white frame, solid filled border, no border, text, watermark, "
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
