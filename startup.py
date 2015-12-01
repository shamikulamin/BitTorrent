import time
import subprocess
import thread

import resource

serverFlag = 1
peerFlag = 1
peerFlag2 = 1

resource.setrlimit(resource.RLIMIT_CORE,(resource.RLIM_INFINITY, resource.RLIM_INFINITY))

startSeconds = int(round(time.time()))

while 1:
    currentTime = int(round(time.time()))
    if currentTime==startSeconds and serverFlag==1:
        serverFlag=0
        print "Starting Server Thread and First 2 Peers"      
        p1 = subprocess.Popen('exec python ./PyTracker/Tracker.py',shell=True)
        p2 = subprocess.Popen('exec python ./Client1/driver.py',shell=True)
        p3 = subprocess.Popen('exec python ./Client2/driver.py',shell=True)
    elif currentTime==startSeconds+30 and peerFlag==1:
        peerFlag=0
        print "Starting First Batch of Peers"
        p4 = subprocess.Popen('exec python ./Client3/driver.py',shell=True)
        p5 = subprocess.Popen('exec python ./Client4/driver.py',shell=True)
        p6 = subprocess.Popen('exec python ./Client5/driver.py',shell=True)
        p7 = subprocess.Popen('exec python ./Client6/driver.py',shell=True)
        p8 = subprocess.Popen('exec python ./Client7/driver.py',shell=True)
    elif currentTime==startSeconds+90 and peerFlag2==1:
        peerFlag2=0
        print "Starting Second Batch of Peers and Stopping Peer 1 and Peer 2"
        p2.kill()
        p3.kill()
        p9 = subprocess.Popen('exec python ./Client8/driver.py',shell=True)
        p10 = subprocess.Popen('exec python ./Client9/driver.py',shell=True)
        p11 = subprocess.Popen('exec python ./Client10/driver.py',shell=True)
        p12 = subprocess.Popen('exec python ./Client11/driver.py',shell=True)
        p13 = subprocess.Popen('exec python ./Client12/driver.py',shell=True)
    elif currentTime>=startSeconds+100:
        break;
