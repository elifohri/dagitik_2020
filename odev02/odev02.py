import sys

s1 = sys.argv[1].strip()
s2 = sys.argv[2].strip()

myDict = {}
myList = []
fid = open("airlines.txt","r")

for line in fid:
    splittedLine = line.strip().split(",")
    myList = splittedLine[1:]
    myDict[splittedLine[0]] = myList

if s2 in myDict[s1] :
    print("Millerinizi kullanabilirsiniz!")
else :
    print("Millerinizi bu havayolunda kullanamazsınız!")   

fid.close()
