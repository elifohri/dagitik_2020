#!/usr/bin/env python3

import sys
import threading
import socket
import queue
import datetime

jNo=0

class ReadThread(threading.Thread):
    def __init__(self, name, counter, conn_sock, client_address, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.counter = counter
        self.conn_sock = conn_sock
        self.client_address = client_address
        self.threadQueue = threadQueue
        dict_queues[counter] = self.threadQueue
        self.nick = ""
    
    def run(self):
        print("Starting: ", self.name, self.counter)
        logQueue.put("New Read Thread (no: %s) is created for: %s" % (self.counter, self.client_address))
        while True:
            data = self.conn_sock.recv(1024)
            self.parser(data.decode())
            if data.decode().strip().split(" ")[0] == "QUI":
                client = self.nick
                if client in dict_clients.keys():
                    del dict_clients[client]
                    del dict_queues[self.counter]
                    for val in dict_queues:
                        dict_queues[val].put("WRN %s has just left the group." % (client))
                print("Ending: ", self.name, self.counter)
                break
        #self.conn_sock.close()

    def parser(self, data):
        msg = data.strip().split(" ")
        logQueue.put("Message Received: %s From Thread %s From Client: %s" % (msg[0], self.counter, self.client_address))
        if self.nick == "":
            if msg[0] == "QUI":
                self.threadQueue.put("BYE")
            elif msg[0] == "PIN":
                self.threadQueue.put("PON")
            elif msg[0] == 'NIC':
                if msg[1] in dict_clients.keys():
                    self.threadQueue.put("REJ %s" % msg[1])
                else:
                    self.threadQueue.put("WEL %s" % msg[1])
                    dict_clients[msg[1]] = self.threadQueue
                    self.nick = msg[1]
                    for val in dict_queues:
                        if not val == self.counter:
                            dict_queues[val].put("WRN %s has just joined the group." % self.nick)
            else:
                self.threadQueue.put("LRR")
        else:
            if msg[0] == "QUI":
                self.threadQueue.put("BYE %s" % (self.nick))
            elif msg[0] == "TON":
                pass
            elif msg[0] == "PIN":
                self.threadQueue.put("PON")
            elif msg[0] == "NIC":
                self.threadQueue.put("REJ %s" % msg[1])
            elif msg[0] == 'GLS':
                client_list = ""
                for key in dict_clients:
                    client_list += (key+":")
                client_list = client_list[:-1]
                self.threadQueue.put("LST %s" % client_list)
            elif msg[0] == 'GNL':
                message = ""
                for element in range (1, len(msg)):
                    message += (msg[element] + " ") 
                for val in dict_queues:
                    if not val == self.counter:
                        dict_queues[val].put("GNL %s: %s" % (self.nick, message))
                self.threadQueue.put("OKG")
            elif msg[0] == 'PRV':
                client = msg[1]
                message = ""
                for element in range (2, len(msg)):
                    message += (msg[element] + " ") 
                if client in dict_clients.keys():
                    dict_clients[client].put("PRV %s: %s" % (self.nick, message))
                    self.threadQueue.put("OKP")
                else:
                    self.threadQueue.put("NOP %s" % client)
            else:
                self.threadQueue.put("ERR")            

class WriteThread(threading.Thread):
    def __init__(self, name, counter, conn_sock, client_address, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.counter = counter
        self.conn_sock = conn_sock
        self.client_address = client_address
        self.threadQueue = threadQueue


    def run(self):
        print("Starting: ", self.name, self.counter)
        logQueue.put("New Write Thread (no: %s) is created for: %s" % (self.counter, self.client_address))
        while True:
            data = self.threadQueue.get()
            print("Server responding: ", data)
            self.conn_sock.send(data.encode())
            msg = data.strip().split(" ")
            if msg[0]=="BYE":
                print("Ending: ", self.name, self.counter)                
                break

class LoggerThread(threading.Thread):
    def __init__(self, logQueue):
        threading.Thread.__init__(self)
        self.logQueue = logQueue

    def run(self):
        self.logQueue.put("Logger Thread started.")
        while True:
            data = self.logQueue.get()
            JustTime= datetime.datetime.now()
            LogFile = open("LogFile.txt", "a")
            LogFile.write("\n" + JustTime.strftime("%d"+"."+"%m"+"."+"%Y") +  " " + JustTime.strftime("%H"+"."+"%M"+"."+"%S") +" "+ str(data))
            LogFile.close()                                
            
def main():

    try:

        global dict_clients
        dict_clients = {}

        global dict_queues
        dict_queues={}

        global LogFile , logQueue, newLoggerThread
        logQueue = queue.Queue()
        newLoggerThread = LoggerThread(logQueue)
        newLoggerThread.start()

        server_addr = "0.0.0.0"
        server_port = int(sys.argv[1])

        s = socket.socket()
        print("Socket created.")
        logQueue.put("Socket is created.")
        s.bind((server_addr, server_port))
        print("Socket binded to port {}.".format(server_port))
        logQueue.put("Socket binded to port: %s" % str(server_port))
        s.listen(5)
        print("Socket is listening.")        
        logQueue.put("Socket is now listening.")

        counter = 1
        threads = []

        while True:
            conn_sock, client_address = s.accept()
            print('New connection from', client_address)
            logQueue.put("New connection from: %s" % str(client_address))
            threadQueue = queue.Queue()
            newReadThread = ReadThread("ReadThread", counter, conn_sock, client_address, threadQueue)
            newReadThread.start()
            threads.append(newReadThread)            
            newWriteThread = WriteThread("WriteThread", counter, conn_sock, client_address, threadQueue)
            newWriteThread .start()
            threads.append(newWriteThread)
            counter += 1

        print("Exiting Main Thread")

        s.close()
    
    except socket.error:
        print("Error:",socket.error)

if __name__ == '__main__':
  main()