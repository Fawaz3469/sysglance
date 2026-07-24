"""
SysGlance - a tiny local system dashboard.

Run:
    python app.py
Then open http://localhost:5000
"""

import time
from datetime import datetime, timedelta

import psutil
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Prime cpu_percent so the first real reading isn't 0.0
psutil.cpu_percent(percpu=True)
_BOOT_TIME = psutil.boot_time()


def bytes_to_human(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def get_uptime() -> str:
    delta = timedelta(seconds=time.time() - _BOOT_TIME)
    days, rem = divmod(int(delta.total_seconds()), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def get_top_processes(limit: int = 5):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: (x.get("cpu_percent") or 0), reverse=True)
    return procs[:limit]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    cpu_overall = psutil.cpu_percent(interval=None)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)

    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()

    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    try:
        load1, load5, load15 = psutil.getloadavg()
    except (AttributeError, OSError):
        load1 = load5 = load15 = None

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": get_uptime(),
        "cpu": {
            "overall_percent": cpu_overall,
            "per_core": cpu_per_core,
            "core_count": psutil.cpu_count(logical=True),
            "load_avg": {"1m": load1, "5m": load5, "15m": load15},
        },
        "memory": {
            "total": bytes_to_human(vm.total),
            "used": bytes_to_human(vm.used),
            "available": bytes_to_human(vm.available),
            "percent": vm.percent,
            "swap_total": bytes_to_human(swap.total),
            "swap_used": bytes_to_human(swap.used),
            "swap_percent": swap.percent,
        },
        "disk": {
            "total": bytes_to_human(disk.total),
            "used": bytes_to_human(disk.used),
            "free": bytes_to_human(disk.free),
            "percent": disk.percent,
        },
        "network": {
            "sent": bytes_to_human(net.bytes_sent),
            "recv": bytes_to_human(net.bytes_recv),
        },
        "top_processes": [
            {
                "pid": p.get("pid"),
                "name": p.get("name") or "?",
                "cpu_percent": round(p.get("cpu_percent") or 0, 1),
                "memory_percent": round(p.get("memory_percent") or 0, 1),
            }
            for p in get_top_processes()
        ],
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
