#!/usr/bin/env bash
#   loadtest/run_k6.sh <cpu|memory|io> <req/s> <duração> <dir_saida> [base_url]
# Opcionais: ENDPOINT, RAW=1 (salva k6_raw.csv.gz), MAX_VUS, ALLOC_MB
set -euo pipefail
[ $# -ge 4 ] || { sed -n '2,3p' "$0"; exit 1; }
APP="$1" RATE="$2" DURATION="$3" OUT="$4" BASE_URL="${5:-http://localhost:8000}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

if [ -x "$ROOT/.bin/k6" ]; then
  K6=("$ROOT/.bin/k6") SCRIPTS="$ROOT/loadtest/k6" OUT_IN="$OUT"
elif command -v k6 >/dev/null; then
  K6=(k6) SCRIPTS="$ROOT/loadtest/k6" OUT_IN="$OUT"
elif command -v docker >/dev/null; then
  K6=(docker run --rm --network host -u "$(id -u):$(id -g)"
    -v "$ROOT/loadtest/k6:/scripts:ro" -v "$OUT:/out" grafana/k6)
  SCRIPTS=/scripts OUT_IN=/out
else
  echo "k6 não encontrado: rode loadtest/install_k6.sh" >&2
  exit 1
fi

ARGS=(run --quiet
  -e "RATE=$RATE" -e "DURATION=$DURATION" -e "BASE_URL=$BASE_URL" -e "SUMMARY=$OUT_IN/k6_summary.json")
for var in ENDPOINT MAX_VUS ALLOC_MB CACHE_KEYS SEEDED_RECORDS; do
  [ -n "${!var:-}" ] && ARGS+=(-e "$var=${!var}")
done
[ "${RAW:-0}" = 1 ] && ARGS+=(--out "csv=$OUT_IN/k6_raw.csv.gz")

"${K6[@]}" "${ARGS[@]}" "$SCRIPTS/$APP.js"
