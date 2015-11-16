import thread
import time
import socket
import sys
import time


from client import client_module
from server import server_module


def execute_client( threadName, delay):
	#time.sleep(2)
	client_module()

def execute_server(threadName):
	server_module(socket)


# Create two threads as follows
try:
	thread.start_new_thread( execute_server, ("Thread-1",) )
   #thread.start_new_thread( execute_client, ("Thread-2",2,) )
except:
	print "Error: unable to start thread"

while 1:
	pass
