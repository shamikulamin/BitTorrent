import httplib
import urllib
import socket
import threading
import time

host = socket.gethostname()
port = 12345

class AsyncWrite(threading.Thread):
   def __init__(self, text, out):
      threading.Thread.__init__(self)
      self.text = text
      self.out = out

   def run(self):
      f = open(self.out, "w")
      f.write(self.text)
      f.close()

      print "Finished background file write to " + self.out

def upload(commandName):
   socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   socket1.connect((host, port))
   socket1.send(commandName)
   string = commandName.split(' ', 1)
   inputFile = string[1]
   with open(inputFile, 'rb') as file_to_send:
      for data in file_to_send:
         socket1.sendall(data)
   print 'Upload Successful'
   socket1.close()
   return

def download(commandName):
   print "I am here"
   socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   socket1.connect((host, port))
   socket1.send(commandName)
   string = commandName.split(' ', 1)
   inputFile = string[1]
   with open(inputFile, 'wb') as file_to_write:
      while True:
         data = socket1.recv(1024)
         # print data
         if not data:
            break
         # print data
         file_to_write.write(data)
   file_to_write.close()
   print 'Download Successful'
   socket1.close()
   return

#Handle special commands by current client
def input_command():
   ip_address = socket.gethostbyname(socket.gethostname())
   #print "hi"
   while True:
      #print "there"
      #input a command that client needs to perform
      command = raw_input('Enter your command: ')
      #print command
      tokens = command.split(' ')
      #Stop the client program, if you don't need any more commands to be sent
      if tokens[0]=='Quit':
         break;

      #create a tracker for input file below
      if tokens[0] == 'createTracker':
         #send the data to the server over post request
         params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'filesize':tokens[2], 'description':tokens[3],'md5':tokens[4],'ip':ip_address,'port':port})

         #update tracker at tracker server
      elif tokens[0] == 'updateTracker':
         params = urllib.urlencode({'command':tokens[0],'filename':tokens[1], 'startbyte':tokens[2], 'endbyte':tokens[3],'ip':ip_address,'port':port})
   
      elif tokens[0] == 'get':
         params = urllib.urlencode({'command':tokens[0],'filenametrack':tokens[1]})
   
      elif tokens[0] == 'list':
         #if not a createTracker command, send the command type in post request
         params = urllib.urlencode({'command':tokens[0]})
      
      elif tokens[0] == 'upload':
         upload(tokens)

      elif tokens[0] == 'download':
         download(tokens)
     
      else:
         print "wrong command"

      if tokens[0] == 'createTracker' or tokens[0] == 'updateTracker' or tokens[0] == 'get' or tokens[0] =='list':
         #set the header
         headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
         #try to connect to the server
         conn = httplib.HTTPConnection("10.106.78.73:8080")
         conn.request("POST", "/BTTracker/announce", params, headers)
         #response sent by the server
         response = conn.getresponse()
         #print response.read(1024)
         background = AsyncWrite("Hii" , 'vijay.txt')
         uploadFileThread = AsyncUploadFile('README.txt')

         background.start()
         background.join()
      

def process_data(threadName, delay, response, filename):
   #str = response.read(1024)
   str = response
   print filename
   #print "Hi" + str
   if len(str) == 0:
      time.sleep(delay)
   file = open(filename, "w")
   #file.write("hello world in the new file\n")
   #file.write("and another line\n")
   file.write(str)
   file.close()


#main
input_command()

print "Exiting Main"
