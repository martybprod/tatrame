import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_04_Liberte_v9_chemin_nait_sous_ses_pas"
SEED = 777074

# IV · LIBERTÉ — fleurs devant le personnage en v6/v7/v8 malgre consignes "ahead/behind" et
# gauche/droite. Changement d'angle creatif propose par Martin (qui a raison : le modele sait
# parfaitement generer un marcheur sur une plage sans traces devant lui) : au lieu d'interdire
# devant, decrire le chemin comme NAISSANT sous ses pas — le sentier fleuri est incomplet,
# encore en train de se creer, il s'arrete net sous son pied arriere, comme une maree de
# couleurs qui le suit avec un pas de retard. Devant lui, pas un sentier vierge a ne pas
# toucher : il n'y a RIEN DU TOUT, le chemin n'existe pas encore — il est le premier homme a
# marcher ici, il invente son chemin en avancant.
positive = ("A powerful young man seen in clear left-facing profile, walking steadily toward "
"the left edge of the frame, away from an ancient stone monolith carved with ram-head motifs "
"at its base, weathered and deeply cracked, overtaken by climbing green vines, standing in "
"the right background far behind him. He wears a flowing knee-length tunic with a sash, his "
"legs and feet completely bare, no trousers, no boots, no shoes. A small sun emblem is "
"embroidered discreetly on his shoulder. He holds a lit torch low at his side, close to his "
"body, its flame small and warm, lighting his own next step rather than raised overhead in "
"triumph. He is the very first person ever to walk here: a flowering trail is being born "
"under his bare feet as he goes, exactly like footprints appearing in wet sand only behind a "
"lone beach walker. This blooming trail begins at the old monolith far behind him and ends "
"abruptly, precisely beneath his trailing back foot — a tide of small wildflowers of every "
"color chasing him faithfully but always one step late, each burst of bloom rooted inside "
"the shape of a footprint he has already left on the solid rock, never floating above the "
"ground. The unfinished path is still catching up with him: ahead of his leading foot, "
"toward the left edge of the frame, the path does not exist at all yet — nothing but open "
"pristine bare rock, smooth and untouched, without a single footprint, without a single "
"flower, the way wind-swept stone looks when no one has ever crossed it. His next step will "
"create the next flower. Far above, high in the open sky, an eagle circles at a distance, a "
"silent messenger between earth and heaven. His posture is calm and forward-moving, walking "
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

negative = ("footprints ahead of him, footprints in front of the walker, footprints on "
"untouched ground, flowers ahead of him, flowers in front of the walking man, flowers to the "
"left of the man, flowers near the left edge of the frame, complete finished path, path "
"continuing past his feet, path already drawn in front of him, trail ahead of the walker, "
"two trails, trail on both sides of him, "
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
