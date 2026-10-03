# VM VirtualBox

Scripts para os passos do roteiro da disciplina. Rodam no hospedeiro e falam com a VM por SSH
(porta 2222 do hospedeiro → 22 da VM). A aplicação fica em `http://localhost:8000` no hospedeiro.

## Passo a passo

```bash
cp /local/uasc/images/ubuntu_serve_2204_poi.vdi /tmp/   # no LCC; o roteiro pede /tmp
vm/create_vm.sh        # cria a VM (1 vCPU, 1 GB), redireciona portas e inicia
vm/setup_ssh.sh        # instala sua chave SSH na VM (pede a senha osboxes.org uma vez)
vm/deploy.sh cpu       # ou memory, io
curl localhost:8000/health
```

Se `setup_ssh.sh` não conectar, a imagem está sem servidor SSH. Abra o console da VM pelo
VirtualBox (login `osboxes`, senha `osboxes.org`) e rode `sudo apt install -y openssh-server`.

Para mudar o provisionamento manualmente:

```bash
vm/configure_vm.sh 2 2048    # 2 vCPUs, 2 GB: desliga, altera e religa a VM
```

O serviço `poi-app` (systemd) sobe com a VM e usa um worker por vCPU, então acompanha o cenário
sem redeploy. Na VM: `systemctl status poi-app`, `journalctl -u poi-app`.

## Pela interface gráfica

Equivalente ao `create_vm.sh`, seguindo o roteiro: Novo → pasta `/tmp`, tipo Linux / Ubuntu 22.04
(64-bit) → 1 CPU e 1024 MB → usar disco existente (o VDI em `/tmp`). Depois, com a VM desligada,
Configurações → Rede → Avançado → Redirecionamento de Portas, com duas regras TCP:

| Nome | Porta do hospedeiro | Porta do convidado |
|---|---|---|
| app | 8000 | 8000 |
| ssh | 2222 | 22 |

vCPUs e memória ficam em Configurações → Sistema.

## Variáveis

`vm/env.sh` define `VM_NAME` (`poi-vm`), `VDI`, `SSH_PORT`, `APP_PORT`, `VM_USER` e `VM_PASS`;
todas podem ser sobrescritas pelo ambiente.
