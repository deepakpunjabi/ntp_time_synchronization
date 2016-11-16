#! /usr/bin/python
from numpy import mean, sqrt, square, arange

# ------------------------------------------------------input Given by filtering algorithm--------------------------------------------------------------------
#server vector with each element containing  O(i)=offset and r(i)=root distance
#peerjitter vector with each element containing peerjitter for each server
server=[[1.2432343,0.56565],[1.8923232,1.2323],[0.433232,0.43545],[1.202323,0.1112],[0.222323,1.34343],[1.2223232,1.2323],[0.133434343,0.245544]]
peerjitter=[0.454545,0.65756556,0.545432323,0.787878787,0.45454,0.67676, 0.1004343]

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

#***************************************Clock Selection Algorithm****************************************************
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
				z=abs((y[0]-x[0]))*x[1]
				temp.append(z)
		jitterlist.append(temp)
	#print jitterlist
#------------------------------------------------------------------------------------------------------------------------------------

#--------------------------------omputed as the root mean square (RMS)--------------------------------------------------------------
	for x in jitterlist:
		rms = sqrt(mean(square(x)))
		selectjitter.append(rms)
	#print selectjitter
	#print peerjitter
#------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------clustering algorithm to generate final servers-------------------------------------------------------
	maximum_select_jitter=max(selectjitter)
	minimum_peer_jitter=min(peerjitter)
	#print maximum_select_jitter
	#print minimum_peer_jitter
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
y=0
for x in server:
	y=y+(1/x[1])
a=1/y
print a
#----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------Finding final offset value ---------------------------------------------------
y=0
for x in server:
	y=y+(x[0]/x[1])
T=a*y
print T
# T is our final offset value
#----------------------------------------------------------------------------------------------------------------------------------------
#***************************************8End of Clock combining algorithm*******************************************************************