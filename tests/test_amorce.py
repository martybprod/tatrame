"""L'amorce du matin tenue par des tests — la carte d'accueil et la notification.

L'amorce est le conseil court (1-2 phrases) affiché le matin : la charte
vivante vit dans PASSATION_AMORCE.md (§3 la recette, §3.3 les tests du
geste de rédaction). Ces filets mesurent ce que la relecture humaine oublie :
la longueur, l'annonce d'événement, la recopie sur le miroir, les tics
d'ouverture nés ENTRE les batchs, et les repères de temps impossibles
(« aujourd'hui » sur un transit qui dure des semaines).

Décision du 2026-10-16 (batch ChatGPT validé) : le « peut » d'une clause de
bénéfice d'une action proposée (« parler peut t'aider ») reste permis — ce
sont les formes qui ANNONCENT un événement qui sont bannies ci-dessous.
"""
import datetime as dt
import itertools
import json
import pathlib
import re

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "data" / "corpus"

# Transits lents : des semaines d'amplitude — jamais un « aujourd'hui ».
LENTES = ("jupiter", "saturne", "uranus", "neptune", "pluton")

MOTS_BANNIS = (r"\btravaille\b", r"\btravail\b", r"\btravailler\b",
               r"\bappelle\b", r"\bbosser\b", r"\bdu coup\b")

PREDICTION = (r"\bpourrait\b", r"\bpourront\b", r"\brisqu", r"\btu vas\b",
              r"\bça va\b", r"\bva arriver\b", r"\bva se (passer|produire)\b",
              r"\bpeut (arriver|tomber|changer|tourner|se produire|se présenter)\b",
              r"\bpeuvent (arriver|tomber|changer|tourner)\b", r"\bdemain\b")


def _sources():
    """Toutes les amorces du corpus : (famille, clé, entrée, référence).

    La référence porte le miroir/geste à ne jamais recopier — l'entrée
    elle-même pour les génériques, le générique `numero.annee` pour les
    variantes d'année (amorce seule, fusion côté serveur)."""
    out = []
    transits = json.loads((CORPUS / "transits.json").read_text(encoding="utf-8"))
    for k, e in transits["transits_generiques"].items():
        out.append(("generiques", k, e, e))
    for k, e in transits["transits_precis"].items():
        if not e.get("amorce"):
            continue
        if "miroir" in e:
            ref = e
        else:
            # Entrée à phases : la recopie se vérifie contre TOUS les
            # miros/gestes de phase concaténés.
            ref = {
                "miroir": " ".join(v.get("miroir", "") for v in e.values()
                                   if isinstance(v, dict)),
                "geste": " ".join(v.get("geste", "") for v in e.values()
                                  if isinstance(v, dict)),
            }
        out.append(("precis", k, e, ref))
    voix = json.loads((CORPUS / "titres_voix.json").read_text(encoding="utf-8"))
    gen_annee = voix.get("numero", {}).get("annee", {})
    for num, e in voix.get("numero", {}).get("annee_numeros", {}).items():
        if num.startswith("_") or not e.get("amorce"):
            continue
        out.append(("annee_numeros", num, e, gen_annee))
    for num, e in voix.get("numero", {}).get("mois_numeros", {}).items():
        if num.startswith("_") or not e.get("amorce"):
            continue
        out.append(("mois_numeros", num, e, e))
    for quel, e in voix.get("lune", {}).items():
        if quel.startswith("_") or not e.get("amorce"):
            continue
        out.append(("lune", quel, e, e))
    chinois = json.loads((CORPUS / "chinois_detail.json").read_text(encoding="utf-8"))
    for k, e in chinois.get("relations", {}).items():
        if e.get("amorce"):
            out.append(("chinois", k, e, e))
    return out


def _amorces():
    return _sources()


def _phrases(texte):
    return [p for p in re.split(r"[.!?]+", texte.strip()) if p.strip()]


def _suites(texte, n=8):
    mots = re.findall(r"\w+", texte.lower())
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


# ------------------------------------------------------------- présence

def test_amorce_presente_sur_tous_les_generiques():
    """Le champ `amorce` est la carte du matin : une entrée générique sans
    amorce retomberait sur le miroir long — permis en rollout, plus jamais
    une fois le lot écrit."""
    manquants = [k for famille, k, e, _ in _amorces()
                 if not e.get("amorce", "").strip()]
    assert not manquants, f"entrées sans amorce : {manquants}"


