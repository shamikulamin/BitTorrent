import httplib
import urllib
import threading
import time
import socket
import sys

HOST = socket.gethostname()    # server name goes in here
PORT = 12345

class AsyncWrite(threading.Thread):
    def __init__(self, text, out):
        threading.Thread.__init__(self)
        self.text = text
        self.out = out

    def run(self):
        f = open(self.out, "w")
        f.write(self.text)
        f.close()

        print "Finished background file write to " + self.out


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


while(1):
    inputCommand = raw_input("Enter your command: ")
    if (inputCommand == 'quit'):
        socket.send('quit')
        break

    else:
        tokens = inputCommand.split(' ')
        if (tokens[0] == 'upload'):
            put(inputCommand)

        elif (tokens[0] == 'download'):
            get(inputCommand)

        #create a tracker for input file below
        elif tokens[0] == 'createTracker':
            #send the data to the server over post request
            params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'filesize':tokens[2], 'description':tokens[3],'md5':tokens[4],'ip':ip_address,'port':port})

        #update tracker at tracker server
        elif tokens[0] == 'updateTracker':
            params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'startbyte':tokens[2], 'endbyte':tokens[3],'ip':ip_address,'port':port})
   
        elif tokens[0] == 'get':
            params = urllib.urlencode({'command':tokens[0],'filenametrack':tokens[1]})
   
        elif tokens[0] == 'list':
            #if not a createTracker command, send the command type in post request
            params = urllib.urlencode({'command':tokens[0]})
     
        else:
            print "wrong command"

        if tokens[0] == 'createTracker' or tokens[0] == 'updateTracker' or tokens[0] == 'get' or tokens[0] =='list':
            #set the header
            headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
            #try to connect to the server
            conn = httplib.HTTPConnection("10.106.78.73:8080")
            conn.request("POST", "/BTTracker/announce", params, headers)
            #response sent by the server
            response = conn.getresponse()

            background = AsyncWrite("Hii" , 'vijay.txt')
            uploadFileThread = AsyncUploadFile(response.read(1024))

            background.start()
            background.join()


