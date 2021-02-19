##########################################################################
# MB BLOCKCHAIN NETWORK EXPERIMENT - MSP CONFIG - March/2021
# This script generates the mbblocknet MSP structure (cryptographic keys 
# and certificates). All these stuffs are created in a directory called
# crypto-config. The script also generates the network genesis block, the
# mb-channel profile and the anchors profile to update the channel after
# its creation. The script consumes the configurations in the files 
# crypto-config-mb.yaml and configtx.yaml.
# Author: Wilson S. Melo Jr. - Inmetro
##########################################################################
#/bin/bash
export FABRIC_CFG_PATH=$PWD

cd "$(dirname "$0")"

# generates MSP artefacts (keys, digital certificates, etc) in the folder ./crypto-config
cryptogen extend --config=./crypto-config-mb.yaml

# creates the genesis block
configtxgen -profile MBGenesis -outputBlock ./mb-genesis.block

# creates the channel config file 
configtxgen -profile MBChannel -outputCreateChannelTx ./mb-channel.tx -channelID mb-channel

# creates anchors config for each organization 
configtxgen -profile MBChannel -outputAnchorPeersUpdate 1dn.mb-anchors.tx -channelID mb-channel -asOrg 1DN
configtxgen -profile MBChannel -outputAnchorPeersUpdate 2dn.mb-anchors.tx -channelID mb-channel -asOrg 2DN
