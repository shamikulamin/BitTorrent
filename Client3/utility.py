from random import shuffle
import httplib
import urllib
import time
import socket
import sys
import hashlib
import time
import thread
import threading
import os
import collections
import glob
import shutil
import errno
from socket import error as socket_error

segmentDict = collections.defaultdict(list)
lock = threading.Lock()
openFiles = []
openFilesIndex = []

def getMd5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    f.close()
    return hash.hexdigest()

def getFileSize(filename):
    fr = open((filename), "r")
    fr.seek(0,2) # move the cursor to the end of the file
    size = fr.tell()
    fr.close()
    return size

def getFileSizeFromTrackerFile(trackerFile):
    f = open(trackerFile , "r")
    #read file from the end of tracker file
    lines = [line.rstrip('\n') for line in f.readlines()]
    f.close()
    #print "Total lines: " , len(lines) 
    # Read the file from the last line
    # len(lines) -1 should give the last line, decrement i
    fileSize = -1
    for i, val in enumerate(lines):
        
        if i == 1:
            #print " Segment Line is ", i, val
            fileSize = val.split(":")
            break
    #print "File size : ", fileSize[1]
    return fileSize[1]

def getMd5FromTrackerFile(trackerFile):
    f = open(trackerFile , "r")
    #read file from the end of tracker file
    lines = [line.rstrip('\n') for line in f.readlines()]
    f.close()

    md5 = []
    for i, val in enumerate(lines):
        
        if i == 3:
            #print " Segment Line is ", i, val
            md5 = val.split(":")
            break
    #print "md5 : ", md5[1]
    return md5[1]

def getFileNameFromTrackerFile(trackerFile):
    f = open(trackerFile , "r")
    #read file from the end of tracker file
    lines = [line.rstrip('\n') for line in f.readlines()]

    fileName = []
    for i, val in enumerate(lines):
        
        if i == 0:
            #print " Segment Line is ", i, val
            fileName = val.split(":")
            break
    #print "PEER 4 : File NAME : ", fileName[1]
    return fileName[1]

