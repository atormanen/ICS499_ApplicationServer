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
            for game in self.gameDict:
                self.listener.processRequest(game.playerOneSocket,(game.player_one_ip,game.player_two_port))
                self.listener.processRequest(game.playerOneSocket,(game.player_one_ip,game.player_two_port))

    def openGameAvailable(self):
        if(len(self.openGameQueue) > 0):
            print("Open game available")
            return True
        else:
            return False
    def checkIfAlreadyInGame(self, game):
        for games in self.gameDict:
            if(game.player_one == games.player_one):
                return True
            elif(game.player_two == games.player_two):
                return True
        for gaems in self.openGameQueue:
            if(game.player_one == games.player_one):
                return True
            elif(game.player_two == games.player_two):
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
        print(parsedData["move"])
        game = self.getGame(parsedData["game_token"])
        requester = parsedData["username"]

        jsonObj = parsedData["move"]

        if(jsonObj == "white"):
            print("addPlayerTwoSocket")
            game.addPlayerTwoSocket(reqItem.connectionSocket)
            return
        elif(jsonObj == "black"):
            print("addPlayerOneSocket")
            game.addPlayerOneSocket(reqItem.connectionSocket)
            return


        print("did not return")
        game.makeMove(requester, jsonObj, reqItem.connectionSocket)
