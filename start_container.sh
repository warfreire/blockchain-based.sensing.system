#!/bin/bash

cd /home/pfreire/Documentos/workspace/blockchain-based.sensing.system

count=32

while [ $count -gt 0 ]
do 
	docker-compose up > saida.txt &

	sleep 4

	CONTAINER_ID=$(docker ps | awk 'NR==2 { print $1; }')

	echo container $CONTAINER_ID
	/home/pfreire/Documentos/workspace/blockchain-based.sensing.system/performance-analysis/dockerstats.sh $(echo $CONTAINER_ID)
	((count--))
done
