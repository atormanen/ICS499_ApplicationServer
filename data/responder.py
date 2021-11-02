import socket

from data.message_item import MessageItem
from global_logger import *


# from MessageItem import MessageItem

# Responder will handle all the return messages for the servers
## TODO: clean this up... find a better way to implement responder


class Responder:
    """A Responder sends a response to the sender of a request"""
    client_port = 43489

    def __init__(self):
        self.num = 0

    @logged_method
    def send_bad_request_response(self, connection_socket: socket.socket) -> None:

        """Send a generic BAD REQUEST response"""
        msg = "{'ERROR':'BAD REQUEST'}"
        connection_socket.send(msg.encode('utf-8'))
        connection_socket.close()

    @logged_method
    #  I can't find where this is used.
    def send_requested_data(self, connection_socket: socket.socket, requested_data) -> None:

        connection_socket.send(requested_data.encode())

    @logged_method
    #  I can't find where this is used.
    def send_account_creation_status(self, connection_socket: socket.socket, status) -> None:

        status = '' + status
        connection_socket.send(status.encode())

    @logged_method
    def send_response(self, msg_item: MessageItem) -> None:

        try:
            msg_item.connection_socket.send(msg_item.response_obj.encode())
        except ConnectionResetError:
            logger.error(e)

    @logged_method
    # FIXME why don't we just use send_response method instead? I don't see any difference
    def send_random_game_response(self, msg_item):

        try:
            msg_item.connection_socket.send(msg_item.response_obj.encode())
        except ConnectionResetError:
            # This is expected
            logger.error("connection reset error")

    @logged_method
    # FIXME msg_item_p_one is only used to load unused local variables. We should simplify this if it is not needed.
    def send_accepted_response(self, msg_item_p_one, msg_item_p_two):

        try:
            ip = msg_item_p_one.ip_address  # this is unused
            port = msg_item_p_one.port  # this is unused
            msg_item_p_two.connection_socket.send(msg_item_p_two.response_obj.encode())
        except ConnectionResetError:
            # This is expected
            logger.error("connection reset error")
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.connect((ip,self.clientPort))
        # sock.send(msg_item_p_two.response_obj.encode())
        # sock.close()
