import httplib
import urllib


def main():
   print  "name"
   params = urllib.urlencode({'command':'creatracker','filename':'asbd.avi'})
   headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
   conn = httplib.HTTPConnection("localhost:8080")
   conn.request("POST", "/BTTracker/announce", params, headers)
   response = conn.getresponse()
   print response.status, response.reason
main()