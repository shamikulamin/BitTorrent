﻿import httplib
import urllib
import thread
import time
import socket
import sys
import hashlib
import time
import clientThreadConfig
import serverThreadConfig
import glob
import os

from utility import put, get, getMd5, getFileSize, process_data, createTrackerFile, updateTrackerFile, PORT, HOST, ip_address, parseTrackerFile, removeTrackerFilesForExistingFiles

def connect_tracker_server(params,socket, command):
    #print "Tracker server called "
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_server_host ="127.0.0.1"
    tracker_server_port = "4444"
    socket.connect((tracker_server_host, int(tracker_server_port)))

    #print " The current params is: ", params
    socket.send(params)
    data = ''
    recvCode = 404
    while (1):
        time.sleep(2)
        data = socket.recv(1024)
        
        if command == 'list':
            print "LIST of tracker Files  :\n" ,data
            socket.close()
            return data
           
        
        if command == 'get':
            print "GET tracker File :\n" ,data
            socket.close()
            return data

        if command =='createTracker' or command == 'updateTracker':
            code = data.split(':')
            ##print code
            if(code[0] == '200'):  
                socket.close()
                return code[0]
           
        if not data:
            break;

    
    socket.close()
    

def handle_tracker_server(threadname, socket, delay, relevant_path, included_extenstions, listOfFiles, sharedFiles, updateTrackerFilesList, updatedListOfFiles):
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
                    params = createTrackerFile(relevant_path + file, "Hello")
                    #isShared = 1 
                    print "Tracker file being Created for : ", currentFile 
                    
                    #uncomment this line to get server response
                    recvCode=connect_tracker_server(params,socket, 'createTracker')
                    #print " Tracker file has been created: Code - " , code
                    if recvCode == '200':
                        sharedFiles.append(currentFile)
                        recvCode = 404
                   

        else:
            #print "here I am in Update Tracker "
            time.sleep(delay)
           
            # maintain a local copy and updated tracker copy - once updated to tracker file
            # overwrite the local copy with the updated tracker copy
            #update tracker for all downloaded files
            # TODO: should be greater
            if(len(updatedListOfFiles) < len(updateTrackerFilesList)):
                #print (delay , updatedListOfFiles)
                for file in updateTrackerFilesList:
                    updatedFile = file
                    # TODO: uncomment this line
                    #if(file not in listOfFiles):
                    listOfSegments = parseTrackerFile(relevant_path + file)
                    print " Update Tracker File : List of segments: \n ", listOfSegments
                    for index in range(len(listOfSegments) -1):
                        segmentLine = listOfSegments[index].split(":")
                        print segmentLine

                        params = updateTrackerFile(relevant_path+file, segmentLine)
                        print " Update Tracker Params: ", params
                        
                        print "Updated file Tracker for : ", updatedFile
                        #uncomment this line to get server response
                        connect_tracker_server(params, socket, 'updateTracker')
                        if recvCode == '200':
                            allSegmentUpdatedCount += 1
                            recvCode = 404
                          

                    if allSegmentUpdatedCount == len(listOfSegments) -1:
                        updatedListOfFiles.append(updatedFile)
                        print "Tracker file has been UPDATED: ", updatedFile


def connect_peer_server(threadname, delay, relevant_path, downloadedFiles, downloadingFiles, listOfFiles ):
    while(1):
        #print " Connect Peer Server "
        #list all the files available in the tracker server
        params = "GET command=list"    #urllib.urlencode({'command':'list'})
        #TODO: uncomment this line to get server response
        listString=connect_tracker_server(params, socket, 'list')
        #responseString = listOfTrackerFilesString
        #print " Response String is : ", listString
        #read the response and get all the files that doesn't exist with the peer

        #Below list of files should be downloaded at this peer
        allTrackerFilesList = listString.split("\n")
        print " All Tracker Files Obtained: ", allTrackerFilesList
        toBeDownloadedFileList = removeTrackerFilesForExistingFiles(listOfFiles,allTrackerFilesList)
        
        #print "downloading Files" , downloadingFiles, " toBeDownloadedFileList ", toBeDownloadedFileList
        if (len(downloadedFiles) < len(toBeDownloadedFileList)):
            for trackerFile in toBeDownloadedFileList:

                print " To be downloaded List in : ", trackerFile
                downloadedFiles.append(trackerFile)
                #get the tracker file for the this file
                #params = urllib.urlencode({'command':'get','filenametrack':trackerFile})
                params = "GET command=get"+"&filenametrack="+trackerFile
                #uncomment this line to get response from the server
                getTrackerString = connect_tracker_server(params, socket , 'get')
                
                print "Got tracker file - " , getTrackerString, "\n\n"
                try:
                    #print "END HERE "
                    # try downloading the files as per the tracker file
                    #pass the contents of tracker file 
                    thread.start_new_thread( process_data, ("Thread-3", 2, getTrackerString, trackerFile, relevant_path) )
                except:
                    print "Error: unable to start thread - process_data"

            #else:
                #print "Tracker file already in downloadingFiles list"
           


def client_module(socket):
    #isShare = 0;

    #listOfFiles1 = glob.glob("/Users/vijay/BitTorrent/Client2/shared/*.*")
    #listOfFiles1 = glob.glob("./shared/*.*")
    #relevant_path = "/Users/vijay/BitTorrent/Client2/shared/"  <-- can only work on vijay's computer, also affects string split routines in other program functions
    
    #get the shared folders where the files to be uploaded and downloaded would be saved for current peer
    relevant_path = "./shared/"
    included_extenstions = ['jpg', 'txt', 'png', 'gif','png','pdf']
    allowed_extensions =['track']
    listOfFiles = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in included_extenstions)]

    #Send the updated segment information to the tracker server
    #for files with .track extensions
    updateTrackerFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in allowed_extensions)]

    updatedListOfFiles = []
    #print listOfFiles
    #inputCommand = "share"
    sharedFiles = [] 
    trackerUpdateTime = 5

    # List of files which are completely downloaded
    downloadedFiles =[]
    # List of files whose segments are downloaded, incomplete.
    downloadingFiles =[]
    
    # LIST tracker files at tracker server
    listOfTrackerFilesString = ""
    
    #CREATETRACKER file at tracker server
    recvCode = 404
    


   # while(1):

    try:
        #pass the contents of tracker file 
        thread.start_new_thread( handle_tracker_server, ("Thread-1", socket, trackerUpdateTime, relevant_path, included_extenstions, listOfFiles, sharedFiles,updateTrackerFilesList, updatedListOfFiles) )
        thread.start_new_thread(connect_peer_server, ("Thread-2", 2, relevant_path, downloadedFiles, downloadingFiles, listOfFiles))
    except:
        print "Error: unable to start thread - main "



