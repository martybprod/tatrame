"""L'astrologie chinoise — la couche déterministe qui manquait au routeur.

But précis : donner au message du jour une QUATRIÈME voix. Le pilier du jour
(干支) croisé au pilier de naissance produit une relation — harmonie, choc, ou
neutre — et cette relation fournit une saillance 0-1 comparable aux autres
disciplines. Un jour dont l'animal « choque » ton animal de naissance parle
fort ; un jour en harmonie aussi ; un jour neutre se tait et laisse une autre
voix mener.

⚠️ 100 % calculable, 100 % déterministe. Le pilier du jour est une fonction du
calendrier ; le pilier de l'année, une fonction de l'année de naissance (à la
convention de nouvel an près). Aucun tirage. Comme partout : ici on CALCULE,
le texte vit dans le corpus.

⚠️ Deux choses restent à CONFIRMER sur une source (les ouvrages de Walters, via
l'Archiviste), marquées « À CONFIRMER » ci-dessous :
  1. l'ancre du cycle des jours (quelle date est un 甲子 / jiǎzǐ) ;
  2. la convention de début d'année (Nouvel An lunaire vs Li Chun 立春, ~4 fév).
Le reste (les tiges, les branches, les relations) est standard et vérifiable
par sa structure.
"""
import datetime as dt

# --- les dix tiges célestes (天干) : élément + polarité ---
TIGES = ["jiǎ", "yǐ", "bǐng", "dīng", "wù", "jǐ", "gēng", "xīn", "rén", "guǐ"]
ELEMENT_TIGE = ["bois", "bois", "feu", "feu", "terre",
                "terre", "métal", "métal", "eau", "eau"]
# tige d'index pair = yang, impair = yin
def _polarite(i_tige):
    return "yang" if i_tige % 2 == 0 else "yin"

# --- les douze branches terrestres (地支) : l'animal ---
BRANCHES = ["zǐ", "chǒu", "yín", "mǎo", "chén", "sì",
            "wǔ", "wèi", "shēn", "yǒu", "xū", "hài"]
ANIMAUX = ["rat", "buffle", "tigre", "lapin", "dragon", "serpent",
           "cheval", "chèvre", "singe", "coq", "chien", "cochon"]
# l'élément fixe porté par chaque branche (utile pour les cinq éléments)
ELEMENT_BRANCHE = ["eau", "terre", "bois", "bois", "terre", "feu",
                   "feu", "terre", "métal", "métal", "terre", "eau"]

# --- les relations entre branches (le cœur de la saillance) ---
# 六沖 — les six chocs : chaque branche s'oppose à celle 6 crans plus loin.
CHOCS = {(i, (i + 6) % 12) for i in range(12)}
CHOCS |= {(b, a) for a, b in CHOCS}

# 三合 — les triangles d'harmonie (trine), par élément produit.
TRINES = [(8, 0, 4), (11, 3, 7), (2, 6, 10), (5, 9, 1)]  # eau, bois, feu, métal
TRINE_PAIRES = set()
for tri in TRINES:
    for a in tri:
        for b in tri:
            if a != b:
                TRINE_PAIRES.add((a, b))

# 六合 — les six harmonies (paires unies).
HARMONIES = [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]
HARMONIE_PAIRES = {(a, b) for a, b in HARMONIES} | {(b, a) for a, b in HARMONIES}

# 六害 — les six « nuisances » (friction douce).
NUISANCES = [(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)]
NUISANCE_PAIRES = {(a, b) for a, b in NUISANCES} | {(b, a) for a, b in NUISANCES}

# Poids de saillance par relation. Le choc et l'harmonie parlent fort ; la
# nuisance, moins ; le neutre se tait. Valeurs ASSUMÉES, réglées à la validation.
POIDS_RELATION = {
    "choc": 0.90,          # 沖 — l'opposition, la friction franche, le mouvement
    "harmonie": 0.80,      # 六合 — l'union, l'appui
    "trine": 0.70,         # 三合 — l'affinité d'élément
    "nuisance": 0.55,      # 害 — l'accroc discret
    "identique": 0.60,     # même animal que ta naissance (ton année de retour)
    "neutre": 0.15,
}

# CONFIRMÉ contre le calendrier de Joey Yap (« The Ten Thousand Year
# Calendar ») : 5 dates vérifiées, dont le 17 juillet 2026 = 壬辰 (rénchén) et
# le Nouvel An 2026 (17 fév) = 壬戌. Le cycle des jours est ININTERROMPU depuis
# des millénaires : une seule ancre fiable cale tout. 2000-01-07 = 甲子 (jiǎzǐ).
ANCRE_JIAZI = dt.date(2000, 1, 7)