def test_annee_numeros_toutes_presentes():
    """Les 9 variantes d'année existent : c'est ce qui rend la bascule
    « année personnelle » propre à CHAQUE numéro (demande de Martin)."""
    voix = json.loads((CORPUS / "titres_voix.json").read_text(encoding="utf-8"))
    variantes = voix["numero"].get("annee_numeros", {})
    manquants = [n for n in "123456789"
                 if not variantes.get(n, {}).get("amorce", "").strip()]
    assert not manquants, f"annee_numeros sans amorce : {manquants}"


def test_amorce_presente_sur_tous_les_precis():
    """Lot 4 terminé : chaque entrée précise porte son amorce. Pour les
    entrées à phases, le conseil est unique — la variante le reçoit via
    `_resoudre_variantes`."""
    transits = json.loads((CORPUS / "transits.json").read_text(encoding="utf-8"))
    manquants = [k for k, e in transits["transits_precis"].items()
                 if not e.get("amorce", "").strip()]
    assert not manquants, f"entrées précises sans amorce : {manquants}"


def test_phases_de_lune_amorcees():
    """Nouvelle et Pleine ont leur amorce : le pic lunaire gagnant affiche
    le conseil du jour-là, pas le miroir long."""
    voix = json.loads((CORPUS / "titres_voix.json").read_text(encoding="utf-8"))
    manquants = [q for q in ("nouvelle", "pleine")
                 if not voix["lune"].get(q, {}).get("amorce", "").strip()]
    assert not manquants, f"phases de lune sans amorce : {manquants}"


# ------------------------------------------------------------- la forme

def test_amorce_courte_et_complete():
    """1-2 phrases complètes, jamais télégraphiques ; plafond large (38 mots)
    car le goût validé (batch ChatGPT 2026-10-16) monte jusqu'à ~34."""
    fautifs = []
    for famille, k, e, _ in _amorces():
        a = e["amorce"]
        if len(_phrases(a)) > 2:
            fautifs.append((famille, k, "plus de 2 phrases"))
        mots = len(re.findall(r"\w+", a))
        if mots > 38:
            fautifs.append((famille, k, f"{mots} mots"))
    assert not fautifs, f"amorce trop longue : {fautifs}"


def test_amorce_sans_prediction():
    fautifs = []
    for famille, k, e, _ in _amorces():
        for motif in PREDICTION:
            if re.search(motif, e["amorce"], re.IGNORECASE):
                fautifs.append((famille, k, motif))
    assert not fautifs, f"annonce d'événement dans l'amorce : {fautifs}"


def test_amorce_sans_mots_bannis():
    fautifs = []
    for famille, k, e, _ in _amorces():
        for motif in MOTS_BANNIS:
            if re.search(motif, e["amorce"], re.IGNORECASE):
                fautifs.append((famille, k, motif))
    assert not fautifs, f"mot banni dans l'amorce : {fautifs}"


def test_amorce_pas_d_aujourd_hui_sur_un_transit_lent():
    """Un transit lent dure des semaines : « aujourd'hui » y est un mensonge
    de calendrier (demande de Martin, 2026-10-16)."""
    fautifs = []
    for famille, k, e, _ in _amorces():
        if famille != "generiques" or not any(p in k for p in LENTES):
            continue
        if re.search(r"\baujourd['’]hui\b|\bce matin\b", e["amorce"],
                     re.IGNORECASE):
            fautifs.append(k)
    assert not fautifs, (
        f"« aujourd'hui/ce matin » sur un transit lent : {fautifs}")


def test_amorce_pas_de_quand_en_ouverture():
    """« Quand tes plans bougent, … » présuppose l'événement du jour —
    l'amorce conseille, elle n'annonce pas (test du réveil, passation §3.3).
    Les « Si tu sens… » d'état intérieur restent permis."""
    fautifs = []
    for famille, k, e, _ in _amorces():
        if re.match(r"\s*quand\b", e["amorce"], re.IGNORECASE):
            fautifs.append((famille, k, e["amorce"][:40]))
    assert not fautifs, f"ouverture « Quand… » (situation présupposée) : {fautifs}"


# ------------------------------------------------------------- les tics

