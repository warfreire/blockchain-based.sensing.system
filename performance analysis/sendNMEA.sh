#!/bin/bash
############################################################################
# Performance Analysis
#
# This script send NMEA entries from a client to a server in a 
# Maritime Monitoring System. It is used to compare the perfomance
# of the blockchain MMS and a protocol that also uses symmetric and 
# asymmetric cryptography.

# @author: Warlley Paulo Freire - CIAW
# @date Mar/2021
############################################################################

# the script reads the NMEA entries saved by the AIS application in a text file.
for linha in $(cat saida_ais.out); 
do 
    # replace with your server username and IP
    ssh warlleyfreire@192.168.0.3 "echo $linha >> saidaAIS.txt "

done
