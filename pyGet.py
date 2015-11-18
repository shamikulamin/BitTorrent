import httplib

def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()

httpServ = httplib.HTTPConnection("10.106.78.73", 4444)
httpServ.connect()

#httpServ.request('GET', "/")

#response = httpServ.getresponse()
#if response.status == httplib.OK:
#    print "Output from HTML request"
#    printText (response.read())

httpServ.request('GET','name=Brad&quote=Testing.')

response = httpServ.getresponse()
if response.status == httplib.OK:
    print "Output from CGI request"
    printText (response.read())

httpServ.close()