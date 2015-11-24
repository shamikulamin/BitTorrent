def server_module(socket):
    HOST_S = "127.0.0.1"#socket.gethostname()               
    PORT_S = 12345

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind((HOST_S, int(PORT_S)))

    socket.listen(1)
    while (1):
        conn, addr = socket.accept()
        print 'New client connected ..'
        reqCommand = conn.recv(1024)
        response = reqCommand.split(",")
        print 'Client> %s' %(reqCommand)
        if (reqCommand == 'quit'):
            break
        #elif (reqCommand == lls):
            #list file in server directory
        else:
            print "Requested bytes " , response[0], response[1], response[2]
            #string = reqCommand.split(' ', 1)   #in case of 'put' and 'get' method
            reqFile = response[1] 

            if (response[0] == 'upload'):
                with open("./shared"+reqFile, 'wb') as file_to_write:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        file_to_write.write(data)
                        file_to_write.close()
                        break
                print 'Receive Successful'
            elif (response[0] == 'download'):
                #print "Here I am"
                with open("./shared/"+response[1], 'rb') as file_to_send:
                    file_to_send.seek(int(response[2]),0)
                    data = file_to_send.read(int(response[3]) - int(response[2]))
                    print "Sent data : " , "\n From: ",response[2]," To: ", response[3], "\n\n"
                    conn.sendall(data)

                print 'Send Successful'
        conn.close()

    socket.close()