from flask import Flask, render_template_string, request, jsonify
import os, json, uuid
from datetime import datetime, date

app = Flask(__name__)

VISIT_FILE = "visits.json"
ANALYTICS_FILE = "analytics.json"
BOOST = 7192


# ---------------- VISITS ----------------

def load_visits():
    if not os.path.exists(VISIT_FILE):
        return {"ips": {}, "count": 0}
    return json.load(open(VISIT_FILE))


def save_visits(data):
    json.dump(data, open(VISIT_FILE, "w"))


def register_visit(ip):
    data = load_visits()
    today = str(date.today())

    if ip not in data["ips"]:
        data["ips"][ip] = today
        data["count"] += 1
        save_visits(data)

    return data["count"]


# ---------------- ANALYTICS ----------------

def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return {"sessions": {}, "clicks": []}
    return json.load(open(ANALYTICS_FILE))


def save_analytics(data):
    json.dump(data, open(ANALYTICS_FILE, "w"))


# ---------------- HOME ----------------

@app.route('/')
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip = ip.split(",")[0].strip()

    real_views = register_visit(ip)
    public_views = real_views + BOOST

    session_id = str(uuid.uuid4())

    data = load_analytics()
    data["sessions"][session_id] = {
        "ip": ip,
        "start": datetime.utcnow().isoformat(),
        "duration": 0
    }
    save_analytics(data)

    return render_template_string(
        HTML_WITH_TRACKING,
        views=public_views,
        session_id=session_id
    )


# ---------------- TRACK ----------------

@app.route('/track_time', methods=['POST'])
def track_time():
    data = load_analytics()

    try:
        body = json.loads(request.data.decode())
    except:
        return jsonify({"ok": False})

    sid = body.get("session")
    duration = body.get("duration", 0)

    if sid in data["sessions"]:
        data["sessions"][sid]["duration"] = duration

    save_analytics(data)
    return jsonify({"ok": True})


@app.route('/click', methods=['POST'])
def click():
    data = load_analytics()
    body = request.get_json()

    if not body:
        return jsonify({"ok": False})

    data["clicks"].append({
        "link": body.get("link", "unknown"),
        "time": datetime.utcnow().isoformat()
    })

    save_analytics(data)
    return jsonify({"ok": True})


# ---------------- DASHBOARD ----------------

@app.route('/adminanas')
def admin():
    visits = load_visits()
    analytics = load_analytics()

    total = visits["count"]
    boosted = total + BOOST
    unique = len(visits["ips"])

    sessions = analytics.get("sessions", {})
    clicks = analytics.get("clicks", [])

    avg_time = 0
    if sessions:
        avg_time = sum(s.get("duration", 0) for s in sessions.values()) / len(sessions)

    # clicks per link
    link_count = {}
    for c in clicks:
        link = c.get("link", "unknown")
        link_count[link] = link_count.get(link, 0) + 1

    # visits per day
    daily = {}
    for d in visits["ips"].values():
        daily[d] = daily.get(d, 0) + 1

    # safe session table (NO KEYERROR)
    rows = ""
    for s in list(sessions.values())[-20:]:
        ip = s.get("ip", "unknown")
        dur = s.get("duration", 0)
        rows += f"<tr><td>{ip}</td><td>{dur}s</td></tr>"

    return """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body { background:#0f0c29; color:white; font-family:Arial; padding:30px; }
.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(250px,1fr)); gap:20px; }
.box { background:rgba(255,255,255,0.08); padding:20px; border-radius:15px; }
table { width:100%; margin-top:20px; }
td { padding:8px; border-bottom:1px solid rgba(255,255,255,0.1); }
</style>
</head>

<body>

<h1>📊 ANALYTICS</h1>

<div class="grid">
<div class="box">👀 Views: __TOTAL__</div>
<div class="box">🚀 Boosted: __BOOSTED__</div>
<div class="box">🌍 Unique: __UNIQUE__</div>
<div class="box">⏱ Avg Time: __AVG__ sec</div>
<div class="box">🔗 Clicks: __CLICKS__</div>
</div>

<h2>📈 Visits per Day</h2>
<canvas id="c1"></canvas>

<h2>🔥 Top Links</h2>
<canvas id="c2"></canvas>

<h2>🧠 Recent Sessions</h2>
<table>__ROWS__</table>

<script>
new Chart(document.getElementById("c1"), {
type:"line",
data:{labels: __DAYS__, datasets:[{label:"Visits",data: __DAYVAL__}]}
});

new Chart(document.getElementById("c2"), {
type:"bar",
data:{labels: __LINKS__, datasets:[{label:"Clicks",data: __LINKVAL__}]}
});
</script>

</body>
</html>
""".replace("__TOTAL__", str(total))\
.replace("__BOOSTED__", str(boosted))\
.replace("__UNIQUE__", str(unique))\
.replace("__AVG__", str(round(avg_time,2)))\
.replace("__CLICKS__", str(len(clicks)))\
.replace("__DAYS__", str(list(daily.keys())))\
.replace("__DAYVAL__", str(list(daily.values())))\
.replace("__LINKS__", str(list(link_count.keys())))\
.replace("__LINKVAL__", str(list(link_count.values())))\
.replace("__ROWS__", rows)


# ---------------- YOUR HTML (UNCHANGED) + TRACKING ----------------

HTML_WITH_TRACKING = """REPLACE_THIS"""

HTML_WITH_TRACKING = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Spunkkk Social 😛</title>

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

    <div class="footer">nothing more below this 😛<br>
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



</div>

</body>
</html>
"""  # ← already included manually below

HTML_WITH_TRACKING = HTML_WITH_TRACKING.replace("</body>", """
{% raw %}
<script>
const sessionId = "{{ session_id }}";
let start = Date.now();

window.addEventListener("beforeunload", () => {
    let duration = Math.round((Date.now() - start)/1000);
    navigator.sendBeacon("/track_time", JSON.stringify({
        session: sessionId,
        duration: duration
    }));
});

document.querySelectorAll(".link").forEach(link => {
    link.addEventListener("click", () => {
        fetch("/click", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({link: link.href})
        });
    });
});
</script>
{% endraw %}
</body>
""")


# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)