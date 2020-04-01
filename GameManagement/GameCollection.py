import multiprocessing

class GameCollection:

    def __init__(self):
        self.gameDict = dict()
        self.openGameQueue = []
        self.moveQueue = []
        self.lock = multiprocessing.Lock()


    def openGameAvailable(self):
        if(len(self.openGameQueue) > 0):
            print("Open game available")
            return True
        else:
            return False

    def addOpenGame(self, game):
        #self.gameDict[game.gameToken] = game
        self.openGameQueue.append(game)
        print(len(self.openGameQueue))
        print(id(self.openGameQueue))
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

    def makeMove(self, parsedData, reqItem):
        print(parsedData["move"])
        game = self.getGame(parsedData["game_token"])
        requester = parsedData["username"]

        jsonObj = parsedData["move"]

        if(jsonObj == "na")
            print("addPlayerTwoSocket")
            game.addPlayerTwoSocket(reqItem.connectionSocket)
            return


        print("did not return")
        game.makeMove(requester, jsonObj, reqItem.connectionSocket)
