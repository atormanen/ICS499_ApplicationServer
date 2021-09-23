from game.tokens import Tokens
from game.game import Game
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
        userExits = self.db.validate_user_exists(username)
        if (userExits[0][0] == 1):
            # print("user exists")
            return True
        return False

    def tokenUpToDate(self, username):
        print("checking if token is up to date:", username)
        tokenExpiration = self.db.get_token_creation_time(username)
        currentTime = time.time()
        timeDiference = currentTime - tokenExpiration[0][0]
        if (timeDiference > 86400 * 5):
            return False
        return True

    def validateToken(self, username, signonToken):
        print("validating token:", username)
        savedToken = self.db.get_signon_token(username)
        # print("signonToken: " + signonToken)
        if (savedToken == signonToken):
            return True
        return False

    def createGame(self, parsed_data, req_item):
        player_one_username = parsed_data["player_one_username"]
        player_two_username = parsed_data["player_two_username"]
        print("creating game: ", player_one_username + ",", player_two_username)
        player_one_signon_token = parsed_data["signon_token"]

        if (self.validateUsername(player_one_username) == False):
            print(player_one_username, "was an invalid username")
            return False
        if (self.validateUsername(player_two_username) == False):
            print(player_two_username, "was an invalid username")
            return False
        if (self.validateToken(player_one_username, player_one_signon_token) == False):
            print(player_one_username, "had an invalid token")
            return False
        if (self.tokenUpToDate(player_one_username) == False):
            print(player_one_username, "had an out of date token")
            return False

        pOneIp = req_item.ip_address
        pOnePort = req_item.port
        gameToken = self.token.getToken()
        self.db.create_game(gameToken, player_one_username, player_one_signon_token, player_two_username, \
                            pOneIp, pOnePort)
        req_item.create_game_resp_not_accepted(player_one_username, gameToken)

        pOneIp = req_item.ip_address
        pOnePort = req_item.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join
        self.gameCollection.lock.acquire()

        if (self.gameCollection.checkIfAlreadyInGame(player_one_username)):
            self.gameCollection.lock.release()
            print(player_one_username, "already in game")
            req_item.create_random_game_resp_failure(username=player_one_username, was_successful=False, reason="User already in game")
            return False

        game = Game(gameToken, parsed_data, pOneIp, pOnePort, \
                    req_item.connection_socket, self.gameCollection.listener, self.db)
        self.gameCollection.lock.release()

    def waitForPlayer(self, gameToken):
        print("waiting for second player")

        while (self.gameCollection.get_game(gameToken) == False):
            time.sleep(2)
        print(self.gameCollection.get_game(gameToken).game_token)
        print("Second player received")

    def waitForGame(self):
        print("waiting for game")
        game = self.db.search_for_game()
        return game

    def requestGameCanceled(self, parsedData, reqItem):
        print("canceling game request")
        try:
            username = parsedData["username"]
            signonToken = parsedData["signon_token"]
        except KeyError:
            print("KeyError")
            return False
        if (self.gameCollection.checkIfAlreadyInGame(username)):
            game = self.gameCollection.get_game(username)
            self.gameCollection.removeGame(game)
            print("game removed")
            reqItem.cancel_random_game_resp(username, was_successful=True)
        else:
            reqItem.cancel_random_game_resp(username, was_successful=False)

    def createRandomGame(self, parsedData, reqItem):
        print("creating random game")
        try:
            print(parsedData["request_type"])
            playerOne = parsedData["username"]
            playerOneSignonToken = parsedData["signon_token"]
        except KeyError:
            print("KeyError")
            return False
        # gaemToken = parsed_data["game_token"]
        print(playerOne)
        if (self.validateUsername(playerOne) == False):
            print(playerOne, "username was invalid")
            reqItem.create_random_game_resp_failure(playerOne, "failure", "failed validation")
            return False
        if (self.validateToken(playerOne, playerOneSignonToken) == False):
            print(playerOne, "signon Token was invalid")
            reqItem.create_random_game_resp_failure(playerOne, "failure", "failed validation")
            return False
        if (self.tokenUpToDate(playerOne) == False):
            print(playerOne, "signon Token was out of date")
            reqItem.create_random_game_resp_failure(playerOne, "failure", "expired token")
            return False

        print("setting ipaddress and port for", playerOne)
        pOneIp = reqItem.ip_address
        pOnePort = reqItem.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join

        print("waiting for lock", self.counter)
        self.gameCollection.lock.acquire()
        print("got lock", self.counter)

        if (self.gameCollection.checkIfAlreadyInGame(playerOne)):
            self.gameCollection.lock.release()
            print(playerOne, "already in game")
            reqItem.create_random_game_resp_failure(playerOne, "failure", "User already in game")
            return False

        if (self.gameCollection.openGameAvailable()):
            print("An open game is availiable")
            game = self.gameCollection.addSecondPlayer(playerOne, playerOneSignonToken, \
                                                       pOneIp, pOnePort, reqItem.connection_socket)
            self.gameCollection.lock.release()
            game.send_game_response()
        else:
            print("An open game is not availiable")
            gameToken = self.token.getToken()
            game = Game(gameToken, parsedData, pOneIp, pOnePort, \
                        reqItem.connection_socket, self.gameCollection.listener, self.db)
            self.gameCollection.addOpenGame(game)
            # self.db.create_random_game(game)
            self.gameCollection.lock.release()

    def createRandomGameTest(self, parsedData, reqItem):
        playerOne = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        pOneIp = reqItem.ip_address
        pOnePort = reqItem.port

        gameToken = self.token.getToken()
        game = Game(gameToken, parsedData, pOneIp, pOnePort, reqItem.connection_socket)
        self.gameCollection.addOpenGame(game)
        self.gameCollection.get_game(gameToken)

    def acceptGame(self, parsedData, reqItem):
        print("accepting game")
        playerOne = parsedData["player_one_username"]
        playerTwo = parsedData["player_two"]
        playerTwoSignonToken = parsedData["signon_token"]
        gameToken = parsedData["game_token"]

        if (self.validateUsername(playerOne) == False):
            return False
        if (self.validateUsername(playerTwo) == False):
            return False
        if (self.validateToken(playerTwo, playerTwoSignonToken) == False):
            return False
        if (self.tokenUpToDate(playerOne) == False):
            return False

        pOneIp = reqItem.ip_address
        pOnePort = reqItem.port

        self.db.accept_game(gameToken)
        self.db.update_socket(playerTwo, reqItem.ip_address, reqItem.port)
        gameId = self.db.get_game_id(gameToken)
        self.db.create_player(gameId, playerTwo, reqItem.ip_address, reqItem.port, \
                              gameToken)
        game = self.gameCollection.addSecondPlayer(playerTwo, playerTwoSignonToken, \
                                                   pOneIp, pOnePort, reqItem.connection_socket)

    # game.sendGameResposne()

    def checkForGame(self, parsedData, reqItem):
        print("checking for game")
        username = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        if (self.validateUsername(username) == False):
            print(username, "was an invalid username")
            return False
        if (self.validateToken(username, playerOneSignonToken) == False):
            print(username, "had an invalid token")
            return False
        if (self.tokenUpToDate(username) == False):
            print(username, "had an out of date token")
            return False

        token = self.db.check_for_game(username)
        reqItem.check_for_game_response(username, token)
