# SysGlance

A tiny local system dashboard. Flask backend (using `psutil`) serves live CPU, memory, disk, network, and top-process stats to a single-page dashboard that auto-refreshes every 2 seconds.

## Features

- Overall + per-core CPU usage, load average
- Memory and swap usage with progress bars
- Disk usage for the root volume
- Network bytes sent/received (cumulative since boot)
- Top 5 processes by CPU usage
- System uptime
- No external JS/CSS dependencies — pure HTML/CSS/vanilla JS frontend

## Setup

```bash
git clone https://github.com/<your-username>/sysglance.git
cd sysglance
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## Project structure

```
sysglance/
├── app.py              # Flask app + /api/stats endpoint
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## How it works

`app.py` exposes `GET /api/stats`, which returns a JSON snapshot of the current system state (CPU, memory, disk, network, top processes) using the `psutil` library. The frontend polls this endpoint every 2 seconds and updates the DOM directly — no framework needed.

## License

MIT — see [LICENSE](LICENSE).
