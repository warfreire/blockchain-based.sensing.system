"""
    The Blockchain Sensing System Experiment
    ~~~~~~~~~
    This module is necessary to send data to the blockchain. It
    receives the AIS data and its respective public key.
    
        
    :copyright: © 2020 by Wilson Melo Jr.
"""


from hfc.fabric import Client as client_fabric
import asyncio
import sys
import datetime


domain = "1dn.mb" #you can change for "2dn.mb"
channel_name = "mb-channel"
cc_name = "fabpki"
cc_version = "1.0"

#use the following code if you want do decode NMEA entries before sending to the blockchain
#def log( str ):
#  now = datetime.datetime.now()
#  data = now.strftime("%Y-%m-%d %H:%M:%S")
#  arquivo_log.write( data + ' - ' + str + "\n" ) 

# log nmea
#def log_nmea( str, nome_estacao ):
#  now = datetime.datetime.now()
#  data = now.strftime("%Y-%m-%d_%H")
#  arquivo_log_nmea = open( '/home/alarmes/scripts/cron/ais/nmea/' + nome_estacao.lower() + '_' + data + '.txt', 'a+')
#  arquivo_log_nmea.write( str.replace(nome_estacao.upper(), '') )

#log nmea decodificado
#def log_nmea_decodificado( str_nmea, nome_estacao ):
#    now = datetime.datetime.now()
#    data = now.strftime("%Y-%m-%d_%H")
#    arquivo_log_nmea_decod = open( '/home/alarmes/scripts/cron/ais/nmea_decodificado/' + nome_estacao.lower() + '_' + data + '.txt', 'a+')
#    try:	
#        ais_message = NMEAMessage.from_string( str_nmea )
#        message = ais_message.decode().content
#        #print( ais_message.decode() )
#         # adiciona data
#        message["date"]=datetime.datetime.utcnow().strftime("%Y%m%d-%k%M")
#        #print( message )			
#        arquivo_log_nmea_decod.write( str(message) + "\r\n" )	
#    except Exception as e:
#        log( "Erro no seguinte NMEA: " + str_nmea )
#        log(str(traceback.format_exc()))
#        traceback.print_exc(file=sys.stdout)
#        print(e)


if __name__ == "__main__":

    #test if the fuction received no parameters
    if len(sys.argv) != 1:
        print("Usage only:",sys.argv[0]," ")
        exit(1)

    #creates a loop object to manage async transactions
    loop = asyncio.get_event_loop()

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain, 'Admin')
    callpeer = "peer0." + domain
    
    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually
    c_hlf.new_channel(channel_name)

    #open the AIS file
    arquivo_log = open( 'saida_ais.out.txt', 'r')
    
    estacao= ("pi")
    
    linhas = arquivo_log.readlines()
    
    for l in linhas:
        now = datetime.datetime.now()
        data = now.strftime("%Y-%m-%d_%H:%M")
        arquivo_log = ( data + ' - ' + estacao + "\n" )

     #   ais_message = NMEAMessage.from_string( l )
     #   message = ais_message.decode().content
       
        # adiciona data
        #message["date"]=datetime.datetime.utcnow().strftime("%Y%m%d-%k%M")
        #print(arquivo_log)
        #print( str(message))
       
        response = loop.run_until_complete(c_hlf.chaincode_invoke(
            requestor=admin, 
            channel_name=channel_name, 
            peers=[callpeer],
            cc_name=cc_name, 
            cc_version=cc_version,
            fcn='sendMessage', 
            args=[arquivo_log, l], 
            cc_pattern=None))

   #   # le socket do receptor AIS
 #   HOST='127.0.0.1'
 #   PORT='10110'
 #   tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 #   dest = (HOST, PORT)
 #   tcp.connect(dest)
 #   msg = ''
 #   while True:
 #       try:
 #           msg = tcp.recv(1024)
 #           print(msg)
 #       except Ex:
 #           tcp.close()
 #           print("Erro de conexao")  
