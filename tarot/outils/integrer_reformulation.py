#!/usr/bin/env python3
"""Intègre les reformulations de Martin (markdown) dans les fiches JSON.

Lit un fichier de reformulation (format : sections ## par carte, sous-sections
### Lumière / Ombre / Issue / Questions / Leçon / L'image / Micro-geste /
Positions), fusionne dans les fiches JSON existantes de data/corpus/cartes/,
conservant id, nom, type, famille, degre, rang, element, registre, note_grille,
mots_cles, tension et ombre.mode de la fiche existante. Ajoute la note
`reprise` dans source_referentielle.

Usage : ./venv/bin/python outils/integrer_reformulation.py <fichier.md>
"""
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
CORPUS = RACINE / "data" / "corpus" / "cartes"

ORDRE_POS = ["amene", "se_joue", "essayer"]
TITRES_POS = {
    "Aujourd'hui": "jour",
    "Ce que j'amène": "amene",
    "Ce qui se joue": "se_joue",
    "Ce que je peux essayer": "essayer",
}


def nettoyer(t):
    return t.strip()


def parser(fichier):
    texte = fichier.read_text(encoding="utf-8")
    texte = texte.replace("\\_", "_")  # les ids échappés du markdown
    cartes = {}
    blocs = re.split(r"\n## ", texte)
    for bloc in blocs[1:]:
        lignes = bloc.split("\n")
        titre = lignes[0].strip()
        m_nom = re.search(r"\d+\.\s*(.+)", titre)
        nom = m_nom.group(1).strip() if m_nom else titre
        m_id = re.search(
            r"(major_[0-9]{2}|master|(feu|eau|air|terre)_(as|[0-9]{1,2}|page|chevalier|reine|roi))",
            bloc)
        if not m_id:
            continue
        id_carte = m_id.group(1)
        cartes[id_carte] = {"nom": nom, "bloc": bloc}
    return cartes


