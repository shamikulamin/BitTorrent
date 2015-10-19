import subprocess
import os

def splitFile():
    #statinfo = os.stat("./toShare/testfile.exe");
    #segmentSize = 
    subprocess.call(["7z", "a", "./toShare/testfile/archive.7z", "./testfile.exe", "-v50m"])
    print("File split successful")

def mergeFile():
    subprocess.call(["7z", "e", "./toShare/testfile/archive.7z.*", "-o./toShare/"])
def chksumFile():
    file = open('./toShare/testfile.txt', 'w+')
    print(subprocess.call(["7z", "h", "./toShare/testfile/", "> ./toShare/testfile.txt"], stdout=file))

def main():
    splitFile()
    chksumFile()
    #mergeFile()

main()