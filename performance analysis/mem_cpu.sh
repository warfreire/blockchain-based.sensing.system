#!/bin/bash
############################################################################
# Performance Analysis
#
# This script collects statistics related to CPU and MEM usage of blockchain 
# client and save it in a text file.
#
# @author: Warlley Paulo Freire - CIAW
# @date Mar/2021
############################################################################

C="/tmp/medicao.txt"

> $C

while [ 1 ]; do
	MEM=$(free -mh | grep -i mem | awk '{ print $3; }')
	CPU=$(top -n1 | grep Cpu | awk '{print $2"%" " " $4"%";}')
	echo $MEM $CPU >> $C
	sleep 2
done
