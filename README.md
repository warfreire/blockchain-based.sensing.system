# The Inter-NMI Experiment: An experimental blockchain network among National Metrology Institutes

This repository contains the implementation of the **The Inter NMI Experiment**, developed in cooperation between the Physikalisch-Technische Bundesanstalt (PTB) and the National Institute of Metrology, Quality, and Technology (Inmetro), that are respectively the National Metrology Institutes in Germany and Brazil.

Research team:
* *Mahbuba Moni. (mahbuba.moni@ptb.de)*
* *Wilson S. Melo Jr. (wsjunior@inmetro.gov.br)*

Coordination:
* *Daniel Peters (peters@ptb.de)*
* *Wladmir Chapetta (wachapetta@inmetro.gov.br)*

## What the Inter-NMI Experiment is

The Inter-NMI Experiment is an experimental blockchain network formed by National Metrology Institutes around the world. It integrates servers provided by different NMIs and enables the implementation and test of smart contract-based applications related to metrology and conformity assessment. Researchers teams of all the involved NMIs can create their smart contracts and test them with the support of other NMIs.

We adopt [Hyperledger Fabric 1.4 LTS](https://hyperledger-fabric.readthedocs.io/en/release-1.4/) as our blockchain platform. We configure global distributed blockchain network which that support the execution of chaincodes writen in Golang.

We describe in the next sections the main aspects related to the Inter-NMI blockchain network customizing, how to instantiate the network, how to deploy a chaincode and how use a simple Python client to invoke it.

We also invite the reader to check out our previous publications related to this project. They are listed below:
* [here](https://link.springer.com/chapter/10.1007%2F978-3-030-39445-5_51).

## The customized blockchain network

We provide a flexible Fabric blockchain network configuration, initially with three organizations. The first one is the **Orderer** organization, which encapsulates the Inter-NMI network orderer service. So far, we are using the *solo orderer* provided for Fabric. However, we intent to replace it for a complete consensus service as soon as possible. The second and third organizations are **PTB** (under the virtual domain *ptb.de*) and **Inmetro** (under de virtual domain *inmetro.br*). 

PTB and Inmetro represents the NMIs that integrates the Inter-NMI network at the moment. In the Inter-NMI initial configuration, each organization provides two peers (peer0 and peer1). The configuration also considers that peer0 in both organizations are endorser peers, and peer1 are only commit peers. However, the configuration is flexible and the network administrator in each organization can easily change it to include more peers and also to change peers' roles. We also use [couchdb](https://hyperledger-fabric.readthedocs.io/en/release-1.4/couchdb_tutorial.html) containers to improve the performance on storing the ledger state on each peer.

All the configuration files related to the blockchain network  are in the base folder. The main files are:

* [configtx.yaml](configtx.yaml): basic network profile of Inter-NMI blockchain network.
* [crypto-config-nmi.yaml](crypto-config-nmi.yaml): (Membership Service Provider) configuration. We generate all the digital certificates from it.
* [peer-ordererer.yaml](peer-orderer.yaml): contains the orderer docker container configuration for the Orderer organization.
* [peer-ptb.yaml](peer-ptb.yaml): contains the docker containers configuration for the PTB peers. It extends the file [peer-base.yaml](peer-base.yaml) which constitutes a template of standard configuration items.
* [peer-inmetro.yaml](peer-inmetro.yaml): contains the docker containers configuration for the Inmetro peers. It also extends the file [peer-base.yaml](peer-base.yaml), just like the PTB peers configuration.
* [.env](.env): this file works as a source for environment variables in the docker configuration. So we use it to transcribe the IP addresses of each peer.

If you are not used to the Hyperledger Fabric, we strongly recommend this [tutorial](https://hyperledger-fabric.readthedocs.io/en/release-1.4/build_network.html). It teachs in details how to create a basic Fabric network.

You can load and use the Inter-NMI network by executing the steps in the following subsections. All the commands must be executed into the repository base folder.

### 1. Prepare the host machine

You need to install the **Hyperledger Fabric 1.4 LTS** basic software and [dependencies](https://hyperledger-fabric.readthedocs.io/en/release-1.4/prereqs.html). We try to make things simpler to you by providing a shell script that installs all these stuffs in a clean **Ubuntu 18.04 LTS** system. If you are using this distribution, our script works for you. If you have a different distribution, you can still try the script or you can customize it to work in your system.

Execute the [installation script](prerequirements/installFabric.sh):

```console
./installFabric.sh
```

**OBSERVATION**: You do not need to run the script as *sudo*. The script will automatically ask for your *sudo* password when necessary. That is important to keep the docker containers running with your working user account.

### 2. Generate the MSP artifacts

The MSP artifacts include all the cryptographic stuff necessary to identify the peers of a Fabric network. They are basically assymetric criptographic key pairs, and self-signed digital certificates. Since the Inter-NMI is a multi-host configuration, it is important that the hosts have the same MSP artifacts. At the moment, we are working on a security policy to generate and distribute the MSP artifacts among organizations. As a workaround, only one organization must execute this procedure, and replicate the MSP artifacts for the others. 

Before executing this step, check if the environment variable FABRIC_CFG_PATH is properly defined. If it is not, uncomment the following line in the script [configmsp.sh](configmsp.sh).

```console
export FABRIC_CFG_PATH=$PWD
```

After, execute the script:

```console
./configmsp.sh
```

This script uses [configtx.yaml](configtx.yaml) and [crypto-config-nmi.yaml](crypto-config-nmi.yaml) to create the MSP certificates in the folder **crypto-config**. It also generates the genesis block file *nmi-genesis.block*, the channel configuration file *nmi-channel.tx* and the anchor peers transaction files *ptb.de-anchors.tx* and *inmetro.br-anchors.tx*. Notice that this script depends on the tools installed together with Fabric. The script *installFabric.sh* executed previously is expected to modify your $PATH variable and enable the direct execution of the Fabric tools. If this does not happen, try to fix the $PATH manually. The tools usually are in the folder /$HOME/fabric-samples/bin.

### 3. Manage the docker containers

We use the **docker-compose** tool to manage the docker containers in our network. It basically reads the peer-*.yaml files and creates/starts/stops all the containers or a specific group of containers. You can find more details in the [Docker Compose Documents](https://docs.docker.com/compose/).

Before starting, it is important you check the proper content in the file [.env](.env). This file constitute a mechanism to use environment variables into the docker-compose configuration files (*.yaml). In our case, especifically, we use the  *.env* to define the external IP addresses of our servers. This is necessary at the moment, since we are working with virtual domain names. So check your *.env* file and verify if the IP addresses are correct before continuing.

You must use the following command with the respective organization config to start the containers. If your organization is the PTB, your command will be:

```console
docker-compose -f peer-ptb.yaml up -d
```

If your organization is also responsible for hosting the orderer service, you also need to start it. You can use the same command mentioned before, only replacing the .yaml file with [peer-orderer.yaml](peer-orderer.yaml). If this container is running in the same server that hosts your ordinary containers, you *MUST* start them together, by informing both files, as follows:

```console
docker-compose -f peer-orderer.yaml -f peer-ptb.yaml up -d
```

The same tool can be used to stop the containers, just in case you need to stop the blockchain network for any reason. In a similar manner as done before, use the following command to stop all the containers:

```console
docker-compose -f peer-ptb.yaml stop
```

If you need to reset and restart a complete new set of peers, use the provided script [teardown.sh](teardown.sh), informing the same .yaml file used to start the containers before, for instance:

```console
./teardown.sh peer-ptb.yaml
```

### 4. Create the Fabric channel and join the peers

The next step consists in creating a channel (in practice, the ledger among the peers) and join all the active peer on it. It is important to remember that the channel is created only once. Thus the first organization to start its peers *MUST* create the channel. The next organizations will only fetch for an existent channel and join on it. Both situations are implemented by the script [configchannel.sh](configchannel.sh). You need to execute it informing your organization domain (e.g., ptb.de or inmetro.br) and the parameter *-c* if you want also to create the channel:

```console
./configchannel.sh ptb.de -c
```

If you succeed in coming so far, the Hyperledger Fabric shall be running in your server, with an instance of your respective organization network profile. You can see information from the containers by using the following commands:

```console
docker ps
docker stats
```

### 5. Manage a chaincode

Chaincode are smart contracts in Fabric. In this document, we assume you already know how to implement and deploy a chaincode. If it is not your case, there is a [nice tutorial](https://hyperledger-fabric.readthedocs.io/en/release-1.4/chaincode4ade.html) that covers a lot of information about this issue. We strongly recomend you to check it before continuing.

If you already know everything you need about developing and deploying a chaincode, we can talk about how to install, instantiate and upgrade chaincodes in the Inter-NMI blockchain network. As an example, we use the **fabpki** chaincode, which we developed in one of our [previous works](https://doi.org/10.1109/MetroInd4.0IoT48571.2020.9138246).
This chaincode contains basic methods that provides elementary PKI services by using the [Golang ECDSA Library](https://golang.org/pkg/crypto/ecdsa/). A copy of the chaincode source is available [here](fabpki/fabpki.go). If you need more details about this chaincode implementation, please consult our paper.

Our blockchain network profiles include, for each organization, a client container *cli0* which effectively manages chaincodes. The *cli0* is necessary to compile the chaincode and install it in an endorser peer. It is also very helpful to test chaincodes. Basically, it provides an interface to execute the command *peer chaincode*, which the documentation can be found [here](https://hyperledger-fabric.readthedocs.io/en/release-1.4/commands/peerchaincode.html). We strongly recommend you read this documentation before continuing.

By default, the *cli0* is always associated with the *peer0* of the respective organization. However, you can easily change it to also work with the *peer1*, or even replicate the configuration and create additional client containers. We also provide the script [configchaincode.sh](configchaincode.sh) that encapsulates the use of a client container and simplifies the chaincode life cicle management. The script has the following sintax:

```console
./configchaincode.sh install|instantiate|upgrade <CLI container> <chaincode name> <chaincode version>
```

#### How to install a chaincode

Use the **install** command to enable the chaincode execution for a given peer. In practice, you are making this peer an __endorser__. You must reexecute the install command every time you change the chaincode version. Assuming you are using cli0 to install the chaincode fabpki, version 1.0, your command will be:

```console
./configchaincode.sh install cli0 fabpki 1.0
```

Remeber that the chaincode source code must be in a folder with the same name, into your base folder, just like we did with the provided [fabpki](fabpki) example.

#### How to instantiate a chaincode

Use the **instantiate** command to instantiate the chaincode in a the Inter-NMI default channel, i.e. **nmi-channel**. In practice, you are notifying the blockchain network that the chaincode exists (by creating a entry in the ledger with the chaincode hash) and consequently authorizing endorser peers to execute it.

```console
./configchaincode.sh install cli0 fabpki 1.0
```

IMPORTANT: While the install command define endorser peers, the instantiate command notifies all the peers in a channel that they may execute the chaincode. Consequently, the install can be done in many peers we consider necessary. On the other hand, the instantiate is once only once. So, if other organization already instantiate the chaincode, you do not need to (and in fact, you cannot) instantiate it again. If you change anything in your chaincode, you will need to upgrade it, as we describe in the next section.

#### How to upgrade a chaincode

Use the **upgrade** command to enable a new version of the chaincode. That is necessary for any chaincode that was already instantiated before. Notice that a upgraded chaincode need to be re-installed in each one of its endorser peers.

```console
./configchaincode.sh upgrade cli0 fabpki 1.1
```

## Dealing with client applications

The client application is a set of Python 3 modules that use the chaincode services provided by the blockchain network. They make use of the Python ECDSA Library (which implements the our cryptosystem) and the Fabric Python SDK.

You need to install some dependencies and libraries before geting the clients running properly. We described all the steps necessary to prepare your machine to do that.

### Get pip3

Install the Python PIP3 using the following command:

```console
sudo apt install python3-pip
```

### Get the ECDSA Python Library

The ECDSA Library implements the directives related to the Elliptic Curves algorithms. You can find more details [here](https://pypi.org/project/ecdsa/). Run the following command to install the ECDSA Library.

```console
pip3 install ecdsa
```

### Get the Fabric Python SDK

The [Fabric Python SDK](https://github.com/hyperledger/fabric-sdk-py) is not part of the Hyperledger Project. It is maintained by an independent community of users from Fabric. However, this SDK works fine, at least to the basic functionalities we need.

Recently, we have problems with broke interfaces that made our programs stoped of running. So we adopted the 0.8.0 version of the Python SDK (and the respective tag) as our "stable" version.

You need to install the Python SDK dependencies first:

```console
sudo apt-get install python-dev python3-dev libssl-dev
```

Finally, install the Python SDK using *git*. Notice that the repository will be cloned into the current path, so we recommend you install it in your $HOME directory. After cloning the repository, is necessary to checkout the tag associated to the version 0.8.0.

```console
cd $HOME
git clone https://github.com/hyperledger/fabric-sdk-py.git
cd fabric-sdk-py
git checkout tags/v0.8.0
sudo make install
```

### Configure the .json network profile
The Python SDK applications depend on a network profile encoded in a .json format. Since we have two independent organizations, the network profile changes accordingly to them. In this repository, we provide the files [ptb.de.json](fabpki-cli/ptb.de.json) and [inmetro.br.json](fabpki-cli/inmetro.br.json) file. The network profile keeps the necessary credentials to access the blockchain network. You must configure this file properly every time that you create new digital certificates in the MSP:

* Open the respective .json in a text editor;
* Check for the entries called "tlsCACerts", "clientKey", "clientCert", "cert" and "private_key" on each organization. Notice that they point out to different files into the (./cripto-config) directory that corresponds to digital certificates and keys of each organization. The private key must correspond to the user whom will submit the transactions (by default, we use Admin);
* Check the MSP file structure in your deployment and verify the correct name of the files that contain the certificates or keys;
* Modify the .json file with the correct name and path of each required file.

### The Client Application modules

The Client Application includes the following modules:

* [keygen-ecdsa.py](fabpki-cli/keygen-ecdsa.py): It is a simple Python script that generates a pair of ECDSA keys. These keys are necessary to run all the other modules.
* [register-ecdsa.py](fabpki-cli/register-ecdsa.py): It invokes the *registerMeter* chaincode, that appends a new meter digital asset into the ledger. You must provide the respective ECDSA public key.
* [verify-ecdsa.py](fabpki-cli/verify-ecdsa.py): It works as a client that verifies if a given digital signature corresponds to the meter's private key. The client must provide a piece of information and the respective digital signature. The client module will inform **True** for a legitimate signature and **False** in the opposite.


## Using the Hyperledger Explorer

The [Hyperledger Explorer](https://www.hyperledger.org/projects/explorer) is a web tool that helps to monitor the blockchain network with a friendly interface. Our repository includes the extensions to use Explorer together with our experiment. We take the Explorer container-based distribution, that consists of two Docker images:
* **explorer**: a web server which delivers the application.
* **explorer-db**: a PostgreSQL database server that is required to run Explorer.

The following steps describe how to start and stop Explorer. Firstly, make sure that the blockchain network is up and that you executed the previous steps related to install and instantiate the *fabpki* chaincode. You can check these points with the following command:

```console
docker ps
```
The Explorer is also a blockchain client. So, before continuing, you must fix the Explorer connection profile, just like you did previously to the Python client. Again, we have this configuration in the files files [ptb.de.json](explorer/ptb.de.json) and [inmetro.br.json](explorer/inmetro.br.json) file. Notice that these files are very similar to our Python client connection profile. The procedure to fix them is also the same, with the difference that the Explorer **must** use the Admin credentials. Find the entries called "tlsCACerts", "clientKey", "clientCert", "signedCert" and "adminPrivateKey" of each organization. Replace them with the respective filenames in your MSP configuration. Do not change the file path, because it already points to the container internal path that the Explorer knows. Finally, edit the file [config.json](explorer/config.json) to point out for your organization connection profile.

Now, access the [explorer](explorer) folder and start the Hyperledger Explorer containers. If you are working with the PTB organization, your command is:
```console
cd explorer
docker-compose -f explorer-ptb.yaml up -d
```

The first execution will pulldown the Docker images, and also create the PostgresSQL database. These procedures can require some time to execute. Wait 30 seconds and open the following local address in a web browser: [http://localhost:8080](http://localhost:8080). You must see the Hyperledger Explorer login screen.

If you need to stop or shutdown the Hyperledger Explore, proceed with the respective *docker-compose* commands, using *stop* to suspend the containers execution and *down* to remove the containers' instances. Here is as example:
```console
docker-compose -f explorer-ptb.yaml down
```

Eventually, you will need to physically remove the database volumes associated with the Hyperledger Explorer. You can do that by executing the following commands:
```console
docker volume prune
docker volume rm explorer_pgdata explorer_walletstore
```

