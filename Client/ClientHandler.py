import httplib
import urllib
import thread
import time


def input_command(threadName, delay):
	main()	

def process_data(threadName, delay, response, filename):
	
	str = response.read(1024)
	print "Hi" + str
	if len(str) == 0:
		time.sleep(delay)
	file = open(filename, "w")
	#file.write("hello world in the new file\n")
	#file.write("and another line\n")
	file.write(str)

	#print str
	file.close()


while True:
   #input a command that client needs to perform
   command = raw_input('Enter your command: ');

   #Stop the client program, if you don't need any more commands to be sent
   if command=='Quit':
   	break;

   	#create a tracker for input file below
   if command == 'createTracker':

   	#Input a filename
   	filename = raw_input('Input File name: ');
   	#send the data to the server over post request
   	params = urllib.urlencode({'command':command,'filename':filename})
   #if not a createTracker command, send the command type in post request
   params = urllib.urlencode({'command':command})
   #set the header
   headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
   #try to connect to the server
   conn = httplib.HTTPConnection("10.106.78.73:8080")
   conn.request("POST", "/BTTracker/announce", params, headers)
   #response sent by the server
   response = conn.getresponse()
  
   try:
   	#str = response.read(1024)
   	#handle the processes that needs to be done at client side in a thread
   	thread.start_new_thread( process_data, ("Thread-2", 4, response, filename, ) )
   except:
   	print "Error: unable to start thread"
   print "end"
