from __future__ import division
import socket
import sys
import threading
import sched
import time
import datetime
import os
from numpy import mean, sqrt, square, arange
from math import sqrt

bufferSize = 256
host = '10.14.1.153'
hostlist = [('10.14.92.170', 7845), ('10.14.92.144', 7878), ('10.14.92.141', 7845)]
port = 7845
ts = 0
offset = []
delay = []
serverlist = []
jitterlist = []


# Parameters to be passed to the system
adjustThreshold = 120000000
resyncInterval = 64
numPolls = 5

def qmean(num):
    return sqrt(sum(n*n for n in num)/len(num))


def getTimeToAdjust(server, peerjitter):
    print "getTimeToAdjust start ================="
    #peerjitter = getPeerjitter(server)

    # ------------------------------------------------------input Given by filtering algorithm--------------------------------------------------------------------
    #server vector with each element containing  O(i)=offset and r(i)=root distance
    #peerjitter vector with each element containing peerjitter for each server
    #server=[[1.2432343,0.56565],[1.8923232,1.2323],[0.433232,0.43545],[1.202323,0.1112],[0.222323,1.34343],[1.2223232,1.2323],[0.133434343,0.245544]]
    # peerjitter=[0.454545,0.65756556,0.545432323,0.787878787,0.45454,0.67676, 0.1004343]

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    correcteness_interval=[]#for each server construct[O(i)-r(i),O(i)+r(i)]
    jitterlist=[] #select jitter relative to each cadidate in truechimers each element is a list
    lowpoint=[]#lowest point of correctness interval
    midpoint=[]#mid point of correctness interval
    highpoint=[]#highest point of correctness interval
    selectjitter=[] #root mean squred of each element in jitterlist
    temp=[]#lowest, mid and highest point in sorted order
    currentlowpoint=[]#lower end of intersection interval
    currenthighpoint=[]#higher end of inter section interval
    minclock=2#we keep at least 2 clocks as threshold
    print server

    # ***************************************Clock Selection Algorithm**************************************************
    #Input: servers in form of server vector
    #Output: Prune servers in form of server vector

    #----------------------------------------for each server construct[O(i)-r(i),O(i)+r(i)]-------------------------------
    for x in server:
        temp=[]
        temp.append(x[0]-x[1])
        temp.append(x[0]+x[1])
        correcteness_interval.append(temp)

    #-----------------------------------------------------------------------------------------------------------------------------


    #-----------------for each correctness interval find lowest, mid and highest point and sorting them------------------------
    temp=[]
    for x in correcteness_interval:
        temp.append(x[0])
        lowpoint.append(x[0])
        temp.append((x[0]+x[1])/2)
        midpoint.append((x[0]+x[1])/2)
        temp.append(x[1])
        highpoint.append(x[1])
    temp=sorted(temp)
    #-------------------------------------------------------------------------------------------------------------------------


    #-------------------------------Code to find intersection interval-----------------------------------------------------------
    flag=0
    f=0
    print correcteness_interval
    while True:
        n=0
        for x in temp:
            if x in lowpoint:
                n=n+1
            if x in highpoint:
                n=n-1
            if (n>=len(server)-f):
                currentlowpoint=x
                break
        n=0
        for x in reversed(temp):
            if x in lowpoint:
                n=n-1
            if x in highpoint:
                n=n+1
            if (n>=len(server)-f):
                currenthighpoint=x
                break
        if (currentlowpoint<currenthighpoint):
            flag=1
            break
        if f<(len(server)/2):
            f=f+1
        else:
            break
    if flag==1:
        print currentlowpoint
        print currenthighpoint
    if flag==0:
        print "Not found"
    #-----------------------------------------------------------------------------------------------------------------------------


    #---------------------Finding server which lies between intersction interval, prune false server------------------------------
    if flag==1:
        for x in correcteness_interval:
            if (x[1]>currentlowpoint) and (x[0]<currenthighpoint):
                pass
            else:
                if ((len(server))-1)==(correcteness_interval.index(x)):
                    del server[-1]
                else:
                    server.pop(correcteness_interval.index(x))
    print server
    #-------------------------------------------------------------------------------------------------------------------------------

    #***********************************End of Clock Selection Algorithm*************************************************************


    #***********************************Clustering Algorithm*************************************************************************
    #The clock cluster algorithm processes the pruned servers produced by the clock select algorithm to produce a list of survivors.

    jitterlist=[] #jitter relative to the ith candidate is calculated as follows.
    selectjitter=[] #computed as the root mean square (RMS) of the di(j) as j ranges from 1 to n

    #----------------------------------relative jitter for each server----------------------------------------------------------------
    while len(server)>minclock:
        selectjitter=[]
        jitterlist=[]
        for x in server:
            temp=[]
            for y in server:
                if x!=y:
                    print "jitterlist ####"
                    print y[0]
                    print x[0]
                    print x[1]
                    z=abs((y[0]-x[0]))*x[1]
                    temp.append(z)
            print temp
            jitterlist.append(temp)
        print jitterlist
    #------------------------------------------------------------------------------------------------------------------------------------

    #--------------------------------Computed as the root mean square (RMS)--------------------------------------------------------------
        for x in jitterlist:
            print x
            rms = qmean(x)
            #rms = sqrt(mean(square(x)))
            selectjitter.append(rms)
        #print selectjitter
        #print peerjitter
    #------------------------------------------------------------------------------------------------------------------------------------

    #---------------------------------clustering algorithm to generate final servers-------------------------------------------------------
        maximum_select_jitter=max(selectjitter)
        minimum_peer_jitter=min(peerjitter)
        print maximum_select_jitter
        print minimum_peer_jitter
        if maximum_select_jitter>minimum_peer_jitter:
            index=selectjitter.index(maximum_select_jitter)
            if ((len(server))-1)==index:
                del server[-1]
            else:
                server.pop(index)
        else:
            break
    print server
    #---------------------------------------------------------------------------------------------------------------------------------------


    #***********************************End of clustering algorithm*************************************************************************


    #***********************************Clock Combining Algorithm***************************************************************************

    #------------------------------------Calculate normalization constat a-------------------------------------------------------------------
    y=0.0
    for x in server:
        print "x: "
        print x[1]

        y=y+(1.0/x[1])
        print "1/x[1] " + str(1.0/x[1])
        print "y: " + str(y)
    print "y: " + str(y)
    a=1/y
    print a
    #----------------------------------------------------------------------------------------------------------------------------------------

    #-----------------------------------------Finding final offset value ---------------------------------------------------
    y=0
    for x in server:
        x[0] = float(x[0])
        x[1] = float(x[1])
        y=y+(x[0]/x[1])
    T=a*y
    print T
    print "getTimeToAdjust end ================="
    return T
    # T is our final offset value
    #----------------------------------------------------------------------------------------------------------------------------------------
    #***************************************8End of Clock combining algorithm*******************************************************************


