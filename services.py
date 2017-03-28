import hashlib
import uuid
from itertools import product
from string import printable

from config import DIFFICULTY
from models import Block


class TransactionPool:
    def __init__(self):
        self.transactions = set()

    def get_transactions(self):
        return self.transactions

    def update_transactions(self, transactions):
        self.transactions = self.transactions.union(transactions)


class BlockchainService:
    def __init__(self):
        self.blockchain = []
        self.facts_pool = set()

    def get_blockchain(self):
        return self.blockchain

    def get_last_block(self):
        return self.blockchain[0]

    def update_blockchain(self, blockchain):
        pass

    # def set_blockchain(self, command, args):
    #     print "Blockchain received..."
    #
    #     if not self.blockchain_initialized:
    #         print "Blockchain not initialized : new blockchain updated."
    #         self.blockchain = [Block.from_dict(t) for t in args['blockchain']]
    #         self.blockchain_initialized = True
    #     else:
    #         print "Blockchain already initialized : new blockchain ignored."

    def mine(self, miner, transactions):
        id = str(uuid.uuid4())
        previous_block_id = self.get_last_block().id

        for length in [1, 10]:
            for proof_chars in product(printable, repeat=length):
                proof = ''.join(proof_chars)
                hash = hashlib.sha256(
                    Block.generate_payload(id, miner, proof, transactions, previous_block_id)
                ).hexdigest()
                if hash[:DIFFICULTY] == '0' * DIFFICULTY:
                    return Block(id, miner, proof, transactions, previous_block_id)
