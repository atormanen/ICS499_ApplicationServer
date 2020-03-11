from GameManagement.Tokens import Tokens
import time

class GameGenerator:

    def __init__(self, mysqlDB):
        self.db = mysqlDB
        self.token = Tokens()

    def validateUsername(self, username):
        userExits = self.db.validateUserExists(username)
        if(userExits[0][0] == 1):
            print("user exits")
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
        print("signonToken: " + signonToken)
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
