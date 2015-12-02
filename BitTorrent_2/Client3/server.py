import os.path
def server_module(socket, config):
    HOST_S = socket.gethostbyname(socket.gethostname())               
    PORT_S = config["port"]
    maxSegmentSize = config["maxSegmentSize"]
    pathToSharedFolder = config["pathToSharedFolder"]

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind((HOST_S, int(PORT_S)))

    socket.listen(1)
    while (1):
        conn, addr = socket.accept()
        #print 'Peer 3 : New client connected ..'
        reqCommand = conn.recv(maxSegmentSize)
        response = reqCommand.split(",")
        #print 'Client> %s' %(reqCommand)
        if (reqCommand == 'quit'):
            break
        #elif (reqCommand == lls):
            #list file in server directory
        else:
            #print "Peer 3: Requested bytes " , response[0], response[1], response[2]
            #string = reqCommand.split(' ', 1)   #in case of 'put' and 'get' method
            reqFile = response[1] 

            if (response[0] == 'upload'):
                with open(pathToSharedFolder+reqFile, 'wb') as file_to_write:
                    while True:
                        data = conn.recv(maxSegmentSize)
                        if not data:
                            break
                        file_to_write.write(data)
                        file_to_write.close()
                        break
                #print 'Peer 3 - Receive Successful'
            elif (response[0] == 'download'):
                #print "Here I am"
                if ((int(response[3])-int(response[2])) <= int(maxSegmentSize)):
                    if (os.path.exists(pathToSharedFolder+response[1])):
                        with open(pathToSharedFolder+response[1], 'rb') as file_to_send:
                            file_to_send.seek(int(response[2]),0)
                            data = file_to_send.read(int(response[3]) - int(response[2]))
                            #print "Sent data : " , "\n From: ",response[2]," To: ", response[3], "\n\n"
                            conn.sendall(data)
                            file_to_send.close()
                            #print 'Peer 3 - Send Successful'
                    else:
                        #print "Peer 3: Try Downloading segment from Temp folder : ","\n\n"
                        with open(pathToSharedFolder+"temp/"+response[1].split('.')[0]+"_"+response[2]+"."+response[1].split('.')[1], 'rb') as file_to_send:
                            data = file_to_send.read()
                            conn.sendall(data)
                            file_to_send.close()
                            #print 'Peer 3 - Send Segment Successful'
                else: 
                    print "Peer 3 - Request segment size is greater than 1 KB. Don't send anything !! \n\n"
        conn.close()

    socket.close()