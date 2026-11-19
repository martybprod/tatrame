"""Tarot — squelette de l'app de tirage (port 5089).

Même philosophie qu'Align : 100 % déterministe à la lecture, zéro LLM et
zéro réseau au runtime. La variété vient du tirage (Fisher-Yates seedé,
graine conservée) — la lecture n'est qu'un lookup de corpus.

Cette version livre le squelette visuel (éventail, retournement) et l'API
de tirage honnête, sur le jeu complet des 79 cartes.

Contrat santé de l'écosystème : GET /health répond TOUJOURS 200 tant que
le process vit — jamais de 4xx/5xx pour « dégradé ».
"""
import json
import mimetypes
# Les images WebP partaient en `application/octet-stream` en production (le
# conteneur n'a pas de /etc/mime.types qui connaisse .webp) : Safari devait
# deviner le format. Déclaré ici, une fois pour toutes (2026-11-16).
mimetypes.add_type("image/webp", ".webp")
import os
import pathlib
import random
import time

# Deux modes : dans le paquet (monté sous /tarot dans Ta Trame) les modules sont
# relatifs ; en autonome (run.sh, pipeline local) ils sont frères. Le repli garde
# les deux possibles — c'est ce qui rend l'intégration réversible.
try:
    from . import moteur
    from . import album as ALBUM
except ImportError:  # exécution autonome
    import moteur
    import album as ALBUM
from flask import Flask, jsonify, make_response, redirect, render_template, \
    request, session, url_for

RACINE = pathlib.Path(__file__).parent
PORT = 5089
NOM = "Tarot"

# static_url_path="" : les fichiers statiques se servent à la racine
# (/css/app.css, /img/dos.png) — URLs courtes, pas de préfixe /static.
# TEMPLATES_AUTO_RELOAD : en développement, le template se relit à chaque
# requête — sinon une modification de index.html n'apparaît qu'au restart.
app = Flask(__name__, static_url_path="")
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Le nom de cookie de session doit être UNIQUE par app : sur 127.0.0.1, toutes
# les apps Flask au nom par défaut « session » s'écrasent mutuellement (le
# même cookie pour le même hôte). Même leçon que Ta Trame, même fix.
app.config["SESSION_COOKIE_NAME"] = "tarot_session"
# En ligne (PWA), le cookie d'album ne doit pas voyager en clair : TAROT_ENV=prod
# dans Coolify. En local, rien ne change.
if os.environ.get("TAROT_ENV", "dev").strip().lower() == "prod":
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.secret_key = os.environ.get("TAROT_SECRET", "tarot-secret-local")
# Le mot de passe d'édition de l'album : lu dans l'environnement (run.sh
# l'exporte depuis .env). Sans lui, l'album se consulte mais ne s'écrit pas.
MDP_ALBUM = os.environ.get("TAROT_ALBUM_MDP", "")

# ── Jeu + corpus (chargés au démarrage ; hot-reload par mtime en phase 2) ────
JEU = json.loads((RACINE / "data/grammaire/jeu.json").read_text(encoding="utf-8"))
CARTES = {c["id"]: c for c in JEU["cartes"]}
IDS = [c["id"] for c in JEU["cartes"]]  # 79 cartes, Éveil compris (hors cycle)
TIRAGES_BRUT = json.loads((RACINE / "data/grammaire/tirages.json").read_text(encoding="utf-8"))
TIRAGES = {k: v for k, v in TIRAGES_BRUT.items()
           if not k.startswith("_") and isinstance(v, dict) and v.get("id")}


def _grille_causale():
    """La grille d'origine, construite depuis `causale_3` (mêmes positions,
    mêmes textes) : elle lit les positions de la fiche, une par position."""
    bloc = TIRAGES.get("causale_3", {})
    return {
        "id": "causale_3",
        "nom": "Situation · nœud · levier",
        "sous_titre": "la lecture d'origine",
        "cloture": "micro_geste",
        "positions": [dict(p, champ="positions.%s" % p["id"])
                      for p in bloc.get("positions", [])],
        "pedagogie": bloc.get("pedagogie", {}),
    }


# Les grilles de relecture (Greer, les permutations) : la même donne, lue sous
# un autre cadre. Aucun texte nouveau par carte — chaque position déclare le
# champ de la fiche qu'elle lit.
GRILLES = {"causale_3": _grille_causale()}
GRILLES.update(TIRAGES_BRUT.get("grilles", {}))

