#!/usr/bin/env bash
# Roda dentro da VM (Ubuntu 24.04). Na primeira vez, sair e entrar de novo depois do usermod.
set -euo pipefail

if ! command -v docker >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y docker.io conntrack curl
  sudo usermod -aG docker "$USER"
  echo "docker instalado: saia, entre de novo por SSH e rode este script outra vez"
  exit 0
fi

if ! command -v kubectl >/dev/null; then
  curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
fi

if ! command -v minikube >/dev/null; then
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install -m 0755 minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
fi

# --ports publica as NodePorts na interface da VM, que é onde o balanceador entrega o tráfego
minikube start --driver=docker --cpus=4 --memory=6144 \
  --ports=30081:30081 --ports=30082:30082 --ports=30083:30083 \
  --listen-address=0.0.0.0

kubectl get nodes -o wide
