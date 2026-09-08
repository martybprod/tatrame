import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "master_Eveil_v2_tunique_arc"
SEED = 777065

# ÉVEIL (hors cycle) — v2. Retour terrain sur v1 (generation interrompue par Martin) : (a)
# vetements lus comme modernes -> tunique de lin intemporelle, explicite, avec interdits sur
# tout vetement contemporain ; (b) composition jugee peu interessante (portrait statique
# centre, fils scattered) -> repensee en diagonale/tiers, avec UN fil dore dominant qui trace
# une grande courbe Art Nouveau (whiplash) a travers toute la scene comme colonne vertebrale
# visuelle, plutot que plusieurs fils scattered sans hierarchie.
positive = ("A serene older man with a flowing beard, seated on a natural stone ledge "
"overlooking a wide valley at golden hour, positioned slightly off-center within the "
"composition. He wears a simple flowing tunic of undyed natural linen with a loosely draped "
"shawl over one shoulder, timeless and plain, bare feet, no modern clothing of any kind. His "
"hands rest empty and open on his knees, no loom in front of him. Just behind and above him, "
"partly over his shoulder, stands a tall wooden frame bearing his own completed tapestry — a "
"finished, radiant, radially symmetric mandala woven in every color, catching the light. "
"Below in the valley, several small distant looms are scattered, each attended by a "
"different tiny weaver figure working a single thread of a single pure color. From one of "
"these distant looms, a single continuous golden thread rises in one long graceful sweeping "
"arc across the whole sky, a flowing Art Nouveau whiplash curve that dips low to pass "
"directly beside the seated man — brightening into pure radiant gold exactly as it grazes "
"his chest — before curving onward, unbroken, down to another distant loom on the far side "
"of the valley; fainter secondary threads drift in the same direction further back, echoing "
"the same gesture more quietly. The threads are never caught, never redirected, never cut by "
"him; the gold glow belongs only to the thread passing through, borrowed for an instant. His "
"expression is deeply calm, eyes open, gaze low and unfocused, entirely at peace. The whole "
"image framed by an ornate Art Nouveau golden border with flowing organic whiplash lines and "
"delicate openwork corners echoing the sweep of the main thread — the scene's own landscape "
"and sky show through the corner ornaments, no white or solid fill anywhere in the border. "
"The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant clean "
"contour lines, stylized idealized mature features, flowing hair and beard, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured "
"paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across the scene, muted jewel tones, subtle gold linework, soft "
"misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("modern clothing, contemporary clothing, shirt, dress shirt, collared shirt, "
"trousers, pants, jeans, suit, jacket, blazer, robe with modern cut, shoes, boots, sneakers, "
"sandals, wristwatch, "
"lotus flower, concentric rings of light, halo, aura rings, permanent glowing aura, "
"chrysalis, cocoon, butterfly, disciples gathered around him, followers, hierarchy, throne, "
"crown, staff, scepter, third eye mark, bindi, painted eye on forehead, loom in front of him, "
"weaving tool in his hands, shuttle, beater, active weaving, working a loom, second man, "
"another man in foreground, multiple men, woman, female figure, young man, child, old "
"decrepit man, hunched, frail, rainbow arc in sky, literal rainbow across the sky, "
"flat frontal portrait, centered symmetrical composition, static pose, "
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
