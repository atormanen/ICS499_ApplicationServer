from database.DB import DB
from threading import Thread
from DataManagement.Responder import Responder
from DataManagement.MessageItem import MessageItem
import os
from GameManagement.GameGenerator import GameGenerator
from GameManagement.ValidateRequest import ValidateRequest
#from GameManagement.Tokens import Tokens


class ProcessRequest:

    #PrecessReqeust is set up to be a seperate process in the OS and
    #will hold the shared request queue object. It will pull requests
    #from the queue as they are inserted from the listener
    def __init__(self, requestQueue):
        #self.database = DB('admin','ICS4992020','chessgamedb.cxwhpucd0m6k.us-east-2.rds.amazonaws.com','userdb')
        self.database = DB('app','123','192.168.1.106','gamedb')
        self.requestQueue = requestQueue
        self.gameGenerator = GameGenerator(self.database)
        self.reqValidation = ValidateRequest()
        self.responder = Responder()

    ## TODO: find a better way to process these requests types.
    def proccesRequestType(self, reqItem):
        if self.reqValidation.isBadRequest(reqItem.parsedData):
            self.responder.sendBadRequest(reqItem.connectionSocket)
            return

        parsedData = reqItem.parsedData

        if parsedData["requestType"] == "CreateGame":
            self.gameGenerator.createGame(parsedData, reqItem)
            self.responder.sendResponse(reqItem)
        elif parsedData["requestType"] == "AcceptGame":
            self.gameGenerator.acceptGame(parsedData, reqItem)
            addr = self.database.getSocket(parsedData["player_one"])
            pOneMsgItem = MessageItem(null,addr,null)
            self.responder.sendAcceptedResponse(reqItem)
        elif parsedData["requestType"] == "MakeMove":
            return True
        elif parsedData["requestType"] == "CheckForGame":
            self.gameGenerator.checkForGame(parsedData, reqItem)
            self.responser.sendResponse(reqItem)
            return True
        elif parsedData["requestType"] == "GameRequest":
            return True
        else:
            self.responder.sendBadRequest(reqItem.connectionSocket)


    #The process thread will block on requestQueue.get() until something
    #arrives.
    def processRequests(self):
        while True:
            requestItem = self.requestQueue.get()
            #Decrypt parsedData
            self.proccesRequestType(requestItem)