# Les croix à dix cartes : même disposition (les colonnes viennent des données),
# mais chacune déclare ses positions, ses textes et sa pédagogie. La donne se
# relit donc avec l'une ou l'autre, sans retirer les cartes.
CROIX = {k: v for k, v in TIRAGES.items()
         if v.get("grammaire") == "croix" and v.get("nb_cartes") == 10}


def _valeur_champ(fiche, chemin):
    """La valeur d'un champ niché (« ombre.issue », « positions.amene »)."""
    noeud = fiche
    for partie in str(chemin).split("."):
        if isinstance(noeud, dict):
            noeud = noeud.get(partie)
        else:
            return None
    return noeud


def _mots_cles_visuels(fiche):
    """Les mots-clés d'image, quand la fiche n'a pas de description (famille
    eau) : on écarte les entrées techniques (id, registre, élément)."""
    interdits = {"interieur", "extérieur", "exterieur", "transpersonnel",
                 "seuil", "terre", "feu", "air", "eau"}
    mots = []
    for mot in fiche.get("mots_cles") or []:
        propre = mot.strip().strip("*").strip()
        if not propre or propre.lower() == str(fiche.get("id", "")).lower():
            continue
        if propre.lower() in interdits:
            continue
        mots.append(propre)
    return ", ".join(mots)


def _resoudre_position(fiche, position, graine):
    """Le texte d'une carte pour une position de grille, appoint compris.

    Déterministe : la question (position « questions ») est choisie par la
    graine. Éveil (hors cycle) n'a pas de positions : la phrase du regard
    tient la place, et l'appoint est passé.
    """
    texte = None
    champ = position.get("champ", "")
    if champ == "questions":
        questions = fiche.get("questions") or []
        if questions:
            texte = questions[graine % len(questions)]
    elif champ == "tension":
        # la tension est un couple (pousse / retient), pas une phrase : la
        # position qui la lit en texte principal la met en phrase ici.
        tension = fiche.get("tension") or {}
        if (isinstance(tension, dict) and tension.get("pousse")
                and tension.get("retient")):
            texte = (f"Elle te pousse à {tension['pousse']}, et elle te "
                     f"retient {moteur._de_verbe(tension['retient'])}.")
    else:
        texte = _valeur_champ(fiche, champ)

    regard = False
    if not texte and fiche.get("le_regard"):
        variantes = fiche["le_regard"]
        texte = variantes[graine % len(variantes)]
        regard = True

    appoint = None
    spec = position.get("appoint")
    if spec and not regard:
        valeur = None
        for chemin in spec.get("champs") or [spec.get("champ", "")]:
            if chemin == "mots_cles":
                valeur = _mots_cles_visuels(fiche)
            else:
                valeur = _valeur_champ(fiche, chemin)
            if isinstance(valeur, str) and valeur.strip():
                break
        genre = spec.get("genre", "ligne")
        if genre == "tension" and isinstance(valeur, dict):
            if valeur.get("pousse") and valeur.get("retient"):
                appoint = {"genre": "tension", "pousse": valeur["pousse"],
                           "retient": valeur["retient"]}
        elif isinstance(valeur, str) and valeur.strip():
            appoint = {"genre": genre, "texte": valeur.strip()}

    return {"texte": texte or "", "appoint": appoint, "regard": regard}


def _carte_de_tirage(id_carte, graine):
    """La carte telle que l'API la sert (fiche + visage + regard seedé)."""
    carte = CARTES[id_carte]
    fiche = CORPUS.get(id_carte, {})
    choisie = {
        "id": id_carte,
        "nom": carte["nom"],
        "type": carte["type"],
        "famille": carte.get("famille"),
        "degre": carte.get("degre"),
        "rang": carte.get("rang"),
        "element": carte.get("element") or carte.get("famille"),
        "image": visage(id_carte),
        "image_mini": vignette(id_carte),
        "image_moyenne": moyenne(id_carte),
        "corpus": bool(fiche),
        "mots_cles": fiche.get("mots_cles", []),
        "lumiere": fiche.get("lumiere"),
        "ombre": fiche.get("ombre"),
        "questions": fiche.get("questions", []),
        "lecon": fiche.get("lecon"),
        "micro_geste": fiche.get("micro_geste"),
        "positions": fiche.get("positions", {}),
        "tension": fiche.get("tension"),
    }
    # Éveil (hors cycle, forme propre « Le regard ») : la graine choisit la
    # variante de la phrase d'exception — documenté et reproductible.
    if carte.get("type") == "hors_cycle" and fiche.get("le_regard"):
        variantes = fiche["le_regard"]
        choisie["regard"] = variantes[graine % len(variantes)]
    return choisie


