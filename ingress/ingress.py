#Author: Peter Gutstein
import socket
import time

#Important variables
localIP = ""
localPort = 20001
bufferSize = 65507

#IP address of clients/workers
clientIPAdresses = []
workerIPAdresses = []

#Wait .5 seconds for TCPDUMP to get up first
time.sleep(.5)

# Create a datagram socket
UDPIngressSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPIngressSocket.bind((localIP, localPort))
print("UDP ingress up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPIngressSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    #Worker header (1 byte long)
    if len(message) == 1:
        if b'\x00' in message:
            #Acknowledge client message/IP and print
            print("Worker ping acknowledged")
            #Save client IP for later use
            workerIPAdresses.append(address)
            # Sending a reply to client
            bytesToSend = (1).to_bytes(1, 'big')
            UDPIngressSocket.sendto(bytesToSend, address)

    #Initial client header (2 bytes long)
    elif len(message) == 2:
        #Add address if not in clientIPAdresses
        if not(address in clientIPAdresses):
            clientIPAdresses.append(address)

        #Client number = position of address in clientIPAdresses
        clientNum = clientIPAdresses.index(address)
        #3 bytes long (byte 1 = clientNum | byte 2,3 = fileNumber)
        bytesToSend = clientNum.to_bytes(1, 'big') + message
        #Assign worker to client job
        print("Assigning worker #" + str(clientNum) + " to task")
        UDPIngressSocket.sendto(bytesToSend, workerIPAdresses[clientNum])

    #Acknowledgement of packet from client (9 bytes long)
    elif len(message) == 9:
        clientNum = message[0]
        packetNum = int.from_bytes(message[3:5], 'big')
        print("Sending acknowledgement to worker " + str(clientNum) + " on receipt of packet " + str(packetNum+1))
        bytesToSend = message
        UDPIngressSocket.sendto(bytesToSend, workerIPAdresses[clientNum])


    #Data from worker to client
    else:
        clientNum = message[0]
        packetNum = int.from_bytes(message[3:5], 'big')
        totalPackets = int.from_bytes(message[5:7], 'big')
        print("Recieved packet number "+str(packetNum)+" of "+str(totalPackets)+" from worker #"+str(clientNum))
        bytesToSend = message
        UDPIngressSocket.sendto(bytesToSend, clientIPAdresses[clientNum])
