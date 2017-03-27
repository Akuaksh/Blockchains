import json
import socket
import uuid
from threading import Thread

from bottle import route, run, request

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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data_json = json.loads(data)

            if data_json['sender'] != UID:
                print "received message:", data_json['message']


def send_message(message):
    data = {'sender': UID, 'message': message}
    client = ClientThread(UDP_IP, UDP_PORT, json.dumps(data))
    client.start()
    client.join()


@route('/command', method='POST')
def handle_command():
    print request.json


listener = ListeningThread(UDP_IP, UDP_PORT)
listener.start()

run(host='localhost', port=8080, debug=True, reloader=True)