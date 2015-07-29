#!/bin/bash
for cpu_id in `seq 0 7`; do
	echo $cpu_id
	cpufreq-set -c $cpu_id -f 3.4G
done	

