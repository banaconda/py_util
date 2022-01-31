#!/bin/bash
NET_ID=80
IP_WITH_MASK=80.0.0.254/24
GATEWAY=80.0.0.254
CIDR=80.0.0.0/24
ROUTER=br0

sudo ip link add veth.0.$NET_ID type veth peer name veth.$NET_ID.0
sudo ip link set veth.0.$NET_ID up
sudo ip link set veth.$NET_ID.0 up
sudo ovs-vsctl add-port $ROUTER veth.$NET_ID.0
sudo ip addr add $IP_WITH_MASK dev veth.0.$NET_ID
sudo ip route add $CIDR via $GATEWAY
