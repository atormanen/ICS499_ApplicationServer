# from _thread import *
import json
import socket
from threading import Thread

from request_processor import *


# Class listener is used to listen on a servers ip address and port portNumber
# 12345 for incoming requests.
class Listener:
    hostname = socket.gethostname()

    def __init__(self, request_queue):
        self.request_queue = request_queue
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manifest: Manifest = Manifest()
        self.buffer_size: int = self.manifest.listener_buffer_size
        self.port_number: int = self.manifest.port_number
        self.server_ip: str = ''
        self.req_count: int = 0

    @logged_method
    def create_socket(self):

        self.server_socket.bind((self.server_ip, self.port_number))
        self.server_socket.listen(5)

    @logged_method
    def set_ip(self) -> None:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = None
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except socket.error:
            ip = '127.0.0.1'
        finally:
            s.close()
            self.server_ip = ip

    @logged_method
    def send_bad_request(self, connection_socket):

        msg = "{'ERROR':'BAD REQUEST'}"
        connection_socket.send(msg.encode())

    @logged_method
    def process_request(self, connection_socket, addr):

        full_msg = ''
        rcvd_msg = ''
        buffer_exceeded = False
        while True:
            if buffer_exceeded:
                try:
                    connection_socket.settimeout(3)
                    rcvd_msg = connection_socket.recv(self.buffer_size).decode("utf-8", "replace")
                except socket.timeout as err:
                    # Expecting a timeout
                    break
                except BlockingIOError:
                    break
            else:
                try:
                    rcvd_msg = connection_socket.recv(self.buffer_size).decode("utf-8", "replace")
                except UnicodeDecodeError as e:
                    log_error(e)
                    break
                except BlockingIOError:
                    break

            full_msg += rcvd_msg
            if (len(rcvd_msg) == 0):
                break
            elif len(rcvd_msg) < self.buffer_size:
                break
            elif len(rcvd_msg) == self.buffer_size:
                rcvd_msg = ''
                buffer_exceeded = True

        try:
            # print("TEST ",self.reqCount,"  ",full_msg[1::])
            flag = True
            while (flag):
                if not (full_msg[0] == "{"):
                    full_msg = full_msg[1::]
                    if (full_msg[0] == "{"):
                        flag = False
        except (IndexError):
            return
        # print("TEST ",self.reqCount,"  ",full_msg)
        try:
            parsed_data = json.loads(full_msg)
        except (json.decoder.JSONDecodeError) as e:
            log_error(e)
            self.send_bad_request(connection_socket)
            return
        msg_item = MessageItem(connection_socket, addr, parsed_data)
        log(f"message item: {parsed_data}")
        self.request_queue.put(msg_item)

    @logged_method
    def listen(self):

        connection_socket = None
        while True:

            self.req_count = self.req_count + 1
            try:
                connection_socket, addr = self.server_socket.accept()
                log(f"received message from {str(addr)}")
                thread: Thread = Thread(target=self.process_request, args=(connection_socket, addr,))
                thread.start()
            except IOError as error:
                log_error(error)
                if connection_socket is not None:
                    connection_socket.close()

    def create_listener(self):
        self.set_ip()
        self.create_socket()
