import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_04_Liberte_v7_fleurs_arriere_seulement"
SEED = 777072

# IV · LIBERTÉ — v6 interrompue par Martin : des fleurs apparaissaient DEVANT le personnage,
# sur le sentier qu'il n'a pas encore parcouru. Correction : fleurs uniquement DERRIERE lui,
# jusqu'a ses pieds ; le sentier devant lui (sens de la marche) doit rester pierre nue.
positive = ("A powerful young man walking calmly away from an ancient stone monolith carved "
"with ram-head motifs at its base, weathered and deeply cracked, overtaken by climbing green "
"vines — the old authority reclaimed by nature, standing behind him as he moves forward. He "
"wears a flowing knee-length tunic with a sash, his legs and feet completely bare, no "
"trousers, no boots, no shoes. A small sun emblem is embroidered discreetly on his shoulder. "
"He holds a lit torch low at his side, close to his body, its flame small and warm, lighting "
"his own next step rather than raised overhead in triumph. He walks along a clear bare rocky "
"path, solid ground stretching visibly from the foreground all the way back to the monolith, "
"never disappearing into empty space. Each of his bare footprints pressed into that path is "
"distinctly marked by its own small burst of wildflowers of every color, blooming exactly "
"within the shape of that single footprint, rooted directly in the solid rock of the path "
"itself, never floating or hovering above the ground — a clear trail of individually "
"flowering footprints running back along the path, most vivid and abundant at his most "
"recent step, gradually thinning back into plain bare rock near the old monolith. The path "
"ahead of him, in the direction he is walking, remains completely bare rock with no flowers "
"at all — the flowering footprints exist only behind him, on the ground he has already "
"crossed, ending exactly at his most recent footprint; nothing has bloomed yet on the "
"untouched ground still in front of him. Far above, "
"high in the open sky, an eagle circles at a distance, a silent "
"messenger between earth and heaven. His posture is calm and forward-moving, three-quarter "
"view, walking purposefully rather than defiantly, self-possessed. The whole image framed by "
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

negative = ("flowers ahead of him, flowers in his path forward, flowers in front of the "
"walking man, flowers on the untouched path, flowers where he has not yet stepped, "
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
