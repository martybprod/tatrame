import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_06_Union_v14_miroir_qui_s_envole"
SEED = 777080

# VI · UNION — concept retravaille "LE MIROIR QUI S'ENVOLE" (2026-09-09). v1-v13 avaient
# deliberement evite la lecture romantique (deux amis qui courent, sans contact). Renommage en
# "Amitie" envisage puis abandonne (collision avec la carte mineure eau_02). Decision : garder
# le nom "Union" et refaire la carte pour qu'elle y corresponde enfin — romance assumee cette
# fois. Retour aux symboles Osho/Rider originaux laisses de cote : amour comme miroir, deux
# arbres (fruite/nu), serpent, soleil entre eux, ailes (reinterpretees en oiseaux plutot qu'en
# ailes d'ange sur le dos, pour eviter le piege "photo de mariage" deja identifie en v2).
positive = ("A young man and a young woman standing face to face on a gentle grassy rise at "
"the break of dawn, close together, their hands joined between them, gazing at each other "
"with warm, tender intimacy. Behind the man stands a graceful tree, bare and elegant, its "
"bare branches traced delicate against the sky — the tree of knowledge. Behind the woman "
"stands a second tree, heavy with ripe fruit hanging low among its leaves — the tree of "
"life. Each is framed by the tree the other is not standing before, as if the landscape "
"itself completes what is missing in the other, the partner reflected in the world around "
"them. A small serpent lies coiled peacefully at the base of the bare tree, calm and "
"unthreatening, a quiet keeper of wisdom rather than a warning. The first light of the "
"rising sun breaks low on the horizon exactly at the point where their joined hands meet, a "
"warm golden glow gathering there rather than centered blankly above them. From each of "
"their shoulders, a light flock of small birds lifts gently into the air — one flock rising "
"from him, one from her — the two flocks curving together as they climb, merging into a "
"single spiraling flight above the couple, ascending toward the open sky, love visibly "
"lifting them both higher together. Wind stirs their hair and simple flowing garments, quiet "
"motion in an otherwise still moment. The whole image framed by an ornate Art Nouveau golden "
"border with flowing organic whiplash lines and delicate openwork corners — the scene's own "
"sky and landscape show through the corner ornaments, no white or solid fill anywhere in the "
"border. The figures drawn in the flat decorative style of Alphonse Mucha — bold elegant "
"clean contour lines, stylized idealized features, flowing ornamental hair, flat areas of "
"soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured "
"paper, visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich "
"complete color palette spanning the full range of warm and cool hues, harmoniously balanced "
"and distributed naturally across the scene according to its mood, muted jewel tones, subtle "
"gold linework, soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("wedding photo pose, bridal gown, wedding dress, tuxedo, formal wedding attire, "
"veil, static stiff pose, angel wings, feathered wings on their backs, literal wings on the "
"body, wings growing from their shoulders, third person, second couple, child, crowd, "
"modern clothing, sunglasses, wristwatch, phone, jewelry, "
"malformed birds, too many birds, chaotic scattered flock, disconnected flocks, birds not "
"merging, single bird only, "
"random occult symbols, magic circles, alchemical sigils, mystical glyphs, decorative rune "
"circles, meaningless icons, esoteric patterns, extra leg, third leg, two left legs, "
"duplicated limb, missing foot, missing leg, missing limb, extra arm, third arm, phantom "
"hand, disembodied hand, extra hand, floating hand, malformed hands, fused fingers, extra "
"finger, malformed anatomy, bad anatomy, disfigured, mutated, two women, two men, same "
"gender couple, twins, identical faces, white solid border, plain white frame, solid filled "
"border, no border, text, watermark, photorealistic, 3d render")

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
