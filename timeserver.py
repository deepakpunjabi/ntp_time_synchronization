import socket
import sys
import thread
import threading
import fcntl
import struct
import datetime

bufferSize = 256
host = '10.146.62.96'
port = 7845


def getSinceEpoch():
    current = datetime.datetime.now()
    epoch = datetime.datetime.utcfromtimestamp(0)
    diff = current - epoch
    microseconds = (diff.days * 24 * 60 * 60 + diff.seconds) * 1000000 + diff.microseconds
    return microseconds


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


# get_ip_address('eth0')  # '192.168.0.110'


# def portal(clientsock, address):
def portal(sock):
    while True:
        print "Waiting to receive data"
        data, address = sock.recvfrom(bufferSize)
        ts2 = getSinceEpoch()
        print "Data received " + data
        if data.split("##")[0] == "get_ts":
            send_data = data + "##" + str(ts2)+"##"+str(getSinceEpoch())
            print "Sending data as " + send_data
            sock.sendto(send_data, address)
        '''
        print "Waiting to receive data"
        recv_data = sock.recv(bufferSize).decode()
        print "Received data as" + recv_data + "#"
        #processRequest(recv_data)
        if recv_data == "get_ts":
            sock.send(str(i).encode())
        '''


if __name__ == '__main__':

    # get port no from command line arguments
    if len(sys.argv) != 1:
        host = str(sys.argv[1])
        port = int(str(sys.argv[2]))

    # create socket
    host = get_ip_address("eth0")
    address = (host, port)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(address)
    portal(serverSocket)
