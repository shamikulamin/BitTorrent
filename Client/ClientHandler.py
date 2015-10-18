import httplib
import urllib

def openConnection():
   response = httpServ.getresponse()
   if response.status == httplib.OK:
      print "Output from CGI request"
      printText (response.read())

def main():
   print  "name"
   params = urllib.urlencode({'command':'qwerty'})
   headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
   conn = httplib.HTTPConnection("localhost:8080")
   conn.request("POST", "/BTTracker/announce", params, headers)
   response = conn.getresponse()
   print response.status, response.reason
main()