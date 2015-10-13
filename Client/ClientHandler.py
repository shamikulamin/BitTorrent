import socket

def openConnection():
    s = socket.socket()
    host = socket.gethostname()
    port = 12345

    s.connect((host, port))
    print(s.recv(1024))
    s.close()

def main():
    openConnection()

main()