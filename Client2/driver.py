import thread
import time
import socket
import sys
import time
import glob
import os
import shutil


from client import client_module
from server import server_module

if __name__ == "__main__":
    config = {}
    execfile("./Client2/settings.conf", config)
    # python 3: exec(open("example.conf").read(), config)

    

def execute_client( threadName, config):

  relevant_path = config["pathToSharedFolder"]
  if os.path.exists(relevant_path+"temp/"):
    shutil.rmtree(relevant_path+"temp/")
    
  delete_extensions = ['track','temp']
    
  deleteFilesList = [fn for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in delete_extensions)]
  
  for f in deleteFilesList:
    os.remove(relevant_path + f)

  client_module(socket, config)

def execute_server(threadName, config):
	server_module(socket, config)


# Create two threads as follows
try:
   thread.start_new_thread( execute_server, ("Thread-1", config) )
   thread.start_new_thread( execute_client, ("Thread-2", config) )
except:
   print "Peer 2 - Error: unable to start thread"

while 1:
	pass
