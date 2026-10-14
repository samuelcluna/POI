#!/usr/bin/env bash
# Desliga a VM, altera vCPUs, memória e limite de banda do disco, e religa.
#   vm/configure_vm.sh <vcpus> <memoria_mb> [limite_disco_mb_s]   (sem limite ou 0 = disco livre)
set -euo pipefail
source "$(dirname "$0")/env.sh"
[ $# -ge 2 ] || { sed -n '2,3p' "$0"; exit 1; }
CPUS="$1" MEM_MB="$2" DISK_MBPS="${3:-0}"

if vm_running; then
  vm_sudo poweroff || VBoxManage controlvm "$VM_NAME" acpipowerbutton || true
  wait_for 60 "desligamento da VM" bash -c "! VBoxManage list runningvms | grep -q '\"$VM_NAME\"'" ||
    VBoxManage controlvm "$VM_NAME" poweroff
  sleep 2
fi

VBoxManage modifyvm "$VM_NAME" --cpus "$CPUS" --memory "$MEM_MB"
VBoxManage bandwidthctl "$VM_NAME" list | grep -q "Name: 'disk'" ||
  VBoxManage bandwidthctl "$VM_NAME" add disk --type disk --limit 1000M
if [ "$DISK_MBPS" -gt 0 ]; then
  VBoxManage bandwidthctl "$VM_NAME" set disk --limit "${DISK_MBPS}M"
  GROUP=disk
else
  GROUP=none
fi
VBoxManage storageattach "$VM_NAME" --storagectl SATA --port 0 --device 0 --type hdd --medium "$VDI" --bandwidthgroup "$GROUP"
VBoxManage startvm "$VM_NAME" --type headless
wait_for 180 "SSH da VM" vm_ssh true
wait_for 120 "aplicação em /health" curl -fsS "http://localhost:$APP_PORT/health"
echo "VM com $(vm_ssh nproc) vCPU e $(vm_ssh "free -m | awk '/^Mem/ {print \$2}'") MB, limite de disco: ${DISK_MBPS} MB/s (0 = sem limite)"