def process_data(threadName, delay, response, trackerFile, relevant_path, maxSegmentSize, ip_address, peer_server_port):
    # response is the tracker file to be parsed #
    #TODO: uncomment if response is obtained here instead of response.read()
    #string = response.read(1024)

    string = response
    while len(string) == 0:
        time.sleep(delay)

    #print "Create a local copy of the tracker File: ", trackerFile, "\n"
    if len(string) > 0:
        #filenameList = filename.split('.')
        # begin write recd tracker data to filename.track #
        file = open(relevant_path + trackerFile, "w")
        file.write(string)
        file.close()
        
        time.sleep(2)
        #check if the entire file for current tracker file is already downloaded

        isFileAlreadyDownloaded = checkIfFileisDownloaded(relevant_path, trackerFile)

        if isFileAlreadyDownloaded == False:
            #get latest updated tracker file
            listOfSegmentsInTrackerFile = parseTrackerFile(relevant_path + trackerFile)

            #print "Peer 3: ", listOfSegmentsInTrackerFile,"\n\n"
            # get filename
            filename = listOfSegmentsInTrackerFile[len(listOfSegmentsInTrackerFile) - 1]

            fileSize = getFileSizeFromTrackerFile(relevant_path + trackerFile)
            md5  = getMd5FromTrackerFile(relevant_path + trackerFile)
            #create a temporary file to write the segment one by one
            fileNameTemp = relevant_path + filename + ".temp"
            
            resultFile = open(fileNameTemp, "wb")
            #resultFile.seek(0,2)
            resultFile.close()

            while(checkIfAllSegmentsDownloaded(filename, maxSegmentSize, fileSize) == False):
                time.sleep(2)
                try:
                    #get latest updated tracker file
                    listOfSegmentsInTrackerFile = parseTrackerFile(relevant_path + trackerFile)
                    #print " Peer 3: List of segments in tracker file: ",listOfSegmentsInTrackerFile,"\n\n"
                    # get filename
                    filename = listOfSegmentsInTrackerFile[len(listOfSegmentsInTrackerFile) - 1]
                    listOfSegmentsInTrackerFile.pop()
                    randomizedListOfSegments = listOfSegmentsInTrackerFile
                    shuffle(randomizedListOfSegments)

                    #print " list of segments in tracker file is: ", randomizedListOfSegments, "\n\n"
                    for segmentLine in randomizedListOfSegments:
                        time.sleep(2)
                        # segmentLine = randomizedListOfSegments[index]
                        #print "Peer 3: Try downloading current segment : from " ,  , "\n\n"

                        # calculate which segements to download, then download them
                        inf = segmentLine.split(":")

                        #print "Peer 3: Try downloading segment from " , inf[2], " to ", inf[3], "\n\n"
                        if int(inf[3]) - int(inf[2]) == int(fileSize):
                            #print "Peer 3: Entire file is present with the peer ", "\n"
                            #check if any segment in the entire file is pending to be downloaded in increasing order
                            startByte = int(inf[2])
                            endByte = startByte + int(maxSegmentSize)
                            # for last segment
                            if(endByte > int(fileSize)):
                                endByte = int(fileSize)
                            #try downloading each segment in increasing sequential order from the original peer
                            while(startByte < int(fileSize)):
                                #print "StartByte: ", startByte, " EndByte: ", endByte
                                isSegmentNeededToBeDownloaded = checkIfSegmentIsAlreadyDownloaded(filename, str(startByte))
                                
                                if isSegmentNeededToBeDownloaded == True:
                                    inf[2] = str(startByte)
                                    inf[3] = str(endByte)
                                    break;

                                startByte = endByte
                                endByte = startByte + int(maxSegmentSize)
                                if(endByte > int(fileSize)):
                                    endByte = int(fileSize)
                        else:
                            isSegmentNeededToBeDownloaded = checkIfSegmentIsAlreadyDownloaded(filename, inf[2])
                        #print " Peer 3: Does this segment need to be downloaded ? ", inf[2], " ", inf[3], isSegmentNeededToBeDownloaded, "\n\n"
                        #downloadSegment_old(string)
                        
                        try:
                            #print "END HERE "
                            if isSegmentNeededToBeDownloaded == True:
                                thread.start_new_thread( downloadSegmentInTempFolder, ("Thread-4", fileNameTemp, inf[0], inf[1], inf[2], inf[3], filename, maxSegmentSize,ip_address,peer_server_port, relevant_path));
                            #print "data successfully written to file"
                        except:
                            print "Error: unable to start thread - process_data"
                        #resultFile.seek(inf[2])
                        # new download segment executes as thread, downloads segment indicated to stream, updates local tracker #
                        # pass arguments: open filestream, server ip, server port, segment begin, segment end
                except:
                    print " Peer 3 : try getting segments \n\n"

                if not os.path.exists(relevant_path+"temp/"):
                    print " Peer 3: Complete file for this tracker file Downloaded - ", trackerFile, " \n\n" 

                else:
                    if os.path.isfile(fileNameTemp) == True:
                        #print " Peer 3 : All segments are Downloaded: ", filename,"\n\n"
                        fileNameTemp = mergeAllSegments(relevant_path, filename, fileNameTemp)

                        md5ForDownloadedFile = getMd5FromTrackerFile(relevant_path+trackerFile)
                        md5ForOriginalFile = getMd5(fileNameTemp)
                        
                        if md5ForDownloadedFile.strip() == md5ForOriginalFile.strip():
                            #shutil.rmtree(relevant_path+"temp/")
                            if os.path.isfile(fileNameTemp) == True:
                                os.rename(fileNameTemp, relevant_path+filename)
                            print "Peer 3 - File successfully Downloaded. Not Corrupted \n\n"

                #print "DONE\n\n"
                
                #check if the downloaded file is CORRECTLY downloaded
        else:
            print "\n Peer 3 : Corresponding file for current tracker file is already downloaded. ", trackerFile , "\n\n"
        

def createTrackerFile(filename, description, ip_address, PORT):
    #print filename
    fileNameList = filename.split("/")
    #actualFileName = fileNameList[6]  <--written only to ever work on vijay's computer...
    actualFileName = fileNameList[len(fileNameList) -1]
    filesize = getFileSize(filename)
    md5 = getMd5(filename)
    timestamp = int(time.time())

    #create the local copy of the tracker file
    #file = open("tracker"+str(timestamp)+".txt", "w")
    string = "Peer 3: "+ "Create Tracker" + " Filename: "+actualFileName+" Filesize: "+ str(filesize)+" Description:"+description+" MD5:"+md5+" "+str(ip_address)+":"+str(PORT)+":0:"+str(filesize)+":"+str(timestamp)
    # print string, "\n\n"
    params = "GET command=createTracker&filename="+actualFileName+"&filesize="+str(filesize)+"&description="+description+"&md5="+md5+"&ip="+str(ip_address)+"&port="+str(PORT)+"&timestamp="+str(timestamp)
    #file.write(string)
    #file.close()
    #send the data to the server over post request
    #please take a quick shower we are running late # Sweta Ojha
   
    return params

