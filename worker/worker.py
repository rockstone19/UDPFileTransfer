#Author: Peter Gutstein
import socket
import time
import math

#Important variables for keeping between loops
files = ["alphabets.txt", "numbers.txt", "test.txt", "smallImage.jpeg", "image.png", "largeImage.jpg", "earth.gif", "flag.mp4", "nGGYU.mp3"]
maxPacketSize = 65507
sizePerPacket = maxPacketSize - 20

ingressAddressPort = ("", 20001)
bufferSize  = 65507
bytesToSend = (0).to_bytes(1, 'big')

fileBytes = None
numOfPackets = 0
packetToSend = 0
fileInBytes = []

#Wait .5 seconds for TCPDUMP to get up first
time.sleep(.5)

# Create a socket & Declare self to ingress
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPWorkerSocket.sendto(bytesToSend, ingressAddressPort)

while(True):
    #Recieve from the ingress
    bytesAddressPair = UDPWorkerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    #Worker acknowledged by ingress
    if len(message) == 1:
        if b'\x01' in message:
            print("Ping acknowledged by ingress")

    #Request from ingress (first packet)
    elif len(message) == 3:
        #Store important variables
        clientNum = message[0]
        fileNumber = int.from_bytes(message[1:3], 'big')

        #Print out confirmation of sending file
        print("Fuffilling request for file for client #" + str(clientNum))

        fileName = files[fileNumber]
        file = open(fileName, "rb")
        fileBytes = file.read()

        if len(fileBytes) % sizePerPacket == 0:
            numOfPackets = int(len(fileBytes)/sizePerPacket)
        else:
            numOfPackets = math.ceil(len(fileBytes)/sizePerPacket)

        for i in range(numOfPackets):
            #HEADER: byte0=clientNum | byte1,2=fileNumber | byte3,4=packetNum | byte5,6=totalPackets
            header = message[0:3] + (i+1).to_bytes(2, 'big') + (numOfPackets).to_bytes(2, 'big')
            packetData = fileBytes[(i*sizePerPacket):((i+1)*sizePerPacket)]
            completePacket = header + packetData
            #Add each packet to an array which can be accessed later on
            fileInBytes.append(completePacket)

        print("Sending packet 1 of " + str(numOfPackets))
        UDPWorkerSocket.sendto(fileInBytes[packetToSend], ingressAddressPort)

    elif len(message) == 9:
        #Store important variables
        clientNum = message[0]
        fileNumber = int.from_bytes(message[1:3], 'big')
        lastPacketRec = int.from_bytes(message[3:5], 'big')
        nextPacket = int.from_bytes(message[5:7], 'big')

        print("Received confirmation on packet " + str(lastPacketRec+1))

        #If valid packet request
        if nextPacket < numOfPackets:
            #If system worked as intended (next packet in sequence)
            if lastPacketRec + 1 == nextPacket:
                packetToSend += 1
                print("Sending packet " + str(packetToSend+1) + " of " + str(numOfPackets))
            #If need to resend packet
            else:
                print("Resending packet " + str(packetToSend+1) + " of " + str(numOfPackets))
            UDPWorkerSocket.sendto(fileInBytes[packetToSend], ingressAddressPort)
        else:
            print("ERROR: Requested packet out of range")
