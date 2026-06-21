# Spunkkk Social

A Flask-powered link-in-bio page for **Anas Badran (spunkkk)** — social links, visit tracking, and **PWA push notifications** to everyone who installs the site on their phone.

Live site: [spunkkk.com](https://spunkkk.com)

## Features

### Link-in-bio page
- Mobile-friendly landing page with animated gradient UI
- Social links with follower counts (TikTok, Instagram, Snapchat, GitHub, NGL, Steam, X, Threads, WhatsApp)
- Unique visitor counter (IP-based)
- Public view count with configurable boost offset

### PWA & push notifications
- Installable Progressive Web App (`manifest.json` + service worker)
- Users subscribe by opening the Home Screen app and tapping **“nothing more below this 😛”** in the footer
- Hidden admin page at `/admin` to broadcast a message to all subscribed devices
- Powered by Web Push (VAPID) via [`pywebpush`](https://github.com/web-push-libs/pywebpush)

### Admin dashboards
| Route | Purpose |
|-------|---------|
| `/admin` | Send push notifications to all PWA subscribers |
| `/adminanas` | View real vs. boosted visit stats |

### Extended version
`main2.py` adds session duration, link click tracking, and Chart.js analytics (same link page, richer stats).

## Project structure

| File / folder | Description |
|---------------|-------------|
| `main.py` | Production app — links, visits, PWA, push notifications |
| `main2.py` | Analytics variant — click/session tracking + charts |
| `static/sw.js` | Service worker — receives and displays push notifications |
| `requirements.txt` | Python dependencies |
| `visits.json` | Visitor data (auto-created, not in git) |
| `push_subscriptions.json` | Push subscriber endpoints (auto-created, not in git) |
| `vapid_private.pem` | VAPID signing key (auto-created on first run, not in git) |

## Requirements

- Python 3.8+
- Flask
- pywebpush (installed via `requirements.txt`)

## Setup

```bash
git clone https://github.com/spunkkk2/AllMyLinks_Custom_Website.git
cd AllMyLinks_Custom_Website

pip install -r requirements.txt

# Production app (used on spunkkk.com)
python main.py

# Or analytics version
python main2.py
```

Open [http://127.0.0.1:5005](http://127.0.0.1:5005) in your browser.

> **Note:** Push notifications require **HTTPS** in production. Local testing of subscribe/send is limited without HTTPS.

## Push notifications — how it works

### For users (iPhone / Android)
1. Open the site in the browser (Safari on iPhone).
2. **Add to Home Screen**.
3. Open the app from the **Home Screen icon** (not Safari).
4. Tap **“nothing more below this 😛”** at the bottom.
5. Tap **Allow** when asked for notification permission.

### For admin (you)
1. Go to [spunkkk.com/admin](https://spunkkk.com/admin) (hidden link — not linked from the main page).
2. Type a message in the text box.
3. Click **Send notification** — all subscribed devices receive it.

The admin page shows the current **subscriber count**.

## API routes

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/manifest.json` | PWA manifest |
| `GET` | `/sw.js` | Service worker |
| `GET` | `/api/push/vapid-public-key` | Public VAPID key for browser subscription |
| `POST` | `/api/push/subscribe` | Save a device push subscription |
| `POST` | `/api/push/send` | Broadcast a notification to all subscribers |

## Configuration

In `main.py` you can adjust:

- `BOOST` — offset added to the public view counter
- `VAPID_CLAIMS` — VAPID subject (defaults to `https://spunkkk.com`)
- Social links, bio text, and avatar in the HTML template
- `port=5005` — server port in the `app.run()` call

VAPID keys are generated automatically on first run and stored in `vapid_private.pem`.

## Deployment

The app runs behind nginx on port `5005` in production. After updating files on the server:

```bash
pip install -r requirements.txt
systemctl restart spunkkk-website   # if using systemd
```

## License

Personal project — use and modify as you like.
