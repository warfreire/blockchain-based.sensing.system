# Blockchain-based Maritime Monitoring System (MMS): An experimental blockchain prototype to protect critical maritime sensing data 

[This is the Blockchain-based MMS v 2.1 prototype. The v 2.0 prototype relative to the IEEE 2021 MetroSea article is [here](https://github.com/warfreire/blockchain-based.sensing.system/tree/2.0)] 

This repository contains the implementation of a **Blockchain-based MMS**, developed in cooperation between the Admiral Wandenkolk Instruction Center (CIAW), the National Institute of Metrology, Quality, and Technology (Inmetro), and Pontifical Catholic University (PUC-RJ).

Research team:
* *[Warlley Paulo Freire](https://www.researchgate.net/profile/Wilson-Melo-Junior) (paulo.freire@marinha.mil.br / warlleyfreire@gmail.com)*
* *[Wilson S. Melo Jr.](https://www.researchgate.net/profile/Wilson-Melo-Junior) (wsjunior@inmetro.gov.br)*
* *[Alan Oliveira de Sá](https://www.researchgate.net/profile/Wilson-Melo-Junior) (alan.oliveira.sa@gmail.com)*
* *[Vinicius Dalto do Nascimento](https://www.researchgate.net/profile/Wilson-Melo-Junior) (dalto@cos.ufrj.br)*


*Revised on June 10th, 2021.*

## What the experiment is:

This experiment was designed to evaluate the feasibility of a permissioned blockchain tailored to secure critical sensing data on a Maritime Monitoring System. To do so, we integrate the blockchain prototype with a low-cost Automatic Identification System (AIS) developed by the Brazilian Navy, and analyzed the overall perfomance of the system  receiving marine traffic data on a real environment. In this 2.1 version, we seek to adress scalability in a MMS, setting a Raft Consensus protocol and introducing a dockerized blockchain-client.   


We adopt [Hyperledger Fabric 1.4 LTS](https://hyperledger-fabric.readthedocs.io/en/release-1.4/) as our blockchain platform. We configure a globally distributed blockchain network that supports the execution of Golang chaincodes.

We describe in the next sections the main aspects related to the  blockchain network customizing, how to instantiate the network, how to deploy a chaincode, and how to use a simple Python client to invoke it.

We also invite the reader to check out our previous publications related to this project. They are listed below:

* [Freire, W., Melo, W., Nascimento, V., Sá, A. (2021). Blockchain-based Maritime Monitoring System](www.researchgate.com/warfreire/blockchain-basedmms)

* [Moni, M., Melo, W., Peters, D., & Machado, R. (2021). When Measurements Meet Blockchain: On Behalf of an Inter-NMI Network. Sensors, 21(5), 1564.](https://doi.org/10.3390/s21051564)

* [Melo, W., Machado, R. C., Peters, D., & Moni, M. (2020). Public-Key Infrastructure for Smart Meters using Blockchains. In 2020 IEEE International Workshop on Metrology for Industry 4.0 & IoT (pp. 429-434). IEEE.](https://doi.org/10.1109/MetroInd4.0IoT48571.2020.9138246)

* [Melo Jr., W. S., Bessani, A., Neves, N., Santin, A. O., & Carmo, L. F. R. C. (2019). Using Blockchains to Implement Distributed Measuring Systems. IEEE Transactions on Instrumentation and Measurement, 68(5), 1503–1512.](https://doi.org/10.1109/TIM.2019.2898013)



## The customized blockchain network

We provide a flexible Fabric blockchain network configuration, initially with three organizations. The first one is the **Orderer** organization, which encapsulates the blockchain network orderer service. Each and all orderer peers in the network reach consensus through the Raft Consensus protocol, adding fault tolerance mechanisms to the prototype(resilient even with 50% compromised peers). The second and third organizations are **1DN** (1st Naval District) and **2DN** (2nd Naval District) capable of receiving the AIS data of the sensing nodes and storing it on blockchain's Ledger. 

. In our configuration, each organization provides two peers (peer0 and peer1). The configuration also considers that peer0 in both organizations are endorser peers, and peer1 are only committer peers. However, the configuration is flexible, and the network administrator in each organization can easily change it to include more peers and also to change peers' roles. We also use [Couchdb](https://hyperledger-fabric.readthedocs.io/en/release-1.4/couchdb_tutorial.html) containers to improve the performance of storing the ledger state on each peer.

All the configuration files related to the blockchain network are in the base folder. The main files are:

* [configtx.yaml](configtx.yaml): basic network profile of Inter-NMI blockchain network.
* [crypto-config-mb.yaml](crypto-config-nmi.yaml): (Membership Service Provider) configuration. We generate all the digital certificates from it.
* [peer-ordererer.yaml](peer-orderer.yaml): contains the orderer docker container configuration for the Orderer organization.
* [peer-1dn.yaml](peer-1dn.yaml): contains the docker containers configuration for the 1DN peers. It extends the file [peer-base.yaml](peer-base.yaml), which constitutes a template of standard configuration items.
* [.env](.env): this file works as a source for environment variables in the docker configuration. So we use it to transcribe the IP addresses of each peer.

If you are not used to the Hyperledger Fabric, we strongly recommend this [tutorial](https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html). It teaches in detail how to create a basic Fabric network.

You can load and use the Inter-NMI network by executing the steps in the following subsections. You must execute all the commands into the repository base folder.

### 1. Prepare the host machine.

You need to install the **Hyperledger Fabric 1.4 LTS** basic software and [dependencies](https://hyperledger-fabric.readthedocs.io/en/release-1.4/prereqs.html). We try to make things simpler by providing a shell script that installs all these stuff (including the Fabric's **docker images in the version 1.4.9**) in a clean **Ubuntu 20.04 LTS** system. If you are using this distribution, our script works for you. If you have a different distribution, you can still try the script or customize it to work in your system.

Execute the [installation script](prerequirements/installFabric.sh):

```console
./installFabric.sh
```

**OBSERVATION**: You do not need to run the script as *sudo*. The script will automatically ask for your *sudo* password when necessary. That is important to keep the docker containers running with your working user account.

### 2. Generate the MSP artifacts

The MSP artifacts include all the cryptographic stuff necessary to identify the peers of a Fabric network. They are basically asymmetric cryptographic key pairs and self-signed digital certificates. As a workaround, only one organization must execute this procedure and replicate the MSP artifacts for the others. 

Before executing this step, check if the environment variable FABRIC_CFG_PATH is properly defined. If it is not, uncomment the following line in the script [configmsp.sh](configmsp.sh).

```console
export FABRIC_CFG_PATH=$PWD
```

After, execute the script:

```console
./configmsp.sh
```

This script uses [crypto-config-mb.yaml](crypto-config-mb.yaml) to create the MSP certificates in the folder **crypto-config**. It also uses [configtx.yaml](configtx.yaml) and generates the genesis block file *nmi-genesis.block*, the channel configuration file *nmi-channel.tx*, and the anchor peers transaction files *1dn.mb-anchors.tx*. Notice that this script depends on the tools installed together with Fabric. The script *installFabric.sh* executed previously is expected to modify your $PATH variable and enable the Fabric tools' direct execution. If this does not happen, try to fix the $PATH manually. The tools usually are in the folder /$HOME/fabric-samples/bin.

### 3. Manage the docker containers

We use the **docker-compose** tool to manage the docker containers in our network. It reads the peer-*.yaml files and creates/starts/stops all the containers or a specific group of containers. You can find more details in the [Docker Compose Documents](https://docs.docker.com/compose/).

Before starting, you must check the proper content in the file [.env](.env). This file constitutes a mechanism to use environment variables into the docker-compose configuration files (*.yaml). In our case, specifically, we use the  *.env* to define the external IP addresses of our servers. This definition is necessary at the moment since we are working with virtual domain names. So check your *.env* file and verify if the IP addresses are correct before continuing.

You must use the following command with the respective organization config to start the containers. If your organization is 1DN, your command will be:

```console
docker-compose -f peer-1dn.yaml up -d
```

If your organization is also responsible for hosting the orderer service, you also need to start it. You can use the same command mentioned before, only replacing the .yaml file with [peer-orderer.yaml](peer-orderer.yaml). If this container is running in the same server that hosts your ordinary containers, you *MUST* start them together, by informing both files:

```console
docker-compose -f peer-orderer.yaml -f peer-1dn.yaml up -d
```

The same tool can be used to stop the containers, just if you need to stop the blockchain network for any reason. In a similar manner as done before, use the following command to stop all the containers:

```console
docker-compose -f peer-1dn.yaml stop
```

If you need to reset and restart a complete new set of peers, use the provided script [teardown.sh](teardown.sh), informing the same .yaml file used to start the containers before, for instance:

```console
./teardown.sh peer-1dn.yaml
```

### 4. Create the Fabric channel and join the peers

The next step consists of creating a channel (in practice, the ledger among the peers) and joining all the active peers on it. It is important to remember that we create a channel only once. Thus the first organization to start its peers *MUST* create the channel. The following organizations will only fetch for an existing channel and join on it. The script [configchannel.sh](configchannel.sh) implements both situations. You need to execute it informing your organization domain (e.g., 1dn.mb or 2dn.mb) and the parameter *-c* if you also want to create the channel:

```console
./configchannel.sh 1dn.mb -c
```

If you succeed in coming so far, the Hyperledger Fabric shall be running in your server, with an instance of your organization network profile. You can see information from the containers by using the following commands:

```console
docker ps
docker stats
```

### 5. Manage a chaincode

Chaincodes are smart contracts in Fabric. In this document, we assume you already know how to implement and deploy a chaincode. If it is not your case, there is a [nice tutorial](https://hyperledger-fabric.readthedocs.io/en/release-1.4/chaincode4ade.html) covering a lot of information about this issue. We strongly recommend you to check it before continuing.

If you already know everything you need about developing and deploying a chaincode, we can talk about installing, instantiate, and upgrade chaincodes in the Inter-NMI blockchain network. We use the **fabpki** chaincode as an example, which we developed in one of our [previous works](https://doi.org/10.1109/MetroInd4.0IoT48571.2020.9138246).
This chaincode contains basic methods to process the AIS data by using the [Golang ECDSA Library](https://golang.org/pkg/crypto/ecdsa/). A copy of the chaincode source is available [here](fabpki/fabpki.go). If you need more details about this chaincode implementation, please consult our paper.

Our blockchain network profiles include, for each organization, a client container *cli0*, which effectively manages chaincodes. The *cli0* is necessary to compile the chaincode and install it in an endorser peer. It is also handy to test chaincodes. It provides an interface to execute the command *peer chaincode*, whose documentation is available [here](https://hyperledger-fabric.readthedocs.io/en/release-1.4/commands/peerchaincode.html). We strongly recommend you read this documentation before continuing.

By default, we associate *cli0* with the *peer0* of the respective organization. However, you can easily change it to work with the *peer1* too. You also can replicate its configuration to create additional client containers. We provide the script [configchaincode.sh](configchaincode.sh) that encapsulates the use of a client container and simplifies the chaincode life cycle management. The script has the following syntax:

```console
./configchaincode.sh install|instantiate|upgrade <CLI container> <chaincode name> <chaincode version>
```

#### How to install a chaincode

Use the **install** command to enable the chaincode execution for a given peer. In practice, you are making this peer an __endorser__. You must re-execute the install command every time you change the chaincode version. Assuming you are using cli0 to install the chaincode fabpki, version 1.0, your command will be:

```console
./configchaincode.sh install cli0 fabpki 1.0
```

Remember that the chaincode source code must be in a folder with the same name, into your base folder, just like we did with the provided [fabpki](fabpki) example.

#### How to instantiate a chaincode

Use the **instantiate** command to instantiate the chaincode in the Inter-NMI default channel, i.e., **nmi-channel**. In practice, you notify the blockchain network that the chaincode exists (by creating an entry in the ledger with the chaincode hash) and consequently authorizing endorser peers to execute it.

```console
./configchaincode.sh instantiate cli0 fabpki 1.0
```

IMPORTANT: While the install command defines endorser peers, the instantiate command notifies all the peers in a channel that they may execute the chaincode. Consequently, you can perform the install on many peers as necessary. On the other hand, you perform the instantiate only once. If another organization already instantiate the chaincode, you do not need to (and in fact, you cannot) instantiate it again. If you change anything in your chaincode, you will need to upgrade it, as we describe in the next section.

#### How to upgrade a chaincode

Use the **upgrade** command to enable a new version of the chaincode. That is necessary for any chaincode that you instantiated before. Notice that an upgraded chaincode needs to be re-installed in each one of its endorser peers.

```console
./configchaincode.sh upgrade cli0 fabpki 1.1
```

## Dealing with client applications

The client application is a set of Python 3 modules that use the blockchain network's chaincode services. They use the Python ECDSA library (which implements our cryptosystem) and the Fabric Python SDK.

You need to install some dependencies and libraries before getting the clients running correctly. We described all the steps necessary to prepare your machine to do that.

### Get pip3

Install the Python PIP3 using the following command:

```console
sudo apt install python3-pip
```

### Get the ECDSA Python Library

The ECDSA library implements the directives related to the Elliptic Curves algorithms. You can find more details [here](https://pypi.org/project/ecdsa/). Run the following command to install the ECDSA library.

```console
pip3 install ecdsa
```

### Get the Fabric Python SDK

The [Fabric Python SDK](https://github.com/hyperledger/fabric-sdk-py) is not part of the Hyperledger Project. It is maintained by an independent community of users from Fabric. However, this SDK works fine, at least to the basic functionalities we need.

Recently, we had problems with broke interfaces that made our programs stoped of running. Thus we adopted the 0.8.0 version of the Python SDK (and the respective tag) as our "stable" version.

You need to install the Python SDK dependencies first:

```console
sudo apt-get install python-dev python3-dev libssl-dev
```

Finally, install the Python SDK using *git*. Notice that the repository is cloned into the current path, so we recommend installing it in your $HOME directory. After cloning the repository, it is necessary to check out the tag associated with the version 0.8.0.

```console
cd $HOME
git clone https://github.com/hyperledger/fabric-sdk-py.git
cd fabric-sdk-py
git checkout tags/v0.8.0
sudo make install
```

### Configure the JSON network profile
The Python SDK applications depend on a **network profile** encoded in JSON format and the network profile changes accordingly to them. In this repository, we provide the file [1dn.mb.json](fabpki-cli/1dn.mb.json). The network profile keeps the necessary credentials to access the blockchain network. You must configure this file properly every time that you create new digital certificates in the MSP:

* Open the respective .json in a text editor;
* Check for the entries called "tlsCACerts", "clientKey", "clientCert", "cert" and "private_key" on each organization. Notice that they point out to different files into the (./cripto-config) directory that corresponds to digital certificates and keys of each organization. The private key must correspond to the user who will submit the transactions (by default, we use Admin);
* Check the MSP file structure in your deployment and verify the correct name of the files that contain the certificates or keys;
* Modify the .json file with the correct name and path of each required file;
* Also, verify the explicit IP addresses related to the known orderer and entry peer. They must reflect your network configuration.

### The Client Application module

The Client Application includes the following module:

* [sendMessage.py](fabpki-cli/keygen-ecdsa.py): It is a Python script that receive and process the AIS data received on NMEA format. This format is a standardization National Marine Electronics Association used in GPS, AIS, VTS and other maritime services.


## Monitoring local ledger copies with Fauxton and Mango

One of the advantages of using CouchDB is its database management system (DBMS) graphical interface. One can access the [Fauxton](https://couchdb.apache.org/fauxton-visual-guide/index.html#using-fauxton) project's web interface instance on each CouchDB container. First, observe in the docker containers list the active CouchDB containers (for example, in the 1dn.mb domain, they should be 1dndb0 and 1dndb1):

```console
docker ps | grep couchdb
```

In the returned containers list, notice the respective ports where each container is listening to for connections. For instance, the default configuration sets 1dndb0 and 1dndb1 in ports 5984 and 6984, respectively. Now, by assuming you have an Internet browser in your blockchain host, you can access the ptbdb0's Fauxton interface in the following URL: http://localhost:5984/_utils. Observe that you need to change this URL according to your own configuration (i.e., replace localhost with the respective IP and the port number with your own configuration port).

Once you have the CouchDB web interface opened, access the chaincode *fabpki* records link by clicking on the **nmi-channel_fabpki** option. You will be able to consult all the digital assets associated with this chaincode.

**IMPORTANT:** The CouchDB web interface does NOT use blockchain access mechanisms. It gives a direct view corresponding to the local ledger's copy in the respective peer container. Remember that any changes in the local ledger instance may compromise this replica.

CouchDB web interface also integrates the **Mango** tool for querying data. You need to write these queries in JSON format. At first glance, this format is a little complex. However, these JSON queries still make it easier to retrieve information from CouchDB. You can learn a little about Mango queries [here](https://docs.couchdb.org/en/latest/intro/tour.html?highlight=mango#running-a-mango-query). The code below illustrates how to run a query using Mango. Click on the option **Run a Query with Mango**, copy the code below to the **Mango Query** textbox, click on the **Run Query** button and observe the result. You will see that this query returns the record where the meter ID is "123".

```console
{
   "selector": {
      "_id": "123"
   }
}
```

## Performance Analysis

To analyze the feasibility of the Blockchain-based MMS, we evaluate the performance of the system. First we compare the client CPU and MEM consumption sending the AIS data to the server through SSH and then through blockchain transactions. We chose SSH protocol because, like blockchain mechanisms, it also employs symmetric and asymmetric cryptography.

To send AIS data through SSH, run the following script on the client:

```console
./sendNMEA.sh
```

And then simultaneously run the script that capture the client CPU and MEM consumption and save it in /tmp/medicao.txt:

```console
./mem_cpu.sh
```

Thereon you can send the AIS data through blockchain transactions and compare each performance to evaluate the blockchain overhead. Don't forget that you need to run all the containers, create the channel among the peers and install/instantiate the chaincode in the server as well as prepare your client application as explained in the previous topics. 

Then you need to invoke the python client function sendMessage.py to start sending each NMEA string as a transaction to the blockchain server:

```console
python3 sendMessage.py
```
And then simultaneously run the script that capture the client CPU and MEM consumption and save it in /tmp/medicao.txt:

```console
./mem_cpu.sh
```

Finally, you also need to simultaneously run the script that captures CPU and MEM consumption of each blockchain container in the server and save it in cpu.stats.txt: 
```console
./dockerstats.sh
```
