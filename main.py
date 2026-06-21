from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import json
import base64
from datetime import date
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)
from py_vapid import Vapid02
from pywebpush import WebPushException, webpush

app = Flask(__name__)

# ------------Counter Codes
VISIT_FILE = "visits.json"
SUBSCRIPTIONS_FILE = "push_subscriptions.json"
VAPID_PRIVATE_FILE = "vapid_private.pem"
VAPID_CLAIMS = {"sub": "https://spunkkk.com"}
ICON_URL = "https://ucarecdn.com/c96495e5-f0c8-4a28-bfd8-eac380d14d2e/630692742_18558533275053061_243982538138301450_n.jpg"
BOOST = 7192

_vapid_private_pem = None
_vapid_public_key = None


def load_data():
    if not os.path.exists(VISIT_FILE):
        return {"ips": {}, "count": 0}

    with open(VISIT_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(VISIT_FILE, "w") as f:
        json.dump(data, f)


def register_visit(ip):
    data = load_data()
    today = str(date.today())

    if ip not in data["ips"]:
        data["ips"][ip] = today
        data["count"] += 1
        save_data(data)

    return data["count"]


def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []

    with open(SUBSCRIPTIONS_FILE, "r") as f:
        return json.load(f)


def save_subscriptions(subscriptions):
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subscriptions, f)


def ensure_vapid_private_pem():
    if os.path.exists(VAPID_PRIVATE_FILE):
        with open(VAPID_PRIVATE_FILE, "rb") as f:
            pem = f.read()
        try:
            load_pem_private_key(pem, password=None)
            return pem
        except Exception:
            pass

    vapid = Vapid02()
    vapid.generate_keys()
    pem = vapid.private_pem()
    with open(VAPID_PRIVATE_FILE, "wb") as f:
        f.write(pem)
    return pem


def public_key_from_private_pem(pem):
    private_key = load_pem_private_key(pem, password=None)
    public_key = private_key.public_key()
    raw = public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def get_vapid_keys():
    global _vapid_private_pem, _vapid_public_key

    if _vapid_private_pem is None:
        _vapid_private_pem = ensure_vapid_private_pem()
        _vapid_public_key = public_key_from_private_pem(_vapid_private_pem)

    return _vapid_private_pem, _vapid_public_key


def vapid_private_path():
    return os.path.join(app.root_path, VAPID_PRIVATE_FILE)


def send_push_notifications(message):
    ensure_vapid_private_pem()
    subscriptions = load_subscriptions()
    payload = json.dumps({"title": "Spunkkk", "body": message, "icon": ICON_URL})
    sent = 0
    failed = 0
    active_subscriptions = []

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=payload,
                vapid_private_key=vapid_private_path(),
                vapid_claims=VAPID_CLAIMS,
            )
            sent += 1
            active_subscriptions.append(subscription)
        except WebPushException as exc:
            failed += 1
            status = exc.response.status_code if exc.response else None
            if status not in (404, 410):
                active_subscriptions.append(subscription)
        except Exception:
            failed += 1
            active_subscriptions.append(subscription)

    if len(active_subscriptions) != len(subscriptions):
        save_subscriptions(active_subscriptions)

    return sent, failed, len(active_subscriptions)


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Spunkkk Social 😛</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#302b63">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Spunkkk">
<link rel="apple-touch-icon" href="https://ucarecdn.com/c96495e5-f0c8-4a28-bfd8-eac380d14d2e/630692742_18558533275053061_243982538138301450_n.jpg">

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
}

body {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
    min-height: 100dvh;
    overflow-y: auto;
    overflow-x: hidden;
}

/* container FIXED */
.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100dvh;
    padding: 40px 20px 80px;
    text-align: center;
    animation: fadeIn 1.2s ease forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* avatar */
.avatar-wrapper {
    position: relative;
    display: inline-block;
    margin-bottom: 10px;
}

.avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 3px solid rgba(255,255,255,0.3);
    animation: float 4s ease-in-out infinite, zoomIn 1s ease;
}

