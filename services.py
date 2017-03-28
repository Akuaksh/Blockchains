import hashlib
import uuid
from itertools import product
from string import printable

from config import DIFFICULTY
from models import Block, Blockchain


class TransactionPool:
    def __init__(self):
        self.transactions = set()

    def get_transactions(self):
        return self.transactions

    def update_transactions(self, transactions):
        self.transactions = self.transactions.union(transactions)
        print "transation pool updated: ", self.transactions


class BlockchainService:
    def __init__(self):
        self.blockchains = [Blockchain()]

    def get_blockchain(self):
        return self.blockchains[0]

    def get_last_block(self):
        return self.get_blockchain().get_last_block()

    def update_blockchain(self, blockchain):
        if blockchain.length() > self.get_blockchain().length():
            if blockchain.contains_ancestor(self.get_last_block()):
                self.blockchains = [blockchain]
                print "blockchain updated: ", self.blockchains
        else:
            self.add_fork_if_valid(blockchain)

    def add_fork_if_valid(self, blockchain):
        pass

class BlockService:
    def mine(self, miner, transactions, previous_block = None):
        print "Start mining block: ", transactions, previous_block
        id = str(uuid.uuid4())
        previous_block_id = previous_block.id if previous_block is not None else '-1'

        for length in [1, 10]:
            for proof_chars in product(printable, repeat=length):
                proof = ''.join(proof_chars)
                hash = hashlib.sha256(
                    Block.generate_payload(id, miner, proof, transactions, previous_block_id)
                ).hexdigest()
                if hash[:DIFFICULTY] == '0' * DIFFICULTY:
                    block =  Block(id, miner, proof, transactions, previous_block_id)
                    print "Block successfully mined: ", block
                    return block
