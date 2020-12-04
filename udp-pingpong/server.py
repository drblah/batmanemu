import socket
import argparse

def main():
    parser = argparse.ArgumentParser(description='Simple UDP echo server')
    parser.add_argument('--serverIP', action='store', type=str)
    parser.add_argument('--serverPort', action='store', type=int)

    arguments = parser.parse_args()

    serverIP = arguments.serverIP #'127.0.0.1'
    serverPort = arguments.serverPort #20000
    msgSize = 1024

    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    soc.bind((serverIP, serverPort))

    while(True):
        bytesAddrTuple = soc.recvfrom(msgSize)

        msg = bytesAddrTuple[0]
        clientAddr = bytesAddrTuple[1]

        soc.sendto(msg, clientAddr)


if __name__ == "__main__":
    main()