html, body {
    height: 100%;
    overflow-x: hidden;
    overscroll-behavior: none;
}
body {
    -webkit-overflow-scrolling: touch;
}

/* verification badge */
.badge {
    position: absolute;
    bottom: 8px;
    right: 4px;
    width: 28px;
    height: 28px;
    background: #1DA1F2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
    box-shadow: 0 0 10px rgba(29,161,242,0.7);
    animation: popIn 0.6s ease;
}

.badge i {
    color: white;
    font-size: 14px;
}

@keyframes popIn {
    from { transform: scale(0); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes zoomIn {
    from { transform: scale(0.5); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

h1 {
    font-weight: 700;
    margin-top: 10px;
}

.bio {
    font-size: 14px;
    opacity: 0.8;
    margin-bottom: 25px;
}

/* links */
.links {
    width: 100%;
    max-width: 400px;
}

/* FIXED link animation */
.link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 15px;
    margin: 12px 0;
    text-decoration: none;
    color: white;
    font-weight: 500;
    transition: 0.3s ease;
    position: relative;
    overflow: hidden;

    opacity: 0;
    animation: slideUp 0.6s ease forwards;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

/* stagger automatically with CSS variable (clean trick) */
.link {
    animation-delay: calc(var(--i) * 0.1s);
}

/* hover */
.link::before {
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: -100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: 0.5s;
}

.link:hover::before {
    left: 100%;
}

.link:hover {
    transform: scale(1.05);
    background: rgba(255,255,255,0.2);
}

/* layout */
.left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.icon {
    font-size: 22px;
}

.instagram { color: #E1306C; }
.twitter { color: #1DA1F2; }
.tiktok { color: #000000; }
.youtube { color: #FF0000; }
.snapchat { color: #FFFC00; text-shadow: 0 0 3px #000; }
.github { color: #ffffff; }

.right {
    text-align: right;
    font-size: 12px;
    opacity: 0.8;
}

.count {
    font-weight: 700;
    font-size: 14px;
}

/* footer */
.footer {
    margin-top: 30px;
    font-size: 12px;
    opacity: 0.5;
}

/* glow */
.glow {
    position: fixed;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255,0,150,0.5), transparent);
    filter: blur(80px);
    animation: moveGlow 10s infinite alternate;
}

@keyframes moveGlow {
    from { transform: translate(-50px, -50px); }
    to { transform: translate(50px, 50px); }
}
</style>
</head>
<body>

<div class="glow"></div>

<div class="container">

    <div class="avatar-wrapper">
        <img src="https://ucarecdn.com/c96495e5-f0c8-4a28-bfd8-eac380d14d2e/630692742_18558533275053061_243982538138301450_n.jpg" class="avatar">
        <div class="badge">
            <i class="fas fa-check"></i>
        </div>
    </div>

    <h1>Anas Badran 🤞🏼</h1>
    <div class="bio">✨ stalking me made easier ✨</div>

    <div class="links">

        <a href="https://www.tiktok.com/@spunkkk" class="link" style="--i:1">
            <div class="left">
                <i class="fab fa-tiktok icon tiktok"></i>
                TikTok
            </div>
            <div class="right">
                <div class="count">2M</div>
                Followers
            </div>
        </a>

        <a href="https://instagram.com/spunkkk2" class="link" style="--i:2">
            <div class="left">
                <i class="fab fa-instagram icon instagram"></i>
                Instagram
            </div>
            <div class="right">
                <div class="count">150K</div>
                Followers
            </div>
        </a>

        <a href="https://www.snapchat.com/@spunkkk2" class="link" style="--i:3">
            <div class="left">
                <i class="fab fa-snapchat icon snapchat"></i>
                Snapchat
            </div>
            <div class="right">
                <div class="count">16K</div>
                Followers
            </div>
        </a>

        <a href="https://github.com/spunkkk2" class="link" style="--i:4" target="_blank">
            <div class="left">
                <i class="fab fa-github icon github"></i>
                GitHub
            </div>
            <div class="right">
                Personal Account
            </div>
        </a>

        <a href="https://ngl.link/spunkkk2" class="link" style="--i:5" target="_blank">
    <div class="left">
        <i class="fas fa-comment-dots" style="color:#ff4d6d;"></i>
        NGL
    </div>
    <div class="right">
        <div class="count"></div>
        Anonymous Msgs
    </div>
</a>


        <a href="https://steamcommunity.com/id/spunkkk2/" class="link" style="--i:6">
            <div class="left">
                <i class="fab fa-steam icon" style="color:#2596be;"></i>
                Steam
            </div>
            <div class="right">
                Gaming Account
            </div>
        </a>

        <a href="https://x.com/spunkkk" class="link" style="--i:7">
            <div class="left">
                <i class="fab fa-x-twitter icon twitter"></i>
                Twitter
            </div>
            <div class="right">
                Personal Account
            </div>
        </a>

        <a href="https://www.threads.com/@spunkkk2" class="link" style="--i:8">
            <div class="left">
                <i class="fa-brands fa-threads icon" style="color:#000;"></i>
                Threads
            </div>
            <div class="right">
                Personal Account
            </div>
        </a>

        <a href="https://wa.me/962789995251" class="link" style="--i:9" target="_blank">
        <div class="left">
        <i class="fab fa-whatsapp icon" style="color:#25D366;"></i>
        WhatsApp
        </div>
        <div class="right">
        <div class="count"></div>
        Work Inquiries
        </div>
        </a>




    </div>

    <div class="footer"><span id="notifyTrigger">nothing more below this 😛</span><br>
    👀 <span id="views">0</span> views
</div></div>

<script>
function formatNumber(x){
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

let target = {{ views }};
let el = document.getElementById("views");

let current = target - 80;

let interval = setInterval(() => {
    current++;
    el.innerText = formatNumber(current);

    if(current >= target){
        el.innerText = formatNumber(target);
        clearInterval(interval);
    }
}, 15);
</script>

<script>
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function setupPushNotifications() {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        return;
    }

    if (Notification.permission === "default") {
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
            return;
        }
    } else if (Notification.permission !== "granted") {
        return;
    }

    const registration = await navigator.serviceWorker.register("/sw.js");
    await navigator.serviceWorker.ready;

    const keyResponse = await fetch("/api/push/vapid-public-key");
    if (!keyResponse.ok) {
        return;
    }
    const keyData = await keyResponse.json();
    if (!keyData.publicKey) {
        return;
    }

    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(keyData.publicKey)
        });
    }

    const subscribeResponse = await fetch("/api/push/subscribe", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(subscription.toJSON())
    });
    if (!subscribeResponse.ok) {
        return;
    }
}

document.getElementById("notifyTrigger").addEventListener("click", function () {
    setupPushNotifications().catch(function () {});
});
</script>



</div>

</body>
</html>
"""


@app.route('/')
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip = ip.split(",")[0].strip()
    print("IP:", ip)
    real_views = register_visit(ip)
    public_views = real_views + BOOST

    return render_template_string(
        HTML,
        views=public_views,
        real=real_views
    )


ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Push Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: "Poppins", sans-serif; }
body {
    min-height: 100dvh;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}
.card {
    width: 100%;
    max-width: 420px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 28px;
}
h1 { font-size: 24px; margin-bottom: 8px; }
.subtitle { opacity: 0.75; font-size: 13px; margin-bottom: 18px; }
input {
    width: 100%;
    border: none;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 14px;
    font-size: 15px;
}
button {
    width: 100%;
    border: none;
    border-radius: 12px;
    padding: 14px 16px;
    background: #1DA1F2;
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
}
button:disabled { opacity: 0.6; cursor: wait; }
.meta, #status {
    margin-top: 14px;
    font-size: 13px;
    opacity: 0.85;
}
#status.error { color: #ff8a8a; opacity: 1; }
#status.success { color: #8dffb5; opacity: 1; }
</style>
</head>
<body>
<div class="card">
    <h1>Send Notification</h1>
    <div class="subtitle">Push to all installed PWA users</div>
    <div class="meta">Subscribers: {{ subscribers }}</div>
    <input type="text" id="message" placeholder="">
    <button id="sendBtn">Send notification</button>
    <div id="status"></div>
</div>
<script>
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const statusEl = document.getElementById("status");

sendBtn.addEventListener("click", async () => {
    const message = messageInput.value.trim();
    statusEl.className = "";
    statusEl.textContent = "";

    if (!message) {
        statusEl.className = "error";
        statusEl.textContent = "Please enter a message.";
        return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = "Sending...";

    try {
        const response = await fetch("/api/push/send", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });
        const raw = await response.text();
        let data;
        try {
            data = JSON.parse(raw);
        } catch (error) {
            throw new Error("Server returned an invalid response.");
        }

        if (!response.ok || !data.ok) {
            throw new Error(data.error || "Failed to send notification.");
        }

        statusEl.className = "success";
        statusEl.textContent = "Sent to " + data.sent + " device(s). Failed: " + data.failed + ".";
        messageInput.value = "";
    } catch (error) {
        statusEl.className = "error";
        statusEl.textContent = error.message;
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = "Send notification";
    }
});
</script>
</body>
</html>
"""


@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Spunkkk Social",
        "short_name": "Spunkkk",
        "description": "Anas Badran link in bio",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0f0c29",
        "theme_color": "#302b63",
        "icons": [
            {"src": ICON_URL, "sizes": "192x192", "type": "image/jpeg", "purpose": "any"},
            {"src": ICON_URL, "sizes": "512x512", "type": "image/jpeg", "purpose": "any maskable"},
        ],
    })


@app.route('/sw.js')
def service_worker():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "sw.js",
        mimetype="application/javascript",
    )


