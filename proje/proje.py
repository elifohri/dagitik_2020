#!/usr/bin/env python3

import sys
import threading
import socket
import queue
import datetime

class ReadThread(threading.Thread):
    def __init__(self, name, counter, conn_sock, client_address, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.counter = counter
        self.conn_sock = conn_sock
        self.client_address = client_address
        self.threadQueue = threadQueue        
        self.nick = ""
        self.logged_in = False
        self.isAdmin = False
    
    def run(self):
        print("Starting: ", self.name, self.counter)
        logQueue.put("New Read Thread (no: %s) is created for: %s" % (self.counter, self.client_address))
        while True:
            data = self.conn_sock.recv(1024)
            self.parser(data.decode())

    def parser(self, data):
        msg = data.strip().split(" ")
        logQueue.put("Message Received: %s From Thread %s From Client: %s" % (msg[0], self.counter, self.client_address))
        if self.logged_in == False:
            if msg[0] == "QUI":
                self.threadQueue.put("BYE")
            elif msg[0] == "PIN":
                self.threadQueue.put("PON")
            elif msg[0] == "REG":
                if not len(msg) == 3:
                    # Komut 3 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    if msg[1] in dict_clients.keys():
                        # Kullanici ismi basarısız
                        self.threadQueue.put("UNT %s" % msg[1])
                    elif msg[2] in dict_clients.values():
                        # Kullanici sifresi basarısız
                        self.threadQueue.put("PWT %s" % msg[1])                
                    else:
                        try:
                            psswrd = int(msg[2])                            
                        except ValueError:
                            self.threadQueue.put("NIP")
                        else:
                            # Kullanici ismi ve parolası başarılı
                            self.threadQueue.put("SUC %s" % msg[1])
                            dict_clients[msg[1]] = msg[2]  
                             
            elif msg[0] == "LGI":
                if not len(msg) == 3:
                    # Komut 3 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    if not msg[1] in dict_clients.keys():
                        # Kullanici ismi yanlis girilmis
                        self.threadQueue.put("WUN %s" % msg[1])
                    elif msg[1] in dict_clients.keys() and not dict_clients[msg[1]] == msg[2]:
                        # Kullanici parolasi yanlis
                        self.threadQueue.put("WPW %s" % msg[1])
                    elif dict_clients[msg[1]] == msg[2]:
                        # Kullanici girisi basarili
                        self.threadQueue.put("WEL %s" % msg[1])   
                        self.logged_in = True
                        self.nick = msg[1]   
                        dict_client_queues[self.nick] = self.threadQueue                  
            else:
                # Yukaridaki komutlar haricinde bu mesaj gönderilir
                self.threadQueue.put("LRR")
                

        else:
            if msg[0] == "TIN":
                self.threadQueue.put("TON")
            elif msg[0] == "CHG":
                if not len(msg) == 4:
                    # Komut 4 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    if not msg[1] in dict_clients.keys():
                        # Kullanici ismi bulunamadi
                        self.threadQueue.put("UNF %s" % msg[1])
                    elif msg[1] in dict_clients.keys() and not dict_clients[msg[1]] == msg[2]:
                        # Kullanici eski parolasi yanlis
                        self.threadQueue.put("WOP %s" % msg[1])
                    elif msg[3] in dict_clients.values():
                        # Kullanici yeni parolasi alinmis
                        self.threadQueue.put("NPT %s" % msg[1])
                    else:
                        try: 
                            psswrd = int(msg[3])
                        except ValueError:
                            self.threadQueue.put("NIP")
                        else:
                            dict_clients[msg[1]] = msg[3]
                            # Kullanici sifre degistirme islemi basarılı               
                            self.threadQueue.put("PCS %s" % msg[1])
            elif msg[0] == "SCR":
                if not len(msg) == 2:
                    # Komut 2 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[1]
                    if chat_room_name in dict_chat_rooms.keys():
                        # Bu isimde bir chat room zaten var
                        self.threadQueue.put("RNT %s" % chat_room_name)
                    else: 
                        # dict_chat_rooms'da key olarak oda ismi, value olarak chat room'u kuran kisiyi (admin) tuttum
                        dict_chat_rooms[chat_room_name] = self.nick
                        self.isAdmin = True
                        # Chat room olusturuldu
                        self.threadQueue.put("CRS %s" % chat_room_name)
            elif msg[0] == "GLR":
                if not len(msg) == 1:
                    # Komut 2 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    chat_room_list = ""
                    for key in dict_chat_rooms:
                        chat_room_list += (key+":")
                    chat_room_list = chat_room_list[:-1]
                    # Butun odalarin listesi yazdirilir
                    self.threadQueue.put("LST %s" % chat_room_list) 
            elif msg[0] == "GCR":   
                if not len(msg) == 2:
                    # Komut 2 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[1]
                    if chat_room_name in dict_chat_rooms.keys():
                        # odalardaki kullanicilari tutmak için chat_room_clients adinda yeni bir dictionary olusturdum, key olarak oda ismi value olarak kullanicilari ekledim
                        dict_chat_room_clients[chat_room_name] = dict_chat_room_clients.get(chat_room_name, []) + [self.nick]
                        # Yeni kullanici odaya eklendi
                        self.threadQueue.put("NWU %s" % self.nick)    
                        client_list = ""                 
                        if chat_room_name in dict_chat_room_clients.keys():
                            for key in dict_chat_room_clients:
                                if key == chat_room_name:
                                    client_list = dict_chat_room_clients[chat_room_name]                    
                            for val in client_list:
                                if not self.nick == val:
                                    # Odadaki diger kullanicilara yeni kullanicinin geldigi bildirilir
                                    dict_client_queues[val].put("NEW USER %s IN ROOM %s" % (self.nick, chat_room_name))   
                    elif not chat_room_name in dict_chat_rooms.keys():
                        # Yanlis oda ismi verilmis
                        self.threadQueue.put("WRN %s" % chat_room_name)  
                    else: 
                        # Odaya gitme istegi basarısız
                        self.threadQueue.put("UNA")  
            elif msg[0] == "GLU": 
                if not len(msg) == 2:
                    # Komut 2 parametreden olusmuyor
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[1]  
                    client_list = ""
                    if chat_room_name in dict_chat_room_clients.keys():
                        for key in dict_chat_room_clients:
                            if key == chat_room_name:
                                client_list = dict_chat_room_clients[chat_room_name]                
                        clients = ""
                        clients = dict_chat_rooms.get(chat_room_name, "no admin") + "-"
                        for val in client_list:
                            clients += (val+":")
                        clients = clients[:-1]
                        # Odanın yoneticisi ve kullanicilar yazdirilir
                        self.threadQueue.put("LSU %s" % clients)
                    else:
                        # Bu isimde bir oda yoksa
                        self.threadQueue.put("RNF %s" % chat_room_name)
            elif msg[0] == "GLC":
                if not len(msg) == 1:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    room_list = ""
                    for val in dict_chat_room_clients:
                        if self.nick in dict_chat_room_clients[val]:
                            room_list += (val+":")
                    room_list = room_list[:-1]
                    # Odadaki isimler yazdirilir
                    self.threadQueue.put("LST %s" % room_list)
            elif msg[0] == "QCR": 
                if not len(msg) == 2:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[1]
                    client = self.nick
                    if chat_room_name in dict_chat_room_clients.keys():
                        for key in dict_chat_room_clients:
                            if key == chat_room_name:
                                if any(client for val in dict_chat_room_clients.values()):
                                    dict_chat_room_clients[key].remove(client)
                                    # Kullanici odadan ayrildi
                                    self.threadQueue.put("GBU %s" % self.nick)
                                    client_list = ""                 
                                    if chat_room_name in dict_chat_room_clients.keys():
                                        for key in dict_chat_room_clients:
                                            if key == chat_room_name:
                                                client_list = dict_chat_room_clients[chat_room_name]                    
                                        for val in client_list:
                                            dict_client_queues[val].put("USER %s LEFT THE ROOM %s" % (self.nick, chat_room_name))
                                else:
                                    # Bu odada bu kullanici yoksa
                                    self.threadQueue.put("NUF %s" % self.nick)
                        # Odadan cikan kullanici eğer admin ise adminlikten de cikar
                        if self.nick == dict_chat_rooms[chat_room_name]:
                            dict_chat_rooms[chat_room_name] = ""
                    else:
                        # Bu isimde bir oda yoksa
                        self.threadQueue.put("CNF %s" % chat_room_name)
            elif msg[0] == "KOU": 
                if not len(msg) == 3:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[2] 
                    client = msg[1]
                    if chat_room_name in dict_chat_rooms:
                        admin = dict_chat_rooms[chat_room_name]
                        for key in dict_chat_room_clients:
                            if key == chat_room_name:
                                if any(client for val in dict_chat_room_clients.values()):
                                    if self.nick == admin:
                                        dict_chat_room_clients[key].remove(client)
                                        # Kullanici odadan atildi
                                        self.threadQueue.put("BYU %s" % client)
                                        client_list = ""                 
                                        if chat_room_name in dict_chat_room_clients.keys():
                                            for key in dict_chat_room_clients:
                                                if key == chat_room_name:
                                                    client_list = dict_chat_room_clients[chat_room_name]                    
                                            for val in client_list:
                                                dict_client_queues[val].put("USER %s IS KICKED OUT OF THE ROOM %s" % (client, chat_room_name))
                                    else:
                                        # Sadece admin odadan atabilir
                                        self.threadQueue.put("NRA")
                                else:
                                    # Bu isimde bir kullanici yoksa
                                    self.threadQueue.put("NCL %s" % client)
                    else:
                        # Bu isimde bir oda yoktur
                        self.threadQueue.put("NCR %s" % chat_room_name)
            elif msg[0] == "DEL": 
                if not len(msg) == 2:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    chat_room_name = msg[1] 
                    if chat_room_name in dict_chat_rooms.keys():
                        del dict_chat_rooms[chat_room_name]
                        if chat_room_name in dict_chat_room_clients.keys():
                            del dict_chat_room_clients[chat_room_name]
                            # Chat room silindi
                        self.threadQueue.put("CRD %s" % chat_room_name)
                    else: 
                        # Bu isimde bir oda bulunamadi
                        self.threadQueue.put("NOC %s" % chat_room_name)
            elif msg[0] == "GNL": 
                if len(msg) < 3:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    message = ""
                    chat_room_name = msg[1]
                    client_list = ""
                    for element in range (2, len(msg)):
                        message += (msg[element] + " ")                    
                    if chat_room_name in dict_chat_room_clients.keys():
                        for key in dict_chat_room_clients:
                            if key == chat_room_name:
                                client_list = dict_chat_room_clients[chat_room_name]                
                        if not self.nick in client_list:
                            # Mesaji atan kisi bu odada bulunmamaktadir
                            self.threadQueue.put("NUR %s" % self.nick)
                        else:
                            for val in client_list:
                                if not val == self.nick:
                                    # Genel mesaj odadakilere gonderildi 
                                    dict_client_queues[val].put("GNL %s: %s" % (self.nick, message))    
                            # Mesajın gittiğine dair teyit gonderilr
                            self.threadQueue.put("OKG")
                    else: 
                        self.threadQueue.put("CRF %s" % chat_room_name)
            elif msg[0] == "PRV":
                if len(msg) < 3:
                    # Komutta oda ismi belirtilmediyse
                    self.threadQueue.put("WNP")
                else:
                    client = msg[1]
                    message = ""
                    for element in range (2, len(msg)):
                        message += (msg[element] + " ") 
                    if client in dict_client_queues.keys():
                        dict_client_queues[client].put("PRV %s: %s" % (self.nick, message))
                        # Özel mesaj gonderildi
                        self.threadQueue.put("OKP")
                    else:
                        # Bu isimde bir kullanici bulunamadi
                        self.threadQueue.put("NOP %s" % client)

            else:
                # Yukaridaki komutlar haricinde bu mesaj gönderilir
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

        global dict_client_queues
        dict_client_queues = {}

        global dict_clients
        dict_clients = {}        

        global dict_chat_rooms
        dict_chat_rooms = {}

        global dict_chat_room_clients
        dict_chat_room_clients = {}

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
