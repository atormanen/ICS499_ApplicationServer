from GameManagement.Tokens import Tokens
from GameManagement.Game import Game
import multiprocessing
import time

class GameGenerator:

    def __init__(self, mysqlDB, gameQueue):
        self.db = mysqlDB
        self.token = Tokens()
        self.gameQueue = gameQueue


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
        while(self.db.validateGameExists(gameToken) == 0):
            time.sleep(2)

    def createRandomGame(self, parsedData, reqItem):
        playerOne = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]

        if(self.validateUsername(playerOne) == False):
            return False
        if(self.validateToken(playerOne, playerOneSignonToken) == False):
            return False
        if(self.tokenUpToDate(playerOne) == False):
            return False

        pOneIp = reqItem.ipAddress
        pOnePort = reqItem.port

        if(self.gameQueue.empty()):
            gameToken = self.token.getToken()
            print(gameToken)
            game = Game(gameToken, parsedData, pOneIp, pOnePort)
            self.gameQueue.put(game)
            print(self.gameQueue.empty())
            self.waitForPlayer(gameToken)
            newGame = self.db.getGame(gameToken)
            game.addPlayerTwo(newGame[1][7],newGame[1][12], newGame[1][9], newGame[1][11])
        else:
            game = self.gameQueue.get()
            game.addPlayerTwo(playerOne,playerOneSignonToken, pOneIp, pOnePort)
            self.db.createRandomGame(game)

        reqItem.createRandomGameResp(game)

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