@app.route('/api/push/vapid-public-key')
def push_vapid_public_key():
    try:
        _, public_key = get_vapid_keys()
        return jsonify({"publicKey": public_key})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route('/api/push/subscribe', methods=['POST'])
def push_subscribe():
    try:
        subscription = request.get_json(silent=True)
        if not subscription or "endpoint" not in subscription:
            return jsonify({"ok": False, "error": "Invalid subscription"}), 400

        subscriptions = load_subscriptions()
        endpoints = {item.get("endpoint") for item in subscriptions}

        if subscription["endpoint"] not in endpoints:
            subscriptions.append(subscription)
            save_subscriptions(subscriptions)

        return jsonify({"ok": True, "total": len(subscriptions)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route('/api/push/send', methods=['POST'])
def push_send():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()

    if not message:
        return jsonify({"ok": False, "error": "Message is required."}), 400

    try:
        sent, failed, total = send_push_notifications(message)
        return jsonify({"ok": True, "sent": sent, "failed": failed, "subscribers": total})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route('/admin')
def admin_notifications():
    subscriptions = load_subscriptions()
    return render_template_string(
        ADMIN_HTML,
        subscribers=len(subscriptions),
    )


@app.route('/adminanas')
def admin():
    data = load_data()
    real_views = data["count"]
    boosted = real_views + BOOST

    total_ips = len(data["ips"])

    return f"""
    <html>
    <head>
        <title>Admin Dashboard</title>
        <style>
            body {{
                background:#0f0c29;
                color:white;
                font-family:Arial;
                padding:30px;
            }}
            .box {{
                background:rgba(255,255,255,0.08);
                padding:20px;
                margin:10px 0;
                border-radius:15px;
            }}
            h1 {{ color:#1DA1F2; }}
        </style>
    </head>

    <body>
        <h1>📊 LIVE DASHBOARD</h1>

        <div class="box">👀 Real views: {real_views}</div>
        <div class="box">🚀 Boosted views: {boosted}</div>
        <div class="box">🌍 Unique visitors (IPs): {total_ips}</div>

        <div class="box">
            ⚡ Boost value: {BOOST}
        </div>
    </body>
    </html>
    """


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)