import multiprocessing
from threading import Thread

class GameCollection:

    def __init__(self, listener):
        self.listener = listener
        self.gameDict = dict()
        self.openGameQueue = []
        self.moveQueue = []
        self.lock = multiprocessing.Lock()
        self.db = ""
        #self.socketChecker()

    #This method is not used
    def checkSockets(self):
        while(True):
            #print("checking sockets")
            for key, value in self.gameDict.items():
                print("Chekcing sockets")
                print("Key: " + key + "     Value: " + value.gameToken)
                self.listener.processRequest(value.playerOneSocket,(value.player_one_ip,value.player_two_port))
                self.listener.processRequest(value.playerOneSocket,(value.player_one_ip,value.player_two_port))


    def startSocketChecker(self):
        thread = Thread(target=self.checkSockets)
        print("Starting socket checker")
        thread.start()

    def setDatabase(self, database):
        self.db = database

    def openGameAvailable(self):
        if(len(self.openGameQueue) > 0):
            print("Open game available")
            return True
        else:
            return False

    def checkIfAlreadyInGame(self, username):
        print("Inside check games")
        for key, games in self.gameDict.items():
            print("Key: " + key + "     Value: " + games.gameToken)

            if(username == games.player_one):
                if(games.checkIfStillAlive(username)):
                    self.removeGame(games)
                return True
            elif(username == games.player_two):
                if(games.checkIfStillAlive(username)):
                    self.removeGame(games)
                return True

        for games in self.openGameQueue:
            print("Value: " + games.player_one)
            if(username == games.player_one):
                if(games.checkIfStillAlive(username)):
                    print("socket not available")
                    self.removeGame(games)
                return True
            elif(username == games.player_two):
                if(games.checkIfStillAlive(username)):
                    self.removeGame(games)
                return True
        return False

    def addOpenGame(self, game):
        self.openGameQueue.append(game)
        return True

    def addSecondPlayer(self, player, signonToken, playerIp, playerPort, socket):
        game = self.openGameQueue.pop(0)
        #username, signonToken, pTwoIp, pOnePort, socket
        game.addPlayerTwo(player, signonToken, playerIp, playerPort, socket)
        self.gameDict[game.gameToken] = game
        return game

    def getGame(self, gameToken):
        try:
            print("GameCollection getGame: " + self.gameDict[gameToken].gameToken)
            return self.gameDict[gameToken]
        except KeyError:
            print("KeyError")
            return False

    def removeGame(self, game):
        removedResult = self.gameDict.pop(game.gameToken)
        return removedResult

    def makeMove(self, parsedData, reqItem):
        ## TODO: Check jsonObj for end of game
        game = self.getGame(parsedData["game_token"])
        requester = parsedData["username"]
        print(parsedData)

        jsonObj = parsedData["move"]
        print(jsonObj)

        #If this is end of game signal, save game stats in db and send end
        #game to both players
        try:
            if not(jsonObj["matchResult"] == None):
                print("matchResult" != None)
                if(jsonObj["matchResult"]["winningColor"]["name"] ==  'WHITE'):
                    #Send victory to WHITE and defeat to BLACK
                    self.db.addGameWon(game.player_two)
                    if(jsonObj["matchResult"]["type"]["name"] == 'RESIGNATION'):
                        self.db.addGameResigned(game.player_one)
                    else:
                        self.db.addGameLost(game.player_one)
                    type = jsonObj["matchResult"]["type"]["name"]
                elif(jsonObj["matchResult"]["winningColor"]["name"] ==  'BLACK'):
                    #Send victory to BLACK and defeat to WHITE
                    self.db.addGameWon(game.player_one)
                    if(jsonObj["matchResult"]["type"]["name"] == 'RESIGNATION'):
                        self.db.addGameResigned(game.player_two)
                    else:
                        self.db.addGameLost(game.player_two)
                    type = jsonObj["matchResult"]["type"]["name"]
                elif(jsonObj["matchResult"]["winningColor"]["name"] ==  None):
                    #Draw
                    type = jsonObj["matchResult"]["type"]["name"]

                game.lastMove = True
                game.makeMove(requester, jsonObj, game.playerOneSocket)
                game.makeMove(requester, jsonObj, game.playerTwoSocket)
                if(game.lastMove == True):
                    self.removeGame(game)
                    game.playerTwoSocket.close()
                    game.playerOneSocket.close()
                    print("closed player one socket")
                    print("closed player one socket")

                game.gameClosedFlag = True
                return False
        except TypeError:
            print("Type error")


        #Weird way to tell which socket is associated with which player
        #Only runs on initial startup of game
        if(jsonObj == "white"):
            print("addPlayerTwoSocket")
            game.addPlayerTwoSocket(reqItem.connectionSocket)
            return
        elif(jsonObj == "black"):
            print("addPlayerOneSocket")
            game.addPlayerOneSocket(reqItem.connectionSocket)
            return

        game.makeMove(requester, jsonObj, reqItem.connectionSocket)
