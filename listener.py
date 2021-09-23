import socket
import sys
# from _thread import *
from threading import Thread
import json
from process_request import *
from multiprocessing import Process
from data.message_item import MessageItem
from manifest import Manifest


# Class listener is used to listen on a servers ip address and port portNumber
# 12345 for incoming requests.
class Listener:
    hostname = socket.gethostname()

    def __init__(self, requestQueue):
        self.requestQueue = requestQueue
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manifest = Manifest()
        self.bufferSize = self.manifest.listener_buffer_size
        self.portNumber = self.manifest.port_number
        self.serverIp = ''
        self.reqCount = 0

    def createSocket(self):
        self.serverSocket.bind((self.serverIp, self.portNumber))
        self.serverSocket.listen(5)
        # print("Server Initialized on ", self.serverIp, ":", self.portNumber)

    def set_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
            self.serverIp = IP

    def sendBadRequest(self, connectionSocket):
        # print("Error-bad request")
        msg = "{'ERROoR':'BAD REQUEST'}"
        connectionSocket.send(msg.encode())

    def processRequest(self, connectionSocket, addr):
        full_msg = ''
        rcvd_msg = ''
        bufferExceeded = False
        while True:
            if bufferExceeded:
                try:
                    connectionSocket.settimeout(3)
                    rcvd_msg = connectionSocket.recv(self.bufferSize).decode("utf-8", "replace")
                except socket.timeout as err:
                    # Expecting a timeout
                    break
                except BlockingIOError:
                    break
            else:
                try:
                    rcvd_msg = connectionSocket.recv(self.bufferSize).decode("utf-8", "replace")
                except UnicodeDecodeError:
                    print("UnicodeDecodeError")
                    break
                except BlockingIOError:
                    break

            full_msg += rcvd_msg
            if (len(rcvd_msg) == 0):
                break
            elif len(rcvd_msg) < self.bufferSize:
                break
            elif len(rcvd_msg) == self.bufferSize:
                rcvd_msg = ''
                bufferExceeded = True

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
            parsedData = json.loads(full_msg)
        except (json.decoder.JSONDecodeError):
            print("unable to load json")
            self.sendBadRequest(connectionSocket)
            # print("Badd req from listener")
            return
        msgItem = MessageItem(connectionSocket, addr, parsedData)
        self.requestQueue.put(msgItem)

    def listen(self):
        while True:
            # print(counter)
            self.reqCount = self.reqCount + 1
            try:
                # print("waiting for connection")
                connectionSocket, addr = self.serverSocket.accept()
                # print(address[0])
                thread = Thread(target=self.processRequest, args=(connectionSocket, addr,))
                thread.start()
                # is thread.join nececary?
                # thread.join()
            except IOError:
                print('Listener: IOError')
                connectionSocket.close()

    def createListener(self):
        self.set_ip()
        self.createSocket()