def _textes_des_grilles(choisies, graine):
    """Chaque grille lit des champs différents de la même fiche : la résolution
    se fait côté serveur (règles testables, UI simple)."""
    return {
        gid: {
            carte["id"]: {
                pos["id"]: _resoudre_position(
                    CORPUS.get(carte["id"], {}), pos, graine)
                for pos in grille["positions"]
            }
            for carte in choisies
        }
        for gid, grille in GRILLES.items()
    }


def charger_corpus():
    """Fiches écrites sous charte (data/corpus/cartes/), complétées par les
    deux moules d'exemple de la phase 0."""
    corpus = {}
    dossier = RACINE / "data/corpus/cartes"
    if dossier.is_dir():
        for f in sorted(dossier.glob("*.json")):
            fiche = json.loads(f.read_text(encoding="utf-8"))
            corpus[fiche["id"]] = fiche
    exemples = RACINE / "data/grammaire/exemples"
    if exemples.is_dir():
        for f in sorted(exemples.glob("*.json")):
            fiche = json.loads(f.read_text(encoding="utf-8"))
            corpus.setdefault(fiche["id"], fiche)
    return corpus


CORPUS = charger_corpus()


def visage(id_carte):
    """URL de la face d'app si elle existe, sinon None (le dos seul s'affiche).
    ?v=3 : les faces sont désormais les cartouches CLAIRS (médaillon + nom sur
    la carte) — le numéro force le navigateur à recharger les images en cache."""
    p = RACINE / "static" / "img" / "cartes" / f"{id_carte}.jpg"
    return f"img/cartes/{id_carte}.jpg?v=3" if p.exists() else None


# Vignettes (400 px, WebP — outils/generer_vignettes.py) : dans les cases du
# tirage, le mur du choix et les liens. La face entière reste pour le plein
# écran et le récit. Monter le numéro après avoir régénéré les vignettes.
VERSION_VIGNETTES = 6


def moyenne(id_carte):
    """La taille intermédiaire (800 px, WebP) : récit et plein écran sur
    téléphone. Repli : la face entière."""
    p = RACINE / "static" / "img" / "cartes" / "moyenne" / f"{id_carte}.webp"
    if p.exists():
        return f"img/cartes/moyenne/{id_carte}.webp?v={VERSION_VIGNETTES}"
    return visage(id_carte)


def vignette(id_carte):
    p = RACINE / "static" / "img" / "cartes" / "mini" / f"{id_carte}.webp"
    if p.exists():
        return f"img/cartes/mini/{id_carte}.webp?v={VERSION_VIGNETTES}"
    return visage(id_carte)


@app.after_request
def cache_des_fichiers_versionnes(reponse):
    """Les fichiers statiques appelés AVEC un numéro de version (?v=…) ne
    changent jamais sous cette adresse : le téléphone les garde un an sans
    redemander. Avant (2026-11-16) : `no-cache` + une signature qui changeait
    à chaque déploiement — chaque mise à jour faisait retélécharger toutes
    les cartes (340 Ko pièce). Sans ?v=, rien ne change (no-cache)."""
    if request.args.get("v") and request.path.rsplit(".", 1)[-1] in (
            "jpg", "png", "webp", "css", "js", "svg", "woff2"):
        reponse.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return reponse


@app.get("/health")
def health():
    return jsonify({
        "service": "tarot",
        "name": NOM,
        "status": "ok",
        "port": PORT,
        "detail": f"{len(CARTES)} cartes, {len(CORPUS)} fiches de corpus",
    })


