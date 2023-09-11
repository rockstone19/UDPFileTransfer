#Author: Peter Gutstein
import socket
import time
import random

files = ["alphabets.txt", "numbers.txt", "test.txt", "smallImage.jpeg", "image.png", "largeImage.jpg", "earth.gif", "flag.mp4", "nGGYU.mp3"]
fileReqNum = random.randint(0,8)    #get random file each time

ingressAddressPort = ("", 20001)
bufferSize = 65507

#Wait 1 second for everything to get up first
time.sleep(1)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Request file from ingress
print("Requesting file " + files[fileReqNum])
bytesToSend = (fileReqNum).to_bytes(2, 'big')
UDPClientSocket.sendto(bytesToSend, ingressAddressPort)

#Makes sure entire process of request is only done once
requestFulfilled = False

#Important variables that need to stay outside of scope of loop
bytesFromIngress = []
numPacketsRecieved = 0;
dataSorted = b''

#Set socket timeout for if packet gets lost
UDPClientSocket.settimeout(3)
while(requestFulfilled == False):
    try:
        #Recieve ingress data
        bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        packetNum = int.from_bytes(message[3:5], 'big')
        totalPackets = int.from_bytes(message[5:7], 'big')

        #If it is the correct packet
        if packetNum == (numPacketsRecieved+1):
            bytesFromIngress.append(message[3:])
            print("Recieved packet " + str(packetNum) + " of " + str(totalPackets) + " from ingress")
            numPacketsRecieved += 1
            #Request next packet if there are more packets
            if numPacketsRecieved < totalPackets:
                bytesToSend = message[0:3] + (numPacketsRecieved-1).to_bytes(2, 'big') + (numPacketsRecieved).to_bytes(2, 'big') + (totalPackets).to_bytes(2, 'big')
                UDPClientSocket.sendto(bytesToSend, ingressAddressPort)
        else:
            print("Recieved packet " + str(packetNum) + " instead of packet " + str(numPacketsRecieved+1) + ". Resending request")
            bytesToSend = message[0:3] + (numPacketsRecieved).to_bytes(2, 'big') + (numPacketsRecieved+1).to_bytes(2, 'big') + (totalPackets).to_bytes(2, 'big')
            UDPClientSocket.sendto(bytesToSend, ingressAddressPort)

        #if all packets have been received
        if numPacketsRecieved == totalPackets:
            UDPClientSocket.settimeout(None)
            print("All packets recieved from ingress")

            for i in bytesFromIngress:
                dataSorted = dataSorted + i[4:]

            file = open(r"../recievedFiles/{}".format(files[fileReqNum]), "wb")
            file.write(dataSorted)
            file.close()

            requestFulfilled = True
            print("All packets written to " + files[fileReqNum])
    #If timeout occurs
    except socket.timeout:
        print("Socket timeout occured. Resending request for packet " + str(numPacketsRecieved+1))
        bytesToSend = message[0:3] + (numPacketsRecieved).to_bytes(2, 'big') + (numPacketsRecieved+1).to_bytes(2, 'big') + (totalPackets).to_bytes(2, 'big')
        UDPClientSocket.sendto(bytesToSend, ingressAddressPort)
