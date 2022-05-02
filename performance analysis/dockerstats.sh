#!/bin/bash
############################################################################
# Performance Analysis
#
# This script collects statistics related to CPU usage of until 3 containers.
# They usually are the chaincode container (that is created in runtime and 
# usually has a composed name with the chaincode name), the endorser container
# (where the chaincode was installed) and the couchdb container associated with
# the endorser.
#
# The script output is a table with 3 collumns showing the CPU usage curve.
#
# @author: Wilson S. Melo - Inmetro
# @date Mar/2019
############################################################################

#test if we have the paramaters
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <blk-client container ID>" >&2
  exit 1
fi

#remove any previous cpu.stats file
rm -f cpu.stats


mem=0
cpu=0
count=0
OUT=""
DATE=$(date +"%Y%m%d%H%M%S")
while [ -z `echo -n $OUT | egrep "0.00"` ]; 
do 	
	OUT=$(docker stats $1 $2 $3 $4 --no-stream | awk '{print $3 $4}' | tr '\n' ' ' | tr -d 'NAME' | tr -d 'CPU' )
	echo $OUT >> ./resultados/cpu.stats.$DATE; 
	
    str_mem=$(echo $OUT | tr '%'  ' ' | tr 'iB' ' ' | awk '{print $2;}' )
    mem=$(echo $mem + $str_mem | bc )

    str_cpu=$(echo $OUT | tr '%'  ' ' | tr 'iB' ' ' | awk '{print $1;}' )
    cpu=$(echo $cpu + $str_cpu | bc )    

    ((count++))
done
media_cpu=$(echo $cpu / $count | bc -l)
media_mem=$(echo $mem / $count | bc -l)
echo -n "media_mem="  
echo "scale=2;$mem / $count" | bc
echo -n "media_cpu="  
echo "media cpu=" | echo "scale=2;$cpu / $count" | bc
echo $media_cpu >> ./resultados/cpu.stats.$DATE; 
echo $media_mem >> ./resultados/cpu.stats.$DATE; 
