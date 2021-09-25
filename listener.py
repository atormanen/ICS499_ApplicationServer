# from _thread import *
import json
import socket
from threading import Thread

from data.message_item import MessageItem
from manifest import Manifest
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

    def create_socket(self):
        self.server_socket.bind((self.server_ip, self.port_number))
        self.server_socket.listen(5)
        # print("Server Initialized on ", self.serverIp, ":", self.portNumber)

    def set_ip(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:  # FIXME too broad exception clause
            IP = '127.0.0.1'
        finally:
            s.close()
            self.server_ip = IP

    def send_bad_request(self, connection_socket):
        # print("Error-bad request")
        msg = "{'ERROoR':'BAD REQUEST'}"
        connection_socket.send(msg.encode())

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
                except UnicodeDecodeError:
                    print("UnicodeDecodeError")
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
            # print("error")
            return
        # print("TEST ",self.reqCount,"  ",full_msg)
        try:
            parsed_data = json.loads(full_msg)
        except (json.decoder.JSONDecodeError):
            print("unable to load json")
            self.send_bad_request(connection_socket)
            # print("Bad req from listener")
            return
        msg_item = MessageItem(connection_socket, addr, parsed_data)
        self.request_queue.put(msg_item)

    def listen(self):
        connection_socket = None
        while True:
            # print(counter)
            self.req_count = self.req_count + 1
            try:
                # print("waiting for connection")
                connection_socket, addr = self.server_socket.accept()
                # print(address[0])
                thread: Thread = Thread(target=self.process_request, args=(connection_socket, addr,))
                thread.start()
                # is thread.join nececary?
                # thread.join()
            except IOError:
                print('Listener: IOError')
                if connection_socket is not None:
                    connection_socket.close()

    def create_listener(self):
        self.set_ip()
        self.create_socket()
