# Variáveis e funções usadas pelos scripts de VM.
VM_NAME="${VM_NAME:-poi-vm}"
VDI="${VDI:-/tmp/ubuntu_serve_2204_poi.vdi}"
VM_BASEDIR="${VM_BASEDIR:-/tmp}"
VM_USER="${VM_USER:-osboxes}"
VM_PASS="${VM_PASS:-osboxes.org}"
# portas no hospedeiro -> 22 e 8000 da VM
SSH_PORT="${SSH_PORT:-2222}"
APP_PORT="${APP_PORT:-8000}"
VM_APP_DIR="/home/$VM_USER/poi"

SSH_OPTS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR
  -o ConnectTimeout=5 -o BatchMode=yes)

vm_ssh() { ssh -p "$SSH_PORT" "${SSH_OPTS[@]}" "$VM_USER@localhost" "$@"; }
vm_scp_from() { scp -P "$SSH_PORT" "${SSH_OPTS[@]}" "$VM_USER@localhost:$1" "$2"; }
vm_sudo() { vm_ssh "echo '$VM_PASS' | sudo -S -p '' $*"; }

vm_running() { VBoxManage list runningvms | grep -q "\"$VM_NAME\""; }

wait_for() { # wait_for <segundos> <descrição> <comando...>
  local timeout="$1" what="$2" start=$SECONDS
  shift 2
  until "$@" >/dev/null 2>&1; do
    if ((SECONDS - start > timeout)); then
      echo "tempo esgotado esperando: $what" >&2
      return 1
    fi
    sleep 2
  done
}