def getSinceEpoch():
    current = datetime.datetime.now()
    epoch = datetime.datetime.utcfromtimestamp(0)
    diff = current - epoch
    microseconds = (diff.days * 24 * 60 * 60 + diff.seconds) * 1000000 + diff.microseconds
    # microseconds = (diff.days * 24 * 60 * 60 + diff.seconds) + diff.microseconds/1000000
    print "getSinceEpoch returning time as "
    print microseconds
    return microseconds


def handler():
    global ts
    while True:
        ts += 1


def peerThread():
    print "peerThread called"
    while True:
        print "Waiting to receive data at peerThread"
        recv_data, server = clientSocket.recvfrom(bufferSize)
        code, ts1, ts2, ts3 = recv_data.split("##")
        ts4 = getSinceEpoch()
        ts1 = int(ts1)
        ts2 = int(ts2)
        ts3 = int(ts3)
        ts4 = int(ts4)
        print "Received ts1"
        print ts1
        print datetime.timedelta(microseconds=ts1)
        print "Received ts2"
        print ts2
        print datetime.timedelta(microseconds=ts2)
        print "Received ts3"
        print ts3
        print datetime.timedelta(microseconds=ts3)
        print "Received ts4"
        print ts4
        print datetime.timedelta(microseconds=ts4)
        tempoffset = ((ts2 - ts1) + (ts3 - ts4)) / 2
        tempdelay = (ts4 - ts1) - (ts3 - ts2)
        offset.append(tempoffset)
        delay.append(tempdelay)
        print "Minimum delay offset " + str(tempoffset)
        #print str(timetoset)
        # print "sudo date -s " + str(timetoset)
        # os.system('sudo date -s "' + str(timetoset) + '"')


