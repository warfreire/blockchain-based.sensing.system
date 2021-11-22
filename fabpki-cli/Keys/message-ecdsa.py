"""
    The Blockchain Sensing System Experiment
    ~~~~~~~~~
    This module is necessary to send data to the blockchain. It
    receives the AIS data and its respective public key.
    
        
    :copyright: © 2020 by Wilson Melo Jr.
"""

import sys
from hfc.fabric import Client as client_fabric
import asyncio
import base64
import hashlib
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sigencode_der, sigdecode_der

domain = "1dn.mb" #you can change for "inmetro.br"
channel_name = "mb-channel"
cc_name = "fabpki"
cc_version = "1.0"

if __name__ == "__main__":

    #test if the meter ID was informed as argument
    if len(sys.argv) != 4:
        print("Usage:",sys.argv[0],"<sender id> <message> <receiver id>")
        exit(1)

    #get the meter ID
    sender_id = sys.argv[1]
    message = sys.argv[2]
    receiver_id= sys.argv[3]

    #format the name of the expected private key
    priv_key_file = sender_id + ".priv"

    #try to retrieve the private key
    try:
        print(priv_key_file)
        with open(priv_key_file, 'r') as file:
            priv_key = SigningKey.from_pem(file.read())
    except:
        print("I could not find a valid private key to the meter",sender_id)
        exit(1)

    #signs the message using the private key and converts it to base64 encoding
    signature = priv_key.sign(message.encode(), hashfunc=hashlib.sha256, sigencode=sigencode_der)
    b64sig = base64.b64encode(signature)

    #giving the signature feedback
    print("Continuing with the information...\nmessage:", message, "\nsignature:", b64sig)

    #creates a loop object to manage async transactions
    loop = asyncio.get_event_loop()

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain, 'Admin')
    callpeer = "peer0." + domain
    
    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually
    c_hlf.new_channel(channel_name)

    #invoke the chaincode to send the messeger
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=[callpeer],
        cc_name=cc_name, 
        cc_version=cc_version,
        fcn='sendMessage', 
        args=[sender_id, message, receiver_id, b64sig], 
        cc_pattern=None))

    #the signature checking returned... (true or false)
    print("The message was send from", sender_id,"to ", receiver_id)
