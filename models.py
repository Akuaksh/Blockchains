import hashlib

from config import DIFFICULTY


class Transaction:
    def __init__(self, id, sender, recipient, amount):
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def payload(self):
        return '__'.join([self.sender, self.recipient, str(self.amount)])

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

    @staticmethod
    def from_dict(dict):
        return Transaction(
            dict['id'],
            dict['sender'],
            dict['recipient'],
            dict['amount']
        )


class Block:
    def __init__(self, id, miner, proof, transactions, previous_block_id):
        self.id = id
        self.miner = miner
        self.proof = proof
        self.transactions = transactions
        self.previous_block_id = previous_block_id

        if not self.is_verified():
            raise RuntimeError('The block cannot be verified with the provided proof.')

    def __eq__(self, other):
        return self.id == other.id if other is not None else False

    def payload(self):
        return Block.generate_payload(
            self.id,
            self.miner,
            self.proof,
            self.transactions,
            self.previous_block_id
        )

    def is_verified(self):
        hash = hashlib.sha256(self.payload()).hexdigest()
        return hash[:DIFFICULTY] == '0' * DIFFICULTY

    def to_dict(self):
        return {
            'id': self.id,
            'miner': self.miner,
            'proof': self.proof,
            'transactions': [t.to_dict() for t in self.transactions],
            'previous_block_id': self.previous_block_id
        }

    @staticmethod
    def from_dict(dict):
        return Block(
            dict['id'],
            dict['miner'],
            dict['proof'],
            [Transaction.from_dict(t) for t in dict['transactions']],
            dict['previous_block_id']
        )

    @staticmethod
    def generate_payload(id, miner, proof, transactions, previous_block_id):
        return '__'.join(
            [id, miner, proof, previous_block_id] + [t.payload() for t in transactions]
        )


class Blockchain:
    # noinspection PyDefaultArgument
    def __init__(self, blocks=[]):
        self.blocks = blocks

    def add_block(self, block):
        self.blocks = [block] + self.blocks

    def get_last_block(self):
        return self.blocks[0] if len(self.blocks) > 0 else None

    def contains_ancestor(self, block):
        return (block is None and self.length() == 1) or \
               (block in self.blocks)

    def length(self):
        return len(self.blocks)

    def to_dict(self):
        return {
            'blocks': [b.to_dict() for b in self.blocks],
        }

    @classmethod
    def from_dict(cls, param):
        return Blockchain([Block.from_dict(b) for b in param['blocks']])
