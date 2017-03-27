import socket
from threading import Thread
from time import sleep
import uuid
import json

UDP_IP = '192.168.1.255'
UDP_PORT = 4455
UID = str(uuid.uuid4())

class ClientThread(Thread):
    def __init__(self, ip, port, message):
        Thread.__init__(self)
        self.daemon = True

        self.ip = ip
        self.port = port
        self.message = message

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

    def run(self):
        self.sock.sendto(self.message, (self.ip, self.port))

class ListeningThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
        self.daemon = True

        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.bind((ip, port))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024) 
            data_json = json.loads(data)

            if data_json['sender'] != UID:
                print "received message:", data_json['message']

def send_message(message):
    data = { 'sender': UID, 'message': message }
    client =  ClientThread(UDP_IP, UDP_PORT, json.dumps(data))
    client.start()
    client.join()

listener = ListeningThread(UDP_IP, UDP_PORT)
listener.start()

while True:
    prompt = raw_input()
    send_message(prompt)
