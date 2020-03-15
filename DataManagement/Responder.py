import socket
import sys
#from MessageItem import MessageItem

#Responder will handle all the return messages for the servers
## TODO: clean this up... find a better way to implement responder
class Responder:
    clientPort = 43489

    def __init__(self):
        self.num = 0

    def sendBadRequest(self,connectionSocket):
        msg = "{'ERROR':'BAD REQUEST'}"
        connectionSocket.send(msg.encode('utf-8'))
        #connectionSocket.close()

    def sendRequestedData(self,connectionSocket,reqestedData):
        connectionSocket.send(requestedData.encode())

    def sendAccountCreationStatus(self, connectionSocket,status):
        status = '' + status
        connectionSocket.send(status.encode())

    def sendResponse(self, msgItem):
        try:
            msgItem.connectionSocket.send(msgItem.responseObj.encode())
        except ConnectionResetError as e:
            #This is expected
            print("ERROR: Connection reset error")

    def sendAcceptedResponse(self, msgItemPOne, msgItemPTwo):
        try:
            ip = msgItemPOne.ipAddress
            port = msgItemPOne.port
            msgItemPTwo.connectionSocket.send(msgItemPTwo.responseObj.encode())
        except ConnectionResetError as e:
            #This is expected
            print("ERROR: Connection reset error")
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.connect((ip,self.clientPort))
        #sock.send(msgItemPTwo.responseObj.encode())
        #sock.close()
