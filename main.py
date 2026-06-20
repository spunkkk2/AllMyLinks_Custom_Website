from flask import Flask, render_template_string
import os
import json
from datetime import date
from flask import request

app = Flask(__name__)

# ------------Counter Codes
VISIT_FILE = "visits.json"
BOOST = 7192


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


HTML = """
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


        <a href="https://ngl.link/spunkkk2" class="link" style="--i:4" target="_blank">
    <div class="left">
        <i class="fas fa-comment-dots" style="color:#ff4d6d;"></i>
        NGL
    </div>
    <div class="right">
        <div class="count"></div>
        Anonymous Msgs
    </div>
</a>


        <a href="https://steamcommunity.com/id/spunkkk2/" class="link" style="--i:5">
            <div class="left">
                <i class="fab fa-steam icon" style="color:#2596be;"></i>
                Steam
            </div>
            <div class="right">
                Gaming Account
            </div>
        </a>

        <a href="https://x.com/spunkkk" class="link" style="--i:6">
            <div class="left">
                <i class="fab fa-x-twitter icon twitter"></i>
                Twitter
            </div>
            <div class="right">
                Personal Account
            </div>
        </a>

        <a href="https://www.threads.com/@spunkkk2" class="link" style="--i:7">
            <div class="left">
                <i class="fa-brands fa-threads icon" style="color:#000;"></i>
                Threads
            </div>
            <div class="right">
                Personal Account
            </div>
        </a>

        <a href="https://wa.me/962789995251" class="link" style="--i:8" target="_blank">
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