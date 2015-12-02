import httplib
import urllib
import thread
import time
import socket
import sys
import hashlib
import time
import glob
import os

from utility import connect_tracker_server, getMd5, getFileSize, process_data, createTrackerFile, updateTrackerFile, parseTrackerFile, removeTrackerFilesForExistingFiles, removeOriginallySharedFiles


    

def handle_tracker_server(threadname, socket, delay, relevant_path, included_extenstions, listOfFiles, sharedFiles, updateTrackerFilesList, updatedListOfFiles, ip_address, PORT, tracker_server_port, maxSegmentSize,maxFileSizeFromTrackerServer):
    while (1):
        # keep track of segment count in a particular tracker file
        # so that inform the peer not to send the update request for another tracker file
        # unless current tracker file is done updating

        allSegmentUpdatedCount = 0

        #create tracker files for all the files that peer wants to share
        if (len(sharedFiles) < len(listOfFiles)) :
            #print "Shared Files: " , sharedFiles , " List of Files: ", listOfFiles
            for file in listOfFiles:
                if(file not in sharedFiles):
                    currentFile = file
                    #print currentFile
                    params = createTrackerFile(relevant_path + file, "Hello", ip_address, PORT)
                    #isShared = 1 
                    #print "Tracker file being Created for : ", currentFile ,"\n"
                    
                    #uncomment this line to get server response
                    recvCode=connect_tracker_server(params,socket, 'createTracker',ip_address, tracker_server_port, maxSegmentSize,maxFileSizeFromTrackerServer)
                    #print " Tracker file has been created: Code - " , code
                    if recvCode == '200':
                        sharedFiles.append(currentFile)
                        recvCode = 404
                   

        else:
            
            time.sleep(delay)

            #print "here I am in Update Tracker "
            allowed_extensions = ["track"]
            updateTrackerFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in allowed_extensions)]

            updateTrackerFilesList = removeOriginallySharedFiles(relevant_path, updateTrackerFilesList)
            # maintain a local copy and updated tracker copy - once updated to tracker file
            # overwrite the local copy with the updated tracker copy
            #update tracker for all downloaded files
            # TODO: should be greater
            #if(len(updatedListOfFiles) < len(updateTrackerFilesList)):
                #print (delay , updatedListOfFiles)
            for file in updateTrackerFilesList:
                updatedFile = file
                # TODO: uncomment this line
                #if(file not in listOfFiles):
                listOfSegments = parseTrackerFile(relevant_path + file)
                #print " Update Tracker File : List of segments: \n ", listOfSegments
                for index in range(len(listOfSegments) -1):
                    segmentLine = listOfSegments[index].split(":")
                    #print "Peer 8: Update the tracker server file with ", segmentLine,"\n\n"

                    params = updateTrackerFile(relevant_path+file, segmentLine)
                    #print " Update Tracker Params: ", params
                    
                    #print "Updated file Tracker for : ", updatedFile
                    #uncomment this line to get server response
                    recvCode = connect_tracker_server(params, socket, 'updateTracker',ip_address, tracker_server_port, maxSegmentSize,maxFileSizeFromTrackerServer)
                    if recvCode == '200':
                        allSegmentUpdatedCount += 1
                        recvCode = 404
                    else:
                        index = index - 1
                      

                # if allSegmentUpdatedCount == len(listOfSegments) -1:
                #     updatedListOfFiles.append(updatedFile)
                    #print "Tracker file has been UPDATED: ", updatedFile


