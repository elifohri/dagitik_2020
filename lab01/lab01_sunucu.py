#Bağlantı kontrolü (TIC,TOC) ve bozuk mesaj geldiğinde (ERR) mesajı dışındaki kısımları yaptım.
#Thread oluştururak farklı bağlantıların kurulmasını sağladım

import sys
import socket 
import threading
import random

class connThread(threading.Thread):
    def __init__(self, threadID, conn, c_addr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.c_addr = c_addr

    def run(self):
        conn.send("Sayi bulmaca oyununa hosgeldiniz!".encode()) 
       
        while True:
            data = self.conn.recv(1024)
            data_str = data.decode().strip().split()
            if data_str[0] == "QUI":
                print("BYE")
                break
            elif data_str[0] == "TRY":
                self.conn.send("GRR".encode())             
                    
            elif data_str[0] == "STA":                    
                n = random.randint(1, 99)                    
                self.conn.send("RDY".encode()) 
                data2 = self.conn.recv(1024)
                data_str2 = data2.decode().strip().split()
                while data_str2[0] == "TRY":
                    try:
                        guess = int(data_str2[1])
                    except ValueError:
                        self.conn.send("PRR".encode()) 
                    else:                        
                        if (guess < n):
                            self.conn.send("LTH".encode()) 
                            data2 = self.conn.recv(1024)
                            data_str2 = data2.decode().strip().split()
                        elif (guess > n):
                            self.conn.send("GTH".encode()) 
                            data2 = self.conn.recv(1024)
                            data_str2 = data2.decode().strip().split()
                        else :
                            self.conn.send("WIN".encode()) 
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