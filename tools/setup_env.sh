#!/bin/bash

ip tuntap add mode tap dev tap0 user inets
ip addr add dev tap0 192.168.200.1/24
ip link set dev tap0 up

for cpu_id in `seq 0 7`; do
    cpufreq-set -c $cpu_id -f 2.7G
done	

sysctl -w net.core.rmem_max=33554432
sysctl -w net.core.wmem_max=33554432
