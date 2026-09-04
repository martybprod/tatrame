import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_13_Transformation_v6"
SEED = 777035

positive = ("An immense chrysalis hangs suspended above a vast flower of the void — a real, clearly "
"recognizable flower with large unfurling petals, its shape unmistakably floral, softly glowing from "
"within — a faint, soft, indistinct silhouette of a form can just barely be guessed within the warm "
"inner glow, its outline gentle and unclear, no visible limbs, no discernible face, just the hint "
"that a being is taking shape inside. A single elegant double-edged sword with a long clean blade and "
"no pommel, one sword only, rests flat on the flower's petals well away from the flower's stem, not "
"near it, not threatening to cut it in any way, at a clear distance from everything else, its blade "
"catching soft light. Nearby, a snake is caught mid-shedding, its old translucent skin peeling away "
"along its body to reveal fresh scales beneath, a vivid image of transformation itself — its head and "
"tail both clearly visible and well-formed. The sword and the snake are clearly separated, never "
"touching. A broken chain lies unmistakably snapped and open on the ground below the chrysalis, one "
"link clearly split apart with its two broken ends visibly separated from each other, the whole chain "
"lying slack and loose, binding absolutely nothing — a clear, unambiguous symbol of liberation, of "
"old limitations finally shattered and set down. A small yin-yang symbol glows softly exactly where "
"the chrysalis touches the flower. A single white rose, and only this one additional flower, blooms "
"beside it on the same stem — no other flowers anywhere. Centered in the background behind the "
"chrysalis, larger and clearly visible, a pale white horse stands quietly in soft mist — an important "
"presence centered on the horizon, not tiny, not in a corner. No human figure anywhere in the "
"composition. Flat decorative Art Nouveau illustration style, bold elegant clean contour lines, flat "
"areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured "
"paper, visible paper grain and pigment bleeds, mystical dreamlike mood, a rich complete color "
"palette spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold linework, soft "
"misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("sword near stem, sword touching stem, sword cutting stem, intact chain, closed chain, "
"unbroken chain, chain still linked, abstract shape not a flower, platform not a flower, headless "
"snake, snake without head, snake ring, ouroboros, snake biting tail, human figure, person, people, "
"visible anatomy, arms in chrysalis, body in chrysalis, face in chrysalis, clearly visible figure in "
"chrysalis, two swords, multiple swords, sword piercing snake, sword through snake, sword impaling, "
"pink flower, second flower, extra flowers, skeleton, skull, grim reaper, dead body, corpse, macabre, "
"scary, horse in corner, tiny horse, extra leg, third leg, two left legs, duplicated limb, missing "
"foot, missing leg, missing limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, "
"floating hand, malformed hands, fused fingers, extra finger, extra wing, three wings, deformed wing, "
"malformed anatomy, bad anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow "
"river, rainbow sky, prismatic streak, spectrum band, random occult symbols, magic circles, "
"alchemical sigils, mystical glyphs, decorative rune circles, meaningless icons, esoteric patterns, "
"embroidered symbols, medallion patterns, text, watermark, photorealistic, 3d render")

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
