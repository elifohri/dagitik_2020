#Bağlantı kontrolü (TIC,TOC) ve bozuk mesaj geldiğinde (ERR) mesajı dışındaki kısımları yaptım.
#Thread oluştururak farklı bağlantıların kurulmasını sağladım

import sys
import socket 
import threading
import random

def number_guess(n,guess):
    try:
        guess = int(guess)
    except ValueError:
        print("hata")
    else:                        
        if (guess < n):
            return("LTH")
        elif (guess > n):
            return("GTH")
        else :
            return("WIN")  

class connThread(threading.Thread):
    def __init__(self, threadID, conn, c_addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.c_addr = c_addr

    def run(self):
        conn.send("Sayi bulmaca oyununa hosgeldiniz!".encode()) 
       
        while True:
            start = 0
            data = self.conn.recv(1024)
            data_str = data.decode().strip()
            if data_str == "QUI":  
                print("BYE")
                break
            elif data_str == "TRY": 
                self.conn.send("GRR".encode())             
            elif data_str == "TIC":
                self.conn.send("TOC".encode())  
            elif data_str == "STA":                 
                n = random.randint(1, 99) 
                self.conn.send(str(n).encode()) 
                self.conn.send("RDY".encode()) 
                start = 1
            elif (data_str.startswith("TRY")):
                while (start == 1):
                    data_splitted = data_str.split(" ")
                    res = number_guess(n,data_splitted[1])
                    self.conn.send(str(res).encode()) 
                    if (res == "WIN") : 
                        break
        self.conn.close()     

s = socket.socket()

ip = "0.0.0.0"
port = int(sys.argv[1])

addr_server = (ip, port)
s.bind(addr_server)

s.listen(5)

counter = 0
threads = []
while True:
    conn, addr = s.accept() #blocking method
    newConnThread = connThread(counter, conn, addr)
    threads.append(newConnThread)
    newConnThread.start()
    counter += 1

s.close()
