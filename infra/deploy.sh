#!/usr/bin/env bash
# Aplica os manifestos no cluster e espera as três apps ficarem prontas.
set -euo pipefail
cd "$(dirname "$0")/.."

kubectl apply -f k8s/namespace.yaml
kubectl apply -R -f k8s/cpu -f k8s/memory -f k8s/io

kubectl -n poi rollout status deployment/cpu --timeout=180s
kubectl -n poi rollout status deployment/memory --timeout=180s
kubectl -n poi rollout status statefulset/io --timeout=300s
kubectl -n poi get all,pvc -o wide
