#!/usr/bin/env bash
# Cria a VM do cluster e coloca no pool de SSH do balanceador. Rodar com o openrc carregado.
set -euo pipefail

VM=grupo-7-k8s
LB=57c2b14a-b746-4f34-8719-d0627e409609   # poi-atividades (há outro LB com o mesmo nome)
SUBNET=provider-sub

espera() { until [ "$(openstack loadbalancer show $LB -f value -c provisioning_status)" = ACTIVE ]; do sleep 3; done; }

openstack server create --flavor general.large --image ubuntu-24.04 --key-name samuel-key \
  --security-group default --security-group grupo-7 --wait "$VM"
VM_IP=$(openstack server show "$VM" -f value -c addresses | grep -oE '10\.5\.[0-9]+\.[0-9]+')
echo "VM $VM em $VM_IP"

# NodePorts das três apps
openstack security group rule create --protocol tcp --dst-port 30081:30083 grupo-7

espera
openstack loadbalancer member create --subnet-id "$SUBNET" --address "$VM_IP" --protocol-port 22 \
  --name "$VM-ssh" grupo-7-ssh-pool
