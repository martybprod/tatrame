"""Tests du moteur de composition — déterminisme, liaisons, motifs, clôture.

Les cartes de test sont des dicts au format de l'API (/api/tirage).
"""
import random
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import moteur as moteur_module
from moteur import TABLES, composer, carte_ressource, phrases_liaisons, type_liaison


def carte(id_, nom=None, type_="mineur", element=None, famille=None,
          degre=None, rang=None, question="Q ?", micro="G."):
    return {
        "id": id_, "nom": nom or id_, "type": type_,
        "famille": famille, "degre": degre, "rang": rang,
        "element": element or famille,
        "positions": {"jour": "j", "amene": "a", "se_joue": "s", "essayer": "e"},
        "questions": [question], "micro_geste": micro,
    }


def test_liaisons_elementaires():
    assert type_liaison("feu", "air") == "renforce"
    assert type_liaison("air", "feu") == "renforce"
    assert type_liaison("eau", "terre") == "renforce"
    assert type_liaison("feu", "eau") == "tension"
    assert type_liaison("air", "terre") == "tension"
    assert type_liaison("feu", "terre") == "neutralise"
    assert type_liaison("air", "eau") == "neutralise"
    assert type_liaison("feu", "feu") is None      # même élément = écho
    assert type_liaison("feu", None) is None       # carte sans élément


def test_liaisons_adjacentes_phrases():
    cartes = [
        carte("feu_08", famille="feu", degre=8),
        carte("eau_05", famille="eau", degre=5),
        carte("terre_04", famille="terre", degre=4),
    ]
    l = phrases_liaisons(cartes)
    assert len(l) == 2
    assert l[0]["type"] == "tension"        # feu × eau
    assert l[1]["type"] == "renforce"       # eau × terre
    assert all(p["phrase"] for p in l)


def test_echo_meme_famille():
    cartes = [carte("feu_02", famille="feu", degre=2),
              carte("feu_07", famille="feu", degre=7)]
    l = phrases_liaisons(cartes)
    assert l[0]["type"] == "echo"
    assert "feu" in l[0]["phrase"]


def test_composition_deterministe():
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("eau_05", famille="eau", degre=5),
              carte("air_02", famille="air", degre=2)]
    a = composer(cartes)
    b = composer(cartes)
    assert a == b


def test_composition_structure():
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("eau_05", famille="eau", degre=5),
              carte("air_02", famille="air", degre=2)]
    L = composer(cartes)
    assert L["seuil"]
    assert len(L["liaisons"]) == 2
    assert len(L["motifs"]) <= 3          # plafond motifs
    assert L["cloture"]["nom"]
    assert L["cloture"]["question"]
    assert L["cloture"]["micro_geste"]


def test_motif_famille_absente():
    # feu + air tirés, aucune terre → la première absente dans l'ordre
    # de la création (feu → eau → air → terre) est l'eau
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("air_02", famille="air", degre=2),
              carte("feu_03", famille="feu", degre=3)]
    L = composer(cartes)
    assert any("carte d'eau" in m for m in L["motifs"])


def test_motif_nombre_repete():
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("eau_05", famille="eau", degre=5),
              carte("air_08", famille="air", degre=8)]
    L = composer(cartes)
    # le degré 8 (mise en circulation, maîtrise) est le thème répété
    texte_8 = TABLES["degres"]["8"]["texte"]
    assert any(texte_8 in m for m in L["motifs"])


def test_aucun_espace_non_rempli_dans_la_lecture():
    """Les gabarits reformulés contiennent des espaces ({famille}, {glose},
    {texte}) : le moteur doit les remplir TOUS — jamais d'accolade servie."""
    cartes = [carte("eau_02", famille="eau", degre=5),
              carte("eau_05", famille="eau", degre=5),
              carte("major_13", nom="Transformation", type_="majeur", element="eau")]
    L = composer(cartes)
    phrases = [L["seuil"]] + [l["phrase"] for l in L["liaisons"]] + L["motifs"] \
        + [L["cloture"]["question"], L["cloture"]["micro_geste"]]
    for p in phrases:
        assert "{" not in p, p


def test_absence_et_liaison_sur_tirage_majeur_de_feu():
    """Le tirage reproché du 2026-11-11 : eau + eau + Changement (majeure de
    feu). L'absence de feu ne doit PAS sortir (la majeure porte l'élément),
    et la tension doit nommer la paire exacte, pas « l'une de ces deux »."""
    cartes = [carte("eau_04", famille="eau", degre=4),
              carte("eau_08", famille="eau", degre=8),
              carte("major_10", nom="Changement", type_="majeur", element="feu")]
    L = composer(cartes)
    assert not any("feu n'apparaît" in m for m in L["motifs"])
    tensions = [l["phrase"] for l in L["liaisons"] if l["type"] == "tension"]
    assert tensions
    assert "eau_08 (eau) et Changement (feu)" in tensions[0]


