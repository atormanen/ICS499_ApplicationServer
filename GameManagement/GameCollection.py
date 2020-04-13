import multiprocessing
from threading import Thread

class GameCollection:

    def __init__(self, listener):
        self.listener = listener
        self.gameDict = dict()
        self.openGameQueue = []
        self.moveQueue = []
        self.lock = multiprocessing.Lock()
        self.socketChecker()


    def socketChecker(self):
        thread = Thread(target=self.checkSockets)
        print("Starting socket checker")
        thread.start()

    #This method is not used
    def checkSockets(self):
        while(True):
            #print("checking sockets")
            for key, value in self.gameDict.items():
                print("Chekcing sockets")
                self.listener.processRequest(value.playerOneSocket,(value.player_one_ip,value.player_two_port))
                self.listener.processRequest(value.playerOneSocket,(value.player_one_ip,value.player_two_port))

    def openGameAvailable(self):
        if(len(self.openGameQueue) > 0):
            print("Open game available")
            return True
        else:
            return False

    def checkIfAlreadyInGame(self, username):
        for games in self.gameDict:
            if(username == games.player_one):
                return True
            elif(username == games.player_two):
                return True
        for games in self.openGameQueue:
            if(username == games.player_one):
                return True
            elif(username == games.player_two):
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

        #If this is end of game signal, save game stats in db and send end
        #game to both players


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
