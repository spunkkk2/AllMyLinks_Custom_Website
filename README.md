# Spunkkk Social

A Flask-powered link-in-bio page for **Anas Badran (spunkkk)** — one place for TikTok, Instagram, Snapchat, and other social profiles, with visit tracking and a private analytics dashboard.

## Features

- Mobile-friendly landing page with animated gradient UI
- Social links with follower counts (TikTok, Instagram, Snapchat, NGL, Steam, X, Threads, WhatsApp)
- Unique visitor counter (IP-based, stored in `visits.json`)
- Public view count with configurable boost offset
- Admin dashboard at `/adminanas` with real vs. boosted stats
- **Extended version** (`main2.py`): session duration, link click tracking, and Chart.js analytics

## Project structure

| File | Description |
|------|-------------|
| `main.py` | Basic app — visit counter and simple admin page |
| `main2.py` | Full app — click tracking, session analytics, charts |
| `visits.json` | Unique visitor data (auto-created) |
| `analytics.json` | Session and click data for `main2.py` (auto-created) |

## Requirements

- Python 3.8+
- [Flask](https://flask.palletsprojects.com/)

## Setup

```bash
# Clone the repo
git clone https://github.com/spunkkk2/AllMyLinks_Custom_Website.git
cd AllMyLinks_Custom_Website

# Install dependencies
pip install -r requirements.txt

# Run the basic version
python main.py

# Or run the analytics version
python main2.py
```

Open [http://127.0.0.1:5005](http://127.0.0.1:5005) in your browser.

## Admin dashboard

Visit `/adminanas` while the server is running to see:

- Real and boosted view counts
- Unique visitors
- *(main2.py only)* Average session time, link clicks, visits per day, and charts

## Configuration

In `main.py` or `main2.py`, you can adjust:

- `BOOST` — offset added to the public view counter
- Social links, bio text, and avatar in the HTML template
- `port=5005` — server port in the `app.run()` call

## License

Personal project — use and modify as you like.