def test_chaine_de_liaisons_fusionnee():
    """Solitude (terre) → Jeu (feu) → Avarice (terre) : deux liaisons
    « neutralise » identiques → UNE phrase de chaîne, les trois cartes nommées,
    l'alternation dite. Jamais deux fois la même phrase."""
    cartes = [carte("major_09", nom="Solitude", type_="majeur", element="terre"),
              carte("feu_page", nom="Jeu", type_="figure", famille="feu", element="feu"),
              carte("terre_04", nom="Avarice", famille="terre", element="terre")]
    l = phrases_liaisons(cartes)
    assert len(l) == 1
    assert l[0]["chaine"] is True
    assert "Solitude" in l[0]["phrase"] and "Jeu" in l[0]["phrase"] \
        and "Avarice" in l[0]["phrase"]
    assert "alternance" in l[0]["phrase"] or "tour de rôle" in l[0]["phrase"]
    assert "d'air" not in l[0]["phrase"] and "d'eau" not in l[0]["phrase"]


def test_echo_et_dominante_ne_se_repettent_pas():
    """Le doublon signalé le 2026-11-12 : Lutte (air) + Renaissance (air) +
    Accomplissement (terre). L'écho et le motif de dominance disaient la même
    chose. Désormais : une seule famille expliquée une fois, la prudence
    « pas un verdict » rejointe à l'écho, aucun second paragraphe."""
    cartes = [carte("air_08", nom="Lutte", famille="air", degre=8),
              carte("air_03", nom="Renaissance", famille="air", degre=3),
              carte("major_21", nom="Accomplissement", type_="majeur", element="terre")]
    L = composer(cartes)
    echo = [l["phrase"] for l in L["liaisons"] if l["type"] == "echo"]
    assert len(echo) == 1
    assert "Deux cartes d'air (Lutte et Renaissance)" in echo[0]
    assert "ne constitue pas un verdict" in echo[0]
    # la glose n'apparaît qu'une fois dans toute la lecture
    assert "représente les idées" not in echo[0]
    phrases = [L["seuil"]] + [l["phrase"] for l in L["liaisons"]] + L["motifs"]
    assert sum(p.count("représente les idées") for p in phrases) == 1
    # aucun motif de dominance ne redit la même chose
    assert not any("apparaissent dans ce tirage" in m for m in L["motifs"])


def test_trois_cartes_meme_famille_une_seule_phrase():
    """Trois cartes d'air : un écho fusionné, « Trois cartes », « trois fois
    de suite » — jamais deux paragraphes qui redisent la même chose."""
    cartes = [carte("air_01", nom="Un", famille="air", degre=1),
              carte("air_02", nom="Deux", famille="air", degre=2),
              carte("air_03", nom="Trois", famille="air", degre=3)]
    L = composer(cartes)
    echos = [l["phrase"] for l in L["liaisons"] if l["type"] == "echo"]
    assert len(echos) == 1
    assert echos[0].startswith("Trois cartes d'air (Un, Deux et Trois)")
    assert "trois fois de suite" in echos[0]
    assert "Deux cartes" not in echos[0]


def test_dominante_sans_echo_garde_la_prudence():
    """Air, terre, air : pas d'écho, mais l'air domine. Le motif de dominance
    sort avec la prudence, sans répéter la glose déjà donnée par le seuil."""
    cartes = [carte("air_01", nom="Un", famille="air", degre=1),
              carte("terre_02", nom="Deux", famille="terre", degre=2),
              carte("air_03", nom="Trois", famille="air", degre=3)]
    L = composer(cartes)
    assert not [l for l in L["liaisons"] if l["type"] == "echo"]
    dominantes = [m for m in L["motifs"] if "apparaissent dans ce tirage" in m]
    assert len(dominantes) == 1
    assert "ne constitue pas un verdict" in dominantes[0]
    assert "représente les idées" not in dominantes[0]
    phrases = [L["seuil"]] + [l["phrase"] for l in L["liaisons"]] + L["motifs"]
    assert sum(p.count("représente les idées") for p in phrases) == 1


def test_percee_blocage_ressource_cle(client=None):
    """La percée : friction (feu × eau) → ressource (terre, la mieux
    soutenue) → carte clé (la troisième, qui fait le pont)."""
    cartes = [
        carte("feu_08", nom="Passage", famille="feu", degre=8),
        carte("eau_04", nom="Accueil", famille="eau", degre=4),
        carte("terre_07", nom="Patience", famille="terre", degre=7),
    ]
    for c in cartes:
        c["tension"] = {"pousse": "avancer", "retient": "attendre"}
    L = compose_avec_tension(cartes)
    P = L["percee"]
    assert P["blocage"]["nom"] == "Accueil"      # reçoit la tension
    assert P["ressource"]["nom"] == "Patience"   # reçoit le renforcement
    assert P["cle"]["nom"] == "Passage"          # la troisième carte
    assert "relie le blocage et la ressource" in P["cle"]["phrase"]
    assert P["geste"]["phrase"] == "G."  # le geste, sans formule d'introduction


