import sys
import string
import threading
from threading import Thread
import queue
import time

s = int(sys.argv[1])
n = int(sys.argv[2])
l = int(sys.argv[3])

f1 = open("input.txt", "r")
f2 = open("crypted_thread_12_6_48.txt", "a")

def sezar_sifreleme(text, shift):
    
    text1 = ""
    text2 = []
	
    alphabet = list(string.ascii_lowercase)
    text = text.lower()
    
    for i in text:
        if i in alphabet:
            index = alphabet.index(i)
            sifre = (index + int(shift)) % 26
            text2.append(sifre)
            text1 += alphabet[sifre]
        else:
            text1 += i
    return text1
 
class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print ("Starting" + self.name)
        sezar(self.name, self.q)
        print ("Exiting" + self.name)
        
def sezar(threadName, q):
    while True:
        queueLock.acquire()
        if not q.empty():
            data = q.get()
            queueLock.release()
            if data == "Quit" :
                print("%s received quit request" % (threadName))
                break
            text = sezar_sifreleme(data, s)
            textQueue.put(text)
        else :
            queueLock.release()          
        time.sleep(1)       
            
threadID = 1
threads = []
queueLock = threading.Lock()
workQueue = queue.Queue(0)
textQueue = queue.Queue(0)

# Yeni thread yaratma
for i in range(0,n):
    tName = "Thread" + str(i+1)
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1
    
# Kuyruğu doldurma  
queueLock.acquire()
while True :
    metin = f1.read(l)
    workQueue.put(metin)
    if not metin : 
        break     
queueLock.release()

# Kuyruğun boşalmasını bekliyoruz
while not workQueue.empty() :
    pass

# Threadlerin bittiğini söylüyoruz
for i in range(0,n):
    workQueue.put("Quit")
    
# Bütün threadlerin bitmesini bekliyoruz   
for t in threads:
    t.join()
    
for n in list(textQueue.queue):
    f2.write(n)

print("Exiting Main Thread")  
    
f2.close()
f1.close()