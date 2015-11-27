import time
import subprocess
import thread
serverFlag = 1
peerFlag = 1



startSeconds = int(round(time.time()))

while 1:
    currentTime = int(round(time.time()))
    if currentTime==startSeconds and serverFlag==1:
        #global serverFlag
        if serverFlag==1:
            serverFlag=0
            print "Starting Server Thread"      
            subprocess.Popen('python ./PyTracker/Tracker.py',shell=True)
            subprocess.Popen('python ./Client1/driver.py',shell=True)
    else:
        break;