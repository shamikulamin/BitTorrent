import httplib
import urllib
import time
import socket
import sys
import hashlib
import time
import thread
import os
import clientThreadConfig
import serverThreadConfig

HOST = socket.gethostname()    # server name goes in here
PORT = serverThreadConfig.config['port']
ip_address = socket.gethostbyname(socket.gethostname())

def put(commandName):
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect((HOST, PORT))
    socket1.send(commandName)
    string = commandName.split(' ', 1)
    inputFile = string[1]
    with open(inputFile, 'rb') as file_to_send:
        for data in file_to_send:
            socket1.sendall(data)
    print 'Upload file Successful'
    socket1.close()
    return


def get(commandName):
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect((HOST, PORT))
    socket1.send(commandName)
    string = commandName.split(' ', 1)
    inputFile = string[1]
    with open(inputFile, 'wb') as file_to_write:
        while True:
            data = socket1.recv(1024)
            # print data
            if not data:
                break
            # print data
            file_to_write.write(data)
    file_to_write.close()
    print 'Download file Successful'
    socket1.close()
    return



def getMd5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def getFileSize(filename):
    fr = open(filename, "r")
    fr.seek(0,2) # move the cursor to the end of the file
    size = fr.tell()
    return size

def process_data(threadName, delay, response, filename):
    string = response.read(1024)
    while len(string) == 0:
        time.sleep(delay)

    if len(string) > 0:
        #filenameList = filename.split('.')
        file = open(filename+".track", "w")
        
        file.write(string)
        file.close()
        string = parseTrackerFile(filename+'.track')
        #print string
        downloadSegment(string)


def createTrackerFile(filename, description):
    filesize = getFileSize(filename)
    md5 = getMd5(filename)
    timestamp = int(time.time())
    print timestamp
    print filesize
    print md5
    #create the local copy of the tracker file
    file = open("tracker"+str(timestamp)+".txt", "w")
    string = "Filename: "+filename+"\nFilesize: "+ str(filesize)+"\nDescription:"+description+"\nMD5:"+md5+"\n#list of peers follow next\n"+str(ip_address)+":"+str(PORT)+":0:"+str(filesize)+":"+str(timestamp)

    file.write(string)
    file.close()
    #send the data to the server over post request
    params = urllib.urlencode({'command':'createTracker','filename':filename, 'filesize':filesize, 'description':description,'md5':md5,'ip':ip_address,'port':PORT,'timestamp':timestamp})
    return params

def parseTrackerFile(trackerFilename):
    string=""
    lines = [line.rstrip('\n') for line in open(trackerFilename, "r")]
    for i, val in enumerate(lines):
        if i == 0:
            fileName = val.split(": ");
            string += str(fileName[1])+":"
        if i>3:
            string += val
    return string

def downloadSegment(string):
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    inf = string.split(":")
    socket1.connect((inf[1], int(inf[2])))
    socket1.send("download " + inf[0])
    
    with open(inf[0]+".temp", 'wb') as file_to_write:
        while True:
            data = socket1.recv(1024)
            # print data
            if not data:
                break
            # print data
            file_to_write.write(data)
    file_to_write.close()

    #os.rename(file_to_write, file_to_write.replace(".temp",""))
    print 'Download file Successful'
    socket1.close()
    return 
                
    