def updateTrackerFile(filename, segmentLine):
    fileNameList = filename.split("/")
    actualFileName = fileNameList[len(fileNameList) -1]
   

    string = "Peer 3: "+" Updatetracker "+ " Filename: "+ actualFileName+ " start byte "+ segmentLine[2]+" End byte "+ segmentLine[3]+" ip-address "+ segmentLine[0]+" port "+segmentLine[1]
    # print string ,"\n\n"
    params = "GET command=updateTracker&filename="+actualFileName+"&s_byte="+segmentLine[2]+"&e_byte="+segmentLine[3]+"&ip="+segmentLine[0]+"&port="+segmentLine[1]+"&timestamp="+segmentLine[4]
    
    return params

def parseTrackerFile(trackerFilename):
    
    listOfSegments = []
   
    file_to_read = open(trackerFilename, "r")
    #read file from the end of tracker file
    lines = [line.rstrip('\n') for line in reversed(file_to_read.readlines())]
    file_to_read.close()

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


def downloadSegment(threadName, fileNameTemp, server_addr, server_port, segment_beginaddr, segment_endaddr, fileName, maxSegmentSize,ip_address,peer_server_port, relevant_path):
    #print "Download segment: ", server_addr, server_port, segment_beginaddr, "  ",segment_endaddr,"\n\n"
    downloadSegmentStr = "download," + fileName + ","+segment_beginaddr+"," + segment_endaddr
    #print "Server Address : ", server_addr, " Server Port: ", server_port   
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect((server_addr, int(server_port)))
    socket1.send(downloadSegmentStr)
    #data = socket1.recv(1024)
    # print "Peer 3: Received data :" ,"\n"
    lock.acquire()
    global file_to_write
    #with open(fileNameTemp, 'rb+') as file_to_write:   
    if (fileNameTemp not in openFilesIndex):
        file_to_write = open(fileNameTemp, 'wb')
        #print 'opening file now\n'
        openFiles.append(file_to_write)
        openFilesIndex.append(fileNameTemp)
    else:
        index = openFilesIndex.index(fileNameTemp)
        # print 'opening existing file\n'
        file_to_write = openFiles[index] 

    file_to_write.seek(int(segment_beginaddr)+1,0)
    while True:
        data = socket1.recv(maxSegmentSize)
        #print data
        if not data:
            break

        #print data
        file_to_write.write(data)

        with open(relevant_path+fileName+".track", "ab") as updateTrackerFileWithCurrentSegment:
            segmentLineStr =str(ip_address)+":"+str(peer_server_port)+":"+segment_beginaddr+":"+segment_endaddr+":"+str(int(time.time()))+"\n"
            #print "Peer 3: Update tracker file with the current segment: \n"
            # print segmentLineStr
            updateTrackerFileWithCurrentSegment.write(segmentLineStr)
        updateTrackerFileWithCurrentSegment.close()
        
    file_to_write.close()
    updateDownloadedSegmentList(fileName, segment_beginaddr)
    lock.release();
    #print 'Client 1 : Download segment Successful from ',segment_beginaddr, " to ", segment_endaddr,"\n\n"

    socket1.close()
   
   
def downloadSegmentInTempFolder(threadName, fileNameTemp, server_addr, server_port, segment_beginaddr, segment_endaddr, fileName, maxSegmentSize,ip_address,peer_server_port, relevant_path):
    #lock.acquire()
    print "\n\n  Peer 3 : Try Downloading segment: ", " from " , segment_beginaddr, " to  ",segment_endaddr,"\n\n"
    downloadSegmentStr = "download," + fileName + ","+segment_beginaddr+"," + segment_endaddr
    #print "Server Address : ", server_addr, " Server Port: ", server_port
    try:
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket1.connect((server_addr, int(server_port)))
    
        socket1.send(downloadSegmentStr)

   
        #data = socket1.recv(1024)
        #print "Peer 3: Received data :" ,"\n" 
        
        if not os.path.exists(relevant_path+"temp/"):
            os.makedirs(relevant_path+"temp/")

        fileNames = fileName.split(".")
        with open(relevant_path+"temp/"+fileNames[0]+"_"+segment_beginaddr+"."+fileNames[1],"w") as file_to_write:   
            while True:
                data = socket1.recv(maxSegmentSize)
                #print data
                if not data:
                    break

                #print data
                file_to_write.write(data)

                with open(relevant_path+fileName+".track", "ab") as updateTrackerFileWithCurrentSegment:
                    segmentLineStr =str(ip_address)+":"+str(peer_server_port)+":"+segment_beginaddr+":"+segment_endaddr+":"+str(int(time.time()))+"\n"
                    #print "Peer 3: Update tracker file with the current segment: \n"
                    #  print segmentLineStr
                    updateTrackerFileWithCurrentSegment.write(segmentLineStr)
                updateTrackerFileWithCurrentSegment.close()
            
        file_to_write.close()
        updateDownloadedSegmentList(fileName, segment_beginaddr)
        

        #print 'Client 1 : Download segment Successful from ',segment_beginaddr, " to ", segment_endaddr,"\n\n"
        socket1.close()
        #lock.release();
    except socket_error as serr:
        print " \n\n Peer 3 : The requesting Peer is terminated \n\n"
        # if serr.errno != errno.ECONNREFUSED:
        #     # Not the error we are looking for, re-raise
        #     raise serr


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
        return False
    return True

