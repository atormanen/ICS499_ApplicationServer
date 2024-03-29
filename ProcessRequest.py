from database.DB import DB
from threading import Thread
from DataManagement.Responder import Responder
from DataManagement.MessageItem import MessageItem
from GameManagement.GameCollection import GameCollection
import os
from GameManagement.GameGenerator import GameGenerator
from GameManagement.ValidateRequest import ValidateRequest
from Manifest import Manifest
#from GameManagement.Tokens import Tokens


class ProcessRequest:

    #PrecessReqeust is set up to be a seperate process in the OS and
    #will hold the shared request queue object. It will pull requests
    #from the queue as they are inserted from the listener
    def __init__(self, requestQueue, gameQueue, gameCollection):
        self.manifest = Manifest()
        reader = self.manifest.database_reader
        writer = self.manifest.database_writer
        username = self.manifest.database_username
        password = self.manifest.database_password
        gameDatabase = self.manifest.game_database_name
        self.database = DB(username,password,reader,writer,gameDatabase)
        #self.database = DB('app','123','192.168.1.106', '192.168.1.106','gamedb')
        self.requestQueue = requestQueue
        self.gameQueue = gameQueue
        self.reqValidation = ValidateRequest()
        self.responder = Responder()
        self.gameCollection = gameCollection
        self.gameCollection.setDatabase(self.database)
        self.gameGenerator = GameGenerator(self.database, self.gameQueue, self.gameCollection)

    ## TODO: find a better way to process these requests types.
    def proccesRequestType(self, reqItem):
        if self.reqValidation.isBadRequest(reqItem.parsedData):
            self.responder.sendBadRequest(reqItem.connectionSocket)
            return
        print(reqItem.parsedData)
        parsedData = reqItem.parsedData
        try:
            if parsedData["requestType"] == "CreateGame":
                self.gameGenerator.createGame(parsedData, reqItem)
                self.responder.sendResponse(reqItem)
            elif parsedData["requestType"] == "AcceptGame":
                self.gameGenerator.acceptGame(parsedData, reqItem)
                addr = self.database.getSocket(parsedData["player_one"])
                pOneMsgItem = MessageItem(None,addr,None)
                self.responder.sendAcceptedResponse(pOneMsgItem, reqItem)
            elif parsedData["requestType"] == "MakeMove":
                print("MakeMove!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #Find game in game GameCollection... call make move in game
                self.gameCollection.makeMove(parsedData, reqItem)
                return True
            elif parsedData["requestType"] == "CheckForGame":
                self.gameGenerator.checkForGame(parsedData, reqItem)
                self.responder.sendResponse(reqItem)
            elif parsedData["requestType"] == "RequestGame":
                result = self.gameGenerator.createRandomGame(parsedData, reqItem)
                if(result == False):
                    self.responder.sendRandomGameResponse(reqItem)
            elif parsedData["requestType"] == "RequestGameCanceled":
                self.gameGenerator.requestGameCanceled(parsedData, reqItem)
                self.responder.sendResponse(reqItem)
            else:
                self.responder.sendBadRequest(reqItem.connectionSocket)
        except KeyError:
            print("Process Request - Key error")


    #The process thread will block on requestQueue.get() until something
    #arrives.
    def processRequests(self):
        while True:
            #print("blocking on req item")
            requestItem = self.requestQueue.get()
            print("Processing request")
            #Decrypt parsedData
            self.proccesRequestType(requestItem)
