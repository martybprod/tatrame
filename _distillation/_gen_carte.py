import json, urllib.request, base64, time

URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTDIR = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/"

NAME = "major_15_Emprise_v3"
SEED = 777040

positive = ("A single person standing on a small low black pedestal, held like a puppet: fine threads "
"descend from a faint, indistinct hand and source high above, attaching to the person's wrists, "
"shoulders and head, controlling them from outside. These same threads have woven a dull, drab grey "
"costume all around the person's body, an imposed second skin spun over them — yet a warm radiant "
"inner light clearly shines through the woven costume, the person's true luminous nature glowing "
"through the drab weave, impossible to fully hide. A loose iron chain lies slack on the ground at "
"the pedestal's base, its links open and unlocked, binding nothing — a servitude that could be shed "
"at any moment. Nearby, a single torch is held completely upside down — its handle pointing straight "
"up, its flame burning downward toward the ground, clearly inverted, unmistakably not in its normal "
"upright position. At the person's feet, a still reflective pool shows something entirely different "
"from the person above: not a detailed figure, but a pure luminous silhouette of light in the vague "
"shape of a being, glowing in rich multicolored light — no distinct facial features, no visible "
"anatomy, no threads, no chains, no drab costume, just a radiant abstract glow of many colors in a "
"humanoid shape, free and shining. The figure drawn in the flat decorative style of Alphonse Mucha — "
"bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat areas "
"of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, a rich complete color "
"palette spanning the full range of warm and cool hues, harmoniously balanced and distributed "
"naturally across the scene according to its mood, muted jewel tones, subtle gold linework, soft "
"misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("detailed face in reflection, anatomy in reflection, chains in reflection, threads in "
"reflection, costume in reflection, upright torch, torch standing upright, flame pointing up, grey "
"pedestal, white pedestal, horned devil, demon, baphomet, satanic, inverted pentagram, scary "
"monster, extra leg, third leg, two left legs, duplicated limb, missing foot, missing leg, missing "
"limb, extra arm, third arm, phantom hand, disembodied hand, extra hand, floating hand, malformed "
"hands, fused fingers, extra finger, extra wing, three wings, deformed wing, malformed anatomy, bad "
"anatomy, disfigured, mutated, rainbow, rainbow arc, rainbow gradient, rainbow river, rainbow sky, "
"prismatic streak, spectrum band, random occult symbols, magic circles, alchemical sigils, mystical "
"glyphs, decorative rune circles, meaningless icons, esoteric patterns, embroidered symbols, "
"medallion patterns, circular emblems, text, watermark, photorealistic, 3d render")

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
