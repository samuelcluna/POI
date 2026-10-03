#!/usr/bin/env bash
# Desliga a VM, altera vCPUs e memória e religa.
#   vm/configure_vm.sh <vcpus> <memoria_mb>
set -euo pipefail
source "$(dirname "$0")/env.sh"
[ $# -eq 2 ] || { sed -n '2,3p' "$0"; exit 1; }
CPUS="$1" MEM_MB="$2"

if vm_running; then
  vm_sudo poweroff || VBoxManage controlvm "$VM_NAME" acpipowerbutton || true
  wait_for 60 "desligamento da VM" bash -c "! VBoxManage list runningvms | grep -q '\"$VM_NAME\"'" ||
    VBoxManage controlvm "$VM_NAME" poweroff
  sleep 2
fi

VBoxManage modifyvm "$VM_NAME" --cpus "$CPUS" --memory "$MEM_MB"
VBoxManage startvm "$VM_NAME" --type headless
wait_for 180 "SSH da VM" vm_ssh true
wait_for 120 "aplicação em /health" curl -fsS "http://localhost:$APP_PORT/health"
echo "VM com $(vm_ssh nproc) vCPU e $(vm_ssh "free -m | awk '/^Mem/ {print \$2}'") MB"
