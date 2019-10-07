#!/usr/bin/env bash

IFACE_ID=868e530d-04aa-45f8-8afb-1a24f6175679
IFACE_IPV4=10.1.0.6
IFACE_IPV6=fd2a:d02c:d36b:1a::b
IFACE_MAC=fa:16:3e:5f:7f:44
IFACE_NAME=rx-miguel

# Set up namespace
sudo ip netns add ns-$IFACE_NAME
sudo ip netns exec ns-$IFACE_NAME ip link set lo up
sudo ip netns exec ns-$IFACE_NAME sysctl -w net.ipv6.conf.default.accept_ra=0

# Set up veth device
TAPNAME=tap${IFACE_ID::11}
DEVNAME=ns-${IFACE_ID::11}
sudo ip link add $TAPNAME type veth peer name $DEVNAME netns ns-$IFACE_NAME
sudo sysctl net.ipv6.conf.$TAPNAME.disable_ipv6=1
IFS=':'
a=($IFACE_MAC)
sudo ip netns exec ns-$IFACE_NAME ip link set $DEVNAME address ${a[0]}':'${a[1]}':'${a[2]}':'${a[3]}':'${a[4]}':'${a[5]}
sudo ip netns exec ns-$IFACE_NAME ip link set $DEVNAME mtu 1450
sudo ip link set $TAPNAME up
sudo ip netns exec ns-$IFACE_NAME ip link set $DEVNAME up

# Set up VIFs L3
IFS='.'
a=($IFACE_IPV4)
sudo ip netns exec ns-$IFACE_NAME ip addr add ${a[0]}.${a[1]}.${a[2]}.${a[3]}/24 broadcast ${a[0]}.${a[1]}.${a[2]}.255 dev $DEVNAME
sudo ip netns exec ns-$IFACE_NAME ip addr add $IFACE_IPV6/64  dev $DEVNAME

# Set up VIFs routes
sudo ip netns exec ns-$IFACE_NAME ip -4 route replace default via ${a[0]}.${a[1]}.${a[2]}.1 dev $DEVNAME
IFS=':'
a=($IFACE_IPV6)
sudo ip netns exec ns-$IFACE_NAME ip -6 route replace default via ${a[0]}:${a[1]}:${a[2]}:${a[3]}::1 dev $DEVNAME
