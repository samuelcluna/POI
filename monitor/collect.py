#!/usr/bin/env python3
"""Amostra uso de recursos do sistema e dos processos da aplicação e grava em CSV.

    python monitor/collect.py --output vm_metrics.csv [--interval 1] [--match poi.run]

Encerra com SIGTERM ou Ctrl+C.
"""
import argparse
import csv
import os
import signal
import time

import psutil

MB = 1024 * 1024


def find_app_processes(match: str, known: dict[int, psutil.Process]) -> dict[int, psutil.Process]:
    found: dict[int, psutil.Process] = {}
    for proc in psutil.process_iter(["cmdline"]):
        if match not in (proc.info["cmdline"] or []):
            continue
        try:
            for p in [proc, *proc.children(recursive=True)]:
                found[p.pid] = known.get(p.pid, p)
        except psutil.Error:
            continue
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--match", default="poi.run", help="argumento que identifica o processo da aplicação")
    args = parser.parse_args()

    running = True

    def stop(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    ncpu = psutil.cpu_count()
    header = [
        "timestamp", "cpu_pct", "cpu_user", "cpu_system", "cpu_iowait", "load1",
        "mem_total_mb", "mem_used_mb", "mem_available_mb", "swap_used_mb",
        "disk_read_bytes", "disk_write_bytes",
        "proc_count", "proc_cpu_pct", "proc_rss_mb",
        *[f"cpu{i}_pct" for i in range(ncpu)],
    ]

    procs: dict[int, psutil.Process] = {}
    psutil.cpu_percent(percpu=True)
    psutil.cpu_times_percent()
    disk_prev = psutil.disk_io_counters()

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        f.flush()
        next_tick = time.monotonic() + args.interval
        while running:
            time.sleep(max(0.0, next_tick - time.monotonic()))
            next_tick += args.interval
            if not running:
                break

            per_cpu = psutil.cpu_percent(percpu=True)
            times = psutil.cpu_times_percent()
            mem = psutil.virtual_memory()
            disk = psutil.disk_io_counters()

            procs = find_app_processes(args.match, procs)
            proc_cpu = proc_rss = 0.0
            for p in procs.values():
                try:
                    proc_cpu += p.cpu_percent()
                    proc_rss += p.memory_info().rss
                except psutil.Error:
                    pass

            writer.writerow([
                f"{time.time():.3f}",
                round(sum(per_cpu) / ncpu, 1), times.user, times.system, getattr(times, "iowait", 0.0),
                round(os.getloadavg()[0], 2),
                round(mem.total / MB, 1), round((mem.total - mem.available) / MB, 1), round(mem.available / MB, 1),
                round(psutil.swap_memory().used / MB, 1),
                disk.read_bytes - disk_prev.read_bytes, disk.write_bytes - disk_prev.write_bytes,
                len(procs), round(proc_cpu, 1), round(proc_rss / MB, 1),
                *per_cpu,
            ])
            f.flush()
            disk_prev = disk


if __name__ == "__main__":
    main()
