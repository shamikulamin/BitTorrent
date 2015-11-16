def server_module(socket):
    HOST_S = socket.gethostname()               
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
            string = reqCommand.split(' ', 1)   #in case of 'put' and 'get' method
            reqFile = string[1] 

            if (string[0] == 'upload'):
                with open(reqFile, 'wb') as file_to_write:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        file_to_write.write(data)
                        file_to_write.close()
                        break
                print 'Receive Successful'
            elif (string[0] == 'download'):
                with open(response[0], 'rb') as file_to_send:
                    file_to_send.seek(int(response[1]))
                    conn.sendall(file_to_send.read(1024))
                print 'Send Successful'
        conn.close()

    socket.close()