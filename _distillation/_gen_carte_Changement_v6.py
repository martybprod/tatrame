import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_10_Changement_v6_roue_tisseuse"
SEED = 777082

# X · CHANGEMENT — concept retravaille "LA ROUE-TISSEUSE" (2026-09-09). v5 (roue cosmique
# statique) jugee "poster esoterique" ; le candidat tissage note au kit jamais exploite. La
# roue a rayons-fils tourne et TISSE le monde : cote montant = fil brut (chaine vierge),
# cote descendant = tissu acheve ou les quatre saisons se succendent cousues dans la trame.
# Sphinx assis a distance, observant (l'enigme regarde le temps passer sans y toucher —
# lesson v2-v3 : jamais juche/prominent). Serpent = fil dore qui se devide le long d'un rayon
# (lacher-prise litteral, UN SEUL serpent — lesson v4-v5). Yin/yang au moyeu immobile (Osho).
positive = ("A vast upright weaver's wheel filling the composition like a great spinning "
"mandala, its spokes made of taut luminous threads radiating from a still center marked by "
"a small yin-yang symbol, perfectly motionless while everything else turns. As the wheel "
"slowly rotates, it weaves the world itself: on the rising side of the wheel the threads are "
"still raw and undyed, a virgin warp of pale unbleached strands stretching away upward; on "
"the descending side the threads have already become finished woven cloth, and sewn into "
"that fabric the four seasons appear in sequence — spring blossoms, summer green, autumn "
"gold, winter white — flowing down and away as completed cloth. The wheel is turning, and "
"the world is being woven through it. Galaxies and stars swirl faintly around the wheel's "
"outer rim, the twelve zodiac signs etched discreetly along its circumference, faint I "
"Ching trigrams nested just inside them, and four small soft glowing diamond-like points of "
"light marking the cardinal directions nearer the center — never lightning bolts, never "
"zigzags. At a respectful distance from the wheel, seated calmly on a low outcrop of rock, "
"a sphinx in slight three-quarter profile with a single tail curving naturally behind it "
"watches the great wheel turn, the silent riddle observing time pass without touching it. "
"A single small serpent of golden thread slides down along one spoke, unravelling itself "
"from the weave as it descends — letting go made visible, one smooth sinuous golden thread "
"working loose from the pattern and slipping free toward the ground. No human figure — the "
"wheel itself is the subject, vast, turning, weaving. The whole image framed by an ornate "
"Art Nouveau golden border with flowing organic whiplash lines and delicate openwork "
"corners — the scene's own sky and stars show through the corner ornaments, no white or "
"solid fill anywhere in the border. Flat decorative Art Nouveau illustration style, bold "
"elegant clean contour lines, flat areas of soft watercolor pigment, minimal shading. "
"Entirely hand-painted watercolor on textured paper, visible paper grain and pigment "
"bleeds, mystical dreamlike mood, a rich complete color palette spanning the full range of "
"warm and cool hues, harmoniously balanced and distributed naturally across the scene "
"according to its mood, muted jewel tones, subtle gold linework, soft misty atmosphere, not "
"photorealistic, not 3d, not airbrushed.")

negative = ("two serpents, second serpent, multiple serpents, snake attacking, threatening "
"serpent, prominent large serpent, sphinx on top of the wheel, sphinx touching the wheel, "
"sphinx perfectly symmetrical, two tails, doubled sphinx, lightning bolts, zigzag marks, "
"static wheel, wheel not weaving, plain empty wheel, human figure, person at the wheel, "
"weaver, hands, "
"random occult symbols, alchemical sigils, mystical glyphs, decorative rune circles, "
"meaningless icons, solid beige circle in border, miniature scene inside border circle, "
"white solid border, plain white frame, solid filled border, no border, text, watermark, "
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
