import json
import socket
from threading import Thread

from config import UID, UDP_IP, UDP_PORT


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


# noinspection PyDefaultArgument
def send_message(name, parameters={}):
    data = {'sender': UID, 'name': name, 'parameters': parameters}
    client = ClientThread(UDP_IP, UDP_PORT, json.dumps(data))
    client.start()
    client.join()


class CommandHandler:
    def __init__(self, blockchain_service, transaction_pool):
        self.transaction_pool = transaction_pool
        self.blockchain_service = blockchain_service

    def execute(self, command, args, sender):
        print "Command received: ", sender, command, args,
        {
            'broadcast_blockchain': self.broadcast_blockchain,
            'set_blockchain': self.set_blockchain,
            'broadcast_facts': self.broadcast_facts,
            'set_facts': self.set_facts
        }.get(command, self.command_not_found)(command, args)

    def broadcast_blockchain(self, command, args):
        print "Broadcasting blockchain as requested: ", self.blockchain_service.get_blockchain()
        send_message("set_blockchain", {'blockchain': self.blockchain_service.get_blockchain()})

    def broadcast_facts(self, command, args):
        print "Broadcasting facts as requested: ", self.transaction_pool.get_transactions()
        send_message("set_facts", {'facts': self.transaction_pool.get_transactions()})

    def set_facts(self, command, args):
        print "Facts received..."
        self.transaction_pool.update_transactions(args['facts'])
        print "New facts pool:", self.transaction_pool.get_transactions()

    def set_blockchain(self, command, args):
        print "Blockchain received..."
        self.blockchain_service.update_blockchain(args['blockchain'])

    def command_not_found(self, command, args):
        print "Command not found :", command, args


class ListeningThread(Thread):
    def __init__(self, ip, port, command_handler):
        Thread.__init__(self)
        self.daemon = True

        self.ip = ip
        self.port = port
        self.command_handler = command_handler

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data_json = json.loads(data)

            if data_json['sender'] != UID:
                self.command_handler.execute(data_json['name'], data_json.get('parameters', {}), data_json['sender'])
