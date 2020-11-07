import sys
import string
import queue
import time
from multiprocessing import Lock, Process, Queue, current_process

s = int(sys.argv[1])
n = int(sys.argv[2])
l = int(sys.argv[3])

f1 = open("input.txt", "r")
f2 = open("crypted_fork_20_8_8.txt", "a")

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

def sezar(work_queue, text_queue, s):
    while True:
        if not work_queue.empty():
            data = work_queue.get()
            if data == "STOP" :
                print("received quit request" )
                break
            text = sezar_sifreleme(data, s)
            text_queue.put(text)         
        time.sleep(1)  

def main() :
    
    work_queue = Queue()
    text_queue = Queue()
    processes = []

    while True :
        metin = f1.read(l)
        work_queue.put(metin)
        if not metin : 
            break

    for i in range(0,n):
        p = Process(target=sezar, args=(work_queue, text_queue, s))
        p.start()
        processes.append(p)
        work_queue.put('STOP')
    
    for p in processes:
        p.join()
    
    text_queue.put('STOP')

    for status in iter(text_queue.get, 'STOP'):
        f2.write(status)

if __name__ == '__main__':
    main()

f1.close()
f2.close()