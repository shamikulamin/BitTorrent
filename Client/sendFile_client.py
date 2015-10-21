import socket

s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))
f = open('sentfile.txt', 'w')
s.listen(5)
while True:
	c, addr = s.accept() # open connection with the client
	print 'Connection established from', addr
	print "Receiving..."
	l = c.recv(1024)
	while (l):
		print "Receiving..."
		f.write(l)
		l = c.recv(1024)
	f. close()
	print "Done, finished!"
	c.send('Terminating connection')
	c.close()