def checkIfAllSegmentsDownloaded(filename, maxSegmentSize, fileSize):
    startByte = 0
    returnValue = True
    while(startByte < int(fileSize)):
        if(checkIfSegmentIsAlreadyDownloaded(filename, str(startByte)) == True):
            returnValue = False
            break
        startByte += int(maxSegmentSize)

    #print "Check if All segments Downloaded: ", returnValue, "\n"
    return returnValue

# Let's not download the files for which the entire file exist or 
# is completely downloaded
def removeTrackerFilesForExistingFiles(relevant_path, allTrackerFilesList):
    toBeDownloadedList = []
    isNotFound = 0

    all_extenstions = ['jpg', 'txt', 'png', 'gif','png','pdf','track']
    
    allFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in all_extenstions)]

    #print "All tracker Files ", allTrackerFilesList, " all Files List: ", allFilesList
    for index in range(len(allTrackerFilesList)-1):

        trackerFileNameList = allTrackerFilesList[index].split(".track")
        for filename in allFilesList:
            #print filename, " ", trackerFileNameList[0] , " ",allTrackerFilesList[index]
            #Only check for files that are completely downloaded
            if filename == trackerFileNameList[0]:
                isNotFound = 1
                break
            else:
                isNotFound = 0

        if isNotFound == 0:
            #print " File: ",trackerFileName[0] ,"  -  ", allTrackerFilesList[index]
            toBeDownloadedList.append(allTrackerFilesList[index])
            


    if(len(toBeDownloadedList)>0):
        do="nothing"
        # print " Peer 3 : To be downloaded List in : ", toBeDownloadedList
    else:
        print "Peer 3 : No new files that need to be downloaded. "
    return toBeDownloadedList


#Let's not try download already downloaded files
def checkIfFileisDownloaded(relevant_path, trackerFile):
    downloaded_extenstions = ['jpg', 'txt', 'png', 'gif','png','pdf']
    
    downloadedFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in downloaded_extenstions)]

    #toBeDownloadedFileTrackerList =downloadedFilesList

    trackerFileName = trackerFile.split(".track")

    if trackerFileName[0] in downloadedFilesList:
        #print " Peer 3: Existing downloaded files : ", downloadedFilesList, " -  ", trackerFileName
        return True
    #print " Peer 3: Existing downloaded files : ", downloadedFilesList, " -  ", trackerFileName, ": ", trackerFileName[0]
    return False

def removeOriginallySharedFiles(relevant_path, allTrackerFilesList):
    toBeDownloadedList = []
    isNotFound = 0

    all_extensions = ['jpg', 'txt', 'png', 'gif','png','pdf']
    
    allFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in all_extensions)]

    for trackerFile in allTrackerFilesList:
        trackerFileName = trackerFile.split(".track")
        if trackerFileName[0] not in allFilesList:
            toBeDownloadedList.append(trackerFile)
   
    return toBeDownloadedList

def mergeAllSegments(relevant_path, fileName, fileNameTemp):
    selectedFiles = []
    all_extensions = ['jpg', 'txt', 'png', 'gif','png','pdf']
    
    allFilesList = [fn for fn in os.listdir(relevant_path + "temp/")
            if any(fn.endswith(ext) for ext in all_extensions)]
    
    fileNameList = fileName.split(".")
    #print "All Files: ", fileName, " ",allFilesList, "\n\n"
    allFilesList = sorted(allFilesList, key=lambda x: int((x.split('_')[1]).split('.')[0]))
    #get all segments for the current file
    
    #print selectedFiles
    #print allFilesList
    with open(fileNameTemp, "wb") as outfile:
        for f in allFilesList:
            if f.startswith(fileNameList[0]) == True:
                with open(relevant_path +"temp/"+f, "rb") as infile:
                    outfile.write(infile.read())
                infile.close()
    outfile.close()

    return fileNameTemp  

   
