import httplib
import urllib
import time
import socket
import sys
import hashlib
import time
import thread
import os
import collections
import clientThreadConfig
import serverThreadConfig

#HOST = socket.gethostname()    # server name goes in here
HOST = "127.0.0.1"
PORT = 12345
#ip_address = socket.gethostbyname(socket.gethostname())
ip_address = "127.0.0.1"
segmentDict = collections.defaultdict(list)

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
        # begin write recd tracker data to filename.track #
        file = open(relevant_path + filename, "w")
        file.write(string)
        file.close()
        # end write recd tracker data to filename.track #
        #currently read from file itself, later we will read from created tracker file
        listOfSegmentsInTrackerFile = parseTrackerFile(relevant_path + filename)
        print " list of segments in tracker file is: ", listOfSegmentsInTrackerFile, "\n\n"
        for index in range(len(listOfSegmentsInTrackerFile) -1):
        	segmentLine = listOfSegmentsInTrackerFile[index]
        	#print "The segment line is : " , segmentLine, "\n\n"
	        # calculate which segements to download, then download them
	        inf = segmentLine.split(":")
	        #print " The entire information: " , inf, "\n\n"
	        #create a temporary file to write the segment one by one
	        resultFileName = relevant_path + filename + ".temp"
	        resultFile = open(resultFileName, "wb")
	        #print inf[1], inf[2]

	        isSegmentDownloaded = checkIfSegmentIsAlreadyDownloaded(filename, inf[2])
	        #print " The segment list for file : " , filename, " is: ", segmentDict.get(filename,"NoT"), " ", isSegmentDownloaded
	        #downloadSegment_old(string)
	        
	        try:
	        	#print "END HERE "
	        	if isSegmentDownloaded == False:
	        		thread.start_new_thread( downloadSegment, ("Thread-4",resultFile, inf[0], inf[1], inf[2], inf[3], filename));
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
    string = "Peer 2: "+ "Create Tracker" + " Filename: "+actualFileName+" Filesize: "+ str(filesize)+" Description:"+description+" MD5:"+md5+" "+str(ip_address)+":"+str(PORT)+":0:"+str(filesize)+":"+str(timestamp)
    #print string
    params = "GET command=createTracker&filename="+actualFileName+"&filesize="+str(filesize)+"&description="+description+"&md5="+md5+"&ip="+str(ip_address)+"&port="+str(PORT)+"&timestamp="+str(timestamp)
    #file.write(string)
    #file.close()
    #send the data to the server over post request
    #please take a quick shower we are running late # Sweta Ojha
   
    return params

def updateTrackerFile(filename, segmentLine):
    fileNameList = filename.split("/")
    actualFileName = fileNameList[len(fileNameList) -1]
    
    # listOfSegments = parseTrackerFile(filename)
    # print " Update Tracker File : List of segments: \n ", listOfSegments
    # for index in range(len(listOfSegments) -1):
    #     segmentLine = listOfSegments[index].split(":")
    #     print segmentLine

    string = "Peer 2: "+" Updatetracker "+ " Filename: "+ actualFileName+ " start byte "+ segmentLine[2]+" End byte "+ segmentLine[3]+" ip-address "+ segmentLine[0]+" port "+segmentLine[1]
    params = "GET command=updateTracker&filename="+actualFileName+"&s_byte="+segmentLine[2]+"&e_byte="+segmentLine[3]+"&ip="+segmentLine[0]+"&port="+segmentLine[1]
    
    return params

def parseTrackerFile(trackerFilename):
    
    listOfSegments = []
    #for line in reversed(open(trackerFilename).readlines()):
    	#print "Line is: " , line.rstrip()

    #read file from the end of tracker file
    lines = [line.rstrip('\n') for line in reversed(open(trackerFilename).readlines())]
    #print "Total lines: " , len(lines) 
    # Read the file from the last line
    # len(lines) -1 should give the last line, decrement i
    for i, val in enumerate(lines):
    	string=""
    	#get the file name
    	if i == len(lines) -1:
    		#print " Line is ", i, val
    		fileName = val.split(": ")
    		string += str(fileName[1])
    		listOfSegments.append(string)
   
        #read segment one after the other
        if i < (len(lines)-5):
        	#print " Segment Line is ", i, val
        	string = string + val 
        	listOfSegments.append(string)
    #print string
    return listOfSegments

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

def downloadSegment(threadName, file_to_write, server_addr, server_port, segment_beginaddr, segment_endaddr, fileName):
    downloadSegmentStr = "download," + fileName + ","+segment_beginaddr+"," + segment_endaddr
    #print "Server Address : ", server_addr, " Server Port: ", server_port   
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect((server_addr, int(server_port)))
    socket1.send(downloadSegmentStr)
    #data = socket1.recv(1024)

    #with open(, 'wb') as file_to_write:
    file_to_write.seek(int(segment_beginaddr),0)
    #while True:
    data = socket1.recv(1024)
    print "Received data :" ,"\n\n" ,data
    #if not data:
        #break
    # print data
    file_to_write.write(data)
    file_to_write.close()
    print 'Download segment Successful from ',segment_beginaddr, " to ", segment_endaddr

    socket1.close()
    #resultFile.seek(int(segment_beginaddr))
    #print "write: ", data, " into : " , fileName
    #print " The segment list for file : " , fileName, " is: ", segmentDict.get(fileName," Not")
    #resultFile.write(data)
    updateDownloadedSegmentList(fileName, segment_beginaddr)
    #socket1.close()


def updateDownloadedSegmentList(filename, s_byte):
	#print " The segment Dict in updateDownloadedSegmentList is : " , segmentDict.items()
	if(segmentDict.get(filename) == "None"):
		segmentDict[filename] = s_byte
	else:
		segmentDict[filename].append(s_byte)
		
	

def checkIfSegmentIsAlreadyDownloaded(filename, s_byte):
	#print "File name: ", filename, " s_byte ", s_byte
	#print " The segment Dict is : " , segmentDict.get(filename,"None")
	segmentStr = segmentDict.get(filename,"None")


	#print " The segementStr is : ", segmentStr, " Current start byte: ", s_byte
	if s_byte in segmentStr:
		return True
	return False
                
    