# CONVENTION D'ALIGN, appuyée sur Walters (« The Secrets of Chinese Astrology ») :
# l'année chinoise commence au Li Chun 立春 (« début du printemps », frontière
# SOLAIRE), et non au Nouvel An lunaire — c'est le choix de la majorité des
# astrologues (« most Chinese astrologers agree the data should be based on the
# vernal calendar, which begins with the Beginning of Spring in early February »).
# ⚠️ La date exacte DÉRIVE entre le 3 et le 5 février selon l'année (Walters :
# ~5 fév au début du XXe s., ~3 fév à la fin du XXIe). Align fixe le 4 février :
# approximation stable, qui ne peut décaler que les natifs à ±1 jour de la
# frontière. À publier dans /api/conventions, comme les règles numérologiques.
LICHUN_MOIS, LICHUN_JOUR = 2, 4


def pilier_du_jour(date):
    """Le pilier (tige+branche) du jour. Cycle ininterrompu de 60 jours."""
    i = (date - ANCRE_JIAZI).days % 60
    i_tige, i_branche = i % 10, i % 12
    return {
        "index": i,
        "tige": TIGES[i_tige], "element": ELEMENT_TIGE[i_tige],
        "polarite": _polarite(i_tige),
        "branche": BRANCHES[i_branche], "animal": ANIMAUX[i_branche],
        "i_branche": i_branche,
    }


def _annee_chinoise(date):
    """L'année chinoise d'une date, selon la frontière retenue (~Li Chun).

    Avant Li Chun, on est encore dans l'année précédente. C'est ce qui fait
    qu'un natif du 1er février « appartient » à l'animal de l'an d'avant.
    """
    frontiere = dt.date(date.year, LICHUN_MOIS, LICHUN_JOUR)
    return date.year if date >= frontiere else date.year - 1


def pilier_annee(annee_naissance, mois_naissance, jour_naissance):
    """Le pilier de l'année de naissance — animal + élément.

    Prend la date complète pour trancher les naissances de janvier/début février
    (avant le passage d'année chinoise).
    """
    a = _annee_chinoise(dt.date(annee_naissance, mois_naissance, jour_naissance))
    i_tige, i_branche = (a - 4) % 10, (a - 4) % 12
    return {
        "annee_chinoise": a,
        "tige": TIGES[i_tige], "element": ELEMENT_TIGE[i_tige],
        "polarite": _polarite(i_tige),
        "branche": BRANCHES[i_branche], "animal": ANIMAUX[i_branche],
        "i_branche": i_branche,
    }


def relation_branches(i_jour, i_natal):
    """La relation entre la branche du jour et la branche de naissance.

    Ordre de priorité quand plusieurs s'appliquent : le choc prime (le plus
    fort), puis l'harmonie, le trine, la nuisance, l'identité, le neutre. Cet
    ordre est un CHOIX stable — le déterminisme avant la nuance.
    """
    p = (i_jour, i_natal)
    if p in CHOCS:
        return "choc"
    if p in HARMONIE_PAIRES:
        return "harmonie"
    if p in TRINE_PAIRES:
        return "trine"
    if p in NUISANCE_PAIRES:
        return "nuisance"
    if i_jour == i_natal:
        return "identique"
    return "neutre"


def saillance_chinoise(annee_naiss, mois_naiss, jour_naiss, date):
    """La voix « chinois » pour le routeur : 0-1 + la relation du jour.

    Fondé sur la relation entre l'animal du JOUR et l'animal de NAISSANCE — le
    mécanisme le plus robuste et le plus calculable (l'animal de naissance ne
    demande que l'année, pas l'heure). Renvoie de quoi élire la voix ET nommer
    la clé de corpus (`relation_animalNatal`, ex. `choc_dragon`).
    """
    jour = pilier_du_jour(date)
    natal = pilier_annee(annee_naiss, mois_naiss, jour_naiss)
    rel = relation_branches(jour["i_branche"], natal["i_branche"])
    return {
        "score": POIDS_RELATION[rel],
        "relation": rel,
        "animal_du_jour": jour["animal"],
        "animal_natal": natal["animal"],
        "element_du_jour": jour["element"],
        "element_natal": natal["element"],
        "cle": f"{rel}_{natal['animal']}",
    }
