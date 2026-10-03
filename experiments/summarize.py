#!/usr/bin/env python3
"""Consolida os resultados de uma aplicação em um único CSV, uma linha por (cenário, demanda).

    python3 experiments/summarize.py results/<app>
"""
import csv
import json
import sys
from pathlib import Path

VM_AGGREGATES = {
    "cpu_avg_pct": ("cpu_pct", "avg"),
    "cpu_max_pct": ("cpu_pct", "max"),
    "iowait_avg_pct": ("cpu_iowait", "avg"),
    "mem_used_avg_mb": ("mem_used_mb", "avg"),
    "mem_used_max_mb": ("mem_used_mb", "max"),
    "swap_used_max_mb": ("swap_used_mb", "max"),
    "disk_read_avg_bytes_s": ("disk_read_bytes", "avg"),
    "disk_write_avg_bytes_s": ("disk_write_bytes", "avg"),
    "proc_cpu_avg_pct": ("proc_cpu_pct", "avg"),
    "proc_rss_max_mb": ("proc_rss_mb", "max"),
}


def aggregate_vm_metrics(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {}
    out = {}
    for name, (column, how) in VM_AGGREGATES.items():
        values = [float(r[column]) for r in rows]
        out[name] = round(max(values) if how == "max" else sum(values) / len(values), 2)
    return out


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    rows = []
    for meta_path in root.glob("*/*/meta.json"):
        run = meta_path.parent
        summary_path = run / "k6_summary.json"
        if not summary_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        k6 = json.loads(summary_path.read_text())
        latency = {f"latency_{k}_ms": round(v, 2) for k, v in k6["latency_ms"].items() if v is not None}
        rows.append({
            "app": meta["app"], "scenario": meta["scenario"], "cpus": meta["cpus"], "mem_mb": meta["mem_mb"],
            "rate_target": meta["rate_target"],
            "throughput_rps": round(k6["throughput_rps"], 2),
            "requests": k6["requests"],
            "error_rate": round(k6["error_rate"], 4),
            "dropped_iterations": k6["dropped_iterations"],
            **latency,
            **aggregate_vm_metrics(run / "vm_metrics.csv"),
        })

    rows.sort(key=lambda r: (r["cpus"], r["mem_mb"], r["scenario"], r["rate_target"]))
    columns = list(dict.fromkeys(key for row in rows for key in row))
    out = root / "summary.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} execuções consolidadas em {out}")


if __name__ == "__main__":
    main()
