import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_04_Liberte_v14_pied_phare"
SEED = 777079

# IV · LIBERTÉ — v13 "mieux, mais pas encore parfait". Deux corrections : (a) la nouvelle
# fleur doit etre VRAIMENT sous le pied, pas juste "a ses pieds" -> ancrage physique direct
# (elle touche/effleure la plante du pied, pousse entre ses orteils) ; (b) flamme de la torche
# trop discrete -> reference concrete "lumiere de phare" (chaude, qui porte loin, sans etre
# eblouissante).
positive = ("A powerful young man walking toward the viewer down a gentle rocky slope, seen "
"in a low three-quarter frontal view, positioned large in the lower-left foreground of the "
"frame, mid-stride, calmly heading toward the bottom-left corner as if about to step out of "
"the picture. The first light of dawn enters from the lower left, warm gold washing over his "
"face and the near rock. He wears a flowing knee-length tunic with a sash, his legs and feet "
"completely bare, no trousers, no boots, no shoes. A small sun emblem is embroidered "
"discreetly on his shoulder. In one hand, held low at his side, he carries a lit torch whose "
"flame burns like a small lighthouse beacon — warm, radiant, and clearly the brightest light "
"in the scene, its glow visibly touching the nearby rock and his own skin, carrying further "
"than an ordinary candle flame yet soft-edged and warm rather than harsh or blinding, never "
"raised overhead in triumph. Far behind him, high up the slope in the upper-right distance, stands an ancient "
"stone monolith carved with ram-head motifs at its base and two weathered stone wings "
"spreading from its sides, deeply cracked and overtaken by green climbing vines, standing in "
"cool blue shadow — the old authority reclaimed by nature. A single narrow trail of blooming "
"footprints recedes from the man's trailing back foot up the slope toward that monolith, "
"exactly like the trail a lone walker leaves behind in wet sand: each footprint is filled "
"with its own small burst of wildflowers of every color, rooted in the solid rock, growing "
"smaller and softer with distance until the trail ends at the base of the monolith. This "
"trail exists only in that one single line behind him. Everywhere else the rock is bare: in "
"particular the whole stretch of smooth stone between the man and the bottom-left corner of "
"the frame — the ground he is about to cross — is completely pristine, without a single "
"footprint, without a single flower, untouched as wind-swept stone that no one has ever "
"crossed. His leading front foot is lifted just barely off the ground, mid-step. One or two "
"small wildflowers grow directly underneath the sole of that raised foot, their petals "
"brushing and touching his bare skin, small stems reaching up between his toes — the bloom "
"is physically in contact with his foot, tucked right under it, not on the ground a step "
"away, not beside it, not near it but genuinely touching the sole itself, the very first and "
"freshest bloom of the whole trail. High in the open sky on the "
"upper-left side of the frame, clearly separated from "
"the monolith and far away from any structure, a single golden eagle soars at a great "
"distance — a true majestic eagle with a broad wingspan, both wide wings fully spread in a "
"shallow steady V, its fanned tail clearly visible, its white-hooked head turned along its "
"flight line, every feather defined — crossing the dawn sky above the empty quarter of the "
"composition, a silent messenger "
"between earth and heaven. His face is turned toward the dawn light, his gaze soft and "
"confident at once — a gentle, open, assured expression, serene certainty without hardness, "
"the past crumbled behind him, dawn ahead. The whole composition is evenly balanced: the "
"large figure anchoring the lower-left foreground, the monolith and its blooming trail "
"occupying the upper-right distance, the eagle and open sky breathing in between. The whole "
"image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners — the scene's own "
"sky and mountains show through the corner ornaments, no white or solid fill anywhere in the "
"border. The figure drawn in the flat decorative style of Alphonse Mucha — bold elegant "
"clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured "
"paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across the scene according to its mood, muted jewel tones, "
"subtle gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("dim torch flame, weak torch flame, small candle flame, faint torch light, "
"flowers beside his foot, flowers offset from his foot, flowers next to his "
"feet, flowers not aligned with his footprint, flowers near but not touching his foot, "
"flowers a step away from him, flowers under the wrong foot, flowers detached from his foot, "
"deformed bird, malformed eagle, blurry bird, generic dark bird shape, "
"shapeless black bird, wingless bird, stubby wings, asymmetric wings, extra wing, "
"eagle next to the monolith, eagle touching the monolith, eagle perched on "
"stone, eagle low in the frame, large dominant eagle, "
"harsh gaze, defiant stare, aggressive expression, hard face, scowling, "
"flowers in the lower-left foreground, flowers near the bottom-left corner, "
"flowers around his leading foot, footprints in the foreground, blooming trail in the "
"foreground, footprints beside the walker, footprints on both sides of him, two trails, "
"scattered flowers everywhere, flowers in front of his feet, flowers ahead of the walker, "
"footprints ahead of the walker, side profile view, profile walking view, "
"broken chain, chains, raised torch, torch held overhead, triumphant pose, Statue of Liberty "
"pose, wings on his own body, organic wings, feathered wings on the man, modern clothing, "
"trousers, pants, jeans, shoes, boots, sneakers, sandals, second man, another man, woman, "
"child, rainbow arc in sky, random occult symbols, magic circles, alchemical sigils, "
"mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, extra leg, "
"third leg, two left legs, duplicated limb, missing foot, missing leg, missing limb, extra "
"arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed hands, "
"fused fingers, extra finger, malformed anatomy, bad anatomy, disfigured, mutated, white "
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
