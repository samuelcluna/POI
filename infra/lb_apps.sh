#!/usr/bin/env bash
# Aponta os pools das apps no balanceador para as NodePorts da VM. Rodar com o openrc carregado.
set -euo pipefail

VM=grupo-7-k8s
LB=57c2b14a-b746-4f34-8719-d0627e409609
SUBNET=provider-sub
VM_IP=$(openstack server show "$VM" -f value -c addresses | grep -oE '10\.5\.[0-9]+\.[0-9]+')

espera() { until [ "$(openstack loadbalancer show $LB -f value -c provisioning_status)" = ACTIVE ]; do sleep 3; done; }

# app -> NodePort; os listeners 8071-8073 e os health monitors já existem desde a atividade 3
for par in cpu:30081 memory:30082 io:30083; do
  app=${par%%:*} port=${par##*:}
  pool=grupo-7-$app-pool
  if openstack loadbalancer member list "$pool" -f value -c address -c protocol_port | grep -q "^$VM_IP $port$"; then
    echo "$pool já aponta para $VM_IP:$port"; continue
  fi
  espera
  openstack loadbalancer member create --subnet-id "$SUBNET" --address "$VM_IP" --protocol-port "$port" \
    --name "$VM-$app" "$pool"
done
espera

for app in cpu memory io; do
  echo "== grupo-7-$app-pool"
  openstack loadbalancer member list "grupo-7-$app-pool" -c name -c address -c protocol_port -c operating_status
done
