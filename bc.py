import hashlib
import json
import socket
import uuid
from itertools import product
from string import printable
from threading import Thread

from bottle import route, run, request

UDP_IP = '192.168.1.255'
UDP_PORT = 4455
UID = str(uuid.uuid4())

DIFFICULTY = 2

# 0. Initialize the blockchain as an empty array
def blockchain = []
def blockchain_initialized = false

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
                CommandHandler().execute(data_json['name'], data_json.get('parameters', {}))

class CommandHandler:
    def execute(self, command, args):
        print "received command:", command, args
        switch command:
            case "getblockchain":
                send_message("blockchain", { 'blockchain': blockchain })
            # 1. Initialize local blockchain from info received by other members (naive approach)
            case "blockchain":
                if !blockchain_initialized:
                    blockchain = [Block.from_dict(t) for t in args['blockchain']]
                    blockchain_initialized = true
            # 2. React to block chain updates from other users: verify ?


class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def payload(self):
        return '__'.join([self.sender, self.recipient, str(self.amount)])

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

    @staticmethod
    def from_dict(dict):
        return Transaction(
            dict['sender'],
            dict['recipient'],
            dict['amount']
        )


class Block:
    def __init__(self, id, miner, proof, transactions):
        self.id = id
        self.miner = miner
        self.proof = proof
        self.transactions = transactions

        if not self.is_verified():
            raise RuntimeError('The block cannot be verified with the provided proof.')

    def payload(self):
        return Block.generate_payload(
            self.id,
            self.miner,
            self.proof,
            self.transactions
        )

    def is_verified(self):
        hash = hashlib.sha256(self.payload()).hexdigest()
        return hash[:DIFFICULTY] == '0' * DIFFICULTY

    def to_dict(self):
        return {
            'id': self.id,
            'miner': self.miner,
            'proof': self.proof,
            'transactions': [t.to_dict() for t in self.transactions]
        }

    @staticmethod
    def generate_payload(id, miner, proof, transactions):
        return '__'.join(
            [id, miner, proof] + [t.payload() for t in transactions]
        )

    @staticmethod
    def from_dict(dict):
        return Block(
            dict['id'],
            dict['miner'],
            dict['proof'],
            [Transaction.from_dict(t) for t in dict['transactions']]
        )

    @staticmethod
    def mine(miner, transactions):
        id = str(uuid.uuid4())
        for length in [1, 10]:
            for proof_chars in product(printable, repeat=length):
                proof = ''.join(proof_chars)
                hash = hashlib.sha256(Block.generate_payload(id, miner, proof, transactions)).hexdigest()
                if hash[:DIFFICULTY] == '0' * DIFFICULTY:
                    return Block(id, miner, proof, transactions)

def send_message(name, parameters):
    data = {'sender': UID, 'name': name, 'parameters': parameters}
    client = ClientThread(UDP_IP, UDP_PORT, json.dumps(data))
    client.start()
    client.join()


@route('/command', method='POST')
def handle_command():
    CommandHandler().execute(request.json['name'], request.json.get('parameters', {}))



# TODO

# If, i'm a miner : check the transaction pool for new transactions at x sec interval
# => The pool is not empty : take n transaction and mine
# => Else, wait

# When a new block is formed, send a message to others : send proof ?



# 1. Read the blockchain status on init
# Ask for other users on the network
def read_blockchain():
    send_message('getblockchain')


print 'Mining...'
b = Block.mine('Alice', [
    Transaction('Maxime', 'Jon', 100),
    Transaction('Jon', 'Maxime', 30),
])
print 'Done : ', b.to_dict()

listener = ListeningThread(UDP_IP, UDP_PORT)
listener.start()

run(host='localhost', port=8080, debug=True, reloader=True)
