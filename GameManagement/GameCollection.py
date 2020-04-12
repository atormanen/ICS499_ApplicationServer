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

    def checkSockets(self):
        while(True):
            #print("checking sockets")
            for game in self.gameDict:
                try:
                    game.playerOneSocket.settimeout(1)
                    rcvd_msg = game.playerOneSocket.recv(1024)
                    rcvd_msg.decode()
                    listener.processRequest(game.playerOneSocket, game.player_one_ip)
                except socket.timeout:
                    print("socket timeout")
                try:
                    game.playerTwoSocket.settimeout(1)
                    game.playerTwoSocket.recv(1024)
                    rcvd_msg.decode()
                    listener.processRequest(game.playerTwoSocket, game.player_two_ip)
                except socket.timeout:
                    print("socket timeout")

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
