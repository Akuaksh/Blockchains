import uuid

from bottle import route, request, run

from config import UDP_IP, UDP_PORT, UID
from network import ListeningThread, CommandHandler, send_message
from services import TransactionPool, BlockchainService, BlockService
from models import Transaction, Blockchain

block_service = BlockService()
blockchain_service = BlockchainService()
transaction_pool = TransactionPool()
command_handler = CommandHandler(blockchain_service, transaction_pool)


@route('/command', method='POST')
def handle_command():
    command_handler.execute(
        request.json['name'],
        request.json.get('parameters', {}),
        request.json['sender']
    )


def retrieve_blockchain():
    send_message('broadcast_blockchain')


def main():
    print "Launching BitEcu client with UID : ", UID

    listener = ListeningThread(UDP_IP, UDP_PORT, command_handler)
    listener.start()

    # retrieve_blockchain()
    # Add a new transaction
    id = str(uuid.uuid4())
    transaction_pool.update_transactions([Transaction(id, 'max', 'jon', 50)])
    block = block_service.mine('alice', transaction_pool.get_transactions())
    blockchain_service.update_blockchain(Blockchain([block]))

    run(host='localhost', port=8080, debug=True)


main()
