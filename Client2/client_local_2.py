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

from utility import put, get, getMd5, getFileSize, process_data, createTrackerFile, PORT, HOST, ip_address

isShare = 0;
while(1):
    inputCommand = raw_input("Enter your command: ")
    if (inputCommand == 'quit'):
        socket.send('quit')
        break

    else:
        tokens = inputCommand.split(' ')
        if (tokens[0] == 'share'):
            params = createTrackerFile(tokens[1], tokens[2])
            isShare = 1

        elif (tokens[0] == 'upload'):
            put(inputCommand)

        elif (tokens[0] == 'download'):
            get(inputCommand)

        #create a tracker for input file below
        elif tokens[0] == 'createTracker':
            #send the data to the server over post request
            params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'filesize':tokens[2], 'description':tokens[3],'md5':tokens[4],'ip':ip_address,'port':PORT})

        #update tracker at tracker server
        elif tokens[0] == 'updateTracker':
            params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'sbyte':tokens[2], 'ebyte':tokens[3],'ip':ip_address,'port':PORT})
   
        elif tokens[0] == 'get':
            params = urllib.urlencode({'command':tokens[0],'filenametrack':tokens[1]})
   
        elif tokens[0] == 'list':
            #if not a createTracker command, send the command type in post request
            params = urllib.urlencode({'command':tokens[0]})
     
        else:
            print "wrong command"

        if isShare == 1 or tokens[0] == 'createTracker' or tokens[0] == 'updateTracker' or tokens[0] == 'get' or tokens[0] =='list':
            #set the header
            headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
            #try to connect to the server
            #print clientThreadConfig.config['ip']
            conn = httplib.HTTPConnection(clientThreadConfig.config['ip'] + ":" + clientThreadConfig.config['port']);
            conn.request("POST", "/BTTracker/announce", params, headers)
            #response sent by the server
            response = conn.getresponse()
            
            if tokens[0] !='get':
                print response.read()

            if tokens[0] == 'get':
                #print response.read()
                try:
                    thread.start_new_thread( process_data, ("Thread-1", 2, response, tokens[1]) )
                except:
                    print "Error: unable to start thread"

            #background = AsyncWrite("Hii" , 'vijay.txt')
            #uploadFileThread = AsyncUploadFile(response.read(1024))

            #background.start()
            #background.join()


