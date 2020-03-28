import multiprocessing

class GameCollection:

    def __init__(self):
        self.gameDict = dict()
        self.openGameQueue = []
        self.moveQueue = []
        self.lock = multiprocessing.Lock()


    def openGameAvailable(self):
        print("Acquiring lock")
        self.lock.acquire()
        if(len(self.openGameQueue) > 0):
            self.lock.release()
            return True
        else:
            self.lock.release()
            return False

    def addOpenGame(self, game):
        print("adding open game")
        print("Acquiring lock")
        self.lock.acquire()
        print("Lock acquired")
        #self.gameDict[game.gameToken] = game
        self.openGameQueue.append(game)
        print(len(self.openGameQueue))
        self.lock.release()
        return True

    def addSecondPlayer(self, player, signonToken, playerIp, playerPort, socket):
        game = self.openGameQueue.pop(0)
        #username, signonToken, pTwoIp, pOnePort, socket
        game.addPlayerTwo(player, signonToken, playerIp, playerPort, socket)
        self.gameDict[game.gameToken] = game

    def getGame(self, gameToken):
        try:
            print("GameCollection getGame: " + self.gameDict[gameToken].gameToken)
            return self.gameDict[gameToken]
        except KeyError:
            print("KeyError")
            return False

    def makeMove(self, parsedData):
        self.lock.acquire()
        jsonObj = parsedData["move"]
        game = self.getGame(parsedData["game_token"])
        requester = parsedData["username"]
        game.makeMove(requester, jsonObj)
        self.lock.release()
