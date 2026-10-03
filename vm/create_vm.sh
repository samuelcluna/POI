#!/usr/bin/env bash
# Cria a VM a partir do VDI da disciplina (passos 2-7 do roteiro).
set -euo pipefail
source "$(dirname "$0")/env.sh"

[ -f "$VDI" ] || { echo "VDI não encontrado em $VDI (copie de /local/uasc/images para /tmp)" >&2; exit 1; }

VBoxManage createvm --name "$VM_NAME" --ostype Ubuntu_64 --basefolder "$VM_BASEDIR" --register
VBoxManage modifyvm "$VM_NAME" --cpus 1 --memory 1024 --nic1 nat \
  --natpf1 "app,tcp,,$APP_PORT,,8000" \
  --natpf1 "ssh,tcp,,$SSH_PORT,,22"
VBoxManage storagectl "$VM_NAME" --name SATA --add sata --controller IntelAhci
VBoxManage storageattach "$VM_NAME" --storagectl SATA --port 0 --device 0 --type hdd --medium "$VDI"
VBoxManage startvm "$VM_NAME" --type headless

echo "VM '$VM_NAME' criada e iniciada. Próximo passo: vm/setup_ssh.sh"
