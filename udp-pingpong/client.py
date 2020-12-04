import socket
import time
import select
import argparse

def main():
    parser = argparse.ArgumentParser(description='Simple UDP echo client')
    parser.add_argument('--serverIP', action='store', type=str)
    parser.add_argument('--serverPort', action='store', type=int)
    parser.add_argument('--clientIP', action='store', type=str)
    parser.add_argument('--clientPort', action='store', type=int)

    arguments = parser.parse_args()

    serverIP = arguments.serverIP
    ownIP = arguments.clientIP

    serverPort = arguments.serverPort
    clientPort = arguments.clientPort
    msgSize = 1024
    msg = str.encode("1234567890"*10)

    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    soc.bind((ownIP, clientPort))

    sentCount = 0
    recvCount = 0

    while(True):
        soc.sendto(msg, (serverIP, serverPort))
        sentCount = sentCount + 1

        ready = select.select([soc], [], [], 1)

        if ready[0]:
            bytesAddrTuple = soc.recvfrom(msgSize) 

            msg = bytesAddrTuple[0]
            clientAddr = bytesAddrTuple[1]

            print("Response from server: {} @ {}".format(msg, clientAddr))
            recvCount = recvCount + 1
            

        print("Sent/Received: {}/{}".format(sentCount, recvCount))

        time.sleep(0.1)
        #soc.sendto(msg, clientAddr)


if __name__ == "__main__":
    main()