def compose_avec_tension(cartes):
    """composer() sans le champ manquant : les cartes de test n'ont pas de
    micro-geste nommé — on leur en donne un."""
    for c in cartes:
        c.setdefault("micro_geste", "G.")
    return composer(cartes)


def test_percee_absente_sur_une_carte():
    L = composer([carte("feu_02", famille="feu", degre=2)])
    assert L["percee"] is None


def test_percee_sans_friction_nomme_le_point_fragile():
    """Trois cartes qui se renforcent : pas de friction, donc le point
    fragile est la carte la moins soutenue — et la phrase le dit."""
    cartes = [
        carte("feu_02", nom="A", famille="feu", degre=2),
        carte("air_02", nom="B", famille="air", degre=2),
        carte("feu_05", nom="C", famille="feu", degre=5),
    ]
    for c in cartes:
        c["tension"] = {"pousse": "aller", "retient": "rester"}
    L = composer(cartes)
    P = L["percee"]
    # sans ombre sur la fiche de test, le repli est la phrase de tension
    assert "blocage tient à cette carte" in P["blocage"]["phrase"]


def test_percee_deterministe():
    cartes = [carte("feu_08", nom="A", famille="feu", degre=8),
              carte("eau_04", nom="B", famille="eau", degre=4),
              carte("terre_07", nom="C", famille="terre", degre=7)]
    for c in cartes:
        c["tension"] = {"pousse": "x", "retient": "y"}
    assert composer(cartes)["percee"] == composer(cartes)["percee"]



def test_percee_blocage_reprend_la_premiere_phrase_de_l_ombre():
    """Le blocage se dit avec la voix de la carte : la première phrase de son
    ombre — jamais deux verbes nus (« elle pousse puiser »)."""
    cartes = [carte("terre_04", nom="Avarice", famille="terre", degre=4),
              carte("air_07", nom="Manipulation", famille="air", degre=7),
              carte("feu_04", nom="Participation", famille="feu", degre=4)]
    for c in cartes:
        c["tension"] = {"pousse": "adapter", "retient": "masquer"}
    # la carte qui reçoit la friction est Manipulation : c'est son ombre qui parle
    cartes[1]["ombre"] = {"texte": "Tu finis par présenter à chacun la version "
                                   "de toi qu'il semble attendre. La suite est ici."}
    P = composer(cartes)["percee"]
    assert P["blocage"]["nom"] == "Manipulation"
    assert P["blocage"]["phrase"] == ("Tu finis par présenter à chacun la version "
                                      "de toi qu'il semble attendre.")

def test_seuil_passage_avec_majeures():
    cartes = [carte("major_06", nom="Union", type_="majeur", element="air"),
              carte("major_13", nom="Transformation", type_="majeur", element="eau"),
              carte("feu_08", famille="feu", degre=8)]
    L = composer(cartes)
    assert "majeures" in L["seuil"].lower() or "passage" in L["seuil"].lower()


def test_cloture_ressource_par_force():
    # feu+air se renforce → la carte du milieu (vers) accumule la force
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("air_02", famille="air", degre=2),
              carte("eau_05", famille="eau", degre=5)]
    l = phrases_liaisons(cartes)
    ressource = carte_ressource(cartes, l)
    assert ressource["id"] == "air_02"


def test_cloture_pas_de_verdict_vide():
    cartes = [carte("feu_08", famille="feu", degre=8),
              carte("eau_05", famille="eau", degre=5),
              carte("air_02", famille="air", degre=2)]
    L = composer(cartes)
    c = L["cloture"]
    assert c["nom"] and c["question"] and c["micro_geste"]


def test_balayage_500_graines_jeu_complet():
    """Le mode 3 sur le jeu complet traverse toutes les combinaisons
    possibles du mélange — aucune ne doit planter (Éveil, majeures sans
    famille, cartes sans corpus, adjacences mixtes…)."""
    import app as app_module

    echecs = []
    for graine in range(500):
        ids_jeu = app_module.IDS
        rng = random.Random(graine)
        melange = ids_jeu[:]
        rng.shuffle(melange)
        choisies = []
        for id_carte in melange[:3]:
            carte = app_module.CARTES[id_carte]
            fiche = app_module.CORPUS.get(id_carte, {})
            choisies.append({
                "id": id_carte, "nom": carte["nom"], "type": carte["type"],
                "famille": carte.get("famille"), "degre": carte.get("degre"),
                "rang": carte.get("rang"),
                "element": carte.get("element") or carte.get("famille"),
                "positions": fiche.get("positions", {}),
                "questions": fiche.get("questions", []),
                "micro_geste": fiche.get("micro_geste", ""),
            })
        try:
            moteur_module.composer(choisies)
        except Exception as e:
            echecs.append((graine, [c["id"] for c in choisies], str(e)))
    assert not echecs, echecs[:5]
