/* Tarot — le tirage. Vanilla, sans dépendance, sans réseau.
   L'API pré-mélange le jeu (seed honnête conservée) ; le geste du clic
   choisit LÀ où l'utilisateur touche le jeu, la carte répondue est celle
   que le mélange a placée — comme quand on effleure une vraie tirette.
   Présentation : les cartes dépliées sur une ligne droite ; révélation
   en deux temps (vignette → plein écran) ; en tirage à trois, pose face
   cachée puis révélation une par une, avec le texte de position de chaque
   carte (table A du corpus). */

(() => {
  "use strict";

  // le dos porte la date du fichier : jamais de vieux dos servi par le cache
  const DOS_DEFAUT = window.DOS_URL || "img/dos.png";

  const eventail = document.getElementById("eventail");
  const slotsBox = document.getElementById("slots");
  const lecture = document.getElementById("lecture");
  const replierBtn = document.getElementById("replier");
  const boutonsMode = Array.from(document.querySelectorAll(".mode"));
  const plein = document.getElementById("plein");
  const pleinCorps = plein.querySelector(".plein-corps");
  const pleinImg = plein.querySelector(".plein-img");
  const pleinTexte = plein.querySelector(".plein-texte");
  const surtitre = document.getElementById("surtitre-jeu");
  const piedTexte = document.getElementById("pied-texte");

  // ── Grilles de relecture ────────────────────────────────────────────
  // La même donne se relit sous plusieurs cadres (Greer, les permutations) :
  // les cartes ne changent pas, seule change la question posée à la position.
  let grilleActive = "causale_3";
  let ordreRevelation = [];   // [{carte, i}] dans l'ordre choisi par celui qui tire
  let rangeesAnnoncees = new Set();  // mode 10 : les trois temps déjà lus

  function grilleCourante() {
    if (!tirage) return null;
    if (tirage.mode === 1) {
      return { id: "jour", nom: "La carte du jour", cloture: "micro_geste",
               positions: tirage.positions_def || [],
               pedagogie: tirage.pedagogie || {} };
    }
    if (tirage.mode === 10) {
      return { id: "etendu_9_1", nom: "Neuf + une", cloture: "percee",
               positions: [],
               pedagogie: tirage.pedagogie || {} };
    }
    if (tirage.mode === 11) {
      return { id: "croix_celtique", nom: "La croix celtique", cloture: "percee",
               positions: [],
               pedagogie: tirage.pedagogie || {} };
    }
    return (tirage.grilles || []).find(g => g.id === grilleActive) || null;
  }

  function positionsActives() {
    const g = grilleCourante();
    return (g && g.positions) || [];
  }

  let mode = 1;
  let dernierTotal = 79;      // nombre de cartes en jeu (défaut : jeu complet)
  let tirage = null;          // {graine, cartes:[…]}
  let choisies = [];          // cartes déjà retournées
  let carteEnPlace = false;   // une carte est en cours d'animation
  let carteRevelation = false;// un retournement de révélation en cours
  let cartesRevelees = 0;     // compteur des révélations (mode 3)

  // ── Ligne de cartes ─────────────────────────────────────────────────

  function carteLargeur() {
    const l = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--carte-l"));
    return Number.isFinite(l) ? l : 92;
  }

  function construireEventail(nbCartes) {
    eventail.innerHTML = "";
    eventail.classList.remove("estompe");
    eventail.scrollLeft = 0;
    const n = nbCartes || dernierTotal;
    const w = eventail.clientWidth - 4; // padding interne
    const l = carteLargeur();
    // tout le jeu tient dans la largeur, sans défilement : sur téléphone le
    // pas tombe à ~3 px (un ruban de tranches) ; la loupe rend le geste précis
    const pas = n > 1 ? (w - l) / (n - 1) : 0;
    pasLigne = pas;
    const total = Math.ceil(l + pas * (n - 1));

    const ligne = document.createElement("div");
    ligne.className = "ligne";
    ligne.style.width = total + "px";
    const frag = document.createDocumentFragment();

    for (let i = 0; i < n; i++) {
      const el = document.createElement("button");
      el.className = "carte";
      el.type = "button";
      el.setAttribute("aria-label", "Carte " + (i + 1) + " sur " + n);
      el.style.left = Math.round(i * pas) + "px";
      el.innerHTML =
        '<span class="interieur">' +
        '<span class="dos"><img src="' + DOS_DEFAUT + '" alt="" draggable="false"></span>' +
        '<span class="face"><span class="sans-visage">✦</span></span>' +
        "</span>";
      // le doigt (ou la souris) passe par la loupe : on pige au relâchement.
      // Le clic ne sert qu'au clavier (detail === 0 : Entrée / Espace).
      // Une fois posée dans sa case, la carte reprend le clic normal
      // (révéler, puis plein écran).
      el.addEventListener("click", (e) => {
        // le clic qui suit le relâchement du geste de pige ne compte pas
        if (el._pigeeA && Date.now() - el._pigeeA < 500) return;
        if (e.detail === 0 || el.classList.contains("choisie")) choisir(el);
      });
      frag.appendChild(el);
    }
    ligne.appendChild(frag);
    eventail.appendChild(ligne);

    // entrée en scène, en cascade — setTimeout, pas rAF : rAF est bridé
    // dans un onglet d'arrière-plan et l'entrée n'arriverait jamais
    const cartes = Array.from(ligne.children);
    setTimeout(() => {
      cartes.forEach((c, i) => {
        setTimeout(() => c.classList.add("visible"), Math.min(i * 6, 420));
      });
    }, 60);
  }

  // ── La loupe : la carte sous le doigt se soulève, ses voisines un peu ──

  let pasLigne = 0;
  let loupeIndex = -1;

  function cartesLibres() {
    const ligne = eventail.querySelector(".ligne");
    return ligne ? Array.from(ligne.children) : [];
  }

  function indexSous(x) {
    const cartes = cartesLibres();
    if (!cartes.length) return -1;
    const ligne = eventail.querySelector(".ligne").getBoundingClientRect();
    // les cartes déjà pigées ont quitté la ligne : on cherche la plus proche
    // par sa position réelle, pas par son rang
    const cible = x - ligne.left - carteLargeur() / 2;
    let meilleur = 0, ecart = Infinity;
    cartes.forEach((c, j) => {
      const d = Math.abs(parseFloat(c.style.left) - cible);
      if (d < ecart) { ecart = d; meilleur = j; }
    });
    return meilleur;
  }

  function poserLoupe(i) {
    loupeIndex = i;
    const pas = Math.max(pasLigne, 1);
    // rayon : environ une demi-largeur de carte de chaque côté
    const rayon = Math.max(2, Math.round(carteLargeur() / pas / 2));
    const cartes = cartesLibres();
    const x0 = i >= 0 && cartes[i] ? parseFloat(cartes[i].style.left) : 0;
    cartes.forEach((c, j) => {
      const d = i < 0 ? Infinity : Math.round(Math.abs(parseFloat(c.style.left) - x0) / pas);
      const lev = d === 0 ? 26 : d <= rayon ? 14 * (1 - d / (rayon + 1)) : 0;
      c.style.setProperty("--lev", lev.toFixed(1) + "px");
      c.classList.toggle("sous-loupe", d === 0);
    });
  }

  function loupeActive() {
    return tirage && !carteEnPlace && choisies.length < tirage.cartes.length &&
      !eventail.classList.contains("estompe");
  }

  eventail.addEventListener("pointerdown", (e) => {
    if (!loupeActive()) return;
    if (e.pointerType !== "mouse") eventail.setPointerCapture(e.pointerId);
    poserLoupe(indexSous(e.clientX));
  });
  eventail.addEventListener("pointermove", (e) => {
    if (!loupeActive()) return;
    if (e.pointerType === "mouse" || e.buttons) poserLoupe(indexSous(e.clientX));
  });
  eventail.addEventListener("pointerup", (e) => {
    if (!loupeActive() || loupeIndex < 0) return;
    const el = cartesLibres()[indexSous(e.clientX)];
    poserLoupe(-1);
    if (el) choisir(el);
  });
  eventail.addEventListener("pointerleave", (e) => {
    if (e.pointerType === "mouse") poserLoupe(-1);
  });
  eventail.addEventListener("pointercancel", () => poserLoupe(-1));

  // ── Compteur du tirage : où en est-on, quelle position vient ────────

  function libellePosition(n) {
    if (!tirage) return "";
    if (mode === 10) {
      const E = tirage.etendu || {};
      if (n >= 9) return (E.cle && E.cle.libelle) || "la clé d'intégration";
      const niv = (E.niveaux || [])[Math.floor(n / 3)] || {};
      const plan = (E.plans || [])[n % 3] || {};
      return [niv.temps, plan.libelle].filter(Boolean).join(" · ");
    }
    if (mode === 11) {
      const p = ((tirage.croix || {}).positions || []).find((x) => x.numero === n + 1);
      return p ? `${p.numero}. ${p.libelle}` : "";
    }
    const pos = positionsActives()[n];
    return (pos && pos.libelle) || "";
  }

  function majCompteur() {
    const c = document.getElementById("compteur-tirage");
    if (!c || !tirage) return;
    const total = tirage.cartes.length;
    const n = choisies.length;
    slotsBox.querySelectorAll(".cadre.suivante").forEach((x) => x.classList.remove("suivante"));
    if (!document.body.classList.contains("en-tirage") || n >= total) {
      c.classList.add("invisibles");
      return;
    }
    const cadre = slotsBox.querySelector(`.cadre[data-i="${n}"]`);
    if (cadre) cadre.classList.add("suivante");
    const lib = libellePosition(n);
    c.innerHTML = `<span class="ct-nb">${n} / ${total}</span>` +
      (lib ? `<span class="ct-pos">${lib}</span>` : "") +
      `<span class="ct-geste">Glisse sur le paquet · lâche pour piger</span>`;
    c.classList.remove("invisibles");
  }

  // ── Emplacements au-dessus de la ligne ──────────────────────────────

  function construireSlots() {
    slotsBox.innerHTML = "";
    slotsBox.classList.remove("invisibles", "cachee");
    // pendant le tirage à plusieurs cartes : le plan en miniature, pour voir
    // d'un coup toutes les cases et tout le paquet
    document.body.classList.toggle("en-tirage", mode === 3 || mode === 10 || mode === 11);
    document.body.classList.remove("a-commence");
    reinitialiserVues();
    slotsBox.classList.toggle("etendu", mode === 10);
    // le nombre de colonnes de la grille : les cartes occupent la largeur
    // disponible au lieu d'une largeur fixe (--n est lu par le CSS)
    slotsBox.style.setProperty("--n", mode === 1 ? 1 : mode === 10 ? 3 : mode);
    // mode 1 : pas d'emplacement vide avant le choix — il apparaît rempli
    slotsBox.classList.toggle("sans-vide", mode === 1);

    slotsBox.classList.toggle("croix", mode === 11);
    if (mode === 11) {
      const C = (tirage && tirage.croix) || {};
      (C.positions || []).forEach((pos) => {
        const s = document.createElement("div");
        s.className = "slot slot-croix";
        s.style.gridColumn = String(pos.col);
        s.style.gridRow = String(pos.row);
        s.innerHTML = `<div class="cadre" data-i="${pos.numero - 1}"></div>`;
        slotsBox.appendChild(s);
      });
      return;
    }

    if (mode === 10) {
      const E = (tirage && tirage.etendu) || {};
      const plans = E.plans || [];
      const niveaux = E.niveaux || [];

      const entete = document.createElement("div");
      entete.className = "etendu-entete";
      entete.innerHTML = plans.map(p =>
        `<div class="etendu-plan">${p.libelle}</div>`).join("");
      slotsBox.appendChild(entete);

      let index = 0;
      niveaux.forEach((n) => {
        const bande = document.createElement("div");
        bande.className = "etendu-bande";
        bande.innerHTML = `<span>${n.temps}</span><em>${n.invite}</em>`;
        slotsBox.appendChild(bande);
        for (let i = 0; i < 3; i++) {
          const s = document.createElement("div");
          s.className = "slot slot-etendu";
          s.innerHTML = `<div class="cadre" data-i="${index++}"></div>`;
          slotsBox.appendChild(s);
        }
      });

      const bandeCle = document.createElement("div");
      bandeCle.className = "etendu-bande bande-cle";
      bandeCle.innerHTML =
        `<span>${(E.cle && E.cle.libelle) || "la clé d'intégration"}</span>` +
        `<em>${(E.cle && E.cle.se_grade) || ""}</em>`;
      slotsBox.appendChild(bandeCle);
      const slotCle = document.createElement("div");
      slotCle.className = "slot slot-cle";
      slotCle.innerHTML = `<div class="cadre" data-i="${index}"></div>`;
      slotsBox.appendChild(slotCle);
      return;
    }

    const positions = positionsActives();
    const n = mode;
    for (let i = 0; i < n; i++) {
      const s = document.createElement("div");
      s.className = "slot" + (mode === 1 ? " slot-une" : "");
      const pos = positions[i];
      const lib = mode === 3 && pos
        ? `<div class="nom-slot"></div><div class="libelle clic-position" data-pos="${pos.id}" role="button" tabindex="0" title="Ce que signifie cette position">${pos.libelle}</div>`
        : "";
      s.innerHTML = `<div class="cadre" data-i="${i}"></div>${lib}`;
      slotsBox.appendChild(s);
    }
  }

  // ── Tirage ──────────────────────────────────────────────────────────

  async function demanderTirage() {
    // ?graine=N dans l'URL : reproduire exactement une lecture (les mêmes
    // cartes et la même variante du regard). Sans paramètre : tirage libre.
    const graineUrl = new URLSearchParams(location.search).get("graine");
    const suffixe = graineUrl ? `&graine=${encodeURIComponent(graineUrl)}` : "";
    const r = await fetch(`api/tirage?mode=${mode}${suffixe}`);
    if (!r.ok) throw new Error("tirage refusé");
    tirage = await r.json();
    dernierTotal = tirage.total_jeu;
    choisies = [];
    ordreRevelation = [];
    grilleActive = tirage.grille || "causale_3";
    afficherPedagogie();
    construireSlots();
    majCompteur();
    return tirage;
  }

  async function charger() {
    try {
      const t = await demanderTirage();
      construireEventail(t.total_jeu);
      synchroniserEntete(t.total_jeu);
    } catch (e) {
      construireEventail(79);
    }
  }

  function synchroniserEntete(total) {
    surtitre.textContent = "Le jeu des " + total;
    piedTexte.textContent = total + " cartes · mélange honnête, graine conservée · aucune prédiction";
  }

  async function choisir(el) {
    // vignette déjà révélée → plein écran
    if (el.classList.contains("retournee")) {
      ouvrirPlein(el._carte);
      return;
    }
    // carte posée face cachée (mode 3) → révélation une par une
    if (el.classList.contains("posee")) {
      reveler(el);
      return;
    }
    if (!tirage || carteEnPlace || choisies.length >= tirage.cartes.length) return;
    carteEnPlace = true;

    if (!choisies.length) replierBtn.classList.remove("invisible");
    document.body.classList.add("a-commence");

    const carte = tirage.cartes[choisies.length];
    choisies.push(carte);
    slotsBox.classList.remove("sans-vide");

    if (carte.image) {
      el.querySelector(".face").innerHTML =
        `<img src="${carte.image}" alt="${carte.nom}" draggable="false">`;
    }

    // 1 · la carte quitte la ligne et rejoint son emplacement
    const cadre = slotsBox.querySelector(`.cadre[data-i="${choisies.length - 1}"]`);
    const slot = cadre.closest(".slot");
    slot.classList.add("remplie");
    el.classList.add("choisie");
    cadre.appendChild(el);
    el._carte = carte;
    el._pigeeA = Date.now();
    el._regard = carte.type === "hors_cycle" ? (carte.regard || "") : "";
    el.style.cssText = "";
    el.style.position = "absolute";
    el.style.inset = "0";
    el.style.width = "100%";
    el.style.height = "100%";
    el.style.opacity = "1";

    if (mode === 3 || mode === 10 || mode === 11) {
      // 2a · posée FACE CACHÉE — la révélation se fera clic par clic
      el.classList.add("posee");
      el.title = "Révéler la carte";
      carteEnPlace = false;
      majCompteur();
      if (choisies.length === tirage.cartes.length) {
        // tout est posé : le plan miniature grandit, place à la révélation
        document.body.classList.remove("en-tirage");
        majCompteur();
        eventail.classList.add("estompe");
        montrerAttente();
        construireGrilles();
      }
    } else {
      // 2b · tirage à une carte : retournement immédiat + lecture
      el.style.transform = "scale(0.92)";
      el.title = "Afficher en plein écran";
      requestAnimationFrame(() => { el.style.transform = "scale(1)"; });
      setTimeout(() => el.classList.add("retournee"), 380);
      setTimeout(() => {
        carteEnPlace = false;
        montrerLectureJour(carte);
      }, 1150);
    }
  }

  // la révélation une par une — l'ordre appartient à celui qui tire
  function reveler(el) {
    if (carteRevelation) return;
    carteRevelation = true;
    el.classList.remove("posee");
    el.classList.add("retournee");
    el.title = "Afficher en plein écran";
    const nomSlot = el.closest(".slot").querySelector(".nom-slot");
    const i = Number(el.closest(".cadre").dataset.i);
    const pos = positionsActives()[i];
    ordreRevelation.push({ carte: el._carte, i: i });
    setTimeout(() => {
      if (nomSlot) nomSlot.textContent = el._carte.nom;
      const libelleSlot = el.closest(".slot").querySelector(".libelle");
      if (libelleSlot && el._carte.type === "hors_cycle") {
        libelleSlot.textContent = "le regard";
        libelleSlot.dataset.hors = "1";
      }
      ajouterBlocLecture(el._carte, pos);
      verifierRangee(i);
      carteRevelation = false;
      cartesRevelees++;
      if (cartesRevelees === tirage.cartes.length) {
        montrerCloture();
        montrerVues();
      }
    }, 700);
  }

  function pedagogiePanel(P, positions) {
    if (!P || !P.pourquoi) return "";
    // les textes peuvent porter du markdown léger : **gras**, paragraphes \n\n
    const md = (t) => t
      .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
      .split(/\n\n/).map(x => `<p>${x.replace(/\n/g, "<br>")}</p>`).join("");
    const vocab = (P.vocabulaire || []).map(v =>
      `<div class="ped-vocab"><b>${v.titre}</b>${md(v.texte)}</div>`).join("");
    let bloc = "";
    if (P.positions_expliquees) {
      const items = (positions || []).map(pos => {
        const texte = P.positions_expliquees[pos.id] || "";
        return texte ? `<div class="ped-pos"><b>${pos.libelle}</b>${md(texte)}</div>` : "";
      }).join("");
      bloc = items ? `<h4>Chaque position, ce qu'elle demande</h4>${items}` : "";
    }
    const corps = `
        <h4>Pourquoi ce tirage</h4><p>${md(P.pourquoi)}</p>
        <h4>Le sens général du tirage</h4>${md(P.le_tirage || "")}
        ${bloc}
        <h4>Comment lire</h4>${md(P.comment_lire || "")}
        <h4>Après la lecture</h4>${md(P.apres || "")}
        <h4>Le vocabulaire du jeu</h4>${vocab}`;
    // deux paliers : le résumé d'abord, la méthode complète en tiroir
    if (!P.resume) return `<div class="pedagogie">${corps}</div>`;
    return `
      <div class="pedagogie">
        <div class="ped-resume">${md(P.resume)}</div>
        <details class="ped-complet">
          <summary>La méthode complète</summary>
          ${corps}
        </details>
      </div>`;
  }

  function afficherPedagogie() {
    const boite = document.getElementById("ped-contenu");
    if (!boite) return;
    const g = grilleCourante();
    boite.innerHTML = g ? pedagogiePanel(g.pedagogie, g.positions) : "";
    // les quatre façons de lire trois cartes se choisissent ici aussi :
    // un seul état (grilleActive) partagé avec le sélecteur sous les cartes
    const grilles = (tirage && tirage.mode === 3) ? (tirage.grilles || []) : [];
    if (grilles.length > 1) {
      const barre = document.createElement("div");
      barre.className = "ped-grilles";
      barre.setAttribute("role", "tablist");
      barre.setAttribute("aria-label", "Façon de lire trois cartes");
      grilles.forEach((gr) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "grille-bouton" + (gr.id === grilleActive ? " actif" : "");
        b.setAttribute("role", "tab");
        b.setAttribute("aria-selected", String(gr.id === grilleActive));
        b.textContent = gr.nom;
        b.addEventListener("click", () => changerGrille(gr.id));
        barre.appendChild(b);
      });
      boite.prepend(barre);
    }
  }

  // ── Le détail d'une position : un clic sur son libellé l'ouvre ──────
  let dpDernierFocus = null;

  function detailPosition(labelEl) {
    const posId = labelEl.dataset.pos;
    const hors = labelEl.dataset.hors === "1";
    const slot = labelEl.closest(".slot");
    const carteEl = slot && slot.querySelector(".cadre > .choisie");
    const grille = grilleCourante() || {};
    const def = (grille.positions || []).find(p => p.id === posId) || {};
    const expl = ((grille.pedagogie || {}).positions_expliquees || {})[posId] || "";
    const titre = document.getElementById("dp-titre");
    const corps = document.getElementById("dp-corps");
    if (hors) {
      titre.textContent = "Le regard";
      const regard = carteEl && carteEl._regard
        ? carteEl._regard
        : "Éveil, la 79ᵉ carte du jeu, est venue regarder.";
      corps.innerHTML =
        `<p class="dp-regard">${regard}</p>` +
        `<p class="dp-note">Éveil est la 79ᵉ carte du jeu, hors cycle. ` +
        `Elle ne répond pas à la question de la position : elle la regarde.</p>`;
    } else {
      titre.textContent = labelEl.textContent;
      corps.innerHTML =
        (def.question ? `<p class="dp-bloc"><b>La question posée</b>${def.question}</p>` : "") +
        (def.se_grade ? `<p class="dp-bloc"><b>Ce que la position garde</b>${def.se_grade}</p>` : "") +
        (expl ? `<p class="dp-bloc"><b>Comment la lire</b>${expl}</p>` : "");
    }
    dpDernierFocus = labelEl;
    document.getElementById("detail-position").hidden = false;
    const fermer = document.getElementById("fermer-position");
    if (fermer) fermer.focus({ preventScroll: true });
  }

  function montrerAttente() {
    const seuil = tirage.lecture ? tirage.lecture.seuil : "";
    const invite = mode === 11
      ? "Les dix cartes sont posées, face cachée. Révèle-les dans l'ordre de la croix, puis le bâton."
      : mode === 10
      ? "Les dix cartes sont posées, face cachée. Révèle-les rangée par rangée : le visible, le latent, la résolution — puis la clé."
      : "Les trois cartes sont posées, face cachée. Touche-les une à une pour les révéler.";
    lecture.innerHTML =
      (seuil ? `<p class="seuil-ligne">${seuil}</p>` : "") +
      `<p class="attente">${invite}</p>`;
    lecture.classList.remove("invisibles");
    requestAnimationFrame(() => lecture.classList.add("visible"));
  }

  const MODES_OMBRE = {
    retourne: "retournée", differe: "différée", amoindri: "amoindrie", subi: "subie",
  };

  function appointHTML(appoint) {
    if (!appoint) return "";
    if (appoint.genre === "tension") {
      return `<p class="bloc-appoint appoint-tension"><span>Elle pousse</span> ${appoint.pousse} <span>· elle retient</span> ${appoint.retient}</p>`;
    }
    if (appoint.genre === "tag") {
      return `<p class="bloc-appoint"><span class="ombre-mode">ombre ${MODES_OMBRE[appoint.texte] || appoint.texte}</span></p>`;
    }
    if (appoint.genre === "geste") {
      return `<p class="bloc-appoint"><span>Le geste</span> ${appoint.texte}</p>`;
    }
    return `<p class="bloc-appoint appoint-detail">${appoint.texte}</p>`;
  }

  function ajouterBlocLecture(carte, pos) {
    const d = donneesBloc(carte, pos);
    if (!d) return;
    const bloc = document.createElement("div");
    bloc.className = "bloc-lecture";
    bloc.innerHTML =
      `<p class="bloc-nom">${carte.nom} <span>— ${d.libelle}</span></p>` +
      `<p class="bloc-texte">${d.texte}</p>` +
      appointHTML(d.appoint);
    lecture.appendChild(bloc);
    requestAnimationFrame(() => bloc.classList.add("visible"));
  }

  // le texte d'une carte à sa position, selon le mode et la grille active
  function donneesBloc(carte, pos) {
    let r = {};
    let libelle = (pos && pos.libelle) || "";
    if (mode === 11) {
      const C = tirage.croix || {};
      const cell = ((C.cartes || {})[carte.id]) || {};
      const def = (C.positions || []).find((p) => p.id === cell.position) || {};
      r = { texte: cell.texte, appoint: cell.appoint, regard: cell.regard };
      libelle = def.numero ? `${def.numero}. ${def.libelle}` : (def.libelle || "");
    } else if (mode === 10) {
      const E = tirage.etendu || {};
      if (E.cle && carte.id === E.cle.carte_id) {
        r = { texte: E.cle.texte, regard: E.cle.regard, appoint: null };
        libelle = "la clé d'intégration";
      } else {
        const cell = ((E.cellules || {})[carte.id]) || {};
        r = { texte: cell.texte, appoint: cell.appoint, regard: cell.regard };
        libelle = cell.niveau_nom
          ? `${cell.niveau_nom} — ${cell.plan_libelle}`
          : "";
      }
    } else {
      // le texte vient du champ que la grille active lit dans la fiche
      const res = ((tirage.textes_par_grille || {})[grilleActive] || {})[carte.id] || {};
      r = res[(pos && pos.id) || ""] || {};
      // Éveil (hors cycle) : pas de position narrative — la phrase du regard.
      if (r.regard || carte.type === "hors_cycle") {
        r = { texte: r.texte || carte.regard || "", regard: true, appoint: null };
        libelle = "le regard";
      }
    }
    if (!r.texte) return null;
    return { libelle: libelle, texte: r.texte, appoint: r.appoint };
  }

  // Mode 10 : quand une rangée est complète, son « temps » se lit.
  function verifierRangee(i) {
    if (mode !== 10 || !tirage.etendu) return;
    const E = tirage.etendu;
    const niveauIndex = Math.floor(i / 3);
    const niveau = (E.niveaux || [])[niveauIndex];
    if (!niveau || rangeesAnnoncees.has(niveau.id)) return;
    const ids = tirage.cartes
      .slice(niveauIndex * 3, niveauIndex * 3 + 3)
      .map((c) => c.id);
    const toutes = ids.every((id) =>
      ordreRevelation.some((r) => r.carte.id === id));
    if (!toutes) return;
    rangeesAnnoncees.add(niveau.id);
    const rangee = (E.rangees || [])[niveauIndex] || { liaisons: [] };
    const bloc = document.createElement("div");
    bloc.className = "rangee-bloc";
    bloc.innerHTML =
      `<p class="rangee-titre">${niveau.temps}</p>` +
      (rangee.liaisons || []).map((l) =>
        `<p class="liaison-ligne">${l.phrase}</p>`).join("");
    lecture.appendChild(bloc);
    requestAnimationFrame(() => bloc.classList.add("visible"));
  }

  function clotureHTML() {
    const L = tirage.lecture || {};
    const c = L.cloture || {};
    const g = grilleCourante() || {};
    const genre = g.cloture || "micro_geste";
    const nom = `<p class="cloture-nom">Ce qui porte ce tirage — ${c.nom}</p>`;
    // « leçon · geste · question » : le geste est déjà lu en position 2,
    // la clôture ne le répète pas — elle revient sur la leçon.
    if (genre === "lecon") {
      return nom + (c.lecon
        ? `<p class="surtitre-bloc">À retenir</p><p class="cloture-geste">${c.lecon}</p>`
        : "");
    }
    const question = c.question ? `<p class="cloture-question">${c.question}</p>` : "";
    if (genre === "question") return nom + question;
    return nom + question +
      (c.micro_geste
        ? `<p class="surtitre-bloc">Faire</p><p class="cloture-geste">${c.micro_geste}</p>`
        : "");
  }

  function montrerCloture() {
    const L = tirage.lecture;
    if (!L) return;
    // l'invite de révélation n'a plus lieu d'être une fois tout révélé
    const attente = lecture.querySelector(".attente");
    if (attente) attente.remove();
    // Neuf + une : la clé est une carte de la grille, et la percée referme.
    if (mode === 10 || mode === 11) {
      ajouterPercee();
      return;
    }
    (L.liaisons || []).forEach((l) => {
      const p = document.createElement("p");
      p.className = "liaison-ligne";
      p.textContent = l.phrase;
      lecture.appendChild(p);
      requestAnimationFrame(() => p.classList.add("visible"));
    });
    (L.motifs || []).forEach((m) => {
      const p = document.createElement("p");
      p.className = "motif-ligne";
      p.textContent = m;
      lecture.appendChild(p);
      requestAnimationFrame(() => p.classList.add("visible"));
    });
    const bloc = document.createElement("div");
    bloc.className = "cloture";
    bloc.innerHTML = clotureHTML();
    lecture.appendChild(bloc);
    requestAnimationFrame(() => bloc.classList.add("visible"));
    ajouterPercee();
  }

  // ── La percée — le protocole de clôture, sur les cartes déjà sorties ──

  function ajouterPercee() {
    const L = tirage.lecture || {};
    if (!L.percee) return;
    const ancienne = lecture.querySelector(".percee-bouton-ligne");
    if (ancienne) ancienne.remove();
    const ligne = document.createElement("div");
    ligne.className = "percee-bouton-ligne";
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.className = "bouton-discret";
    bouton.textContent = "Ouvrir la percée";
    bouton.addEventListener("click", () => {
      ligne.remove();
      montrerPercee(L.percee);
    });
    ligne.appendChild(bouton);
    lecture.appendChild(ligne);
  }

  function montrerPercee(percee) {
    const etapes = [
      ["le blocage", percee.blocage],
      ["la ressource", percee.ressource],
      ["la carte clé", percee.cle],
      ["le geste", percee.geste],
    ];
    const bloc = document.createElement("div");
    bloc.className = "percee";
    bloc.innerHTML =
      `<p class="percee-titre">${percee.titre}</p>` +
      etapes.map(([titre, e]) =>
        `<div class="percee-etape">` +
        `<p class="percee-label">${titre} — ${e.nom}</p>` +
        `<p class="percee-phrase">${e.phrase}</p></div>`).join("") +
      `<p class="percee-note">${percee.note}</p>`;
    lecture.appendChild(bloc);
    requestAnimationFrame(() => bloc.classList.add("visible"));
  }

  // Relecture sous une autre grille : on reconstruit la lecture entière, sans
  // animation — les mêmes cartes, le même ordre de révélation, un autre cadre.
  function rendreLecture() {
    if (!tirage || !tirage.lecture) return;
    const L = tirage.lecture;
    lecture.innerHTML = L.seuil ? `<p class="seuil-ligne">${L.seuil}</p>` : "";
    ordreRevelation.forEach(({ carte, i }) => {
      const pos = positionsActives()[i];
      if (pos) ajouterBlocLecture(carte, pos);
    });
    if (cartesRevelees === tirage.cartes.length) {
      (L.liaisons || []).forEach((l) => {
        const p = document.createElement("p");
        p.className = "liaison-ligne visible";
        p.textContent = l.phrase;
        lecture.appendChild(p);
      });
      (L.motifs || []).forEach((m) => {
        const p = document.createElement("p");
        p.className = "motif-ligne visible";
        p.textContent = m;
        lecture.appendChild(p);
      });
      const bloc = document.createElement("div");
      bloc.className = "cloture visible";
      bloc.innerHTML = clotureHTML();
      lecture.appendChild(bloc);
      ajouterPercee();
    }
    lecture.classList.remove("invisibles");
    lecture.classList.add("visible");
  }

  // ── Le sélecteur de grille — après le tirage ────────────────────────

  function construireGrilles() {
    const barre = document.getElementById("grilles");
    if (!barre) return;
    if (mode !== 3 || !tirage || !tirage.grilles) {
      barre.classList.add("invisibles");
      barre.innerHTML = "";
      return;
    }
    barre.innerHTML = "";
    tirage.grilles.forEach((g) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "grille-bouton" + (g.id === grilleActive ? " actif" : "");
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(g.id === grilleActive));
      b.textContent = g.nom;
      if (g.sous_titre) b.title = g.sous_titre;
      b.addEventListener("click", () => changerGrille(g.id));
      barre.appendChild(b);
    });
    barre.classList.remove("invisibles");
  }

  function changerGrille(id) {
    if (!tirage || tirage.mode !== 3 || id === grilleActive) return;
    grilleActive = id;
    construireGrilles();
    const positions = positionsActives();
    slotsBox.querySelectorAll(".slot").forEach((slot, i) => {
      const lib = slot.querySelector(".libelle");
      if (!lib || lib.dataset.hors === "1" || !positions[i]) return;
      lib.textContent = positions[i].libelle;
      lib.dataset.pos = positions[i].id;
    });
    majCompteur();
    afficherPedagogie();
    // avant le tirage, on ne touche pas à l'invite : seuls les libellés changent
    if (ordreRevelation.length) rendreLecture();
    if (vueActive !== "ensemble") afficherVue(vueActive);
    document.getElementById("detail-position").hidden = true;
  }

  function metaDe(carte) {
    const bouts = [];
    if (carte.type === "hors_cycle") bouts.push("hors cycle");
    else if (carte.type === "majeur") bouts.push("arcane majeur");
    if (carte.famille) bouts.push(carte.famille);
    if (carte.rang) bouts.push(carte.rang);
    else if (carte.degre !== null && carte.degre !== undefined) bouts.push(String(carte.degre));
    return bouts.join(" · ");
  }

  // ── Tirage à une carte : le jour en trois temps (voir, écouter, faire)

  function montrerLectureJour(carte) {
    const p = carte.positions || {};
    const regard = carte.type === "hors_cycle" ? carte.regard : "";
    const questions = (carte.questions || [])
      .map((q) => `<li>${q}</li>`).join("");
    lecture.innerHTML =
      `<p class="nom-carte">${carte.nom}</p>` +
      `<p class="meta-carte">${metaDe(carte)}</p>` +
      `<p class="texte-carte">${regard || p.jour || carte.lumiere || ""}</p>` +
      (questions
        ? `<p class="surtitre-bloc">Écouter</p><ul class="ecouter">${questions}</ul>`
        : "") +
      (carte.micro_geste
        ? `<p class="surtitre-bloc">Faire</p><p class="faire">${carte.micro_geste}</p>`
        : "");
    lecture.classList.remove("invisibles");
    requestAnimationFrame(() => lecture.classList.add("visible"));
  }

  // ── Plein écran — la vignette s'agrandit, la fiche complète à côté ──

  function ouvrirPlein(carte) {
    if (!carte) return;
    const img = carte.image || DOS_DEFAUT;
    const q = (carte.questions || []).map((x) => `<li>${x}</li>`).join("");
    const ombre = carte.ombre
      ? `<p class="pt-titre">Ombre — ${carte.ombre.mode}</p>` +
        `<p>${carte.ombre.texte}</p>` +
        `<p class="pt-issue">${carte.ombre.issue}</p>`
      : "";
    pleinImg.src = img;
    pleinImg.alt = carte.nom;
    pleinTexte.innerHTML =
      `<p class="plein-nom">${carte.nom}</p>` +
      `<p class="plein-meta">${metaDe(carte)}</p>` +
      (carte.lumiere ? `<p class="pt-titre">Lumière</p><p>${carte.lumiere}</p>` : "") +
      ombre +
      (q ? `<p class="pt-titre">Questions</p><ul>${q}</ul>` : "") +
      (carte.lecon ? `<p class="pt-titre">Leçon</p><p><i>${carte.lecon}</i></p>` : "") +
      (carte.micro_geste ? `<p class="pt-titre">Faire</p><p>${carte.micro_geste}</p>` : "");
    plein.classList.remove("invisible");
    plein.setAttribute("aria-hidden", "false");
    document.body.classList.add("fige-scroll");
  }

  function fermerPlein() {
    plein.classList.add("invisible");
    plein.setAttribute("aria-hidden", "true");
    document.body.classList.remove("fige-scroll");
  }

  plein.addEventListener("click", fermerPlein);
  pleinTexte.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") fermerPlein();
  });

  // ── Replier ─────────────────────────────────────────────────────────

  function replier() {
    fermerPlein();
    tirage = null;
    choisies = [];
    carteEnPlace = false;
    carteRevelation = false;
    cartesRevelees = 0;
    eventail.innerHTML = "";
    slotsBox.classList.add("invisibles");
    slotsBox.innerHTML = "";
    lecture.classList.add("invisibles");
    lecture.classList.remove("visible");
    lecture.innerHTML = "";
    replierBtn.classList.add("invisible");
    ordreRevelation = [];
    rangeesAnnoncees = new Set();
    document.body.classList.remove("en-tirage", "a-commence");
    reinitialiserVues();
    const barre = document.getElementById("grilles");
    if (barre) {
      barre.classList.add("invisibles");
      barre.innerHTML = "";
    }
    charger();
  }

  // ── Le tirage au choix (mode 0) ─────────────────────────────────────
  // Greer §2.4 : les 79 cartes face visible, un tas « peut-être », puis des
  // éliminations une à une jusqu'à trois. Aucun hasard — et la réticence à
  // écarter une carte est une information.

  const choixEtat = { phase: "attirer", gardees: [], ecartees: [], jeu: null, methode: {} };

  async function demarrerChoix() {
    document.body.classList.remove("en-tirage", "a-commence");
    reinitialiserVues();
    document.getElementById("compteur-tirage").classList.add("invisibles");
    slotsBox.classList.add("invisibles");
    lecture.classList.add("invisibles");
    eventail.classList.add("invisibles");
    replierBtn.classList.add("invisible");
    document.getElementById("choix").classList.remove("invisibles");
    surtitre.textContent = "Le jeu des 79";
    piedTexte.textContent = "79 cartes · choisies face visible, à la main · aucune prédiction";
    if (!choixEtat.jeu) {
      const r = await fetch("api/jeu");
      if (!r.ok) return;
      const d = await r.json();
      choixEtat.jeu = d.cartes || [];
      choixEtat.methode = d.methode || {};
    }
    // la méthode : le texte du tirage au choix (éditable dans l'album)
    const boite = document.getElementById("choix-methode");
    if (boite) {
      const md = (t) => (t || "")
        .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
        .split(/\n\n/).map((x) => `<p>${x.replace(/\n/g, "<br>")}</p>`).join("");
      boite.innerHTML =
        `<div class="pedagogie"><p>${md(choixEtat.methode.comment)}</p>` +
        `<p class="choix-reticence">${md(choixEtat.methode.reticence)}</p></div>`;
    }
    const details = document.querySelector(".ped-conteneur");
    if (details) details.classList.add("invisible");
    choixEtat.phase = "attirer";
    choixEtat.gardees = [];
    choixEtat.ecartees = [];
    dessinerChoix();
  }

  function dessinerChoix() {
    const consigne = document.getElementById("choix-consigne");
    const compteur = document.getElementById("choix-compteur");
    const mur = document.getElementById("choix-mur");
    const bElim = document.getElementById("choix-eliminer");
    const bLire = document.getElementById("choix-lire");
    mur.innerHTML = "";
    const nomDe = (id) => (choixEtat.jeu.find((c) => c.id === id) || {}).nom || id;
    const imageDe = (id) => (choixEtat.jeu.find((c) => c.id === id) || {}).image || "";

    if (choixEtat.phase === "attirer") {
      consigne.textContent = "Passe sur chaque carte. Garde celles qui représentent quelque chose pour toi, maintenant.";
      compteur.textContent = choixEtat.gardees.length
        ? choixEtat.gardees.length + " carte" + (choixEtat.gardees.length > 1 ? "s" : "") +
          " gardée" + (choixEtat.gardees.length > 1 ? "s" : "") +
          " · garde-en cinq à vingt-cinq, ou trois pour lire tout de suite"
        : "Aucune carte gardée pour l'instant";
      choixEtat.jeu.forEach((c) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "carte-choix" + (choixEtat.gardees.includes(c.id) ? " gardee" : "");
        b.setAttribute("aria-label", c.nom);
        b.innerHTML = `<img src="${c.image}" alt="${c.nom}" draggable="false"><span class="carte-choix-nom">${c.nom}</span>`;
        b.addEventListener("click", () => basculerGarde(c.id));
        mur.appendChild(b);
      });
    } else {
      consigne.textContent = "Écarte une carte à la fois. À chaque fois, la question est la même : si je devais en sacrifier une, laquelle ?";
      compteur.textContent = choixEtat.gardees.length +
        " cartes restantes · arrête-toi à trois";
      choixEtat.gardees.forEach((id) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "carte-choix grande";
        b.setAttribute("aria-label", nomDe(id) + " — écarter");
        b.innerHTML = `<img src="${imageDe(id)}" alt="${nomDe(id)}" draggable="false"><span class="carte-choix-nom">${nomDe(id)}</span>`;
        b.addEventListener("click", () => ecarterCarte(id));
        mur.appendChild(b);
      });
    }
    bElim.classList.toggle("invisible",
      choixEtat.phase !== "attirer" || choixEtat.gardees.length <= 3);
    bLire.classList.toggle("invisible", choixEtat.gardees.length !== 3);
    bLire.disabled = choixEtat.gardees.length !== 3;
  }

  function basculerGarde(id) {
    const i = choixEtat.gardees.indexOf(id);
    if (i >= 0) choixEtat.gardees.splice(i, 1);
    else if (choixEtat.gardees.length < 25) choixEtat.gardees.push(id);
    dessinerChoix();
  }

  function ecarterCarte(id) {
    choixEtat.gardees = choixEtat.gardees.filter((x) => x !== id);
    choixEtat.ecartees.push(id);
    dessinerChoix();
  }

  async function lireChoix() {
    if (choixEtat.gardees.length !== 3) return;
    const r = await fetch("api/lecture?cartes=" + choixEtat.gardees.join(","));
    if (!r.ok) return;
    const d = await r.json();
    const derniere = choixEtat.ecartees[choixEtat.ecartees.length - 1];
    const infos = derniere
      ? choixEtat.jeu.find((x) => x.id === derniere) : null;

    document.getElementById("choix").classList.add("invisibles");
    eventail.classList.add("invisibles");
    const details = document.querySelector(".ped-conteneur");
    if (details) details.classList.remove("invisible");
    mode = 3;
    boutonsMode.forEach((b) => {
      const actif = Number(b.dataset.mode) === 3;
      b.classList.toggle("actif", actif);
      b.setAttribute("aria-selected", actif ? "true" : "false");
    });
    tirage = d;
    choisies = [];
    ordreRevelation = [];
    rangeesAnnoncees = new Set();
    grilleActive = d.grille || "causale_3";
    afficherPedagogie();
    construireSlots();
    slotsBox.classList.remove("invisibles");
    placerChoisies();
    lecture.classList.remove("invisibles");
    if (infos) {
      const note = document.createElement("p");
      note.className = "note-reticence";
      note.textContent = "La dernière carte écartée : " + infos.nom +
        ". " + (choixEtat.methode.reticence || "");
      lecture.prepend(note);
    }
  }

  function placerChoisies() {
    document.body.classList.remove("en-tirage", "a-commence");
    majCompteur();
    slotsBox.classList.remove("sans-vide");
    tirage.cartes.forEach((carte, i) => {
      const cadre = slotsBox.querySelector(`.cadre[data-i="${i}"]`);
      if (!cadre) return;
      const el = document.createElement("button");
      el.type = "button";
      el.className = "carte choisie posee";
      el.setAttribute("aria-label", carte.nom);
      el.innerHTML =
        '<span class="interieur">' +
        '<span class="dos"><img src="' + DOS_DEFAUT + '" alt="" draggable="false"></span>' +
        '<span class="face"></span></span>';
      if (carte.image) {
        el.querySelector(".face").innerHTML =
          `<img src="${carte.image}" alt="${carte.nom}" draggable="false">`;
      }
      el._carte = carte;
      el._regard = carte.type === "hors_cycle" ? (carte.regard || "") : "";
      el.style.cssText = "position:absolute;inset:0;width:100%;height:100%;opacity:1";
      el.title = "Révéler la carte";
      el.addEventListener("click", () => choisir(el));
      cadre.appendChild(el);
      const slot = cadre.closest(".slot");
      if (slot) slot.classList.add("remplie");
    });
    eventail.classList.add("estompe");
    montrerAttente();
    construireGrilles();
  }

  document.getElementById("choix-eliminer").addEventListener("click", () => {
    choixEtat.phase = "eliminer";
    dessinerChoix();
  });
  document.getElementById("choix-lire").addEventListener("click", lireChoix);

  // ── Les vues de lecture : Récit · Ensemble · Liens ──────────────────
  // Une fois tout révélé, la même lecture se regarde de trois façons.
  // « Ensemble » est la vue d'origine (le plan + le texte qui suit) ; les
  // deux autres sont reconstruites à partir des mêmes données.

  const vuesBarre = document.getElementById("vues");
  const vueRecit = document.getElementById("vue-recit");
  const vueLiens = document.getElementById("vue-liens");
  let vueActive = "ensemble";
  let recitIndex = 0;

  function lireVueMemo() {
    try { return localStorage.getItem("tarot-vue") || ""; } catch (e) { return ""; }
  }
  function ecrireVueMemo(v) {
    try { localStorage.setItem("tarot-vue", v); } catch (e) { /* sans mémoire */ }
  }

  function reinitialiserVues() {
    vueActive = "ensemble";
    recitIndex = 0;
    document.body.classList.remove("vue-recit", "vue-liens");
    vuesBarre.classList.add("invisibles");
    vueRecit.classList.add("invisibles");
    vueLiens.classList.add("invisibles");
    vueRecit.innerHTML = "";
    vueLiens.innerHTML = "";
  }

  function montrerVues() {
    if (!tirage || (mode !== 3 && mode !== 10 && mode !== 11)) return;
    vuesBarre.querySelector('[data-vue="liens"]').classList.toggle("invisible", mode === 11);
    vuesBarre.classList.remove("invisibles");
    const memo = lireVueMemo();
    afficherVue(memo && !(memo === "liens" && mode === 11) ? memo : "ensemble");
  }

  function afficherVue(v) {
    vueActive = v;
    vuesBarre.querySelectorAll(".vue-bouton").forEach((b) => {
      const actif = b.dataset.vue === v;
      b.classList.toggle("actif", actif);
      b.setAttribute("aria-selected", actif ? "true" : "false");
    });
    document.body.classList.toggle("vue-recit", v === "recit");
    document.body.classList.toggle("vue-liens", v === "liens");
    vueRecit.classList.toggle("invisibles", v !== "recit");
    vueLiens.classList.toggle("invisibles", v !== "liens");
    if (v === "recit") dessinerRecit();
    if (v === "liens") dessinerLiens();
  }

  vuesBarre.addEventListener("click", (e) => {
    const b = e.target.closest(".vue-bouton");
    if (!b) return;
    ecrireVueMemo(b.dataset.vue);
    afficherVue(b.dataset.vue);
    window.scrollTo({ top: vuesBarre.offsetTop - 12, behavior: "smooth" });
  });

  // les pages du récit : une par carte (dans l'ordre des positions), le
  // « temps » de chaque rangée en Neuf + une, puis ce qui referme le tirage
  function pagesRecit() {
    const pages = [];
    const positions = positionsActives();
    const parPosition = ordreRevelation.slice().sort((a, b) => a.i - b.i);
    parPosition.forEach(({ carte, i }) => {
      const d = donneesBloc(carte, positions[i]) || { libelle: libellePosition(i), texte: "", appoint: null };
      pages.push({ genre: "carte", carte: carte, libelle: d.libelle || libellePosition(i),
                   texte: d.texte, appoint: d.appoint });
      if (mode === 10 && i % 3 === 2 && i < 9) {
        const E = tirage.etendu || {};
        const niv = (E.niveaux || [])[Math.floor(i / 3)];
        const rangee = (E.rangees || [])[Math.floor(i / 3)] || {};
        if (niv && (rangee.liaisons || []).length) {
          pages.push({ genre: "temps", titre: niv.temps,
                       phrases: rangee.liaisons.map((l) => l.phrase) });
        }
      }
    });
    // la fin : liaisons, motifs, clôture et percée — déjà rendus dans la
    // lecture d'ensemble, on les reprend tels quels
    const fin = lecture.querySelectorAll(":scope > .liaison-ligne, :scope > .motif-ligne, :scope > .cloture, :scope > .percee");
    if (fin.length || (tirage.lecture || {}).percee) pages.push({ genre: "fin", noeuds: Array.from(fin) });
    return pages;
  }

  function dessinerRecit() {
    const pages = pagesRecit();
    if (!pages.length) { vueRecit.innerHTML = ""; return; }
    recitIndex = Math.max(0, Math.min(pages.length - 1, recitIndex));
    const p = pages[recitIndex];
    let corps = "";
    if (p.genre === "carte") {
      corps =
        `<button type="button" class="recit-image" aria-label="Agrandir ${p.carte.nom}">` +
        `<img src="${p.carte.image || DOS_DEFAUT}" alt="${p.carte.nom}" draggable="false"></button>` +
        `<p class="recit-position">${p.libelle}</p>` +
        `<p class="recit-nom">${p.carte.nom}</p>` +
        (p.texte ? `<p class="recit-texte">${p.texte}</p>` : "") +
        appointHTML(p.appoint);
    } else if (p.genre === "temps") {
      corps = `<p class="recit-temps-titre">${p.titre}</p>` +
        p.phrases.map((x) => `<p class="recit-texte">${x}</p>`).join("");
    } else {
      corps = `<p class="recit-temps-titre">Ce qui porte ce tirage</p><div class="recit-fin"></div>`;
    }
    vueRecit.innerHTML =
      `<div class="recit-page">${corps}</div>` +
      `<div class="recit-nav">` +
      `<button type="button" class="bouton-discret recit-prec"${recitIndex === 0 ? " disabled" : ""}>‹ Précédente</button>` +
      `<span class="recit-points">${pages.map((_, k) => `<i class="${k === recitIndex ? "actif" : ""}"></i>`).join("")}</span>` +
      `<button type="button" class="bouton-discret recit-suiv"${recitIndex === pages.length - 1 ? " disabled" : ""}>Suivante ›</button>` +
      `</div>`;
    if (p.genre === "fin") {
      const boite = vueRecit.querySelector(".recit-fin");
      p.noeuds.forEach((n) => {
        const copie = n.cloneNode(true);
        copie.classList.add("visible");
        boite.appendChild(copie);
      });
      const L = tirage.lecture || {};
      if (L.percee && !lecture.querySelector(":scope > .percee")) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "bouton-discret";
        b.textContent = "Ouvrir la percée";
        b.addEventListener("click", () => {
          const ligne = lecture.querySelector(".percee-bouton-ligne");
          if (ligne) ligne.remove();
          montrerPercee(L.percee);
          dessinerRecit();
        });
        boite.appendChild(b);
      }
    }
    if (p.genre === "carte") {
      vueRecit.querySelector(".recit-image").addEventListener("click", () => ouvrirPlein(p.carte));
    }
    vueRecit.querySelector(".recit-prec").addEventListener("click", () => { recitIndex--; dessinerRecit(); });
    vueRecit.querySelector(".recit-suiv").addEventListener("click", () => { recitIndex++; dessinerRecit(); });
  }

  // glisser le doigt pour passer d'une page à l'autre
  let recitDepart = null;
  vueRecit.addEventListener("pointerdown", (e) => { recitDepart = { x: e.clientX, y: e.clientY }; });
  vueRecit.addEventListener("pointerup", (e) => {
    if (!recitDepart) return;
    const dx = e.clientX - recitDepart.x;
    const dy = e.clientY - recitDepart.y;
    recitDepart = null;
    if (Math.abs(dx) < 50 || Math.abs(dy) > Math.abs(dx)) return;
    const total = pagesRecit().length;
    const suivant = recitIndex + (dx < 0 ? 1 : -1);
    if (suivant < 0 || suivant >= total) return;
    recitIndex = suivant;
    dessinerRecit();
  });

  function vignettes(cartes, libelles) {
    return `<div class="liens-cartes">` + cartes.map((c, k) =>
      `<button type="button" class="liens-carte" data-id="${c.id}" aria-label="${c.nom}">` +
      `<img src="${c.image || DOS_DEFAUT}" alt="" draggable="false">` +
      (libelles && libelles[k] ? `<span>${libelles[k]}</span>` : "") +
      `</button>`).join("") + `</div>`;
  }

  function dessinerLiens() {
    if (!tirage) return;
    const L = tirage.lecture || {};
    let html = "";
    if (mode === 10) {
      const E = tirage.etendu || {};
      const plans = (E.plans || []).map((p) => p.libelle);
      (E.niveaux || []).forEach((niv, k) => {
        const rangee = (E.rangees || [])[k] || {};
        html += `<div class="liens-bande">` +
          `<p class="liens-titre">${niv.temps}</p>` +
          (niv.invite ? `<p class="liens-invite">${niv.invite}</p>` : "") +
          vignettes(tirage.cartes.slice(k * 3, k * 3 + 3), plans) +
          (rangee.liaisons || []).map((l) => `<p class="liens-phrase">${l.phrase}</p>`).join("") +
          `</div><div class="liens-fil"></div>`;
      });
      const cle = tirage.cartes[9];
      if (cle) {
        html += `<div class="liens-bande liens-centre">` +
          `<p class="liens-titre">${(E.cle && E.cle.libelle) || "la clé d'intégration"}</p>` +
          vignettes([cle]) +
          (E.cle && E.cle.texte ? `<p class="liens-phrase">${E.cle.texte}</p>` : "") +
          `</div>`;
      }
    } else {
      const positions = positionsActives();
      html += `<div class="liens-bande">` +
        vignettes(tirage.cartes, tirage.cartes.map((_, i) => (positions[i] || {}).libelle || "")) +
        `</div>`;
      (L.liaisons || []).forEach((l) => {
        html += `<div class="liens-fil"></div><div class="liens-bande"><p class="liens-phrase">${l.phrase}</p></div>`;
      });
      if ((L.motifs || []).length) {
        html += `<div class="liens-fil"></div><div class="liens-bande liens-centre">` +
          `<p class="liens-titre">Les motifs</p>` +
          L.motifs.map((m) => `<p class="liens-phrase">${m}</p>`).join("") + `</div>`;
      }
    }
    vueLiens.innerHTML = html;
    vueLiens.querySelectorAll(".liens-carte").forEach((b) => {
      b.addEventListener("click", () => {
        const c = tirage.cartes.find((x) => x.id === b.dataset.id);
        if (c) ouvrirPlein(c);
      });
    });
  }

  // ── Modes ───────────────────────────────────────────────────────────

  async function changerMode(nouveau, bouton) {
    if (nouveau === mode) return;
    document.getElementById("choix").classList.add("invisibles");
    eventail.classList.remove("invisibles");
    const details = document.querySelector(".ped-conteneur");
    if (details) details.classList.remove("invisible");
    mode = nouveau;
    boutonsMode.forEach((b) => {
      const actif = b === bouton;
      b.classList.toggle("actif", actif);
      b.setAttribute("aria-selected", actif ? "true" : "false");
    });
    if (nouveau === 0) {
      await demarrerChoix();
      return;
    }
    replier();
  }

  boutonsMode.forEach((b) => b.addEventListener("click", () => changerMode(Number(b.dataset.mode), b)));
  replierBtn.addEventListener("click", replier);
  slotsBox.addEventListener("click", (e) => {
    const cible = e.target.closest(".clic-position");
    if (cible) detailPosition(cible);
  });
  // les libellés sont role="button" : Entrée et Espace doivent aussi ouvrir
  slotsBox.addEventListener("keydown", (e) => {
    const cible = e.target.closest(".clic-position");
    if (cible && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      detailPosition(cible);
    }
  });
  const dp = document.getElementById("detail-position");
  function fermerDetail() {
    if (dp.hidden) return;
    dp.hidden = true;
    if (dpDernierFocus) { dpDernierFocus.focus({ preventScroll: true }); dpDernierFocus = null; }
  }
  document.getElementById("fermer-position").addEventListener("click", fermerDetail);
  dp.addEventListener("click", (e) => {
    if (e.target === dp) fermerDetail();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") fermerDetail();
  });
  window.addEventListener("resize", () => {
    if (!tirage && !carteEnPlace) construireEventail(dernierTotal);
  });

  // ?mode=3 dans l'URL : préparer la relecture d'un tirage précis.
  // Sans graine dans l'URL, on ouvre toujours sur « Une carte ».
  const params = new URLSearchParams(location.search);
  const modeUrl = params.has("graine") && params.has("mode") ? Number(params.get("mode")) : 1;
  if (modeUrl === 0 || modeUrl === 1 || modeUrl === 3 || modeUrl === 10 || modeUrl === 11) {
    mode = modeUrl;
    boutonsMode.forEach((b) => {
      const actif = Number(b.dataset.mode) === modeUrl;
      b.classList.toggle("actif", actif);
      b.setAttribute("aria-selected", actif ? "true" : "false");
    });
  }

  // au chargement : le jeu se déplie, la graine est déjà tirée
  if (modeUrl === 0) demarrerChoix();
  else charger();
})();
