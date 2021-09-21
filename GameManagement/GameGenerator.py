from GameManagement.Tokens import Tokens
from GameManagement.Game import Game
import multiprocessing
from threading import Thread

import time

class GameGenerator:

    staticCounter = 0

    def __init__(self, mysqlDB, gameQueue, gameCollection):

        self.counter = GameGenerator.staticCounter
        GameGenerator.staticCounter = GameGenerator.staticCounter + 1

        self.db = mysqlDB
        self.token = Tokens()
        self.gameQueue = gameQueue
        self.gameCollection = gameCollection

    def validateUsername(self, username):
        print("validateing username:", username)
        userExits = self.db.validateUserExists(username)
        if(userExits[0][0] == 1):
            #print("user exists")
            return True
        return False

    def tokenUpToDate(self, username):
        print("checking if token is up to date:", username)
        tokenExpiration = self.db.getTokenCreationTime(username)
        currentTime = time.time()
        timeDiference = currentTime - tokenExpiration[0][0]
        if(timeDiference > 86400*5):
            return False
        return True

    def validateToken(self, username, signonToken):
        print("validating token:", username)
        savedToken = self.db.getSignonToken(username)
        #print("signonToken: " + signonToken)
        if(savedToken == signonToken):
            return True
        return False

    def createGame(self, parsedData, reqItem):
        playerOne = parsedData["player_one"]
        playerTwo = parsedData["player_two"]
        print("creating game: ", playerOne + ",", playerTwo)
        playerOneSignonToken = parsedData["signon_token"]

        if(self.validateUsername(playerOne) == False):
            print(playerOne, "was an invalid username")
            return False
        if(self.validateUsername(playerTwo) == False):
            print(playerTwo, "was an invalid username")
            return False
        if(self.validateToken(playerOne, playerOneSignonToken) == False):
            print(playerOne, "had an invalid token")
            return False
        if(self.tokenUpToDate(playerOne) == False):
            print(playerOne, "had an out of date token")
            return False

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port
        gameToken = self.token.getToken()
        self.db.createGame(gameToken, playerOne, playerOneSignonToken, playerTwo,\
                            pOneIp, pOnePort)
        reqItem.createGameRespNotAccepted(playerOne, gameToken)

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        #Check for open games in game GameCollection
        #If no open games, create a game and wait for a player to join
        self.gameCollection.lock.acquire()

        if(self.gameCollection.checkIfAlreadyInGame(playerOne)):
            self.gameCollection.lock.release()
            print(playerOne, "already in game")
            reqItem.createRandomGameRespFailure(playerOne, "failure", "User already in game")
            return False

        game = Game(gameToken, parsedData, pOneIp, pOnePort,\
            reqItem.connectionSocket, self.gameCollection.listener, self.db)
        self.gameCollection.lock.release()

    def waitForPlayer(self, gameToken):
        print("waiting for second player")

        while(self.gameCollection.getGame(gameToken) == False):

            time.sleep(2)
        print(self.gameCollection.getGame(gameToken).gameToken)
        print("Second player received")

    def waitForGame(self):
        print("waiting for game")
        game = self.db.searchForGame()
        return game

    def requestGameCanceled(self, parsedData, reqItem):
        print("canceling game request")
        try:
            username = parsedData["username"]
            signonToken = parsedData["signon_token"]
        except KeyError:
            print("KeyError")
            return False
        if(self.gameCollection.checkIfAlreadyInGame(username)):
            game = self.gameCollection.getGame(username)
            self.gameCollection.removeGame(game)
            print("game removed")
            reqItem.cancelRandomGameResp(username , "success")
        else:
            reqItem.cancelRandomGameResp(username , "failure")


    def createRandomGame(self, parsedData, reqItem):
        print("creating random game")
        try:
            print(parsedData["requestType"])
            playerOne = parsedData["username"]
            playerOneSignonToken = parsedData["signon_token"]
        except KeyError:
            print("KeyError")
            return False
        #gaemToken = parsedData["game_token"]
        print(playerOne)
        if(self.validateUsername(playerOne) == False):
            print(playerOne, "username was invalid")
            reqItem.createRandomGameRespFailure(playerOne, "failure", "failed validation")
            return False
        if(self.validateToken(playerOne, playerOneSignonToken) == False):
            print(playerOne, "signon Token was invalid")
            reqItem.createRandomGameRespFailure(playerOne, "failure", "failed validation")
            return False
        if(self.tokenUpToDate(playerOne) == False):
            print(playerOne, "signon Token was out of date")
            reqItem.createRandomGameRespFailure(playerOne, "failure", "expired token")
            return False

        print("setting ipaddress and port for", playerOne)
        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        #Check for open games in game GameCollection
        #If no open games, create a game and wait for a player to join

        print("waiting for lock", self.counter)
        self.gameCollection.lock.acquire()
        print("got lock", self.counter)

        if(self.gameCollection.checkIfAlreadyInGame(playerOne)):
            self.gameCollection.lock.release()
            print(playerOne, "already in game")
            reqItem.createRandomGameRespFailure(playerOne, "failure", "User already in game")
            return False

        if(self.gameCollection.openGameAvailable()):
            print("An open game is availiable")
            game = self.gameCollection.addSecondPlayer(playerOne, playerOneSignonToken,\
                                pOneIp, pOnePort, reqItem.connectionSocket)
            self.gameCollection.lock.release()
            game.sendGameResposne()
        else:
            print("An open game is not availiable")
            gameToken = self.token.getToken()
            game = Game(gameToken, parsedData, pOneIp, pOnePort,\
                reqItem.connectionSocket, self.gameCollection.listener, self.db)
            self.gameCollection.addOpenGame(game)
            #self.db.createRandomGame(game)
            self.gameCollection.lock.release()


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
        print("accepting game")
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

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        self.db.acceptGame(gameToken)
        self.db.updateSocket(playerTwo, reqItem.ipAddress, reqItem.port)
        gameId = self.db.getGameId(gameToken)
        self.db.createPlayer(gameId, playerTwo, reqItem.ipAddress, reqItem.port,\
            gameToken)
        game = self.gameCollection.addSecondPlayer(playerTwo, playerTwoSignonToken,\
                            pOneIp, pOnePort, reqItem.connectionSocket)
        #game.sendGameResposne()

    def checkForGame(self, parsedData, reqItem):
        print("checking for game")
        username = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        if(self.validateUsername(username) == False):
            print(username, "was an invalid username")
            return False
        if(self.validateToken(username, playerOneSignonToken) == False):
            print(username, "had an invalid token")
            return False
        if(self.tokenUpToDate(username) == False):
            print(username, "had an out of date token")
            return False

        token = self.db.checkForGame(username)
        reqItem.checkForGameResponse(username, token)