def pollProc():
    global offset
    global delay
    for address in hostlist:
        offset *= 0
        delay *= 0
        for i in range(numPolls):
            send_data = "get_ts" + "##" + str(getSinceEpoch())
            sent = clientSocket.sendto(send_data, address)
        time.sleep(1)
        print "Printing lists in pollProc"
        print offset
        print delay
        try:
            mindelay = min(delay)
            adjust = offset[delay.index(min(delay))]
            if adjust <= adjustThreshold:
                sqsum = 0
                for i in range(len(offset)):
                    sqsum += square(offset[i] - adjust)
                    sqrtsum = (sqrt(sqsum))/(len(offset) - 1)
                tempadjust = [adjust, mindelay]
                serverlist.append(tempadjust)
                jitterlist.append(sqrtsum)
            else:
                print "Adjustment value beyond threshold. Discarding"
        except Exception, e:
            print 'Exception caught ' + str(e)
            #print "List empty"
    print "Sending input to getTimeToAdjust: "
    print serverlist
    print jitterlist
    final_adjust = getTimeToAdjust(serverlist, jitterlist)
    serverlist[:] = []
    jitterlist[:] = []
    # print "Adjust: "
    # print adjust
    # final_adjust = adjust + (min(delay)/2)

    print "adjustment factor after delay " + str(final_adjust)
    timetoset = datetime.datetime.now() + datetime.timedelta(microseconds=final_adjust)
    print "========================================="
    print "Adjusting final time to " + str(timetoset)
    print "========================================="
    os.system('sudo date -s "' + str(timetoset) + '"')
    print "\n\n\n\n\n\n\n\n\n"



def pollThread(val):
    print "pollThread called"
    pollProc()
    while 1:
        s = sched.scheduler(time.time, time.sleep)
        s.enter(resyncInterval, 1, pollProc, ())
        s.run()
    print val


if __name__ == '__main__':
    # get port no from command line arguments
    d = threading.Thread(name='Timer', target=handler)
    d.setDaemon(True)
    #d.start()
    global ts
    if len(sys.argv) != 1:
        host = str(sys.argv[1])
        port = int(str(sys.argv[2]))

    print hostlist
    address = (host, port)
    print(address)
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        poll = threading.Thread(name='Poll', target=pollThread, args=(address,))
        poll.start()
        print "Poll Thread started"
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        peer = threading.Thread(name='Peer', target=peerThread, args=())
        peer.start()
        print "Peer Thread started"
        # clientSocket.connect(address)
        # recv_data = clientSocket.recv(bufferSize).decode()
        # print "Timestamp received from server as " + recv_data
        '''
        send_data = "get_ts"
        sent = clientSocket.sendto(send_data, address)
        data, server = clientSocket.recvfrom(4096)
        print 'received "%s"' % data
        '''
        '''
        clientSocket.send(send_data.encode())
        recv_data = clientSocket.recv(bufferSize).decode()
        print "Tiestamp received from server as " + recv_data

        delay = []
        offset = []
        for i in range(8):
            ts1 = ts
            send_data = "get_ts"
            sent = clientSocket.sendto(send_data, address)
            recv_data, server = clientSocket.recvfrom(bufferSize)
            ts2, ts3 = recv_data.split("##")
            print "Received ts2 as " + ts2 + " and ts3 as " + ts3
            offset.append(ts3)
            # ts4 = ts
            delay.append(ts - ts1)
            print "Timestamp received from server as " + recv_data
        print delay
        print offset
        print offset[delay.index(min(delay))]
        '''
        print "Waiting for thread to join"
        peer.join()
        poll.join()
        print "Thread joined"
    except socket.error as log:
        print("Error: "+str(log))
        sys.exit(1)
    # temp = input("enter something")

    clientSocket.close()
    print "Socket closed"


def getPeerjitter(servers):
    peerjitterlist = []
    for serverx in servers:
        peerjitterlist.append(serverx[2])
    return peerjitterlist


