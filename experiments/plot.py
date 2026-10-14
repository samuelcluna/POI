#!/usr/bin/env python3
"""Gera os gráficos de uma aplicação a partir do summary.csv.

    uv run --no-project --with matplotlib python experiments/plot.py results/<app>
"""
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load(root: Path) -> dict:
    scenarios = {}
    with open(root / "summary.csv", newline="") as f:
        for row in csv.DictReader(f):
            key = (int(row["cpus"]), int(row["mem_mb"]), int(row.get("disk_mbps") or 0))
            values = {k: float(v) for k, v in row.items() if k not in ("app", "scenario") and v != ""}
            values["disk_mb_s"] = (values.get("disk_read_avg_bytes_s", 0) + values.get("disk_write_avg_bytes_s", 0)) / 2**20
            scenarios.setdefault(key, []).append(values)
    for rows in scenarios.values():
        rows.sort(key=lambda r: r["rate_target"])
    return scenarios


def label(key) -> str:
    cpus, mem, disk = key
    text = f"{cpus} vCPU, {mem} MB"
    return text + f", disco {disk} MB/s" if disk else text


def plot(scenarios, keys, column, ylabel, out, log=False, identity=False, scale=1.0):
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for key in keys:
        rows = scenarios[key]
        ax.plot([r["rate_target"] for r in rows], [r[column] * scale for r in rows], marker="o", label=label(key))
    if identity:
        rates = [r["rate_target"] for r in scenarios[keys[0]]]
        ax.plot(rates, rates, linestyle="--", color="gray", linewidth=1, label="vazão = demanda")
    if log:
        ax.set_yscale("log")
    ax.set_xlabel("Demanda (req/s)")
    ax.set_ylabel(ylabel)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    app = root.name
    scenarios = load(root)
    figures = root / "figures"
    figures.mkdir(exist_ok=True)
    every = sorted(scenarios)

    def fig(keys, column, ylabel, name, **kw):
        plot(scenarios, keys, column, ylabel, figures / f"{name}.png", **kw)

    if app == "cpu":
        # cpu: vCPUs variam com 1024 MB; memória varia com 2 vCPUs
        by_cpu = [k for k in every if k[1] == 1024]
        by_mem = [k for k in every if k[0] == 2]
        fig(by_cpu, "latency_p95_ms", "Latência p95 (s)", "latencia_vcpus", log=True, scale=1e-3)
        fig(by_cpu, "goodput_rps", "Vazão útil (req/s)", "vazao_vcpus", identity=True)
        fig(by_cpu, "error_rate", "Requisições com erro (%)", "erros_vcpus", scale=100)
        fig(by_cpu, "cpu_avg_pct", "Uso médio de CPU da VM (%)", "cpu_vcpus")
        fig(by_mem, "latency_p95_ms", "Latência p95 (s)", "latencia_memoria", log=True, scale=1e-3)
        fig(every, "mem_used_max_mb", "Memória em uso, máximo (MB)", "memoria")
    else:
        fig(every, "latency_p95_ms", "Latência p95 (s)", "latencia", log=True, scale=1e-3)
        fig(every, "goodput_rps", "Vazão útil (req/s)", "vazao", identity=True)
        fig(every, "cpu_avg_pct", "Uso médio de CPU da VM (%)", "cpu")
        fig(every, "mem_used_max_mb", "Memória em uso, máximo (MB)", "memoria")
        if app == "memory":
            fig(every, "swap_used_max_mb", "Swap em uso, máximo (MB)", "swap")
            fig(every, "proc_rss_max_mb", "Memória residente da aplicação, máx. (MB)", "rss")
        if app == "io":
            fig(every, "iowait_avg_pct", "CPU esperando IO, média (%)", "iowait")
            fig(every, "disk_mb_s", "Leitura + escrita em disco (MB/s)", "disco")
    print(f"gráficos em {figures}")


if __name__ == "__main__":
    main()
