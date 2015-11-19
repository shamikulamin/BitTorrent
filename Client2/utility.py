﻿import httplib
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

#HOST = socket.gethostname()    # server name goes in here
HOST = "127.0.0.1"
PORT = serverThreadConfig.config['port']
#ip_address = socket.gethostbyname(socket.gethostname())
ip_address = "127.0.0.1"

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
    fr = open((filename), "r")
    fr.seek(0,2) # move the cursor to the end of the file
    size = fr.tell()
    return size

def process_data_old(threadName, delay, response, filename):
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

def process_data(threadName, delay, response, filename, relevant_path):
    # response is the tracker file to be parsed #
    #TODO: uncomment if response is obtained here instead of response.read()
    #string = response.read(1024)

    string = response
    while len(string) == 0:
        time.sleep(delay)

    if len(string) > 0:
        #filenameList = filename.split('.')
        # begin write recd tracker tata to filename.track #
        file = open(relevant_path + filename+"1.track", "w")
        file.write(string)
        file.close()
        # end write recd tracker data to filename.track #

        #string = parseTrackerFile(filename+'.track')
        #print string
        # calculate which segements to download, then download them
        inf = string.split(":")
        resultFile = open(relevant_path + filename+"1.temp", "wb")
        print inf[1], inf[2]
        #downloadSegment_old(string)
        try:
            thread.start_new_thread( downloadSegment, ("Thread-4",resultFile, inf[1], inf[2], inf[3], inf[4], filename));
            #print "data successfully written to file"
        except:
            print "Error: unable to start thread - process_data"
        #resultFile.seek(inf[2])
        # new download segment executes as thread, downloads segment indicated to stream, updates local tracker #
        # pass arguments: open filestream, server ip, server port, segment begin, segment end



def createTrackerFile(filename, description):
    #print filename
    fileNameList = filename.split("/")
    #actualFileName = fileNameList[6]  <--written only to ever work on vijay's computer...
    actualFileName = fileNameList[len(fileNameList) -1]
    filesize = getFileSize(filename)
    md5 = getMd5(filename)
    timestamp = int(time.time())

    #create the local copy of the tracker file
    #file = open("tracker"+str(timestamp)+".txt", "w")
    string = "Peer 1: "+ "Create Tracker" + " Filename: "+actualFileName+" Filesize: "+ str(filesize)+" Description:"+description+" MD5:"+md5+" "+str(ip_address)+":"+str(PORT)+":0:"+str(filesize)+":"+str(timestamp)
    #print string
    params = "command=createTracker&filename="+actualFileName+"&filesize="+str(filesize)+"&description="+description+"&md5="+md5+"&ip="+str(ip_address)+"&port="+str(PORT)+"&timestamp="+str(timestamp)
    #file.write(string)
    #file.close()
    #send the data to the server over post request
   
    return params

def updateTrackerFile(filename):
    fileNameList = filename.split("/")
    actualFileName = fileNameList[len(fileNameList) -1]
    # 
    parseTrackerFile(filename)
    s_byte = 100
    e_byte = 200
    string = "Peer 1: "+" Updatetracker "+ " Filename: "+ actualFileName+ " start byte "+ str(s_byte)+" End byte "+ str(e_byte)+" ip-address "+ str(ip_address)+" port "+str(PORT)
    params = "command=updateTracker&filename="+actualFileName+"&s_byte="+str(s_byte)+"&e_byte="+str(e_byte)+"&ip="+str(ip_address)+"&port="+PORT
    return params

def parseTrackerFile(trackerFilename):
    string=""
    lines = [line.rstrip('\n') for line in open(trackerFilename, "r")]
    #print lines
    # Read the file from the last line
    # len(lines) -1 should give the last line, decrement i
    for i, val in enumerate(lines):
        if i == 0:
            fileName = val.split(": ");
            string += str(fileName[1])+":"
        if i>4:
            string += val
    #print string
    return string

def downloadSegment_old(string):
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

def downloadSegment(threadName, resultFile, server_addr, server_port, segment_beginaddr, segment_endaddr, fileName):
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect((server_addr, int(server_port)))
    print "Server Address : ", server_addr, " Server Port: ", server_port
    socket1.send("download," + fileName + ","+segment_beginaddr+"," + segment_endaddr)
    data = socket1.recv(int(segment_endaddr) - int(segment_beginaddr))
    resultFile.seek(int(segment_beginaddr))
    resultFile.write(data)
    socket1.close()
    
                
    

