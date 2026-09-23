// Service worker d'Align — le cache du jour.
//
// Trois jobs : afficher un rappel push reçu, ramener au premier plan quand
// on le touche, et servir depuis le cache du téléphone ce que le déterminisme
// rend cacheable SANS mentir :
//   - les statiques sont versionnés par `?v=` (empreinte de static/, voir
//     app.py::_empreinte_statique) : un fichier = des octets immuables →
//     cache-d'abord, zéro aller-retour transatlantique ;
//   - la page (le JS/CSS vit inline dedans) : cache-d'abord + revalidation en
//     arrière-plan (stale-while-revalidate) → l'app s'ouvre instantanément,
//     la version suivante arrive pour la PROCHAINE ouverture. Un déploiement
//     se voit donc au ré-open suivant, jamais à des semaines ;
//   - le bundle du jour (/api/bundle) : RÉSEAU d'abord — c'est la donnée
//     vivante de la journée, le serveur reste la source de vérité. Le cache
//     ne parle qu'en repli (hors-ligne / réseau coupé) : il sert alors la
//     dernière journée calculée, datée d'elle-même — la page affiche la date
//     qu'elle montre, donc le repli ne ment pas, il retarde.
// Ce qui reste JAMAIS en cache : les autres /api (activité, profils,
// commentaires…), les POST — rien qui doive être frais à chaque lecture.
//
// Le pré-remplissage des caches (la page entière + les 79 miniatures de
// cartes) ne vit PAS ici mais dans la PAGE (`precharger_cache`, index.html) :
// elle seule connaît l'empreinte `?v=` du déploiement courant, et
// window.caches est accessible à la page autant qu'au worker — même stockage,
// zéro plomberie de messages.
//
// Servi à la racine (`/sw.js`, pas `/static/sw.js`) pour que sa portée couvre
// toute la page — un service worker enregistré sous /static/ ne pourrait
// contrôler que /static/, jamais l'app elle-même.
//
// ⚠️ PRISE DE CONTRÔLE IMMÉDIATE (Martin, 2026-08-27 : « sur mon iPhone, ça
// ne change rien, même sur Safari, alors que ça marche pour mon ami »).
// Par défaut, un NOUVEAU service worker reste en attente (« waiting ») tant
// que tous les onglets/l'app contrôlés par l'ANCIEN n'ont pas été fermés —
// et sur certains appareils, ce moment n'arrive jamais vraiment (l'app reste
// toujours ouverte quelque part, en arrière-plan ou suspendue). `skipWaiting()`
// + `clients.claim()` forcent CE service worker à prendre le contrôle
// sur-le-champ. La purge de `caches` ci-dessous réinitialise les trois caches
// à CHAQUE activation d'une NOUVELLE version du worker : c'est le garde-fou
// qui garantit qu'un worker périmé n'hérite jamais d'un cache périmé.
self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then((noms) => Promise.all(noms.map((n) => caches.delete(n)))),
    ])
  );
});

// ─── Les trois caches (purgés à chaque activation d'une nouvelle version) ───
const CACHE_PAGES = "tatrame-pages-v1";     // la page elle-même (SWR)
const CACHE_STATIQUE = "tatrame-statique-v1"; // ?v= — immuable, cache-d'abord
const CACHE_JOUR = "tatrame-jour-v1";       // le bundle du jour (repli hors-ligne)

// ─── Page : stale-while-revalidate ──────────────────────────────────────────
// Stockée TOUJOURS sous la clé `/` (match avec ignoreSearch) : les navigations
// arrivent avec des requêtes (`/?carte=…` des rappels push) qui ne doivent
// pas multiplier les entrées ni rater le cache.
async function page_swr(event) {
  const cache = await caches.open(CACHE_PAGES);
  const en_cache = await cache.match("/", { ignoreSearch: true });
  const frais = fetch(event.request)
    .then((reponse) => {
      if (reponse && reponse.ok) cache.put("/", reponse.clone());
      return reponse;
    })
    .catch(() => null);
  if (en_cache) return en_cache;   // instantané ; la fraîche part en arrière-plan
  return frais;                    // première visite : le réseau, simplement
}

// ─── Bundle du jour : réseau d'abord, cache en repli ────────────────────────
async function jour_reseau_dabord(event) {
  const cache = await caches.open(CACHE_JOUR);
  try {
    const reponse = await fetch(event.request);
    if (reponse.ok) cache.put(event.request, reponse.clone());
    return reponse;
  } catch (e) {
    const en_cache = await cache.match(event.request);
    if (en_cache) return en_cache;
    throw e;
  }
}

// ─── Statiques : cache-d'abord (les ?v= garantissent l'immuabilité) ─────────
async function statique_cache_dabord(event) {
  const cache = await caches.open(CACHE_STATIQUE);
  const en_cache = await cache.match(event.request);
  if (en_cache) return en_cache;
  const reponse = await fetch(event.request);
  if (reponse.ok) cache.put(event.request, reponse.clone());
  return reponse;
}

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;   // rien d'étranger

  if (url.pathname.startsWith("/api/bundle/")) {
    event.respondWith(jour_reseau_dabord(event));
    return;
  }
  if (event.request.mode === "navigate") {
    event.respondWith(page_swr(event));
    return;
  }
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(statique_cache_dabord(event));
  }
});

self.addEventListener("push", (event) => {
  let titre = "Ta Trame";
  let corps = "";
  let data = {};                          // {carte, domaine, profil} — pour le clic
  try {
    const payload = event.data ? event.data.json() : {};
    titre = payload.titre || titre;
    corps = payload.corps || "";
    data = payload;                       // on garde tout : le clic lira carte/domaine/profil
  } catch (e) {
    corps = event.data ? event.data.text() : "";
  }
  event.waitUntil(
    self.registration.showNotification(titre, {
      body: corps,
      icon: "/static/icone.svg",
      badge: "/static/icone.svg",
      data: data,                         // attaché à la notification, relu au clic
    })
  );
});

// Le clic doit ouvrir l'app DIRECTEMENT sur la carte du rappel (message du jour,
// fil du jour, à méditer). On transporte le choix dans l'URL (`/?carte=…`) : si
// une fenêtre est déjà ouverte, on la ramène au premier plan ET on lui envoie
// l'info par postMessage (une navigation d'URL ne recharge pas une PWA déjà
// vivante) ; sinon on ouvre une nouvelle fenêtre sur l'URL, que l'app lira au
// démarrage. Les deux chemins finissent au même endroit.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const d = event.notification.data || {};
  const params = new URLSearchParams();
  if (d.carte) params.set("carte", d.carte);
  if (d.domaine) params.set("domaine", d.domaine);
  if (d.profil) params.set("profil", d.profil);
  const cible = params.toString() ? `/?${params.toString()}` : "/";
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((tous) => {
      for (const fenetre of tous) {
        if ("focus" in fenetre) {
          fenetre.postMessage({ type: "rappel", carte: d.carte, domaine: d.domaine, profil: d.profil });
          return fenetre.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(cible);
    })
  );
});