def champs_du_bloc(bloc):
    champs = {}
    mots_cles = None
    parties = re.split(r"\n### ", "\n" + bloc)
    # mots-clés : ligne « Symboles : a · b · c » ou ligne en *...* (ancien format)
    for ligne in bloc.split("\n"):
        ligne = ligne.strip()
        ms = re.match(r"^Symboles\s*:\s*(.+)$", ligne)
        if ms and " · " in ms.group(1):
            mots_cles = [x.strip() for x in ms.group(1).split(" · ")]
            break
        mm = re.match(r"^\*(.+)\*$", ligne)
        if mm and " · " in mm.group(1):
            mots_cles = [x.strip() for x in mm.group(1).split(" · ")]
            break
        # ligne pleine : au moins trois segments séparés par « · » (pas l'id, pas un titre)
        if (ligne.count(" · ") >= 2 and ":" not in ligne
                and not ligne.startswith(("#", "_")) and "degré" not in ligne
                and not re.match(r"^(feu|eau|air|terre|major)_", ligne)):
            mots_cles = [x.strip() for x in ligne.split(" · ")]
            break
    if mots_cles:
        champs["mots_cles"] = mots_cles
    # tension : Pousse / Retient, sur une ou deux lignes, majuscules ou minuscules
    pousse = re.search(r"[Pp]ousse\s*:\s*(.+?)(?:\s*[Rr]etient\b|$)", bloc, re.S)
    retient = re.search(r"[Rr]etient\s*:\s*(.+)", bloc)
    if pousse and retient:
        champs["tension"] = {"pousse": pousse.group(1).strip().strip("\\").strip("*").strip(),
                             "retient": retient.group(1).strip().strip("\\").strip("*").strip()}
    for partie in parties[1:]:
        titre, _, corps = partie.partition("\n")
        t = titre.strip().lower()
        corps = corps.strip()
        if t.startswith("lumière"):
            champs["lumiere"] = corps
        elif t.startswith("ombre"):
            champs["ombre_texte"] = corps
        elif t.startswith("issue"):
            champs["ombre_issue"] = corps
        elif t.startswith("le regard"):
            champs["le_regard"] = [
                l[2:].strip() for l in corps.split("\n")
                if l.strip().startswith("- ")
            ]
        elif t.startswith("questions"):
            champs["questions"] = [
                l[2:].strip() for l in corps.split("\n")
                if l.strip().startswith("- ")
            ]
        elif t.startswith("leçon"):
            champs["lecon"] = re.sub(r"^\*|\*$", "", corps)
        elif t.startswith("l'image"):
            # labels en gras (« **geste** — ») ou simples (« - Geste : »)
            geste = re.search(r"\*?\*?geste\*?\*?\s*[—:-]\s*(.+)", corps, re.I)
            seuil = re.search(r"\*?\*?seuil\*?\*?\s*[—:-]\s*(.+)", corps, re.I)
            detail = re.search(r"\*?\*?détail\*?\*?\s*[—:-]\s*(.+)", corps, re.I)
            champs["image"] = {
                "geste": geste.group(1).strip() if geste else "",
                "seuil": seuil.group(1).strip() if seuil else "",
                "detail": detail.group(1).strip() if detail else "",
            }
        elif t.startswith("micro-geste"):
            champs["micro_geste"] = re.sub(r"^\*|\*$", "", corps)
        elif t.startswith("positions"):
            titres = {
                "aujourd'hui — tirage du jour": "jour",
                "ce que j'amène": "amene",
                "ce qui se joue": "se_joue",
                "ce que je peux essayer": "essayer",
            }
            # repères = lignes qui SONT un titre (éventuellement préfixées #/*)
            repères = []
            lignes = corps.split("\n")
            offsets = []
            o = 0
            for l in lignes:
                offsets.append(o)
                o += len(l) + 1
            for i, l in enumerate(lignes):
                dépouillé = l.strip().lstrip("#").lstrip("*").strip()
                cle = titres.get(dépouillé.lower())
                if cle:
                    repères.append((offsets[i], cle, len(l)))
            repères.sort()
            positions = {}
            for i, (idx, cle, longueur) in enumerate(repères):
                début = idx + longueur
                fin = repères[i + 1][0] if i + 1 < len(repères) else len(corps)
                morceau = corps[début:fin].strip().lstrip("*").strip().rstrip("#").strip()
                positions[cle] = morceau
            champs["positions"] = positions
    return champs
    return champs


def main(fichier_reformulation, date):
    cartes = parser(pathlib.Path(fichier_reformulation))
    integrees, manquantes = [], []
    for id_carte, data in cartes.items():
        p = CORPUS / f"{id_carte}.json"
        if not p.exists():
            manquantes.append(id_carte)
            continue
        fiche = json.loads(p.read_text(encoding="utf-8"))
        c = champs_du_bloc(data["bloc"])
        if c.get("mots_cles"):
            fiche["mots_cles"] = c["mots_cles"]
        if c.get("tension"):
            fiche["tension"] = c["tension"]
        if c.get("le_regard"):
            fiche["le_regard"] = c["le_regard"]
        if "lumiere" in c:
            fiche["lumiere"] = c["lumiere"]
        if "ombre_texte" in c:
            fiche.setdefault("ombre", {})["texte"] = c["ombre_texte"]
        if "ombre_issue" in c:
            fiche.setdefault("ombre", {})["issue"] = c["ombre_issue"]
        if c.get("questions"):
            fiche["questions"] = c["questions"]
        if c.get("lecon"):
            fiche["lecon"] = c["lecon"]
        if c.get("image"):
            fiche["image"] = c["image"]
        if c.get("micro_geste"):
            fiche["micro_geste"] = c["micro_geste"]
        for cle, txt in c.get("positions", {}).items():
            fiche.setdefault("positions", {})[cle] = txt
        sr = fiche.setdefault("source_referentielle", {})
        sr["reprise"] = (f"textes reformulés par Martin le {date} (sa voix fait foi), "
                         "puis révisés contre la charte")
        p.write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")
        integrees.append(id_carte)
    print(f"intégrées : {len(integrees)} → {', '.join(integrees)}")
    if manquantes:
        print("SANS fiche JSON :", ", ".join(manquantes))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "2026-11-10")
