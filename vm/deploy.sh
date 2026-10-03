#!/usr/bin/env bash
# Deploy de uma das aplicações na VM (venv + systemd, porta 8000).
#   vm/deploy.sh <cpu|memory|io>
set -euo pipefail
source "$(dirname "$0")/env.sh"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${1:-}"
case "$APP" in cpu | memory | io) ;; *) sed -n '2,3p' "$0"; exit 1 ;; esac

echo ">> dependências do sistema"
vm_sudo "apt-get update -qq"
vm_sudo "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv python3-pip"

echo ">> código"
vm_ssh "mkdir -p $VM_APP_DIR"
tar -C "$ROOT" -czf - pyproject.toml src monitor | vm_ssh "tar -xzf - -C $VM_APP_DIR"

echo ">> ambiente Python"
vm_ssh "cd $VM_APP_DIR && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q ."

echo ">> serviço systemd"
sed -e "s|@APP@|$APP|g" -e "s|@USER@|$VM_USER|g" -e "s|@APP_DIR@|$VM_APP_DIR|g" "$ROOT/vm/poi-app.service" |
  vm_ssh "cat > /tmp/poi-app.service"
vm_sudo "mv /tmp/poi-app.service /etc/systemd/system/poi-app.service"
vm_sudo "systemctl daemon-reload"
vm_sudo "systemctl enable poi-app"
vm_sudo "systemctl restart poi-app"

wait_for 120 "aplicação em /health" curl -fsS "http://localhost:$APP_PORT/health"
curl -fsS "http://localhost:$APP_PORT/health"
echo
