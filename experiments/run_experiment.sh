#!/usr/bin/env bash
# Roda todos os cenários x níveis de demanda de experiments/scenarios.env.
#   experiments/run_experiment.sh <cpu|memory|io>          # na VM (reconfigura a cada cenário)
#   experiments/run_experiment.sh <cpu|memory|io> --local  # app rodando nesta máquina, sem VM
# As variáveis do scenarios.env podem ser sobrescritas: RATES="5 10" DURATION=10s ...
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${1:-}" MODE="${2:-vm}"
case "$APP" in cpu | memory | io) ;; *) sed -n '2,5p' "$0"; exit 1 ;; esac

overrides="$(for v in SCENARIOS RATES DURATION WARMUP COOLDOWN; do [ -n "${!v:-}" ] && declare -p "$v"; done || true)"
source "$ROOT/experiments/scenarios.env"
eval "$overrides"
source "$ROOT/vm/env.sh"

declare -A LOCAL_PORT=([cpu]=8001 [memory]=8002 [io]=8003)
if [ "$MODE" = "--local" ]; then
  BASE_URL="${BASE_URL:-http://localhost:${LOCAL_PORT[$APP]}}"
  SCENARIOS="local"
else
  BASE_URL="http://localhost:$APP_PORT"
fi

COLLECTOR_PID=""
start_collector() {
  if [ "$MODE" = "--local" ]; then
    "$ROOT/.venv/bin/python" "$ROOT/monitor/collect.py" --output "$1/vm_metrics.csv" &
    COLLECTOR_PID=$!
  else
    COLLECTOR_PID="$(vm_ssh "nohup $VM_APP_DIR/.venv/bin/python $VM_APP_DIR/monitor/collect.py \
      --output /tmp/vm_metrics.csv >/dev/null 2>&1 & echo \$!")"
  fi
}
stop_collector() {
  [ -n "$COLLECTOR_PID" ] || return 0
  if [ "$MODE" = "--local" ]; then
    kill "$COLLECTOR_PID" 2>/dev/null && wait "$COLLECTOR_PID" 2>/dev/null || true
  else
    vm_ssh "kill $COLLECTOR_PID 2>/dev/null; while kill -0 $COLLECTOR_PID 2>/dev/null; do sleep 0.2; done" || true
    vm_scp_from /tmp/vm_metrics.csv "$1/vm_metrics.csv" || echo "aviso: não foi possível copiar vm_metrics.csv" >&2
  fi
  COLLECTOR_PID=""
}
trap 'stop_collector /tmp' EXIT

for scenario in $SCENARIOS; do
  if [ "$scenario" = "local" ]; then
    CPUS="$(nproc)" MEM_MB="$(free -m | awk '/^Mem/ {print $2}')" LABEL="local"
  else
    CPUS="${scenario%%:*}" MEM_MB="${scenario##*:}" LABEL="${CPUS}cpu_${MEM_MB}mb"
    echo "=== cenário $LABEL ==="
    "$ROOT/vm/configure_vm.sh" "$CPUS" "$MEM_MB"
  fi

  echo "--- aquecimento ($WARMUP)"
  "$ROOT/loadtest/run_k6.sh" "$APP" 5 "$WARMUP" "$(mktemp -d)" "$BASE_URL" >/dev/null || true

  for rate in $RATES; do
    OUT="$ROOT/results/$APP/$LABEL/${rate}rps"
    mkdir -p "$OUT"
    # se o nível anterior derrubou a app (OOM), espera ela voltar
    wait_for 120 "aplicação em /health" curl -fsS "$BASE_URL/health"
    [ "$APP" = memory ] && curl -fsS -X DELETE "$BASE_URL/cache" >/dev/null

    started="$(date +%s)"
    start_collector "$OUT"
    "$ROOT/loadtest/run_k6.sh" "$APP" "$rate" "$DURATION" "$OUT" "$BASE_URL" || echo "aviso: k6 terminou com erro em ${rate} req/s" >&2
    stop_collector "$OUT"

    printf '{"app": "%s", "scenario": "%s", "cpus": %s, "mem_mb": %s, "rate_target": %s, "duration": "%s", "started_at": %s, "ended_at": %s}\n' \
      "$APP" "$LABEL" "$CPUS" "$MEM_MB" "$rate" "$DURATION" "$started" "$(date +%s)" >"$OUT/meta.json"
    sleep "$COOLDOWN"
  done
done

python3 "$ROOT/experiments/summarize.py" "$ROOT/results/$APP"