def connect_peer_server(threadname, relevant_path, downloadedFiles, downloadingFiles, listOfFiles, allFilesList, ip_address, peer_server_port, tracker_server_port, maxSegmentSize,maxFileSizeFromTrackerServer, socket ):
    while(1):
        #print " Connect Peer Server "
        #list all the files available in the tracker server
        params = "GET command=list"    #urllib.urlencode({'command':'list'})
        print "\n Peer 8 : ", params, " \n\n"
        #TODO: uncomment this line to get server response
        listString=connect_tracker_server(params, socket, 'list', ip_address, tracker_server_port,maxSegmentSize,maxFileSizeFromTrackerServer)
       
        #Below list of files should be downloaded at this peer
        allTrackerFilesList = listString.split("\n")
        #print " All Tracker Files Obtained: ", allTrackerFilesList
        toBeDownloadedFileList = removeOriginallySharedFiles(relevant_path,allTrackerFilesList)
        
        #print "downloading Files" , downloadingFiles, " toBeDownloadedFileList ", toBeDownloadedFileList
        #if (len(downloadedFiles) < len(toBeDownloadedFileList)):
        #print "Peer 8: All tracker files lists that need to be downloaded: ", toBeDownloadedFileList, "\n\n"
        if len(toBeDownloadedFileList) > 0:
            # last one is always empty
            for index in range(len(toBeDownloadedFileList)-1):
                trackerFile = toBeDownloadedFileList[index]
                #print " To be downloaded List in : ", trackerFile
                #downloadedFiles.append(trackerFile)
                #get the tracker file for the this file
                #params = urllib.urlencode({'command':'get','filenametrack':trackerFile})
                params = "GET command=get"+"&filenametrack="+trackerFile
                print "\n Peer 8: ", params, " \n\n"
                #uncomment this line to get response from the server
                getTrackerString = connect_tracker_server(params, socket , 'get',ip_address, tracker_server_port, maxSegmentSize,maxFileSizeFromTrackerServer)
                
                if os.path.isfile(relevant_path + trackerFile) == True: 
                    lines = [line.rstrip('\n') for line in open(relevant_path + trackerFile).readlines()]

                    for line in lines:
                        if line not in getTrackerString:
                            getTrackerString += line +"\n"

                #print "Peer 8 : GET Tracker File: \n " , getTrackerString, "\n\n"
                try:
                    #print "END HERE "
                    # try downloading the files as per the tracker file
                    #pass the contents of tracker file 
                    thread.start_new_thread( process_data, ("Thread-3", 5, getTrackerString, trackerFile, relevant_path, maxSegmentSize, ip_address, peer_server_port, socket, tracker_server_port, maxFileSizeFromTrackerServer) )
                except:
                    print "Error: unable to start thread - process_data"


def client_module(socket, config):
    #isShare = 0;

    #listOfFiles1 = glob.glob("/Users/vijay/BitTorrent/Client2/shared/*.*")
    #listOfFiles1 = glob.glob("./shared/*.*")
    #relevant_path = "/Users/vijay/BitTorrent/Client2/shared/"  <-- can only work on vijay's computer, also affects string split routines in other program functions
    
    #get the shared folders where the files to be uploaded and downloaded would be saved for current peer
    relevant_path = config["pathToSharedFolder"]
    included_extenstions = ['jpg', 'txt', 'png', 'gif','png','pdf','log']
    allowed_extensions =['track']
    all_extenstions = ['jpg', 'txt', 'png', 'gif','png','pdf','track', 'log']
    listOfFiles = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in included_extenstions)]

    allFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in all_extenstions)]

    #Send the updated segment information to the tracker server
    #for files with .track extensions
    updateTrackerFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in allowed_extensions)]

    temp_extensions =['temp','track']

    toBeRemovedFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in allowed_extensions)]
            
    updatedListOfFiles = []
    #print listOfFiles
    #inputCommand = "share"
    sharedFiles = [] 
    trackerUpdateTime = config["updateTime"]
    #print "Update time is: ", trackerUpdateTime

    # List of files which are completely downloaded
    downloadedFiles =[]
    # List of files whose segments are downloaded, incomplete.
    downloadingFiles =[]
    
    # LIST tracker files at tracker server
    listOfTrackerFilesString = ""
    
    #CREATETRACKER file at tracker server
    recvCode = 404
    
    HOST = socket.gethostbyname(socket.gethostname())    # server name goes in here
        #HOST = "127.0.0.1"
    PORT = config["port"]
    tracker_server_port = config["trackerServerPort"]
        
    #ip_address = socket.gethostbyname(socket.gethostname())
    ip_address = socket.gethostbyname(socket.gethostname()) 
    maxSegmentSize = config["maxSegmentSize"]
    maxFileSizeFromTrackerServer = config["maxFileSizeFromTrackerServer"]
    
    #print "Peer 8 : IP ADDRESS: ", ip_address, " PORT: ", PORT

    # files = glob.glob(relevant_path+'*')
    # for f in files:
    #     os.remove(f)
    # #time.sleep(2)
    # files = glob.glob(relevant_path+("*.temp","*.track"))
    # for f in toBeRemovedFilesList:
    #     print "File here : ", f , "\n"
    #     os.remove(relevant_path + f)

   # while(1):

    try:
        #pass the contents of tracker file 
        thread.start_new_thread( handle_tracker_server, ("Thread-1", socket, trackerUpdateTime, relevant_path, included_extenstions, listOfFiles, sharedFiles,updateTrackerFilesList, updatedListOfFiles, ip_address, PORT, tracker_server_port,maxSegmentSize,maxFileSizeFromTrackerServer) )
        thread.start_new_thread(connect_peer_server, ("Thread-2",relevant_path, downloadedFiles, downloadingFiles, listOfFiles, allFilesList, ip_address, PORT, tracker_server_port,maxSegmentSize,maxFileSizeFromTrackerServer, socket))
    except:
        print "Error: unable to start thread - main "



