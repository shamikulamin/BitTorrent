import socket
import sys
import serverThreadConfig
HOST = socket.gethostname()               
#PORT = serverThreadConfig.config['port']
PORT = 12345

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((HOST, int(PORT)))

socket.listen(1)
while (1):
    conn, addr = socket.accept()
    print 'New client connected ..'
    reqCommand = conn.recv(1024)
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
            with open(reqFile, 'rb') as file_to_send:
                for data in file_to_send:
                    conn.sendall(data)
            print 'Send Successful'
    conn.close()

socket.close()