@app.get("/")
def index():
    # le dos est versionné par sa date : un changement se voit au rechargement
    dos = RACINE / "static" / "img" / "dos.png"
    version_dos = int(dos.stat().st_mtime) if dos.exists() else 0
    # ?embed=1 : page nue pour l'intégration dans Ta Trame (sans en-tête ni pied)
    embed = request.args.get("embed") == "1"
    resp = make_response(render_template("index.html", version_dos=version_dos,
                                         embed=embed))
    # la page change à chaque phase : jamais de cache navigateur sur le HTML
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/api/tirage")
def tirage():
    """Tirage honnête : mélange Fisher-Yates seedé, graine renvoyée (et
    reproductible via ?graine= — c'est ce que lira le journal en phase 2).
    La position du clic dans la ligne est un geste ; la carte qui répond
    est celle que le mélange a placée — comme dans un vrai jeu.
    """
    mode = request.args.get("mode", "1")
    if mode not in ("1", "3", "5", "10", "11"):
        return jsonify({"erreur": "mode invalide (1, 3, 5, 10 ou 11)"}), 400
    nb = 10 if mode == "11" else int(mode)

    grille_id = request.args.get("grille", "causale_3")
    if grille_id not in GRILLES:
        return jsonify({"erreur": "grille inconnue"}), 400
    # la croix se choisit avant le tirage ; changer de croix ne change pas les
    # cartes, seulement la question posée à chaque position
    croix_id = request.args.get("croix", "croix_celtique")
    if croix_id not in CROIX:
        return jsonify({"erreur": "croix inconnue"}), 400

    ids_jeu = IDS

    graine = request.args.get("graine", type=int)
    if graine is None:
        # 52 bits : JavaScript lit les nombres JSON en flottants (précis
        # jusqu'à 2^53). Une graine de 64 bits revenait arrondie au navigateur,
        # et rejouer « la même donne » (reprise d'un tirage, tirage gardé,
        # ?graine=) donnait un AUTRE mélange. 4,5 × 10^15 mélanges possibles.
        graine = (int.from_bytes(os.urandom(8), "big")
                  ^ (time.time_ns() & 0xFFFFFFFF)) & ((1 << 52) - 1)
    rng = random.Random(graine)
    melange = ids_jeu[:]
    rng.shuffle(melange)

    choisies = [_carte_de_tirage(id_carte, graine) for id_carte in melange[:nb]]

    lecture = None
    textes_par_grille = {}
    etendu = None
    croix = None
    croix_textes = {}
    croix_choix = []
    questions_textes = {}
    if nb == 3:
        lecture = moteur.composer(choisies)
        textes_par_grille = _textes_des_grilles(choisies, graine)
    elif nb == 10 and mode != "11":
        bloc = TIRAGES["etendu_9_1"]
        niveaux = bloc["niveaux"]
        plans = bloc["plans"]
        neuf = choisies[:9]
        cle_carte = choisies[9]
        cellules = {}
        for i, carte in enumerate(neuf):
            niveau = niveaux[i // 3]
            plan = plans[i % 3]
            res = _resoudre_position(
                CORPUS.get(carte["id"], {}),
                {"champ": niveau["champ"], "appoint": niveau.get("appoint")}, graine)
            cellules[carte["id"]] = {
                "plan": plan["id"], "plan_libelle": plan["libelle"],
                "niveau": niveau["id"], "niveau_nom": niveau["nom"],
                "texte": res["texte"], "appoint": res["appoint"],
                "regard": res["regard"],
            }
        cle_res = _resoudre_position(
            CORPUS.get(cle_carte["id"], {}),
            {"champ": bloc["cle"]["champ"]}, graine)
        lecture = moteur.composer_etendu(neuf, cle_carte)
        etendu = {
            "plans": plans,
            "niveaux": [{k: n[k] for k in ("id", "nom", "temps", "invite")}
                        for n in niveaux],
            "cle": {"carte_id": cle_carte["id"], **bloc["cle"],
                    "texte": cle_res["texte"], "regard": cle_res["regard"]},
            "cellules": cellules,
            "rangees": lecture["rangees"],
        }
    elif mode in ("5", "11"):
        bloc = CROIX[croix_id] if mode == "11" else TIRAGES["diamant"]
        positions = bloc["positions"]
        croix = {
            "positions": [{k: pos[k] for k in ("id", "numero", "libelle",
                                               "question", "se_grade", "col", "row")}
                          for pos in positions],
            "cartes": {},
            "coeur": bloc.get("coeur", []),
            "ligne": bloc.get("ligne_de_probabilite", []),
        }
        for pos, carte in zip(positions, choisies):
            res = _resoudre_position(CORPUS.get(carte["id"], {}), pos, graine)
            croix["cartes"][carte["id"]] = {
                "position": pos["id"], "numero": pos["numero"],
                "texte": res["texte"], "appoint": res["appoint"],
                "regard": res["regard"],
            }
        lecture = moteur.composer(choisies)
        # les trois croix sont résolues d'avance : en changer relit la même
        # donne sans retirer les cartes (choix avant ou après le tirage).
        # Le diamant n'a qu'une forme : il porte sa propre définition.
        blocs = CROIX.items() if mode == "11" else [("diamant", TIRAGES["diamant"])]
        for cid, cbloc in blocs:
            croix_choix.append({
                "id": cid, "nom": cbloc["nom"],
                "sous_titre": cbloc.get("grammaire", ""),
                "positions": cbloc.get("positions", []),
                "pedagogie": cbloc.get("pedagogie", {}),
            })
            croix_textes[cid] = {
                carte["id"]: _resoudre_position(
                    CORPUS.get(carte["id"], {}), pos, graine)
                for pos, carte in zip(cbloc.get("positions", []), choisies)
            }

    if nb == 3:
        grille = GRILLES[grille_id]
    elif mode in ("5", "11"):
        bloc = CROIX[croix_id] if mode == "11" else TIRAGES["diamant"]
        grille = {
            "id": croix_id if mode == "11" else "diamant",
            "nom": bloc["nom"],
            "sous_titre": bloc.get("grammaire", ""),
            "cloture": "percee",
            "positions": bloc.get("positions", []),
            "pedagogie": bloc.get("pedagogie", {}),
        }
    elif nb == 10:
        bloc = TIRAGES["etendu_9_1"]
        grille = {
            "id": "etendu_9_1",
            "nom": bloc["nom"],
            "sous_titre": bloc.get("grammaire", ""),
            "cloture": "percee",
            "positions": [],
            "pedagogie": bloc.get("pedagogie", {}),
        }
    else:
        # Une carte = « Une question » (2026-11-16) : Ta Trame a déjà ses
        # cartes du jour. Chaque question est une position qui lit un champ de
        # la fiche ; les cinq réponses sont résolues d'avance, comme les
        # croix — changer de question relit la même carte.
        bloc = TIRAGES.get("question_1") or TIRAGES.get("jour", {})
        grille = {
            "id": "question_1" if "question_1" in TIRAGES else "jour",
            "nom": bloc.get("nom", "Une question"),
            "sous_titre": "",
            "cloture": "micro_geste",
            "positions": bloc.get("positions", []),
            "pedagogie": bloc.get("pedagogie", {}),
        }
        if choisies and "question_1" in TIRAGES:
            fiche = CORPUS.get(choisies[0]["id"], {})
            questions_textes = {
                pos["id"]: _resoudre_position(fiche, pos, graine)
                for pos in bloc.get("positions", [])}

    return jsonify({
        "mode": 11 if mode == "11" else nb,
        "graine": graine,
        "cartes": choisies,
        "total_jeu": len(ids_jeu),
        "lecture": lecture,
        "grille": grille["id"],
        "grilles": list(GRILLES.values()),
        "textes_par_grille": textes_par_grille,
        "etendu": etendu,
        "croix": croix,
        "croix_textes": croix_textes,
        "croix_choix": croix_choix,
        "questions_textes": questions_textes,
        "question_par_defaut": (TIRAGES.get("question_1") or {}).get("question_par_defaut"),
        "pedagogie": grille.get("pedagogie", {}),
        "cle_pedagogie": grille["id"],
        "positions_def": grille.get("positions", []),
    })


@app.get("/api/jeu")
def jeu_face_visible():
    """Les 79 cartes face visible — pour le tirage au choix (aucun hasard)."""
    return jsonify({
        "total": len(IDS),
        "cartes": [{"id": i, "nom": CARTES[i]["nom"], "type": CARTES[i]["type"],
                    "image": visage(i), "image_mini": vignette(i)} for i in IDS],
        "methode": TIRAGES.get("choix_3", {}).get("pedagogie", {}),
    })


@app.get("/api/lecture")
def lecture_choisie():
    """La lecture de trois cartes CHOISIES face visible (tirage au choix).

    Zéro hasard : les cartes viennent du choix, pas d'un mélange. La graine ne
    sert qu'aux choix internes (variante du regard, question de la grille) —
    par défaut 0, donc reproductible.
    """
    brut = request.args.get("cartes", "")
    ids = [x.strip() for x in brut.split(",") if x.strip()]
    if len(ids) != 3 or len(set(ids)) != 3:
        return jsonify({"erreur": "trois cartes distinctes attendues"}), 400
    inconnues = [i for i in ids if i not in CARTES]
    if inconnues:
        return jsonify({"erreur": "carte inconnue", "ids": inconnues}), 400

    grille_id = request.args.get("grille", "causale_3")
    if grille_id not in GRILLES:
        return jsonify({"erreur": "grille inconnue"}), 400
    graine = request.args.get("graine", type=int) or 0

    choisies = [_carte_de_tirage(i, graine) for i in ids]
    grille = GRILLES[grille_id]
    return jsonify({
        "mode": 3,
        "graine": graine,
        "cartes": choisies,
        "total_jeu": len(IDS),
        "lecture": moteur.composer(choisies),
        "grille": grille["id"],
        "grilles": list(GRILLES.values()),
        "textes_par_grille": _textes_des_grilles(choisies, graine),
        "etendu": None,
        "pedagogie": grille.get("pedagogie", {}),
        "cle_pedagogie": grille["id"],
        "positions_def": grille.get("positions", []),
        "choix": True,
    })


@app.get("/api/tirages")
def liste_tirages():
    """Les tirages disponibles et leur couche pédagogique — pour l'écran
    (les libellés des modes) et pour l'album (l'édition des textes)."""
    return jsonify({mode: {
        "id": v["id"], "nom": v["nom"], "nb_cartes": v["nb_cartes"],
        "pedagogie": v.get("pedagogie", {}),
    } for mode, v in TIRAGES.items()})


# ── L'album (portage exact de Ta Trame : lecture à la source, écriture
#    gardée par la session admin, sauvegarde horodatée, résolution complète
#    avant écriture) ────────────────────────────────────────────────────────

def _session_album_admin():
    return bool(MDP_ALBUM) and bool(session.get("album_admin_ok"))


@app.get("/album")
def album():
    """L'album visuel des 79 cartes, lu à la source à chaque visite.

    ``album_admin`` décide seulement si l'écran propose le mode édition ; la
    vraie garde est côté écriture (api_album_enregistrer), pas ici.
    """
    return render_template("album.html", album=ALBUM.construire_album(),
                           admin=_session_album_admin())


@app.get("/album/connexion")
def album_connexion_form():
    if _session_album_admin():
        return redirect("/album")
    return render_template("album_connexion.html", erreur=None)


@app.post("/album/connexion")
def album_connexion():
    mot_de_passe = request.form.get("mdp", "")
    if not MDP_ALBUM:
        return render_template("album_connexion.html", erreur=(
            "Édition désactivée : TAROT_ALBUM_MDP n'est pas défini dans "
            "l'environnement (voir .env et run.sh).")), 403
    if mot_de_passe != MDP_ALBUM:
        return render_template("album_connexion.html",
                               erreur="Mot de passe incorrect."), 401
    session["album_admin_ok"] = True
    return redirect("/album")


@app.post("/album/deconnexion")
def album_deconnexion():
    session.pop("album_admin_ok", None)
    return redirect("/album")


@app.post("/api/album/enregistrer")
def api_album_enregistrer():
    """Écrit dans le corpus les textes modifiés depuis l'album.

    C'est la SEULE route de l'app qui modifie le corpus — tout le reste lit.
    Trois garde-fous, dans cet ordre :
      1. session album (l'album se consulte, mais ne s'écrit pas) ;
      2. ``album.appliquer`` résout TOUTES les cibles avant d'écrire : une clé
         inconnue arrête le lot entier (jamais de demi-écriture) ;
      3. sauvegarde horodatée de chaque fichier touché, avant écriture.
    Ensuite le corpus est RELU : le tirage parle des nouveaux textes dès le
    prochain appel, sans redémarrer.
    """
    if not _session_album_admin():
        return jsonify({"erreur": "non-admin"}), 403
    body = request.get_json(silent=True) or {}
    modifications = body.get("modifications")
    if not isinstance(modifications, list) or not modifications:
        return jsonify({"erreur": "aucune modification reçue"}), 400
    try:
        rapport = ALBUM.appliquer(modifications)
    except ValueError as e:
        return jsonify({"erreur": str(e)}), 400
    except (OSError, json.JSONDecodeError) as e:
        return jsonify({"erreur": "écriture impossible : %s" % e}), 500

    # Le corpus global est relu (même contrat que Ta Trame : pas de redémarrage).
    global CORPUS
    CORPUS = charger_corpus()
    return jsonify({"ok": True, "rapport": rapport})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
