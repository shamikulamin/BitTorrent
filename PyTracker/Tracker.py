from socket import *
import os
import glob
from os import path
import thread
import time

if __name__ == "__main__":
    config = {}
    execfile("settings.conf", config) 
    # python 3: exec(open("example.conf").read(), config)


BUFF = config["maxSegmentSize"]
HOST = gethostbyname(gethostname()) # must be input parameter @TODO
PORT = config["trackerServerPort"] # must be input parameter @TODO
basePath = "./TrackerFiles/"
def response(key):
    return 'Server response: ' + key

def handler(clientsock,addr):
    while 1:
        data = clientsock.recv(BUFF)
        tokens = data.split(' ',1)
        if not data: break
        print repr(addr) + ' recv:' + repr(data)
       # clientsock.send(response(data))
       # print repr(addr) + ' sent:' + repr(response(data))
        if "GET" == tokens[0]: break # type 'close' on client console to close connection from the server side
    keyVal = tokens[1].split('&')
    command = keyVal[0].split('=')[1]
    print command
    if command.lower() == "createtracker":
        filename = keyVal[1].split('=')[1]
        filesize = keyVal[2].split('=')[1]
        desc = keyVal[3].split('=')[1]
        md5 = keyVal[4].split('=')[1]
        ip = keyVal[5].split('=')[1]
        port = keyVal[6].split('=')[1]
        timestamp = keyVal[7].split('=')[1]
        fo=open(basePath+filename+".track", "w")
        fo.write("File Name: "+filename+'\n')
        fo.write("File Size: "+filesize+'\n')
        fo.write("Description: "+desc+'\n')
        fo.write("MD5: "+md5+'\n')
        fo.write("#list of peers follows next\n")
        fo.write(ip+":"+port+":"+"0:"+filesize+":"+timestamp+'\n')

        fo.close()
        clientsock.send("200:Create Tracker Successful")
    elif command.lower()=="updatetracker":
        filename = keyVal[1].split('=')[1]
        sbyte = keyVal[2].split('=')[1]
        ebyte = keyVal[3].split('=')[1]
        ip = keyVal[4].split('=')[1]
        port = keyVal[5].split('=')[1]
	timestamp = keyVal[6].split('=')[1]
	check = 0
	construct=ip+":"+port+":"+sbyte+":"+ebyte+":"+timestamp+"\n"
	with open(basePath+filename,'r')as f:
	    lines=[line.strip() for line in f]
	    if construct == lines:
		check=1
	if check==1:
	    fo =open(basePath+filename,"a+")
	    fo.write(construct)
	    fo.close()
	    clientsock.send("200:Update Tracker Successful")
	else:
	    clientsock.send("200:Update Tracker Successful")    
    elif command.lower()=="list":
	for files in os.listdir(basePath):
	    if files.endswith(".track"):
		clientsock.send(files+'\n')
    elif command.lower()=="get":
	filename=keyVal[1].split('=')[1]
	with open(basePath+filename,'r')as f:
	    lines=[line.strip() for line in f]
	    for l in lines:
		clientsock.send(l+'\n')
    else:
	clientsock.send("Invalid Command")
	
    clientsock.close()
    print addr, "- closed connection" #log on console

if __name__=='__main__':
    files = glob.glob(basePath+'*')
    for f in files:
        os.remove(f)
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)
    while 1:
        print 'waiting for connection... listening on port', PORT, HOST
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        thread.start_new_thread(handler, (clientsock, addr))