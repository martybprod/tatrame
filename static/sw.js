// Service worker d'Align — minimal, délibérément.
//
// Deux jobs seulement : afficher un rappel push reçu, et ramener au premier
// plan quand on le touche. Pas de mise en cache hors-ligne ici — Align a
// besoin du serveur pour calculer le jour, un shell hors-ligne mentirait sur
// ce qu'il peut montrer.
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
// toujours ouverte quelque part, en arrière-plan ou suspendue). Un ancien
// service worker peut alors rester actif indéfiniment, invisible, et
// contrôler CHAQUE visite de l'origine. `skipWaiting()` + `clients.claim()`
// forcent CE service worker à prendre le contrôle sur-le-champ, dès qu'une
// nouvelle version est détectée — plus besoin de fermer quoi que ce soit.
// La purge de `caches` ci-dessous est une sécurité supplémentaire : CE
// service worker n'en crée aucun, mais un ANCIEN (d'une itération
// antérieure, avant ce fichier) aurait pu en laisser — on ne prend aucun
// risque, on part toujours d'un état propre.
self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then((noms) => Promise.all(noms.map((n) => caches.delete(n)))),
    ])
  );
});

self.addEventListener("push", (event) => {
  let titre = "Ta Trame";
  let corps = "";
  try {
    const payload = event.data ? event.data.json() : {};
    titre = payload.titre || titre;
    corps = payload.corps || "";
  } catch (e) {
    corps = event.data ? event.data.text() : "";
  }
  event.waitUntil(
    self.registration.showNotification(titre, {
      body: corps,
      icon: "/static/icone.svg",
      badge: "/static/icone.svg",
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((tous) => {
      for (const fenetre of tous) {
        if ("focus" in fenetre) return fenetre.focus();
      }
      if (clients.openWindow) return clients.openWindow("/");
    })
  );
});
