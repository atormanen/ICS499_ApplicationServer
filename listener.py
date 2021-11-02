# from _thread import *
import json
import socket
from threading import Thread

from request_processor import *


# Class listener is used to listen on a servers ip address and port portNumber
# 12345 for incoming requests.
class Listener:
    log_function_name = lambda x: logger.debug(f"func {inspect.stack()[1][3]}")
    hostname = socket.gethostname()

    def __init__(self, request_queue):
        self.request_queue = request_queue
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manifest: Manifest = Manifest()
        self.buffer_size: int = self.manifest.listener_buffer_size
        self.port_number: int = self.manifest.port_number
        self.server_ip: str = ''
        self.req_count: int = 0

    def create_socket(self):
        self.log_function_name()
        self.server_socket.bind((self.server_ip, self.port_number))
        self.server_socket.listen(5)

    def set_ip(self) -> None:
        self.log_function_name()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = None
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:  # FIXME too broad exception clause
            ip = '127.0.0.1'
        finally:
            s.close()
            self.server_ip = ip

    def send_bad_request(self, connection_socket):
        self.log_function_name()
        msg = "{'ERROR':'BAD REQUEST'}"
        connection_socket.send(msg.encode())

    def process_request(self, connection_socket, addr):
        self.log_function_name()
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
                    logger.error(e)
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
        except (json.decoder.JSONDecodeError):
            logger.error('unable to load json')
            self.send_bad_request(connection_socket)
            return
        msg_item = MessageItem(connection_socket, addr, parsed_data)
        logger.debug(f"message item: {parsedData}")
        self.request_queue.put(msg_item)

    def listen(self):
        self.log_function_name()
        connection_socket = None
        while True:

            self.req_count = self.req_count + 1
            try:
                connection_socket, addr = self.server_socket.accept()
                logger.debug(f"received message from {str(addr)}")
                thread: Thread = Thread(target=self.process_request, args=(connection_socket, addr,))
                thread.start()
            except IOError as error:
                logger.error(error)
                if connection_socket is not None:
                    connection_socket.close()

    def create_listener(self):
        self.set_ip()
        self.create_socket()
