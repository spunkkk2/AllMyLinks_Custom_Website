self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(clients.claim());
});

self.addEventListener("push", (event) => {
    let payload = { title: "Spunkkk", body: "New update from Spunkkk" };

    if (event.data) {
        try {
            payload = event.data.json();
        } catch (err) {
            payload.body = event.data.text();
        }
    }

    const title = payload.title || "Spunkkk";
    const options = {
        body: payload.body || "",
        icon: payload.icon || "https://ucarecdn.com/c96495e5-f0c8-4a28-bfd8-eac380d14d2e/630692742_18558533275053061_243982538138301450_n.jpg",
        badge: payload.icon || "https://ucarecdn.com/c96495e5-f0c8-4a28-bfd8-eac380d14d2e/630692742_18558533275053061_243982538138301450_n.jpg",
        data: { url: payload.url || "/" }
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    const targetUrl = (event.notification.data && event.notification.data.url) || "/";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
            for (const client of clientList) {
                if (client.url.includes(targetUrl) && "focus" in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
