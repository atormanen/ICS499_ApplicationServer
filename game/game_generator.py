import time

from game.game import Game
from game.tokens import Tokens


class GameGenerator:
    staticCounter = 0

    def __init__(self, mysqlDB, gameQueue, gameCollection):

        self.counter = GameGenerator.staticCounter
        GameGenerator.staticCounter = GameGenerator.staticCounter + 1

        self.db = mysqlDB
        self.token = Tokens()
        self.gameQueue = gameQueue
        self.game_collection = gameCollection

    def validate_username(self, username):
        print("validateing username:", username)
        userExits = self.db.user_exists(username)
        if (userExits[0][0] == 1):
            # print("user exists")
            return True
        return False

    def token_up_to_date(self, username):
        print("checking if token is up to date:", username)
        tokenExpiration = self.db.get_token_creation_time(username)
        currentTime = time.time()
        timeDiference = currentTime - tokenExpiration[0][0]
        if (timeDiference > 86400 * 5):
            return False
        return True

    def validate_token(self, username, signon_token):
        print("validating token:", username)
        saved_token = self.db.get_signon_token(username)
        # print("signon_token: " + signon_token)
        if saved_token == signon_token:
            return True
        return False

    def create_game(self, parsed_data, req_item):
        player_one_username = parsed_data["player_one_username"]
        player_two_username = parsed_data["player_two_username"]
        print("creating game: ", player_one_username + ",", player_two_username)
        player_one_signon_token = parsed_data["signon_token"]

        if not self.validate_username(player_one_username):
            print(player_one_username, "was an invalid username")
            return False
        if not self.validate_username(player_two_username):
            print(player_two_username, "was an invalid username")
            return False
        if not self.validate_token(player_one_username, player_one_signon_token):
            print(player_one_username, "had an invalid token")
            return False
        if not self.token_up_to_date(player_one_username):
            print(player_one_username, "had an out of date token")
            return False

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port
        game_token = self.token.get_token()
        self.db.create_game(game_token, player_one_username, player_one_signon_token, player_two_username,
                            p_one_ip, p_one_port)
        req_item.create_game_resp_not_accepted(player_one_username, game_token)

        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join
        self.game_collection.lock.acquire()

        if (self.game_collection.check_if_already_in_game(player_one_username)):
            self.game_collection.lock.release()
            print(player_one_username, "already in game")
            req_item.create_random_game_resp_failure(username=player_one_username, was_successful=False,
                                                     reason="User already in game")
            return False

        #  FIXME game variable is never used after this assignment.
        game = Game(game_token, parsed_data, p_one_ip, p_one_port,
                    req_item.connection_socket, self.game_collection.listener, self.db)
        self.game_collection.lock.release()

    def wait_for_player(self, game_token):
        print("waiting for second player")

        while not self.game_collection.get_game(game_token):
            time.sleep(2)
        print(self.game_collection.get_game(game_token).game_token)
        print("Second player received")

    def wait_for_game(self):
        print("waiting for game")
        game = self.db.search_for_game()
        return game

    def request_game_canceled(self, parsed_data, req_item):
        print("canceling game request")
        try:
            username = parsed_data["username"]
            signon_token = parsed_data["signon_token"]  # FIXME by removing assignment if we are not using signon_token
        except KeyError:
            print("KeyError")
            return False
        if self.game_collection.check_if_already_in_game(username):
            game = self.game_collection.get_game(username)
            self.game_collection.remove_game(game)
            print("game removed")
            req_item.cancel_random_game_resp(username, was_successful=True)
        else:
            req_item.cancel_random_game_resp(username, was_successful=False)

    def create_random_game(self, parsed_data, req_item):
        print("creating random game")
        try:
            print(parsed_data["request_type"])
            player_one_username = parsed_data["username"]
            playerOneSignonToken = parsed_data["signon_token"]
        except KeyError:
            print("KeyError")
            return False
        # gaemToken = parsed_data["game_token"]
        print(player_one_username)
        if not self.validate_username(player_one_username):
            print(player_one_username, "username was invalid")
            req_item.create_random_game_resp_failure(player_one_username, "failure", "failed validation")
            return False
        if not self.validate_token(player_one_username, playerOneSignonToken):
            print(player_one_username, "signon Token was invalid")
            req_item.create_random_game_resp_failure(player_one_username, "failure", "failed validation")
            return False
        if not self.token_up_to_date(player_one_username):
            print(player_one_username, "signon Token was out of date")
            req_item.create_random_game_resp_failure(player_one_username, "failure", "expired token")
            return False

        print("setting ipaddress and port for", player_one_username)
        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        # Check for open games in game GameCollection
        # If no open games, create a game and wait for a player to join

        print("waiting for lock", self.counter)
        self.game_collection.lock.acquire()
        print("got lock", self.counter)

        if (self.game_collection.check_if_already_in_game(player_one_username)):
            self.game_collection.lock.release()
            print(player_one_username, "already in game")
            req_item.create_random_game_resp_failure(player_one_username, "failure", "User already in game")
            return False

        if (self.game_collection.open_game_available()):
            print("An open game is availiable")
            game = self.game_collection.add_second_player(player_one_username, playerOneSignonToken, \
                                                          p_one_ip, p_one_port, req_item.connection_socket)
            self.game_collection.lock.release()
            game.send_game_response()
        else:
            print("An open game is not availiable")
            game_token = self.token.get_token()
            game = Game(game_token, parsed_data, p_one_ip, p_one_port,
                        req_item.connection_socket, self.game_collection.listener, self.db)
            self.game_collection.add_open_game(game)
            # self.db.create_random_game(game)
            self.game_collection.lock.release()

    def create_random_game_test(self, parsed_data, req_item):
        player_one = parsed_data["username"]
        player_one_signon_token = parsed_data["signon_token"]
        p_one_ip = req_item.ip_address
        p_one_port = req_item.port

        game_token = self.token.get_token()
        game = Game(game_token, parsed_data, p_one_ip, p_one_port, req_item.connection_socket)
        self.game_collection.add_open_game(game)
        self.game_collection.get_game(game_token)

    def acceptGame(self, parsedData, reqItem):
        print("accepting game")
        playerOne = parsedData["player_one_username"]
        playerTwo = parsedData["player_two"]
        playerTwoSignonToken = parsedData["signon_token"]
        gameToken = parsedData["game_token"]

        if (self.validate_username(playerOne) == False):
            return False
        if (self.validate_username(playerTwo) == False):
            return False
        if (self.validate_token(playerTwo, playerTwoSignonToken) == False):
            return False
        if (self.token_up_to_date(playerOne) == False):
            return False

        pOneIp = reqItem.ip_address
        pOnePort = reqItem.port

        self.db.accept_game(gameToken)
        self.db.update_socket(playerTwo, reqItem.ip_address, reqItem.port)
        gameId = self.db.get_game_id(gameToken)
        self.db.create_player(gameId, playerTwo, reqItem.ip_address, reqItem.port, \
                              gameToken)
        game = self.game_collection.add_second_player(playerTwo, playerTwoSignonToken, \
                                                      pOneIp, pOnePort, reqItem.connection_socket)

    # game.sendGameResposne()

    def checkForGame(self, parsedData, reqItem):
        print("checking for game")
        username = parsedData["username"]
        playerOneSignonToken = parsedData["signon_token"]
        if (self.validate_username(username) == False):
            print(username, "was an invalid username")
            return False
        if (self.validate_token(username, playerOneSignonToken) == False):
            print(username, "had an invalid token")
            return False
        if (self.token_up_to_date(username) == False):
            print(username, "had an out of date token")
            return False

        token = self.db.check_for_game(username)
        reqItem.check_for_game_response(username, token)
