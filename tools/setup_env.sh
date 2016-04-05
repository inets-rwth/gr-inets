#!/bin/bash

for cpu_id in `seq 0 7`; do
    cpufreq-set -c $cpu_id -f 2.7G
done	

sysctl -w net.core.rmem_max=33554432
sysctl -w net.core.wmem_max=33554432