def test_amorce_ouvertures_variees():
    """Le tic naît entre les batchs : chaque rédacteur respecte sa consigne,
    le corpus assemblé non (la leçon fondatrice de test_corpus.py)."""
    amorces = [e["amorce"] for _, _, e, _ in _amorces()]
    total = len(amorces)
    rappelle = sum(1 for a in amorces
                   if re.match(r"\s*rappelle-toi que", a, re.IGNORECASE))
    besoin = sum(1 for a in amorces
                 if re.match(r"\s*tu n'as pas besoin", a, re.IGNORECASE))
    assert rappelle / total <= 0.40, (
        f"« Rappelle-toi que » en tête : {rappelle}/{total} (> 40 %)")
    assert besoin / total <= 0.35, (
        f"« Tu n'as pas besoin » en tête : {besoin}/{total} (> 35 %)")


# ------------------------------------------------------------- la recopie

def test_amorce_pas_une_reformulation_du_miroir_ou_du_geste():
    fautifs = []
    for famille, k, e, ref in _amorces():
        suites_amorce = _suites(e["amorce"])
        for champ in ("miroir", "geste"):
            partage = suites_amorce & _suites(ref.get(champ, ""))
            if partage:
                fautifs.append((famille, k, champ, sorted(partage)[:2]))
    assert not fautifs, (
        "l'amorce recopie 8 mots du miroir/geste de sa propre entrée : "
        f"{fautifs[:6]}")


def test_les_amorces_ne_se_recopient_pas_entre_elles():
    amorces = {(famille, k): _suites(e["amorce"])
               for famille, k, e, _ in _amorces()}
    fautifs = []
    for a, b in itertools.combinations(sorted(amorces), 2):
        partage = amorces[a] & amorces[b]
        if partage:
            fautifs.append((a, b, len(partage), sorted(partage)[:1]))
    assert not fautifs, (
        f"des amorces se recopient (suites de 8 mots) : {fautifs[:6]}")


# ------------------------------------------------------------- le serveur

def test_le_serveur_resout_amorce_avec_repli_miroir():
    """`_titre_du_jour` résout l'amorce UNE fois : amorce écrite, sinon le
    miroir. Le front et la notification n'ont qu'un champ à lire, et le
    message long reste entier dans `miroir` (il reste affiché ailleurs)."""
    import app as application

    nb = {"jour": 16, "mois": 7, "annee": 1975}
    transit = {"amorce": "Prends une pause avant de répondre quand ça chauffe.",
               "miroir": "Un long miroir qui décrit la journée en détail.",
               "geste": "Fais un pas."}
    titre, _ = application._titre_du_jour(
        {"transit": transit}, 0.9, dt.date(2026, 10, 16), 90.0, nb)
    assert titre["source"] == "ciel"
    assert titre["amorce"] == transit["amorce"]
    assert titre["miroir"] == transit["miroir"]
    # Repli : sans amorce écrite (ex. entrée à phases), la carte du matin
    # affiche le miroir — le comportement d'avant, jamais un texte manquant.
    titre_repli, _ = application._titre_du_jour(
        {"transit": {"miroir": transit["miroir"], "geste": transit["geste"]}},
        0.9, dt.date(2026, 10, 16), 90.0, nb)
    assert titre_repli["amorce"] == transit["miroir"]


def test_la_bascule_d_annee_utilise_l_amorce_du_numero():
    """Le jour de la bascule d'année, l'amorce porte SA couleur : celle du
    numéro qui commence, posée sur les textes longs génériques (demande de
    Martin — une année 4 ne parle pas comme une année 7)."""
    import app as application

    nb = {"jour": 16, "mois": 7, "annee": 1975}
    titre, routage = application._titre_du_jour(
        {"transit": {"miroir": "ciel", "geste": "pas"}}, 0.2,
        dt.date(2026, 1, 2), 90.0, nb)
    assert titre["source"] == "numero"
    num = application.annee_personnelle(nb["jour"], nb["mois"], 2026)
    voix = json.loads((CORPUS / "titres_voix.json").read_text(encoding="utf-8"))
    variante = voix["numero"]["annee_numeros"][str(num)]
    assert titre["amorce"] == variante["amorce"]
    assert titre["miroir"] == voix["numero"]["annee"]["miroir"]
    assert titre["geste"] == voix["numero"]["annee"]["geste"]
