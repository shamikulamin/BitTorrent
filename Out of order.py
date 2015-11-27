
import os
size = os.stat("DiskSpeedTest.png").st_size
print str(size)
partition = size/3
partition_1 = partition +1
partition_2 = partition +1
partition_3 = partition

total = partition_1+partition_2+partition_3

print total

f = open('newfile.png',"wb")
f.seek(size)
f.write("\0")
f.close()

f1 = open("DiskSpeedTest.png","rb")
f = open('newfile.png',"r+b")
f1.seek(partition_1+partition_2)
f.seek(partition_1+partition_2)
f.write(f1.read(partition_3))
f1.close()
f.close()

f1=open("DiskSpeedTest.png","rb")
f = open('newfile.png',"r+b")
f.write(f1.read(partition_1))
f1.close()
f.close()


f1=open("DiskSpeedTest.png","rb")
f = open('newfile.png',"r+b")
f1.seek(partition_1)
f.seek(partition_1)
f.write(f1.read(partition_2))
f1.close()
f.close()
