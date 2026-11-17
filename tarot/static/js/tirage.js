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
  /* Le dos chargé et DÉCODÉ dès l'ouverture de l'app : le paquet n'apparaît
     qu'avec lui (Martin, 2026-11-16 : « le deck est d'abord noir, puis
     écrasé, puis correct » — il s'affichait avant que son image soit prête). */
  // une image PRÊTE : décodée, ou au moins chargée — et jamais d'attente
  // infinie (decode() peut ne jamais répondre dans un onglet en arrière-plan)
  function imagePrete(src, delaiMax) {
    return new Promise((ok) => {
      const i = new Image();
      const fini = () => ok(i);
      i.onload = fini;
      i.onerror = fini;
      i.src = src;
      if (i.decode) i.decode().then(fini, fini);
      setTimeout(fini, delaiMax);
    });
  }
  const dosPret = imagePrete(DOS_DEFAUT, 1500);

  // l'image « de lecture » (récit, plein écran) : sur téléphone la taille
  // intermédiaire (800 px, ~180 Ko) suffit à l'écran ; la face entière
  // (1024 px, ~500 Ko) reste pour le bureau
  const petitEcran = matchMedia("(max-width: 900px)");
  const imageLecture = (c) => (petitEcran.matches && c.image_moyenne) || c.image;

  const eventail = document.getElementById("eventail");
  const slotsBox = document.getElementById("slots");
  const lecture = document.getElementById("lecture");
  const replierBtn = document.getElementById("replier");
  const plein = document.getElementById("plein");
  const pleinCorps = plein.querySelector(".plein-corps");
  const pleinImg = plein.querySelector(".plein-img");
  const pleinTexte = plein.querySelector(".plein-texte");

  /* ZOOM MAISON de la carte plein écran (2026-11-16 : « je peux zoomer un
     peu, mais ça finit par planter »). Le pincement NATIF d'iOS agrandit
     TOUTE la page — et dans Ta Trame, toute la page HÔTE autour de l'iframe :
     chaque calque (fonds fixes, cartes 3D) est ré-échantillonné à l'échelle
     du zoom, la mémoire explose et iOS tue la page (« Un problème est
     survenu »). Ici, le zoom natif est BLOQUÉ dans #plein et seule l'IMAGE
     grandit (transform) : un bitmap déjà décodé, coût constant. Même code
     que zoomCarte() dans ASTRO_PLUS_APP/templates/index.html.
     Pincer = zoomer (×1 à ×4, autour des doigts) ; un doigt = déplacer ;
     toucher l'image zoomée = revenir à ×1 (au lieu de fermer). */
  function zoomCarte(vue, img) {
    const MAX = 4;
    let s = 1, tx = 0, ty = 0, geste = null, dernierGeste = 0;
    const dist = (a, b) => Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    const milieu = (a, b) => ({ x: (a.clientX + b.clientX) / 2, y: (a.clientY + b.clientY) / 2 });
    const centre = () => {  // centre de l'image SANS la translation courante
      const r = img.getBoundingClientRect();
      return { x: r.left + r.width / 2 - tx, y: r.top + r.height / 2 - ty };
    };
    const appliquer = () => {
      const bx = img.offsetWidth * (s - 1) / 2, by = img.offsetHeight * (s - 1) / 2;
      tx = Math.max(-bx, Math.min(bx, tx));
      ty = Math.max(-by, Math.min(by, ty));
      img.style.transition = geste ? "none" : "transform .25s ease";
      img.style.transform = s > 1 ? `translate(${tx}px, ${ty}px) scale(${s})` : "";
      vue.classList.toggle("zoom-actif", s > 1);
    };
    const reinitialiser = () => { s = 1; tx = ty = 0; geste = null; appliquer(); };
    vue.addEventListener("touchstart", (e) => {
      if (e.touches.length >= 2) {
        e.preventDefault();
        const [a, b] = e.touches;
        geste = { type: "pince", d0: dist(a, b), m0: milieu(a, b), c: centre(), s0: s, tx0: tx, ty0: ty };
      } else if (s > 1) {
        const t = e.touches[0];
        geste = { type: "glisse", x0: t.clientX, y0: t.clientY, tx0: tx, ty0: ty, bouge: false };
      }
    }, { passive: false });
    vue.addEventListener("touchmove", (e) => {
      if (e.touches.length >= 2) e.preventDefault();   // jamais de zoom natif ici
      if (!geste) return;
      if (geste.type === "pince" && e.touches.length >= 2) {
        const [a, b] = e.touches, m = milieu(a, b);
        s = Math.max(1, Math.min(MAX, geste.s0 * dist(a, b) / geste.d0));
        const k = s / geste.s0;   // le point sous les doigts reste sous les doigts
        tx = (m.x - geste.c.x) - (geste.m0.x - geste.c.x - geste.tx0) * k;
        ty = (m.y - geste.c.y) - (geste.m0.y - geste.c.y - geste.ty0) * k;
        appliquer();
      } else if (geste.type === "glisse") {
        e.preventDefault();
        const t = e.touches[0], dx = t.clientX - geste.x0, dy = t.clientY - geste.y0;
        if (Math.abs(dx) + Math.abs(dy) > 6) geste.bouge = true;
        tx = geste.tx0 + dx; ty = geste.ty0 + dy;
        appliquer();
      }
    }, { passive: false });
    vue.addEventListener("touchend", (e) => {
      if (!geste || e.touches.length) return;
      const g = geste;
      geste = null;
      dernierGeste = Date.now();
      if (g.type === "glisse" && !g.bouge) reinitialiser();   // un toucher dézoome
      else if (s < 1.05) reinitialiser();
      else appliquer();
    });
    // Safari : les événements gesture* déclenchent le zoom natif s'ils passent
    ["gesturestart", "gesturechange"].forEach((t) =>
      vue.addEventListener(t, (e) => e.preventDefault(), { passive: false }));
    // occupe : zoomée, ou un geste vient de finir — aucune fermeture dans ce cas
    return { reinitialiser, occupe: () => s > 1 || Date.now() - dernierGeste < 450 };
  }
  const zoomPlein = zoomCarte(plein, pleinImg);
  const surtitre = document.getElementById("surtitre-jeu");
  const piedTexte = document.getElementById("pied-texte");

  // ── Le catalogue des tirages (refonte 2026-11-16) ───────────────────
  /* Avant : 6 onglets par FORME (« Une carte », « Croix »…), trois croix sous
     un seul onglet, « Au choix » rangé comme un tirage alors que c'est une
     façon de piger, et jusqu'à 13 choix visibles avant la lecture.
     Maintenant : on entre par ce qu'on vient chercher (planche validée par
     Martin : maquettes/planche_tirages.html, variante A). Chaque tirage
     montre sa FORME en miniature — le signifiant qui distingue d'un coup
     d'œil une croix de trois cartes alignées. Un tirage = un mode de l'API
     (+ la croix lue) ; « Au choix » vit dans Trois cartes, Celtique / Osho
     dans La croix ; la croix composite devient La croix de la relation. */
  const R = (x, y, w, h, cle) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="1.6"${cle ? ' class="cle"' : ""}/>`;
  const SCHEMAS = {
    un: R(22, 13, 14, 24),
    trois: R(5, 17, 14, 24) + R(22, 17, 14, 24) + R(39, 17, 14, 24),
    diamant: R(23, 2, 12, 17) + R(6, 21, 12, 17) + R(23, 21, 12, 17, true) +
             R(40, 21, 12, 17) + R(23, 40, 12, 17),
    // toutes les cases au même rapport vertical (~0,6, comme une carte) :
    // Neuf + une et le bâton de la croix étaient presque carrés (Martin, 2026-11-16)
    neuf: [15, 25, 35].flatMap((x) => [1, 15, 29].map((y) => R(x, y, 8, 13))).join("") +
          R(25, 44, 8, 13, true),
    croix: R(15, 2, 10, 15) + R(2, 20, 10, 15) + R(15, 20, 10, 15) + R(28, 20, 10, 15) +
           R(15, 38, 10, 15) + R(46, 1, 8, 13) + R(46, 15, 8, 13) + R(46, 29, 8, 13) +
           R(46, 43, 8, 13),
  };
  const CATALOGUE = [
    // « Une question » remplace la carte du jour (2026-11-16) : Ta Trame a déjà
    // ses cartes du jour. Wen : une carte = le cœur du sujet, posé par UNE question.
    { etagere: "Pour une question", items: [
      { id: "question", nom: "Une question", n: 1, mode: 1, schema: "un", vedette: true,
        pour: "Choisis ta question ; une carte l'éclaire." },
    ]},
    { etagere: "Pour éclairer une situation", items: [
      { id: "trois", nom: "Trois cartes", n: 3, mode: 3, schema: "trois", pige: true,
        pour: "Ce que tu amènes, ce qui se joue, ce que tu peux essayer." },
      { id: "diamant", nom: "Le Diamant", n: 5, mode: 5, schema: "diamant",
        pour: "Une question précise, ce qui la nourrit, ce qui la dénoue." },
    ]},
    { etagere: "Pour approfondir", items: [
      { id: "neuf", nom: "Neuf + une", n: 10, mode: 10, schema: "neuf",
        pour: "Le visible, le latent, la résolution — et la carte qui relie tout." },
      { id: "croix", nom: "La croix", n: 10, mode: 11, schema: "croix",
        pour: "Le grand tirage : une situation entière, en dix cartes.",
        lectures: [
          { id: "croix_celtique", nom: "Celtique", sous: "l'état des lieux" },
          { id: "croix_osho", nom: "Osho", sous: "le processus en cours" },
        ] },
    ]},
    { etagere: "Pour une relation", items: [
      { id: "relation", nom: "La croix de la relation", n: 10, mode: 11, schema: "croix",
        croix: "croix_composite",
        pour: "Le lien comme une entité : ce que chacun y met, ce qui le fait évoluer." },
    ]},
  ];
  const TOUS_TIRAGES = CATALOGUE.flatMap((e) => e.items);
  let tirageChoisi = null;   // l'entrée du catalogue ouverte (null = l'accueil)

  // ── Grilles de relecture ────────────────────────────────────────────
  // La même donne se relit sous plusieurs cadres (Greer, les permutations) :
  // les cartes ne changent pas, seule change la question posée à la position.
  let grilleActive = "causale_3";
  let croixActive = "croix_celtique";  // même donne, trois croix possibles
  let questionActive = null;           // Une question : la question posée à la carte
  let ordreRevelation = [];   // [{carte, i}] dans l'ordre choisi par celui qui tire
  let rangeesAnnoncees = new Set();  // mode 10 : les trois temps déjà lus

  // les tirages en croix : les trois croix à dix cartes et le diamant (cinq)
  function estCroix() { return mode === 5 || mode === 11; }

  function croixCourante() {
    const liste = (tirage && tirage.croix_choix) || [];
    return liste.find(c => c.id === croixActive) || liste[0] || null;
  }

  function grilleCourante() {
    if (!tirage) return null;
    if (tirage.mode === 1) {
      return { id: "question_1", nom: "Une question", cloture: "micro_geste",
               positions: tirage.positions_def || [],
               pedagogie: tirage.pedagogie || {} };
    }
    if (tirage.mode === 10) {
      return { id: "etendu_9_1", nom: "Neuf + une", cloture: "percee",
               positions: [],
               pedagogie: tirage.pedagogie || {} };
    }
    if (estCroix()) {
      const C = croixCourante() || {};
      return { id: C.id || croixActive, nom: C.nom || "La croix celtique", cloture: "percee",
               positions: C.positions || [],
               pedagogie: C.pedagogie || tirage.pedagogie || {} };
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
    dosPret.then(() => setTimeout(() => {
      cartes.forEach((c, i) => {
        setTimeout(() => c.classList.add("visible"), Math.min(i * 6, 420));
      });
    }, 30));
  }

  /* Le paquet se REPLACE quand sa largeur change (barre d'adresse d'iOS,
     cadre de Ta Trame qui se cale, rotation) : sinon il garde les positions
     calculées pour l'ancienne largeur et paraît écrasé. */
  function replacerPaquet() {
    const ligne = eventail.querySelector(".ligne");
    const cartes = cartesLibres();
    if (!ligne || !cartes.length || melangeEnCours) return;
    const n = cartes.length;
    const l = carteLargeur();
    const pas = n > 1 ? (eventail.clientWidth - 4 - l) / (n - 1) : 0;
    pasLigne = pas;
    ligne.style.width = Math.ceil(l + pas * (n - 1)) + "px";
    cartes.forEach((c, i) => { c.style.left = Math.round(i * pas) + "px"; });
  }
  let largeurPaquet = 0;
  new ResizeObserver(() => {
    const w = eventail.clientWidth;
    if (w && Math.abs(w - largeurPaquet) > 2) { largeurPaquet = w; replacerPaquet(); }
  }).observe(eventail);

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

  let melangeEnCours = false;   // pendant l'animation : on ne pige pas

  function loupeActive() {
    return tirage && !carteEnPlace && !melangeEnCours && choisies.length < tirage.cartes.length &&
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

  function questionCourante() {
    return (tirage && (tirage.positions_def || []).find((p) => p.id === questionActive)) || null;
  }

  function libellePosition(n) {
    if (!tirage) return "";
    if (mode === 1) { const q = questionCourante(); return q ? q.question : ""; }
    if (mode === 10) {
      const E = tirage.etendu || {};
      if (n >= 9) return (E.cle && E.cle.libelle) || "la clé d'intégration";
      const niv = (E.niveaux || [])[Math.floor(n / 3)] || {};
      const plan = (E.plans || [])[n % 3] || {};
      return [niv.temps, plan.libelle].filter(Boolean).join(" · ");
    }
    if (estCroix()) {
      const p = (positionsActives() || []).find((x) => x.numero === n + 1);
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
    document.body.classList.toggle("en-tirage", mode === 3 || mode === 10 || estCroix());
    document.body.classList.remove("a-commence");
    reinitialiserVues();
    slotsBox.classList.toggle("etendu", mode === 10);
    // le nombre de colonnes de la grille : les cartes occupent la largeur
    // disponible au lieu d'une largeur fixe (--n est lu par le CSS)
    slotsBox.style.setProperty("--n", mode === 1 ? 1 : mode === 10 ? 3 : mode);
    // mode 1 : pas d'emplacement vide avant le choix — il apparaît rempli
    slotsBox.classList.toggle("sans-vide", mode === 1);

    slotsBox.classList.toggle("croix", estCroix());
    slotsBox.classList.toggle("diamant", mode === 5);
    if (estCroix()) {
      const C = croixCourante() || (tirage && tirage.croix) || {};
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
    // ?croix=… choisit la croix lue — SEULEMENT pour les croix à dix cartes.
    // Le Diamant (mode 5) n'a qu'une forme : lui envoyer une croix faisait
    // refuser le 2e tirage (« croix inconnue » pour « diamant ») et la table
    // restait vide après un mélange (bogue 2026-11-16).
    const croixReq = mode === 11 ? `&croix=${encodeURIComponent(croixActive)}` : "";
    const r = await fetch(`api/tirage?mode=${mode}${suffixe}${croixReq}`);
    if (!r.ok) throw new Error("tirage refusé");
    tirage = await r.json();
    dernierTotal = tirage.total_jeu;
    choisies = [];
    ordreRevelation = [];
    // la grille choisie avant de piger survit au mélange (même tirage ouvert)
    if (!(tirage.grilles || []).some((g) => g.id === grilleActive)) {
      grilleActive = tirage.grille || "causale_3";
    }
    if (mode === 11 && tirage.grille) croixActive = tirage.grille;
    if (mode === 1) {
      const ids = (tirage.positions_def || []).map((p) => p.id);
      if (!ids.includes(questionActive)) questionActive = tirage.question_par_defaut || ids[0] || null;
    }
    afficherPedagogie();
    construireSlots();
    // les libellés des cases suivent la grille choisie, pas celle du serveur
    if (mode === 3) {
      const positions = positionsActives();
      slotsBox.querySelectorAll(".slot").forEach((slot, i) => {
        const lib = slot.querySelector(".libelle");
        if (lib && positions[i]) { lib.textContent = positions[i].libelle; lib.dataset.pos = positions[i].id; }
      });
    }
    construireBascule();
    majGrilleAvant();
    majBarre();
    majCompteur();
    return tirage;
  }

  async function charger() {
    try {
      const t = await demanderTirage();
      // les cartes de la donne sont connues d'avance : leurs vignettes se
      // chargent dès maintenant, chaque carte pigée s'affiche sans attendre
      (t.cartes || []).forEach((c) => { if (c.image_mini) new Image().src = c.image_mini; });
      entrerTable();   // AVANT le paquet : la table fixe la taille de ses cartes
      construireEventail(t.total_jeu);
      synchroniserEntete(t.total_jeu);
      majBoutonMelange();
    } catch (e) {
      // jamais une table vide en silence : on le dit, et on offre de réessayer
      construireEventail(79);
      const c = document.getElementById("compteur-tirage");
      c.innerHTML = `<span class="ct-geste">Le jeu n'a pas répondu. Touche « Réessayer ».</span>`;
      c.classList.remove("invisibles");
      replierBtn.textContent = "Réessayer";
      replierBtn.classList.toggle("invisible", !tirageChoisi);
    }
  }

  function synchroniserEntete(total) {
    surtitre.textContent = "Le jeu des " + total;
    piedTexte.textContent = total + " cartes · aucune prédiction";
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
    if (!tirage || carteEnPlace || melangeEnCours || choisies.length >= tirage.cartes.length) return;
    carteEnPlace = true;

    document.body.classList.add("a-commence");

    const carte = tirage.cartes[choisies.length];
    choisies.push(carte);
    majBoutonMelange();
    slotsBox.classList.remove("sans-vide");

    if (carte.image) {
      el.querySelector(".face").innerHTML =
        `<img src="${carte.image_mini || carte.image}" alt="${carte.nom}" draggable="false">`;
    }

    // 1 · la carte quitte la ligne et VOLE jusqu'à son emplacement (FLIP :
    // on note où elle est dans le paquet, on la pose dans sa case, puis on
    // la fait partir de son ancienne place — 2026-11-16, « faire monter la
    // carte pour qu'elle se place »)
    const depart = el.getBoundingClientRect();
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
    const vol = faireVoler(el, depart);
    // la première carte efface les choix du départ : le plan gagne la place
    if (choisies.length === 1) requestAnimationFrame(ajusterPlan);

    if (mode === 3 || mode === 10 || estCroix()) {
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
        // tout est posé : le paquet s'en va, le tirage reprend sa place
        // et l'invite à révéler s'affiche sous lui
        setTimeout(() => { inviteRevelation(); ajusterPlan(); }, vol);
        setTimeout(ajusterPlan, vol + 350);   // une fois le paquet parti
      }
    } else {
      // 2b · tirage à une carte : elle vole, se retourne, puis la lecture ;
      // le paquet n'a plus rien à offrir, il s'efface
      el.title = "Afficher en plein écran";
      setTimeout(() => eventail.classList.add("estompe"), vol);
      setTimeout(() => el.classList.add("retournee"), vol + 60);
      setTimeout(() => {
        carteEnPlace = false;
        sortirTable();
        montrerLectureJour(carte);
      }, vol + 820);
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
    // l'image de lecture (récit, plein écran) se charge dès la révélation
    if (el._carte.image) new Image().src = imageLecture(el._carte);
    setTimeout(() => {
      if (nomSlot) nomSlot.textContent = el._carte.nom;
      const libelleSlot = el.closest(".slot").querySelector(".libelle");
      if (libelleSlot && el._carte.type === "hors_cycle") {
        libelleSlot.textContent = "le regard";
        libelleSlot.dataset.hors = "1";
      }
      ajouterBlocLecture(el._carte, pos, i);
      verifierRangee(i);
      carteRevelation = false;
      cartesRevelees++;
      inviteRevelation();
      if (cartesRevelees === tirage.cartes.length) {
        sortirTable();
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
    /* Sur téléphone, le résumé est coupé à trois lignes (CSS) pour que le
       plan et le paquet tiennent dans l'écran ; « Lire la suite » le
       déplie sur place. Le bouton n'apparaît que si le texte déborde. */
    const res = boite.querySelector(".ped-resume");
    if (res) {
      const suite = document.createElement("button");
      suite.type = "button";
      suite.className = "ped-suite";
      suite.textContent = "Lire la suite";
      suite.hidden = true;
      suite.addEventListener("click", () => { res.classList.add("deplie"); suite.hidden = true; });
      res.after(suite);
      // mesure immédiate (lire scrollHeight force la mise en page) — un
      // requestAnimationFrame n'arrive pas dans un onglet en arrière-plan
      suite.hidden = res.scrollHeight <= res.clientHeight + 2;
    }
    // les grilles de relecture ne se choisissent plus ici : un seul endroit,
    // « Relire autrement », sous la lecture (refonte 2026-11-16)
  }

  // ── La barre du tirage : ‹ Tirages · le nom · la méthode ────────────

  const barreTirage = document.getElementById("barre-tirage");
  const pedZone = document.getElementById("ped-zone");

  function majBarre() {
    if (!tirageChoisi) return;
    document.getElementById("barre-nom").textContent = tirageChoisi.nom;
    const g = (mode === 3 && tirage && tirage.grilles) ? grilleCourante() : null;
    document.getElementById("barre-sous").textContent =
      g ? g.nom : `${tirageChoisi.n} carte${tirageChoisi.n > 1 ? "s" : ""}`;
  }

  // ⓘ : la méthode complète, à la demande — même après le début du tirage
  document.getElementById("barre-info").addEventListener("click", () => {
    const ouvrir = !document.body.classList.contains("ped-ouverte");
    document.body.classList.toggle("ped-ouverte", ouvrir);
    document.getElementById("barre-info").setAttribute("aria-expanded", String(ouvrir));
    const det = pedZone.querySelector(".ped-complet");
    if (det) det.open = ouvrir;
    if (ouvrir) pedZone.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  // ── La bascule : le seul choix avant de piger ───────────────────────
  // Trois cartes : au hasard (mélange) ou au choix (79 faces visibles) — la
  // même lecture au bout. La croix : celtique ou Osho, une seule donne,
  // changeable avant comme après le tirage, sans retirer les cartes.

  const bascule = document.getElementById("bascule");

  function construireBascule() {
    const options = [];
    let genre = "";
    if (tirageChoisi && tirageChoisi.pige && (mode === 3 || mode === 0)) {
      genre = "pige";
      // sans sous-titre (Martin, 2026-11-16 : « mélange honnête », pas très
      // marketing) — les deux libellés se suffisent
      options.push({ id: "hasard", nom: "Au hasard", sous: "", actif: mode === 3 });
      options.push({ id: "choix", nom: "Je choisis", sous: "", actif: mode === 0 });
    } else if (tirageChoisi && tirageChoisi.lectures && mode === 11) {
      genre = "lecture";
      tirageChoisi.lectures.forEach((l) =>
        options.push({ id: l.id, nom: l.nom, sous: l.sous, actif: l.id === croixActive }));
    }
    bascule.innerHTML = "";
    bascule.dataset.genre = genre;
    bascule.setAttribute("aria-label", genre === "pige" ? "Comment piger" : "Quelle lecture");
    bascule.classList.toggle("invisibles", !options.length);
    options.forEach((o) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "bascule-option" + (o.actif ? " actif" : "");
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(o.actif));
      b.innerHTML = o.sous ? `${o.nom}<small>${o.sous}</small>` : o.nom;
      b.addEventListener("click", () => {
        if (genre === "lecture") changerCroix(o.id);
        else if (o.id === "choix" && mode !== 0) passerAuChoix();
        else if (o.id === "hasard" && mode !== 3) passerAuHasard();
      });
      bascule.appendChild(b);
    });
  }

  function changerCroix(id) {
    if (!tirage || mode !== 11 || id === croixActive) return;
    croixActive = id;
    construireBascule();
    afficherPedagogie();
    majCompteur();
    if (ordreRevelation.length) rendreLecture();
    document.getElementById("detail-position").hidden = true;
  }

  async function passerAuChoix() {
    viderTable();
    mode = 0;
    construireBascule();
    await demarrerChoix();
  }

  function passerAuHasard() {
    document.getElementById("choix").classList.add("invisibles");
    eventail.classList.remove("invisibles");
    pedZone.classList.remove("invisible");
    mode = 3;
    replier();
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
    const invite = mode === 5
      ? "Les cinq cartes sont posées, face cachée. Révèle-les dans l'ordre de la croix : l'issue, les deux influences, ce qu'il faut pour dénouer, puis la résolution."
      : mode === 11
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

  /* L'ORDRE DU TIRAGE, pas celui des révélations (Martin, 2026-11-16 : « les
     textes s'affichent dans l'ordre dans lequel les cartes ont été
     dévoilées ») : chaque bloc porte son rang (data-ordre = position dans la
     donne) et s'insère devant le premier bloc de rang supérieur. */
  function insererDansLOrdre(el, ordre) {
    el.dataset.ordre = String(ordre);
    const apres = Array.from(lecture.children)
      .find((x) => x.dataset.ordre !== undefined && Number(x.dataset.ordre) > ordre);
    if (apres) lecture.insertBefore(el, apres);
    else lecture.appendChild(el);
  }

  function ajouterBlocLecture(carte, pos, i) {
    const d = donneesBloc(carte, pos);
    if (!d) return;
    const bloc = document.createElement("div");
    bloc.className = "bloc-lecture";
    bloc.innerHTML =
      `<p class="bloc-nom">${carte.nom} <span>— ${d.libelle}</span></p>` +
      `<p class="bloc-texte">${d.texte}</p>` +
      appointHTML(d.appoint);
    insererDansLOrdre(bloc, i);
    requestAnimationFrame(() => bloc.classList.add("visible"));
  }

  // le texte d'une carte à sa position, selon le mode et la grille active
  function donneesBloc(carte, pos) {
    let r = {};
    let libelle = (pos && pos.libelle) || "";
    if (estCroix()) {
      const def = (positionsActives() || []).find((p) => p.numero === pos.numero) || {};
      // la croix lue : l'active pour les croix à dix cartes, « diamant » pour
      // le Diamant (croixCourante() renvoie la bonne définition dans les deux cas)
      const idCroix = (croixCourante() || {}).id || croixActive;
      const cell = ((tirage.croix_textes || {})[idCroix] || {})[carte.id] || {};
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
    // la synthèse d'un temps se range juste après ses trois cartes
    insererDansLOrdre(bloc, niveauIndex * 3 + 2.5);
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
    if (mode === 10 || estCroix()) {
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
      if (pos) ajouterBlocLecture(carte, pos, i);
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

  // ── « Relire autrement » — après la lecture, un seul tiroir ─────────
  // Avant : 4 pilules dorées AU-DESSUS des cartes, en concurrence avec les
  // modes et les vues. Les relectures viennent après la lecture, pas avant.

  const relire = document.getElementById("relire");
  const feuille = document.getElementById("feuille-relire");

  function construireGrilles() {
    if (mode === 1) {
      const lue = tirage && lecture.querySelector(".question-posee");
      relire.classList.toggle("invisibles", !lue);
      if (!lue) return;
      document.getElementById("relire-titre").textContent = "Poser une autre question";
      document.getElementById("relire-sous").textContent = "à la même carte, sans la retirer";
      return;
    }
    const montrer = mode === 3 && tirage && (tirage.grilles || []).length > 1 &&
      cartesRevelees === tirage.cartes.length;
    relire.classList.toggle("invisibles", !montrer);
    if (!montrer) return;
    document.getElementById("relire-titre").textContent = "Relire autrement";
    const g = grilleCourante();
    document.getElementById("relire-sous").textContent =
      g ? `Grille actuelle : ${g.nom}` : "";
  }

  /* La grille AVANT de piger (Martin, 2026-11-16 : « que toutes les
     possibilités s'offrent dès qu'on ouvre le tirage à trois cartes ») — en
     tarot, la question se choisit avant de tirer : chaque grille donne un
     autre sens aux trois positions. Une seule ligne (Hick), les quatre
     grilles dans le même tiroir que « Relire autrement ». Visible dans Trois
     cartes au hasard, tant qu'aucune carte n'est pigée (CSS : a-commence). */
  const grilleAvant = document.getElementById("grille-avant");

  function majGrilleAvant() {
    const enQuestion = mode === 1 && tirage && (tirage.positions_def || []).length > 1;
    const montrer = enQuestion || (mode === 3 && tirage && (tirage.grilles || []).length > 1 &&
      tirageChoisi && tirageChoisi.pige);
    grilleAvant.classList.toggle("invisibles", !montrer);
    if (!montrer) return;
    if (enQuestion) {
      const q = questionCourante();
      document.getElementById("grille-avant-titre").textContent = "Ta question";
      document.getElementById("grille-avant-sous").textContent = q ? q.question : "";
      return;
    }
    const g = grilleCourante();
    document.getElementById("grille-avant-titre").textContent = "Grille de lecture";
    document.getElementById("grille-avant-sous").textContent = g ? g.nom : "";
  }

  let ouvreurFeuille = null;

  function ouvrirFeuille(e) {
    const avant = !!(e && e.currentTarget === grilleAvant);
    ouvreurFeuille = avant ? grilleAvant : relire;
    document.getElementById("feuille-titre").textContent =
      avant ? "Choisir la grille de lecture" : "Relire la même donne";
    feuille.querySelector(".feuille-quoi").textContent = avant
      ? "Chaque grille pose une autre question aux trois positions. Tu pourras relire la donne sous les autres ensuite."
      : "Les cartes ne bougent pas ; seule la question change.";
    const boite = document.getElementById("feuille-options");
    boite.innerHTML = "";
    if (mode === 1) {
      // Une question : les cinq questions, dans le même tiroir
      document.getElementById("feuille-titre").textContent = "Choisir ta question";
      feuille.querySelector(".feuille-quoi").textContent =
        "La même carte répond autrement selon la question qu'on lui pose.";
      (tirage.positions_def || []).forEach((q) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "feuille-option" + (q.id === questionActive ? " actif" : "");
        b.setAttribute("aria-pressed", String(q.id === questionActive));
        b.textContent = q.question;
        b.addEventListener("click", () => { fermerFeuille(); changerQuestion(q.id); });
        boite.appendChild(b);
      });
      feuille.hidden = false;
      const actifQ = boite.querySelector(".actif") || boite.firstChild;
      if (actifQ) actifQ.focus({ preventScroll: true });
      return;
    }
    (tirage.grilles || []).forEach((g) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "feuille-option" + (g.id === grilleActive ? " actif" : "");
      b.setAttribute("aria-pressed", String(g.id === grilleActive));
      b.innerHTML = `${g.nom}<small>${g.id === "causale_3"
        ? "ce que tu amènes, ce qui se joue, ce que tu peux essayer"
        : (g.sous_titre || "")}</small>`;
      b.addEventListener("click", () => { fermerFeuille(); changerGrille(g.id); });
      boite.appendChild(b);
    });
    feuille.hidden = false;
    const actif = boite.querySelector(".actif") || boite.firstChild;
    if (actif) actif.focus({ preventScroll: true });
  }

  function fermerFeuille() {
    if (feuille.hidden) return;
    feuille.hidden = true;
    if (ouvreurFeuille) ouvreurFeuille.focus({ preventScroll: true });
  }

  relire.addEventListener("click", ouvrirFeuille);
  grilleAvant.addEventListener("click", ouvrirFeuille);
  feuille.addEventListener("click", (e) => { if (e.target === feuille) fermerFeuille(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") fermerFeuille(); });

  // Une question : changer de question relit la MÊME carte (les cinq
  // réponses sont déjà là, résolues par le serveur)
  function changerQuestion(id) {
    if (!tirage || mode !== 1 || id === questionActive) return;
    questionActive = id;
    majGrilleAvant();
    majCompteur();
    const carte = choisies[0];
    if (carte && lecture.querySelector(".question-posee")) {
      montrerLectureJour(carte);
      const q = lecture.querySelector(".question-posee");
      if (q) q.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function changerGrille(id) {
    if (!tirage || tirage.mode !== 3 || id === grilleActive) return;
    grilleActive = id;
    construireGrilles();
    majGrilleAvant();
    majBarre();
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

  /* Une question : la carte répond à LA question choisie (le champ de la
     fiche que cette question lit, résolu par le serveur), puis deux questions
     de la fiche pour prolonger, puis le geste — sauf si la question était
     « comment traverser », dont la réponse porte déjà le geste. */
  function montrerLectureJour(carte) {
    const q = questionCourante();
    const r = ((tirage && tirage.questions_textes) || {})[questionActive] || {};
    const texte = r.texte || (carte.type === "hors_cycle" ? carte.regard : "") ||
      (carte.positions || {}).jour || carte.lumiere || "";
    const questions = (carte.questions || []).slice(0, 2)
      .map((x) => `<li>${x}</li>`).join("");
    const geste = carte.micro_geste && !(r.appoint && r.appoint.genre === "geste");
    lecture.innerHTML =
      `<p class="nom-carte">${carte.nom}</p>` +
      `<p class="meta-carte">${metaDe(carte)}</p>` +
      (q ? `<p class="question-posee">${q.question}</p>` : "") +
      `<p class="texte-carte">${texte}</p>` +
      appointHTML(r.appoint) +
      (questions
        ? `<p class="surtitre-bloc">Prolonger</p><ul class="ecouter">${questions}</ul>`
        : "") +
      (geste
        ? `<p class="surtitre-bloc">Faire</p><p class="faire">${carte.micro_geste}</p>`
        : "");
    construireGrilles();
    lecture.classList.remove("invisibles");
    requestAnimationFrame(() => lecture.classList.add("visible"));
  }

  // ── Plein écran — la vignette s'agrandit, la fiche complète à côté ──

  function ouvrirPlein(carte) {
    if (!carte) return;
    // la vignette (déjà en cache : elle est dans la case) s'affiche tout de
    // suite ; la face entière prend le relais une fois décodée
    const img = carte.image_mini || carte.image || DOS_DEFAUT;
    const grande = carte.image ? imageLecture(carte) : null;
    if (grande && grande !== img) {
      const id = carte.id;
      imagePrete(grande, 8000).then(() => { if (pleinImg.dataset.carte === id) pleinImg.src = grande; });
    }
    const q = (carte.questions || []).map((x) => `<li>${x}</li>`).join("");
    const ombre = carte.ombre
      ? `<p class="pt-titre">Ombre — ${carte.ombre.mode}</p>` +
        `<p>${carte.ombre.texte}</p>` +
        `<p class="pt-issue">${carte.ombre.issue}</p>`
      : "";
    pleinImg.dataset.carte = carte.id;
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
    zoomPlein.reinitialiser();
    plein.classList.remove("invisible");
    plein.setAttribute("aria-hidden", "false");
    document.body.classList.add("fige-scroll", "plein-ouvert");
  }

  function fermerPlein() {
    plein.classList.add("invisible");
    plein.setAttribute("aria-hidden", "true");
    document.body.classList.remove("fige-scroll", "plein-ouvert");
  }

  /* Un pincement se termine par un click, qui refermait la carte plein écran.
     On retient le dernier geste à deux doigts et on ignore ce qui suit. */
  let dernierPincement = 0;
  const noterPincement = (e) => { if (e.touches && e.touches.length > 1) dernierPincement = Date.now(); };
  document.addEventListener("touchstart", noterPincement, { passive: true });
  document.addEventListener("touchmove", noterPincement, { passive: true });
  document.addEventListener("gesturestart", () => { dernierPincement = Date.now(); }, { passive: true });
  const pincementRecent = () => Date.now() - dernierPincement < 800;

  /* Seuls le ✕ et le fond (hors de la carte et du texte) ferment le plein
     écran. Toucher l'IMAGE ne ferme plus (Martin, 2026-11-16 : ça entrait en
     conflit avec le zoom) — même règle que les cartes du jour de Ta Trame.
     Le ✕ ferme toujours, même carte zoomée. */
  plein.addEventListener("click", (e) => {
    if (e.target.closest(".plein-fermer")) { fermerPlein(); return; }
    if (e.target.closest(".plein-img, .plein-texte")) return;
    if (pincementRecent() || zoomPlein.occupe()) return;
    fermerPlein();
  });
  pleinTexte.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") fermerPlein();
  });

  // ── Replier ─────────────────────────────────────────────────────────

  function replier() {
    viderTable();
    charger();
  }

  // la table remise à nu : aucune carte, aucune lecture (sans recharger)
  function viderTable() {
    fermerPlein();
    fermerFeuille();
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
    document.body.classList.remove("en-tirage", "a-commence", "ped-ouverte");
    document.getElementById("barre-info").setAttribute("aria-expanded", "false");
    document.getElementById("detail-position").hidden = true;
    reinitialiserVues();
    relire.classList.add("invisibles");
    grilleAvant.classList.add("invisibles");
    sortirTable();
    slotsBox.style.removeProperty("--case");
    dernierCase = 0;
  }

  // ── Ouvrir un tirage du catalogue, revenir au catalogue ─────────────

  function construireCatalogue() {
    const boite = document.getElementById("cat-etageres");
    boite.innerHTML = CATALOGUE.map((e) => `
      <div class="etagere">
        <p class="etagere-titre">${e.etagere}</p>
        ${e.items.map((t) => `
          <button type="button" class="tuile${t.vedette ? " vedette" : ""}" data-tirage="${t.id}">
            <svg class="tuile-schema" viewBox="0 0 58 58" aria-hidden="true">${SCHEMAS[t.schema]}</svg>
            <span class="tuile-corps">
              <span class="tuile-nom">${t.nom}</span>
              <span class="tuile-pour">${t.pour}</span>
              <span class="tuile-meta">${t.n} carte${t.n > 1 ? "s" : ""}${t.lectures ? ` · ${t.lectures.length} lectures` : ""}</span>
            </span>
            <span class="tuile-chevron" aria-hidden="true">›</span>
          </button>`).join("")}
      </div>`).join("");
    boite.addEventListener("click", (e) => {
      const b = e.target.closest(".tuile");
      if (b) ouvrirTirage(TOUS_TIRAGES.find((t) => t.id === b.dataset.tirage));
    });
  }

  function ouvrirTirage(t) {
    if (!t) return;
    tirageChoisi = t;
    grilleActive = "causale_3";   // chaque ouverture repart de la grille d'origine
    mode = t.mode;
    if (t.croix) croixActive = t.croix;
    else if (t.lectures && !t.lectures.some((l) => l.id === croixActive)) croixActive = t.lectures[0].id;
    document.body.classList.remove("accueil");
    barreTirage.hidden = false;
    document.getElementById("choix").classList.add("invisibles");
    eventail.classList.remove("invisibles");
    pedZone.classList.remove("invisible");
    majBarre();
    construireBascule();
    window.scrollTo(0, 0);
    replier();
  }

  function retourCatalogue() {
    viderTable();
    document.getElementById("choix").classList.add("invisibles");
    eventail.innerHTML = "";
    tirageChoisi = null;
    barreTirage.hidden = true;
    bascule.classList.add("invisibles");
    document.getElementById("ped-contenu").innerHTML = "";
    document.body.classList.add("accueil");
    window.scrollTo(0, 0);
    const premier = document.querySelector(".tuile");
    if (premier) premier.focus({ preventScroll: true });
  }

  document.getElementById("retour-tirages").addEventListener("click", retourCatalogue);

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
    pedZone.classList.add("invisible");
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
    const imageDe = (id) => { const c = choixEtat.jeu.find((x) => x.id === id) || {}; return c.image_mini || c.image || ""; };

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
        b.innerHTML = `<img src="${c.image_mini || c.image}" alt="${c.nom}" loading="lazy" decoding="async" draggable="false"><span class="carte-choix-nom">${c.nom}</span>`;
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
    pedZone.classList.remove("invisible");
    mode = 3;
    tirage = d;
    choisies = [];
    ordreRevelation = [];
    rangeesAnnoncees = new Set();
    cartesRevelees = 0;
    if (!(d.grilles || []).some((g) => g.id === grilleActive)) grilleActive = d.grille || "causale_3";
    afficherPedagogie();
    construireSlots();
    majBarre();
    slotsBox.classList.remove("invisibles");
    placerChoisies();
    // les cartes sont choisies : on passe à la lecture (même état qu'après
    // un tirage au hasard — la bascule « comment piger » se retire).
    // Après placerChoisies, qui remet la table à zéro.
    document.body.classList.add("a-commence");
    lecture.classList.remove("invisibles");
    entrerTable();
    inviteRevelation();
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
          `<img src="${carte.image_mini || carte.image}" alt="${carte.nom}" draggable="false">`;
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
    if (!tirage || (mode !== 3 && mode !== 10 && !estCroix())) return;
    vuesBarre.querySelector('[data-vue="liens"]').classList.toggle("invisible", estCroix());
    vuesBarre.classList.remove("invisibles");
    construireGrilles();   // « Relire autrement » : seulement une fois tout lu
    const memo = lireVueMemo();
    afficherVue(memo && !(memo === "liens" && estCroix()) ? memo : "ensemble");
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
        `<img src="${p.carte.image_mini || p.carte.image || DOS_DEFAUT}" data-grande="${p.carte.image ? imageLecture(p.carte) : ""}" alt="${p.carte.nom}" draggable="false"></button>` +
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
      // la vignette s'affiche d'emblée ; l'image de lecture la remplace
      // dès qu'elle est prête (préchargée à la révélation, souvent déjà là)
      const im = vueRecit.querySelector(".recit-image img");
      const grande = im.dataset.grande;
      if (grande) imagePrete(grande, 8000).then(() => { if (im.isConnected) im.src = grande; });
      // et la page suivante se prépare pendant qu'on lit celle-ci
      const suivante = pages[recitIndex + 1];
      if (suivante && suivante.carte && suivante.carte.image) new Image().src = imageLecture(suivante.carte);
      vueRecit.querySelector(".recit-image").addEventListener("click", () => ouvrirPlein(p.carte));
    }
    vueRecit.querySelector(".recit-prec").addEventListener("click", () => { recitIndex--; dessinerRecit(); hautDuRecit(); });
    vueRecit.querySelector(".recit-suiv").addEventListener("click", () => { recitIndex++; dessinerRecit(); hautDuRecit(); });
  }

  /* Chaque nouvelle page du récit remonte en haut, la carte ENTIÈRE sous la
     barre (Martin, 2026-11-16 : sur téléphone, on arrivait au milieu de la
     page suivante, le bouton « Suivante » étant tout en bas). On vise le haut
     des onglets Récit · Ensemble · Liens : on sait toujours où l'on est. */
  function hautDuRecit() {
    const barre = document.getElementById("barre-tirage");
    const marge = (barre && !barre.hidden ? barre.offsetHeight : 0) + 8;
    const cible = vuesBarre.getBoundingClientRect().top + window.scrollY - marge;
    const reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: Math.max(0, cible), behavior: reduit ? "auto" : "smooth" });
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
    hautDuRecit();
  });

  function vignettes(cartes, libelles) {
    return `<div class="liens-cartes">` + cartes.map((c, k) =>
      `<button type="button" class="liens-carte" data-id="${c.id}" aria-label="${c.nom}">` +
      `<img src="${c.image_mini || c.image || DOS_DEFAUT}" alt="" draggable="false">` +
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

  /* ══ LA TABLE DE JEU (Martin, 2026-11-16 : « il faut un vrai mode où on
     voit toujours les cartes dans lesquelles on peut tirer… ou ça dézoome
     pour qu'on voit tout ») ═══════════════════════════════════════════
     Pendant tout le tirage, l'écran est une table FIXE, sans défilement :
     la barre en haut, le tirage au centre, le paquet en bas. Le tirage est
     AJUSTÉ à l'espace libre (on cherche la plus grande case qui fait tout
     tenir) : petit tant que les choix du départ sont là, il grandit quand
     ils s'effacent, puis quand le paquet s'en va. Une fois tout révélé, la
     table se replie et la lecture se lit en défilant, sous le tirage.
     Dans Ta Trame, on prévient la page hôte pour qu'elle cale le cadre en
     haut de l'écran (fini le défilement dans le défilement). */
  let tableActive = false;

  function entrerTable() {
    if (!tirageChoisi || mode === 0) return;
    tableActive = true;
    document.body.classList.add("table");
    window.scrollTo(0, 0);
    try { if (window.parent !== window) window.parent.postMessage({ tarot: "table" }, "*"); } catch (e) { /* hors cadre */ }
    requestAnimationFrame(ajusterPlan);
    setTimeout(ajusterPlan, 120);   // après le chargement des polices / du paquet
  }

  function sortirTable() {
    if (!tableActive) return;
    tableActive = false;
    hauteurPlan = 0;
    document.body.classList.remove("table");
  }

  // la plus grande case qui fait tenir tout le tirage dans la zone du plan
  function ajusterPlan() {
    if (!tableActive || !slotsBox.children.length) return;
    // une carte en vol (transform depuis le paquet) fausse la mesure du
    // débordement : on attend qu'elle soit posée
    const attente = volJusqua - Date.now();
    if (attente > 0) { clearTimeout(ajusterPlan._t); ajusterPlan._t = setTimeout(ajusterPlan, attente + 20); return; }
    // la transition de largeur coupée AVANT toute mesure : sinon le
    // navigateur mesure la largeur de départ de l'animation
    slotsBox.style.transition = "none";
    slotsBox.style.removeProperty("--case");
    const max = parseFloat(getComputedStyle(slotsBox).getPropertyValue("--case")) || 104;
    // mesure contenu calé en HAUT : centré, il déborde des deux côtés et
    // scrollHeight ne voit que la moitié du débordement
    slotsBox.style.alignContent = "start";
    // les boîtes de MISE EN PAGE des cases (offsetTop/Height ignorent les
    // transform) : une carte en vol ou soulevée ne fausse plus la mesure
    // la marge latérale (padding, 18 px) n'est pas de l'espace utilisable
    const marge = parseFloat(getComputedStyle(slotsBox).paddingLeft) || 0;
    const tient = () => {
      let bas = 0, droite = 0, gauche = Infinity;
      for (const c of slotsBox.children) {
        if (!c.offsetWidth && !c.offsetHeight) continue;   // élément masqué
        bas = Math.max(bas, c.offsetTop + c.offsetHeight);
        droite = Math.max(droite, c.offsetLeft + c.offsetWidth);
        gauche = Math.min(gauche, c.offsetLeft);
      }
      return bas <= slotsBox.clientHeight + 1 &&
             droite <= slotsBox.clientWidth - marge + 1 && gauche >= marge - 1;
    };
    let bas = 22, haut = max, retenu = max;
    slotsBox.style.setProperty("--case", haut + "px");
    if (!tient()) {
      for (let k = 0; k < 9; k++) {
        const mi = (bas + haut) / 2;
        slotsBox.style.setProperty("--case", mi + "px");
        if (tient()) bas = mi; else haut = mi;
      }
      retenu = Math.floor(bas);
    }
    slotsBox.style.alignContent = "";
    // on repart de la taille précédente pour que le changement s'anime
    slotsBox.style.setProperty("--case", (dernierCase || retenu) + "px");
    slotsBox.getBoundingClientRect();
    slotsBox.style.transition = "";
    slotsBox.style.setProperty("--case", retenu + "px");
    dernierCase = retenu;
  }
  let dernierCase = 0;
  let volJusqua = 0;
  // la zone du plan change de taille (résumé déplié, choix effacés, paquet
  // parti, écran tourné…) : on réajuste. Sa hauteur ne dépend pas de --case
  // (flex 1, débordement caché) : aucune boucle possible.
  let hauteurPlan = 0;
  new ResizeObserver(() => {
    const h = slotsBox.clientHeight;
    if (tableActive && Math.abs(h - hauteurPlan) > 2) { hauteurPlan = h; ajusterPlan(); }
  }).observe(slotsBox);
  window.addEventListener("resize", () => { if (tableActive) ajusterPlan(); });

  // l'invite pendant la révélation (la lecture, elle, attend la fin)
  function inviteRevelation() {
    if (!tableActive || !tirage) return;
    const total = tirage.cartes.length;
    // seulement quand TOUTES les cartes sont posées (pige ou « Je choisis »)
    if (slotsBox.querySelectorAll(".carte.choisie").length < total) return;
    const reste = total - cartesRevelees;
    const c = document.getElementById("compteur-tirage");
    if (!tableActive || reste <= 0) { c.classList.add("invisibles"); return; }
    c.innerHTML = `<span class="ct-nb">${cartesRevelees} / ${total} révélées</span>` +
      `<span class="ct-geste">Touche chaque carte pour la retourner</span>`;
    c.classList.remove("invisibles");
  }

  // le vol FLIP : renvoie sa durée (0 sans mouvement réduit)
  function faireVoler(el, depart) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches || !depart.width) return 0;
    const arrivee = el.getBoundingClientRect();
    if (!arrivee.width) return 0;
    const dx = depart.left - arrivee.left, dy = depart.top - arrivee.top;
    const sx = depart.width / arrivee.width, sy = depart.height / arrivee.height;
    el.style.transformOrigin = "0 0";
    el.style.transition = "none";
    el.style.transform = `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`;
    el.style.zIndex = "50";
    el.getBoundingClientRect();   // force la position de départ
    volJusqua = Date.now() + 580;
    el.style.transition = "transform .55s cubic-bezier(.2,.8,.2,1)";
    el.style.transform = "none";
    setTimeout(() => { el.style.zIndex = ""; el.style.transition = ""; el.style.transform = ""; el.style.transformOrigin = ""; }, 600);
    return 560;
  }

  /* MÉLANGER (Martin, 2026-11-16 : « il faut un bouton pour mélanger les
     cartes »). Avant la première carte : le paquet se rassemble au centre,
     puis se redéplie sur un nouveau mélange (nouvelle graine). Après une
     carte pigée, le même bouton recommence le tirage. Absent du tirage au
     choix (aucun hasard) et de l'accueil. */
  function majBoutonMelange() {
    const montrer = !!tirageChoisi && mode !== 0 && !!tirage;
    replierBtn.classList.toggle("invisible", !montrer);
    replierBtn.textContent = choisies.length ? "Recommencer le tirage" : "Mélanger les cartes";
  }

  function melanger() {
    // une graine dans l'adresse rejouerait le même mélange : on l'oublie
    const p = new URLSearchParams(location.search);
    if (p.has("graine")) {
      p.delete("graine"); p.delete("mode");
      history.replaceState(null, "", location.pathname + (p.toString() ? "?" + p : ""));
    }
    const ligne = eventail.querySelector(".ligne");
    const reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (choisies.length || !ligne || reduit) { replier(); return; }
    // le tirage ouvert au départ : si on le quitte pendant l'animation, le
    // mélange ne recharge rien derrière (course vue à l'audit 2026-11-16)
    const ouvert = tirageChoisi;
    melangeEnCours = true;
    jouerMelange(ligne).then(() => {
      melangeEnCours = false;
      if (tirageChoisi === ouvert) replier();
    });
  }

  /* L'animation du mélange (Martin, 2026-11-16 : « une petite animation des
     cartes qui se mélangent ») — un mélange à l'américaine, sur les cartes
     déjà en place : le ruban se rassemble en un paquet, se coupe en deux tas
     qui s'écartent, puis les deux tas se réentrelacent (cartes alternées, de
     petites hauteurs différentes) ; deux fois. Ensuite seulement, le paquet
     se redéplie sur la nouvelle donne (la cascade d'entrée existante).
     ~1,1 s au total ; le mouvement part tout de suite (Doherty). */
  async function jouerMelange(ligne) {
    const attendre = (ms) => new Promise((r) => setTimeout(r, ms));
    const cartes = cartesLibres();
    const l = carteLargeur();
    const centre = (ligne.offsetWidth - l) / 2;
    const ecart = Math.min(l * 0.75, ligne.offsetWidth / 4);
    replierBtn.disabled = true;
    poserLoupe(-1);
    const deplacer = (c, x, lev, duree, courbe) => {
      c.style.transition = `left ${duree}ms ${courbe}, transform ${duree}ms ${courbe}`;
      c.style.left = x + "px";
      c.style.setProperty("--lev", lev + "px");
    };
    // 1 · le ruban se rassemble en un paquet
    cartes.forEach((c, i) => deplacer(c, centre + (i % 3) * 0.4, 0, 320, "cubic-bezier(.3,0,.8,.15)"));
    await attendre(330);
    for (let passe = 0; passe < 2; passe++) {
      // 2 · coupe : deux tas qui s'écartent, celui de droite un peu levé
      cartes.forEach((c, i) => {
        const droite = i >= cartes.length / 2;
        c.style.transitionDelay = "";
        deplacer(c, centre + (droite ? ecart : -ecart), droite ? 6 : 0, 200, "cubic-bezier(.05,.7,.1,1)");
        c.style.zIndex = String(droite ? 2 : 1);
      });
      await attendre(210);
      // 3 · les deux tas se réentrelacent : cartes alternées, hauteurs mêlées
      cartes.forEach((c, i) => {
        deplacer(c, centre + ((i * 7) % 5) - 2, (i % 2) ? 3 : 0, 230, "cubic-bezier(.3,0,.2,1)");
        c.style.zIndex = String(i % 2 ? 2 : 1);
        c.style.transitionDelay = `${(i % 10) * 4}ms`;
      });
      await attendre(280);
    }
    cartes.forEach((c) => { c.style.transitionDelay = ""; c.style.setProperty("--lev", "0px"); });
    replierBtn.disabled = false;
  }

  replierBtn.addEventListener("click", melanger);
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
    if (e.target !== dp || pincementRecent()) return;
    fermerDetail();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") fermerDetail();
  });
  window.addEventListener("resize", () => {
    if (tirageChoisi && !tirage && !carteEnPlace && mode !== 0) construireEventail(dernierTotal);
  });

  // Au chargement : l'accueil, « Que viens-tu chercher ? ».
  // ?mode=N&graine=G (relire une lecture précise) ouvre directement le
  // tirage voulu ; ?croix=croix_osho choisit la lecture de la croix, et
  // ?croix=croix_composite ouvre La croix de la relation.
  construireCatalogue();
  const params = new URLSearchParams(location.search);
  const modeUrl = params.has("graine") && params.has("mode") ? Number(params.get("mode")) : null;
  const croixUrl = params.get("croix") || "";
  if (/^croix_[a-z_]+$/.test(croixUrl)) croixActive = croixUrl;
  const entreeUrl = modeUrl === null ? null
    : modeUrl === 0 ? TOUS_TIRAGES.find((t) => t.id === "trois")
    : modeUrl === 11 ? TOUS_TIRAGES.find((t) => t.id === (croixUrl === "croix_composite" ? "relation" : "croix"))
    : TOUS_TIRAGES.find((t) => t.mode === modeUrl);
  if (entreeUrl) {
    ouvrirTirage(entreeUrl);
    if (modeUrl === 0) passerAuChoix();
  } else {
    document.body.classList.add("accueil");
  }
})();
