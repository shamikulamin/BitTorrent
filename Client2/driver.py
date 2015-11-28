import thread
import time
import socket
import sys
import time


from client import client_module
from server import server_module

if __name__ == "__main__":
    config = {}
    execfile("./Client2/settings.conf", config) 
    # python 3: exec(open("example.conf").read(), config)

    

def execute_client( threadName, config):
	#time.sleep(2)
	client_module(socket, config)

def execute_server(threadName, config):
	server_module(socket, config)


# Create two threads as follows
try:
   thread.start_new_thread( execute_server, ("Thread-1", config) )
   thread.start_new_thread( execute_client, ("Thread-2", config) )
except:
   print "Peer 1 - Error: unable to start thread"

while 1:
	pass
