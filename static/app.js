const REFRESH_MS = 2000;

function pctColor(pct) {
  if (pct >= 85) return "var(--danger)";
  if (pct >= 60) return "var(--warn)";
  return "var(--accent)";
}

async function refresh() {
  try {
    const res = await fetch("/api/stats");
    const d = await res.json();

    document.getElementById("timestamp").textContent = d.timestamp;
    document.getElementById("uptime").textContent = d.uptime;

    // CPU
    document.getElementById("cpu-overall").textContent = `${d.cpu.overall_percent.toFixed(1)}%`;
    const coresEl = document.getElementById("cpu-cores");
    coresEl.innerHTML = "";
    d.cpu.per_core.forEach((pct, i) => {
      const pill = document.createElement("span");
      pill.className = "core-pill";
      pill.textContent = `C${i}: ${pct.toFixed(0)}%`;
      coresEl.appendChild(pill);
    });
    const la = d.cpu.load_avg;
    document.getElementById("load-avg").textContent =
      la["1m"] !== null
        ? `load avg: ${la["1m"].toFixed(2)} / ${la["5m"].toFixed(2)} / ${la["15m"].toFixed(2)}`
        : "load avg: n/a";

    // Memory
    document.getElementById("mem-percent").textContent = `${d.memory.percent.toFixed(1)}%`;
    const memBar = document.getElementById("mem-bar");
    memBar.style.width = `${d.memory.percent}%`;
    memBar.style.background = pctColor(d.memory.percent);
    document.getElementById("mem-detail").textContent = `${d.memory.used} / ${d.memory.total}`;
    document.getElementById("swap-detail").textContent =
      `swap: ${d.memory.swap_used} / ${d.memory.swap_total} (${d.memory.swap_percent}%)`;

    // Disk
    document.getElementById("disk-percent").textContent = `${d.disk.percent.toFixed(1)}%`;
    const diskBar = document.getElementById("disk-bar");
    diskBar.style.width = `${d.disk.percent}%`;
    diskBar.style.background = pctColor(d.disk.percent);
    document.getElementById("disk-detail").textContent = `${d.disk.used} / ${d.disk.total}`;

    // Network
    document.getElementById("net-sent").textContent = d.network.sent;
    document.getElementById("net-recv").textContent = d.network.recv;

    // Processes
    const tbody = document.querySelector("#proc-table tbody");
    tbody.innerHTML = "";
    d.top_processes.forEach((p) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${p.pid}</td><td>${p.name}</td><td>${p.cpu_percent}</td><td>${p.memory_percent}</td>`;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to refresh stats", err);
  }
}

refresh();
setInterval(refresh, REFRESH_MS);
