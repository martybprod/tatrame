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
