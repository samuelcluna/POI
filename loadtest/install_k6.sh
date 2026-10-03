#!/usr/bin/env bash
# Baixa o k6 para .bin/
set -euo pipefail
VERSION="${K6_VERSION:-v0.49.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.bin"
curl -fsSL "https://github.com/grafana/k6/releases/download/${VERSION}/k6-${VERSION}-linux-amd64.tar.gz" |
  tar -xz -C "$ROOT/.bin" --strip-components=1 "k6-${VERSION}-linux-amd64/k6"
"$ROOT/.bin/k6" version
