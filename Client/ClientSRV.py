import socket

def main():
    s = socket.socket()
    host = socket.gethostname();
    port = 12345
    s.bind((host, port))

    s.listen(5)
    while True:
        c, addr = s.accept()
        # Print connection success string to the terminal command line
    
        print('Got Connection from' + str(addr))
        message = "Thank you for connecting"
        c.send(message.encode('utf-8'))
        c.close()

# Accessor Functions

# Mutation and Command functions (to modify the connection, re-establish the socket, etc.

#Main directive (auto-execute this code upon python parser execution)
main()

