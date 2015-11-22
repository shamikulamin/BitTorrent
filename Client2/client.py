import httplib
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

from utility import put, get, getMd5, getFileSize, process_data, createTrackerFile, updateTrackerFile, PORT, HOST, ip_address, parseTrackerFile

def connect_tracker_server(params,socket, command):
    print "Tracker server called "
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_server_host ="10.106.78.73"
    tracker_server_port = "4444"
    socket.bind((tracker_server_host, int(tracker_server_port)))

    socket.listen(1)
    while (1):
        conn, addr = socket.accept()
        print 'Tracker Server connected ..'
        print conn.recv(1024)
    #print params
    #set the header
    #headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    #try to connect to the server
    #print clientThreadConfig.config['ip']
    #httpServ = httplib.HTTPConnection("10.106.38.170", 4444, timeout =10)
    #httpServ.connect()
    #httpServ.request('GET',params)
    #conn = httplib.HTTPConnection(clientThreadConfig.config['ip'] + ":" + clientThreadConfig.config['port']);
    #conn.request("POST", "/BTTracker/announce", params, headers)
    #response sent by the server
    #response = conn.getresponse()
    #responseString = response.read()
    #response = httpServ.getresponse()
    #print "Hi " , response.read()
    #if response.status == httplib.OK:
    print "Output from CGI request"
    #print response.read()
    print "There " , responseString
    
    #httpServ.close()

    print "Hello there Mike "
    if command =='createTracker' or command == 'updateTracker':
        print "Welcome " , responseString
        code = responseString.split(':')
        ##print code
        if(code[0] == '200'):  
            #print "Tracker file created"
            sharedFiles.append(currentFile)
            print "Come here " ,sharedFiles
            return -1

    else:
        return responseString

def handle_tracker_server(threadname, socket, delay, relevant_path, included_extenstions, listOfFiles, sharedFiles):
    while (1):
        isShared = 0
        isUpdated = 0

        #create tracker files for all the files that peer wants to share
        if (len(sharedFiles) < len(listOfFiles)) :
            #print "Shared Files: " , sharedFiles , " List of Files: ", listOfFiles
            for file in listOfFiles:
                if(file not in sharedFiles):
                    currentFile = file
                    #print currentFile
                    params = createTrackerFile(relevant_path + file, "Hello")
                    isShared = 1 
                    #print ("Create tracker file for ", file)
                    break

        else:
            #print "here I am "
            time.sleep(delay)
            updatedListOfFiles = [fn for fn in os.listdir(relevant_path)
                    if any(fn.endswith(ext) for ext in included_extenstions)]

            # maintain a local copy and updated tracker copy - once updated to tracker file
            # overwrite the local copy with the updated tracker copy
            #update tracker for all downloaded files
            # TODO: should be greater
            if(len(updatedListOfFiles) >= len(listOfFiles)):
                #print (delay , updatedListOfFiles)
                for file in updatedListOfFiles:
                    # TODO: uncomment this line
                    #if(file not in listOfFiles):
                        params = updateTrackerFile(relevant_path + file)
                        isUpdated = 1
                        #print ("Update tracker file for ", file)
                        break

        #Temp - Delete this
        # if(currentFile not in sharedFiles):
        #     sharedFiles.append(currentFile)

        # if some file tracker needs to be created or updated
        # Call tracker server and perform the operation
        if(isShared == 1):
            #uncomment this line to get server response
            #connect_tracker_server(params,socket, 'createTracker')
            sharedFiles.append(currentFile)
       # elif(isUpdated == 1):
           # print "Updated file Tracker"
            #uncomment this line to get server response
            #connect_tracker_server(params, 'updateTracker')

    
        #time.sleep(delay)


def connect_peer_server(threadname, delay, relevant_path, downloadedFiles, downloadingFiles ):
    while(1):
        #print " Connect Peer Server "
        #list all the files available in the tracker server
        params = "command=list"    #urllib.urlencode({'command':'list'})
        #TODO: uncomment this line to get server response
        #responseString = connect_tracker_server(params, 'list')

        #read the response and get all the files that doesn't exist with the peer

        #Below list of files should be downloaded at this peer
        toBeDownloadedFileList = ["client1.txt"]
        #print "downloading Files" , downloadingFiles, " toBeDownloadedFileList ", toBeDownloadedFileList
        for trackerFile in toBeDownloadedFileList:
            if trackerFile not in downloadingFiles:
                downloadingFiles.append(trackerFile)
                #get the tracker file for the this file
                #params = urllib.urlencode({'command':'get','filenametrack':trackerFile})
                params = "command=get"+"&filenametrack="+trackerFile
                #uncomment this line to get response from the server
                #responseString = connect_tracker_server(params, 'get')

                pathToFile = relevant_path + trackerFile
                responseString = parseTrackerFile(pathToFile)
                print "Got tracker file - " , responseString, "\n\n"
                try:
                    #print "END HERE "
                    # try downloading the files as per the tracker file
                    #pass the contents of tracker file 
                    thread.start_new_thread( process_data, ("Thread-3", 2, str(responseString[0]), trackerFile, relevant_path) )
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
    listOfFiles = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in included_extenstions)]
    #print listOfFiles
    #inputCommand = "share"
    sharedFiles = [] 
    trackerUpdateTime = 5

    # List of files which are completely downloaded
    downloadedFiles =[]
    # List of files whose segments are downloaded, incomplete.
    downloadingFiles =[]


   # while(1):

    try:
        #pass the contents of tracker file 
        thread.start_new_thread( handle_tracker_server, ("Thread-1", socket, trackerUpdateTime, relevant_path, included_extenstions, listOfFiles, sharedFiles) )
        thread.start_new_thread(connect_peer_server, ("Thread-2", 2, relevant_path, downloadedFiles, downloadingFiles))
    except:
        print "Error: unable to start thread - main "



