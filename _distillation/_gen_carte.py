import json, urllib.request, base64, time, sys

url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

positive = ("A single solitary young man captured mid-stride, in the very act of stepping his leading foot "
"off the edge of a high cliff into empty air, one leg extended forward over the abyss with no ground "
"beneath it, body leaning into the open void, his face refined and serene, gently holding one white rose. "
"He wears a long flowing coat softly patterned with the four elemental colors — red, blue, grey, green. "
"A single small white dog stands alert at the cliff edge behind him. Below, a luminous winding rainbow "
"river flows through misty valleys, a pale dawn sun glows through haze, a single white bird drifts across "
"the sky, distant mountains fade into mist. The figure drawn in the flat decorative style of Alphonse "
"Mucha — bold elegant clean contour lines, stylized idealized features, flowing ornamental hair, flat "
"areas of soft watercolor pigment, minimal shading. Entirely hand-painted watercolor on textured paper, "
"visible paper grain and pigment bleeds, Art Nouveau, mystical dreamlike mood, muted jewel-tone palette "
"with the full rainbow spectrum woven softly throughout in varying proportions, subtle gold linework, "
"soft misty atmosphere, not photorealistic, not 3d, not airbrushed.")

negative = ("two people, twins, duplicate person, multiple figures, extra limbs, deformed hands, extra "
"fingers, text, letters, numbers, watermark, signature, photorealistic, 3d render, oversaturated, candy "
"colors, childish, cartoonish")

payload = {
    "prompt": positive,
    "negative_prompt": negative,
    "seed": -1,
    "steps": 4,
    "cfg_scale": 1,
    "width": 1024,
    "height": 1536,
    "sampler_name": "Euler A Trailing",
    "guidance_embed": 3.5,
    "shift": 3,
    "batch_size": 1,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = resp.read()
    print("HTTP OK, temps:", round(time.time()-t0,1), "s, taille reponse:", len(body))
    out = json.loads(body)
    print("Cles de la reponse:", list(out.keys()))
    imgs = out.get("images", [])
    print("Nombre d'images:", len(imgs))
    if imgs:
        raw = base64.b64decode(imgs[0])
        path = "/Users/martinboucher/Documents/PROJETS_IA/ATRO_PLUS/ASTRO_PLUS_APP/_distillation/tarot_previews_00_confiance_mucha_lora.png"
        with open(path, "wb") as f:
            f.write(raw)
        print("Image sauvegardee:", path, len(raw), "octets")
    info = out.get("info")
    if info:
        try:
            info_d = json.loads(info) if isinstance(info,str) else info
            print("Seed utilise:", info_d.get("seed") if isinstance(info_d,dict) else info)
        except Exception as e:
            print("info brute:", str(info)[:300])
except Exception as e:
    print("ERREUR:", repr(e))
