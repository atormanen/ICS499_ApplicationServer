from GameManagement.Tokens import Tokens
from GameManagement.Game import Game
import multiprocessing
from threading import Thread

import time

class GameGenerator:

    def __init__(self, mysqlDB, gameQueue, gameCollection):
        self.db = mysqlDB
        self.token = Tokens()
        self.gameQueue = gameQueue
        self.gameCollection = gameCollection

    def validateUsername(self, username):
        userExits = self.db.validateUserExists(username)
        if(userExits[0][0] == 1):
            #print("user exists")
            return True
        return False

    def tokenUpToDate(self, username):
        tokenExpiration = self.db.getTokenCreationTime(username)
        currentTime = time.time()
        timeDiference = currentTime - tokenExpiration[0][0]
        if(timeDiference > 86400*5):
            return False
        return True

    def validateToken(self, username, signonToken):
        savedToken = self.db.getSignonToken(username)
        #print("signonToken: " + signonToken)
        if(savedToken == signonToken):
            return True
        return False

    def createGame(self, parsedData, reqItem):
        playerOne = parsedData["player_one"]
        playerTwo = parsedData["player_two"]
        playerOneSignonToken = parsedData["signon_token"]

        if(self.validateUsername(playerOne) == False):
            return False
        if(self.validateUsername(playerTwo) == False):
            return False
        if(self.validateToken(playerOne, playerOneSignonToken) == False):
            return False
        if(self.tokenUpToDate(playerOne) == False):
            return False

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port
        gameToken = self.token.getToken()
        self.db.createGame(gameToken, playerOne, playerOneSignonToken, playerTwo,\
                            pOneIp, pOnePort)
        reqItem.createGameRespNotAccepted(playerOne, gameToken)

    def waitForPlayer(self, gameToken):

        while(self.gameCollection.getGame(gameToken) == False):

            time.sleep(2)
        print(self.gameCollection.getGame(gameToken).gameToken)
        print("Second player received")

    def waitForGame(self):
        game = self.db.searchForGame()
        return game

    def createRandomGame(self, parsedData, reqItem):
        try:
            print(parsedData["requestType"])
            playerOne = parsedData["username"]
            playerOneSignonToken = parsedData["signon_token"]
        except KeyError:
            print("KeyError")
        #gaemToken = parsedData["game_token"]
        print(playerOne)
        if(self.validateUsername(playerOne) == False):
            return False
        if(self.validateToken(playerOne, playerOneSignonToken) == False):
            return False
        if(self.tokenUpToDate(playerOne) == False):
            return False

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        #Check for open games in game GameCollection
        #If no open games, create a game and wait for a player to join
        print("Acquiring lock")
        self.gameCollection.lock.acquire()
        print("Lock acquired")
        print(self.gameCollection.openGameAvailable())
        print("Length of open game queue: " + str(len(self.gameCollection.openGameQueue)))
        if(self.gameCollection.openGameAvailable()):
            game = self.gameCollection.addSecondPlayer(playerOne, playerOneSignonToken,\
                                pOneIp, pOnePort, reqItem.connectionSocket)
            self.gameCollection.lock.release()
            #newGame = self.db.getGame(gameToken)
            #ame.addPlayerTwo(newGame[1][7],newGame[1][12], newGame[1][9], newGame[1][11])
            game.sendGameResposne()
        else:
            gameToken = self.token.getToken()
            print("Game token: " + gameToken)
            game = Game(gameToken, parsedData, pOneIp, pOnePort, reqItem.connectionSocket)
            self.gameCollection.addOpenGame(game)
            #self.db.createRandomGame(game)
            self.gameCollection.lock.release()
            print("Lock released")
            print("Waiting for second player")




    def createRandomGameTest(self, parsedData, reqItem):
        playerOne = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        gameToken = self.token.getToken()
        game = Game(gameToken, parsedData, pOneIp, pOnePort, reqItem.connectionSocket)
        self.gameCollection.addOpenGame(game)
        self.gameCollection.getGame(gameToken)

    def acceptGame(self, parsedData, reqItem):
        playerOne = parsedData["player_one"]
        playerTwo = parsedData["player_two"]
        playerTwoSignonToken = parsedData["signon_token"]
        gameToken = parsedData["game_token"]

        if(self.validateUsername(playerOne) == False):
            return False
        if(self.validateUsername(playerTwo) == False):
            return False
        if(self.validateToken(playerTwo, playerTwoSignonToken) == False):
            return False
        if(self.tokenUpToDate(playerOne) == False):
            return False

        self.db.acceptGame(gameToken)
        self.db.updateSocket(playerTwo, reqItem.ipAddress, reqItem.port)
        gameId = self.db.getGameId(gameToken)
        self.db.createPlayer(gameId, playerTwo, reqItem.ipAddress, reqItem.port,\
            gameToken)
        reqItem.acceptGame(playerOne, playerTwo, gameToken)

    def checkForGame(self, parsedData, reqItem):
        username = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        if(self.validateUsername(username) == False):
            return False
        if(self.validateToken(username, playerOneSignonToken) == False):
            return False
        if(self.tokenUpToDate(username) == False):
            return False

        token = self.db.checkForGame(username)
        reqItem.checkForGameResponse(username, token)
