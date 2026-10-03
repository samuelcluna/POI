#!/usr/bin/env bash
# Copia sua chave SSH para a VM (pede a senha osboxes.org uma vez).
set -euo pipefail
source "$(dirname "$0")/env.sh"

ls ~/.ssh/id_*.pub >/dev/null 2>&1 || ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
ssh-copy-id -p "$SSH_PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$VM_USER@localhost"
vm_ssh "echo acesso por chave ok: \$(hostname), \$(nproc) vCPU"
