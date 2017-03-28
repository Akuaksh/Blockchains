from bottle import route, request, run

from config import UDP_IP, UDP_PORT, UID
from network import ListeningThread, CommandHandler, send_message
from services import TransactionPool, BlockchainService

command_handler = CommandHandler(BlockchainService(), TransactionPool())


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

    retrieve_blockchain()

    run(host='localhost', port=8080, debug=True)


main()
